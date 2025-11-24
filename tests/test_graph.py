"""Tests for LangGraph integration scaffolding."""

from datetime import datetime, timezone
from typing import Any, Dict

import pytest

from chains.parsers import (
    ActionOutput,
    PlannerOutput,
    RetrieverOutput,
    parse_planner_output,
)
from graph import build_graph
from graph.nodes import action as action_node
from graph.nodes import decider as decider_node
from graph.nodes import planner
from graph.nodes import reflector as reflector_node
from graph.nodes import retriever as retriever_node
from state.schemas import (
    ConversationState,
    Message,
    MessageType,
    PlanDecision,
    RetrievedDocument,
)
from tools import register_default_tools


def test_graph_build_placeholder() -> None:
    """Ensure the build function exists."""
    assert callable(build_graph.build_conversation_graph)


def test_parse_planner_output_from_dict() -> None:
    payload = {
        "decision": "retrieve",
        "rationale": "Need more policy details.",
        "plan_steps": ["Collect beneficiary info"],
        "pending_tool": None,
    }
    result = parse_planner_output(payload)
    assert result.decision is PlanDecision.RETRIEVE
    assert result.plan_steps == ["Collect beneficiary info"]
    assert result.pending_tool is None


def test_plan_next_step_updates_state(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_output = PlannerOutput(
        decision=PlanDecision.RETRIEVE,
        rationale="Gather more family information.",
        plan_steps=["Ask about dependents", "Confirm policy preferences"],
        pending_tool=None,
    )

    def fake_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return fake_output.model_dump()

    initial_state = ConversationState(
        messages=[
            Message(
                role="user",
                content="I want to know about policies.",
                timestamp=datetime.now(timezone.utc),
                message_type=MessageType.USER,
            )
        ],
        current_objective="Qualify the lead",
    )

    updated_state = planner.plan_next_step(initial_state, chain=fake_chain)

    assert updated_state.plan_steps == fake_output.plan_steps
    assert updated_state.planner_rationale == fake_output.rationale
    assert updated_state.next_action is PlanDecision.RETRIEVE
    assert updated_state.pending_tool_call is None
    assert updated_state.messages[-1].message_type is MessageType.PLANNER
    assert "decision" in updated_state.messages[-1].metadata


def test_plan_next_step_invalid_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"foo": "bar"}

    state = ConversationState(
        messages=[],
        current_objective="Collect basic information",
    )

    with pytest.raises(ValueError):
        planner.plan_next_step(state, chain=bad_chain)


def test_decider_routes_based_on_plan() -> None:
    state = ConversationState(next_action=PlanDecision.RETRIEVE)
    assert decider_node.decide_next_action(state) == "retriever"

    state.retrieved_context.append(
        RetrievedDocument(content="doc", source=None, score=None, metadata={})
    )
    assert decider_node.decide_next_action(state) == "action"

    state.next_action = PlanDecision.END
    assert decider_node.decide_next_action(state) == "end"


def test_action_node_appends_message() -> None:
    state = ConversationState(
        messages=[
            Message(
                role="assistant",
                content="Previous answer",
                timestamp=datetime.now(timezone.utc),
                message_type=MessageType.ASSISTANT,
            )
        ],
        plan_steps=["Provide quote overview"],
    )

    def fake_action_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "message": "Here is information about your requested policy.",
            "tool_call": None,
            "confidence": 0.9,
        }

    updated_state = action_node.execute_action(state, chain=fake_action_chain)

    assert updated_state.messages[-1].message_type is MessageType.ASSISTANT
    assert "confidence" in updated_state.messages[-1].metadata
    assert updated_state.pending_tool_call is None


def test_action_node_sets_tool_call() -> None:
    register_default_tools()
    state = ConversationState(messages=[])

    def fake_action_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "message": None,
            "tool_call": {"name": "list_policies", "arguments": {}},
        }

    updated_state = action_node.execute_action(state, chain=fake_action_chain)
    assert updated_state.pending_tool_call is None
    assert updated_state.messages[-1].message_type is MessageType.TOOL
    assert "policies" in updated_state.messages[-1].content


def test_planner_retriever_action_integration(monkeypatch: pytest.MonkeyPatch) -> None:
    planner_output = PlannerOutput(
        decision=PlanDecision.RETRIEVE,
        rationale="Need supporting documents.",
        plan_steps=["Retrieve data"],
        pending_tool=None,
    )
    retriever_output = RetrieverOutput(
        results=[
            RetrievedDocument(
                content="Whole life policy overview",
                source="kb/whole_life.md",
                score=0.9,
                metadata={},
            )
        ]
    )
    action_output = ActionOutput(
        message="Whole life policies offer lifetime coverage.",
        tool_call=None,
        confidence=0.8,
    )

    def fake_planner_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return planner_output.model_dump()

    def fake_retriever_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return retriever_output.model_dump()

    def fake_action_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return action_output.model_dump()

    state = ConversationState(
        messages=[
            Message(
                role="user",
                content="Tell me about whole life insurance.",
                timestamp=datetime.now(timezone.utc),
                message_type=MessageType.USER,
            )
        ]
    )

    planner.plan_next_step(state, chain=fake_planner_chain)
    retriever_node.retrieve_context(state, chain=fake_retriever_chain)
    action_node.execute_action(state, chain=fake_action_chain)

    assert state.plan_steps == planner_output.plan_steps
    assert state.retrieved_context[0].content == retriever_output.results[0].content
    assert state.messages[-1].content == action_output.message


def test_conversation_graph_run_turn() -> None:
    planner_output = PlannerOutput(
        decision=PlanDecision.RETRIEVE,
        rationale="Need context.",
        plan_steps=["Retrieve info", "Respond"],
        pending_tool=None,
    )

    retriever_output = RetrieverOutput(
        results=[
            RetrievedDocument(
                content="Policy summary",
                source="kb/policy.md",
                score=0.95,
                metadata={},
            )
        ]
    )

    action_output = ActionOutput(
        message="Here is a summary of the policy.",
        tool_call=None,
        confidence=0.7,
    )

    def fake_planner_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return planner_output.model_dump()

    def fake_retriever_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return retriever_output.model_dump()

    def fake_action_chain(_: Dict[str, Any]) -> Dict[str, Any]:
        return action_output.model_dump()

    graph = build_graph.build_conversation_graph(
        planner_chain=fake_planner_chain,
        retriever_chain=fake_retriever_chain,
        action_chain=fake_action_chain,
        enable_reflection=True,
    )

    state = ConversationState(
        messages=[
            Message(
                role="user",
                content="I need information about policies.",
                timestamp=datetime.now(timezone.utc),
                message_type=MessageType.USER,
            )
        ]
    )

    updated_state = graph.run_turn(state)

    assert updated_state.retrieved_context
    assert updated_state.messages[-1].message_type in {MessageType.SYSTEM, MessageType.ASSISTANT}
    assert any(msg.message_type is MessageType.SYSTEM for msg in updated_state.messages)

