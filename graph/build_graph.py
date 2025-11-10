"""LangGraph assembly for the sales agent conversation flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from graph.nodes import action, decider, planner, reflector, retriever
from state.memory import apply_long_term_memory, apply_short_term_memory
from state.schemas import ConversationState


@dataclass
class ConversationGraph:
    """Lightweight conversation graph used until LangGraph integration."""

    planner_chain: Optional[object] = None
    retriever_chain: Optional[object] = None
    action_chain: Optional[object] = None
    enable_reflection: bool = False

    def run_turn(self, state: Optional[ConversationState] = None) -> ConversationState:
        state = state or ConversationState()

        planner.plan_next_step(state, chain=self.planner_chain)
        next_step = decider.decide_next_action(state)

        if next_step == "retriever":
            retriever.retrieve_context(state, chain=self.retriever_chain)
            next_step = decider.decide_next_action(state)

        if next_step == "action":
            action.execute_action(state, chain=self.action_chain)
        elif next_step == "end":
            state.metadata["conversation_status"] = "completed"

        if self.enable_reflection:
            reflector.reflect_on_conversation(state)

        apply_short_term_memory(state)
        apply_long_term_memory(state)
        return state


def build_conversation_graph(
    *,
    planner_chain: Optional[object] = None,
    retriever_chain: Optional[object] = None,
    action_chain: Optional[object] = None,
    enable_reflection: bool = False,
) -> ConversationGraph:
    """Construct and return the conversation graph wrapper."""
    return ConversationGraph(
        planner_chain=planner_chain,
        retriever_chain=retriever_chain,
        action_chain=action_chain,
        enable_reflection=enable_reflection,
    )

