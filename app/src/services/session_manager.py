from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import json
from redis import asyncio as redis_async

from app.src.config import settings


class ConversationStage(str, Enum):
    INTRODUCTION = "introduction"
    QUALIFICATION = "qualification"
    INFORMATION = "information"
    PERSUASION = "persuasion"
    OBJECTION_HANDLING = "objection_handling"
    INFORMATION_COLLECTION = "information_collection"
    CLOSING = "closing"
    ENDED = "ended"


class InterestLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CustomerProfile:
    age: Optional[int] = None
    current_coverage: Optional[str] = None
    purpose: Optional[str] = None
    coverage_amount_interest: Optional[str] = None
    dependents: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


@dataclass
class CollectedData:
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    nid: Optional[str] = None
    address: Optional[str] = None
    policy_of_interest: Optional[str] = None
    email: Optional[str] = None
    preferred_contact_time: Optional[str] = None
    notes: Optional[str] = None

    def is_complete(self) -> bool:
        return all(
            [
                self.full_name,
                self.phone_number,
                self.nid,
                self.address,
                self.policy_of_interest,
            ]
        )


@dataclass
class SessionState:
    session_id: str
    conversation_id: int
    conversation_stage: ConversationStage = ConversationStage.INTRODUCTION
    customer_profile: CustomerProfile = field(default_factory=CustomerProfile)
    collected_data: CollectedData = field(default_factory=CollectedData)
    interest_level: InterestLevel = InterestLevel.NONE
    message_count: int = 0
    context_summary: str = ""
    awaiting_confirmation: bool = False  # Track if waiting for confirmation
    confirmation_attempts: int = 0  # Track number of confirmation attempts
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SessionManager:
    """Lightweight Redis-backed session manager for conversation state."""

    def __init__(self, redis_client: Optional[redis_async.Redis] = None):
        self._redis = redis_client or redis_async.from_url(
            settings.redis_url, password=settings.redis_password, decode_responses=True
        )
        self._ttl = settings.session_ttl

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    async def create_session(self, session_id: str, conversation_id: int) -> SessionState:
        state = SessionState(session_id=session_id, conversation_id=conversation_id)
        await self.save_session(state)
        return state

    async def get_session(self, session_id: str) -> Optional[SessionState]:
        raw = await self._redis.get(self._key(session_id))
        if not raw:
            return None
        data = json.loads(raw)
        return self._deserialize(data)

    async def save_session(self, state: SessionState) -> None:
        payload = self._serialize(state)
        await self._redis.setex(self._key(state.session_id), self._ttl, json.dumps(payload))

    async def delete_session(self, session_id: str) -> None:
        await self._redis.delete(self._key(session_id))

    async def touch(self, session_id: str) -> None:
        state = await self.get_session(session_id)
        if not state:
            return
        state.last_activity = datetime.now(timezone.utc)
        await self.save_session(state)

    def _serialize(self, state: SessionState) -> Dict[str, Any]:
        def dt_to_str(dt: datetime) -> str:
            return dt.astimezone(timezone.utc).isoformat()

        return {
            "session_id": state.session_id,
            "conversation_id": state.conversation_id,
            "conversation_stage": state.conversation_stage.value,
            "customer_profile": asdict(state.customer_profile),
            "collected_data": asdict(state.collected_data),
            "interest_level": state.interest_level.value,
            "message_count": state.message_count,
            "context_summary": state.context_summary,
            "awaiting_confirmation": state.awaiting_confirmation,
            "confirmation_attempts": state.confirmation_attempts,
            "created_at": dt_to_str(state.created_at),
            "last_activity": dt_to_str(state.last_activity),
        }

    def _deserialize(self, data: Dict[str, Any]) -> SessionState:
        def parse_dt(value: str) -> datetime:
            return datetime.fromisoformat(value)

        return SessionState(
            session_id=data["session_id"],
            conversation_id=int(data["conversation_id"]),
            conversation_stage=ConversationStage(data["conversation_stage"]),
            customer_profile=CustomerProfile(**data.get("customer_profile", {})),
            collected_data=CollectedData(**data.get("collected_data", {})),
            interest_level=InterestLevel(data.get("interest_level", InterestLevel.NONE)),
            message_count=int(data.get("message_count", 0)),
            context_summary=data.get("context_summary", ""),
            awaiting_confirmation=data.get("awaiting_confirmation", False),
            confirmation_attempts=int(data.get("confirmation_attempts", 0)),
            created_at=parse_dt(data["created_at"]),
            last_activity=parse_dt(data["last_activity"]),
        )


