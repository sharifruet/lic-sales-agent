"""Structured output parsers for LangChain/LangGraph nodes."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from state.schemas import PlanDecision, RetrievedDocument


class PlannerOutput(BaseModel):
    """Structured output from the planner chain."""

    decision: PlanDecision
    rationale: str = Field(..., min_length=1)
    plan_steps: List[str] = Field(default_factory=list)
    pending_tool: Optional[str] = None


def _coerce_payload(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError("Planner output string is not valid JSON.") from exc
    if isinstance(data, PlannerOutput):
        return data.model_dump()
    raise ValueError(f"Unsupported planner output type: {type(data)!r}")


def parse_planner_output(data: Any) -> PlannerOutput:
    """Parse raw planner output into a structured object."""
    payload = _coerce_payload(data)
    try:
        return PlannerOutput(**payload)
    except ValidationError as exc:
        raise ValueError("Planner output is missing required fields.") from exc


def parse_action_output(data: Any) -> Any:
    """Placeholder parser for action responses."""
    raise NotImplementedError("Action parser not yet implemented.")


class RetrieverOutput(BaseModel):
    """Structured output from retriever chain."""

    results: List[RetrievedDocument] = Field(default_factory=list)


def parse_retriever_output(data: Any) -> RetrieverOutput:
    """Parse raw retriever output into structured form."""
    if isinstance(data, RetrieverOutput):
        return data
    if isinstance(data, list):
        payload = {"results": data}
    elif isinstance(data, dict):
        payload = data
    elif isinstance(data, str):
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError("Retriever output string is not valid JSON.") from exc
    else:
        raise ValueError(f"Unsupported retriever output type: {type(data)!r}")

    try:
        return RetrieverOutput(**payload)
    except ValidationError as exc:
        raise ValueError("Retriever output is missing required fields.") from exc


class ActionToolCall(BaseModel):
    """Structured representation of a tool invocation."""

    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ActionOutput(BaseModel):
    """Structured response from the action chain."""

    message: Optional[str] = None
    tool_call: Optional[ActionToolCall] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


def parse_action_output(data: Any) -> ActionOutput:
    """Parse raw action output into structured form."""
    if isinstance(data, ActionOutput):
        return data
    if isinstance(data, dict):
        payload = data
    elif isinstance(data, str):
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError("Action output string is not valid JSON.") from exc
    else:
        raise ValueError(f"Unsupported action output type: {type(data)!r}")

    try:
        result = ActionOutput(**payload)
    except ValidationError as exc:
        raise ValueError("Action output is missing required fields.") from exc

    if not result.message and not result.tool_call:
        raise ValueError("Action output must include a message or a tool_call.")
    return result

