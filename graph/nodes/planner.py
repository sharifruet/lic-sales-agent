"""Conversation planner node used within the LangGraph pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional 

from chains.parsers import PlannerOutput, parse_planner_output
from chains.runnables import PlannerChain, build_planner_chain
from state.schemas import ConversationState, Message, MessageType


def _build_planner_inputs(state: ConversationState) -> Dict[str, Any]:
    return {
        "objective": state.current_objective,
        "history": [message.model_dump() for message in state.messages],
        "metadata": state.metadata,
    }


def _append_planner_message(state: ConversationState, planner_output: PlannerOutput) -> None:
    state.messages.append(
        Message(
            role="system",
            content=planner_output.rationale,
            timestamp=datetime.now(timezone.utc),
            message_type=MessageType.PLANNER,
            metadata={
                "decision": planner_output.decision.value,
            },
        )
    )


def plan_next_step(
    state: ConversationState,
    chain: Optional[PlannerChain] = None,
) -> ConversationState:
    """Run the planner chain and update conversation state."""
    planner_chain = chain or build_planner_chain()
    raw_output = planner_chain(_build_planner_inputs(state))
    planner_output = parse_planner_output(raw_output)

    state.plan_steps = planner_output.plan_steps
    state.planner_rationale = planner_output.rationale
    state.pending_tool_call = planner_output.pending_tool
    state.next_action = planner_output.decision

    _append_planner_message(state, planner_output)
    return state

