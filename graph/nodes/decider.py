"""Decision node selects next action based on state."""

from __future__ import annotations

from state.schemas import ConversationState, PlanDecision


def decide_next_action(state: ConversationState) -> str:
    """Return the identifier of the next node to execute."""
    decision = state.next_action or PlanDecision.CONTINUE

    if decision is PlanDecision.RETRIEVE:
        if not state.retrieved_context:
            return "retriever"
        return "action"

    if decision is PlanDecision.TOOL:
        return "action"

    if decision is PlanDecision.END:
        return "end"

    return "action"

