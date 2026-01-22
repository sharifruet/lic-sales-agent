"""LangChain Runnable pipelines used by graph nodes."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from rag.retriever import get_retriever


class PlannerChain(Protocol):
    """Protocol describing planner chain call signature."""

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        ...


class _NotImplementedPlannerChain:
    """Default planner chain that applies heuristic planning rules."""

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        history: List[Dict[str, Any]] = inputs.get("history", [])
        objective: Optional[str] = inputs.get("objective") or inputs.get("current_objective")
        metadata: Dict[str, Any] = inputs.get("metadata") or {}

        latest_user = ""
        for message in reversed(history):
            if message.get("message_type") == "user":
                latest_user = message.get("content", "")
                break

        plan_steps: List[str] = []
        if objective:
            plan_steps.append(f"Advance objective: {objective}")
        if latest_user:
            plan_steps.append("Acknowledge latest customer message.")

        decision = "continue"
        pending_tool = None
        lowered = latest_user.lower()

        if metadata.get("requires_tool"):
            decision = "tool"
            pending_tool = metadata["requires_tool"]
        elif "policy" in lowered or "rate" in lowered or "premium" in lowered:
            decision = "retrieve"
        elif metadata.get("conversation_status") == "completed":
            decision = "end"

        rationale_parts = []
        if latest_user:
            rationale_parts.append(f"Customer asked about: '{latest_user[:60]}'")
        if decision == "retrieve":
            rationale_parts.append("Need supporting knowledge before responding.")
        elif decision == "tool":
            rationale_parts.append(f"Trigger tool: {pending_tool}.")
        elif decision == "end":
            rationale_parts.append("Conversation marked as complete.")
        else:
            rationale_parts.append("Provide a direct response.")

        return {
            "decision": decision,
            "rationale": " ".join(rationale_parts) or "Continue the conversation.",
            "plan_steps": plan_steps[:3],
            "pending_tool": pending_tool,
        }


def build_planner_chain() -> PlannerChain:
    """Return the planner runnable."""
    return _NotImplementedPlannerChain()


class RetrieverChain(Protocol):
    """Protocol describing retriever chain call signature."""

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        ...


class _SimpleRetrieverChain:
    """Retriever chain that delegates to the in-memory retriever."""

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:  # pragma: no cover - thin wrapper
        retriever = get_retriever()
        query = inputs.get("query") or ""
        top_k = inputs.get("top_k", 3)
        results = retriever(query, top_k=top_k)
        return {"results": results}


def build_retriever_chain() -> RetrieverChain:
    """Return the retriever runnable."""
    return _SimpleRetrieverChain()


class ActionChain(Protocol):
    """Protocol describing action chain signature."""

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        ...


class _HeuristicActionChain:
    """Simple action chain that crafts responses based on retrieved context."""

    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pending_tool = inputs.get("pending_tool_call")
        if pending_tool:
            return {"message": None, "tool_call": {"name": pending_tool, "arguments": inputs.get("tool_arguments", {})}, "confidence": 0.6}

        retrieved_context: List[Dict[str, Any]] = inputs.get("retrieved_context") or []
        plan_steps: List[str] = inputs.get("plan_steps") or []
        history: List[Dict[str, Any]] = inputs.get("history") or []

        latest_user = ""
        for message in reversed(history):
            if message.get("message_type") == "user":
                latest_user = message.get("content", "")
                break

        if retrieved_context:
            snippet = retrieved_context[0]["content"]
            message = f"Based on our policies: {snippet}"
        elif plan_steps:
            message = f"Let's proceed: {plan_steps[0]}"
        elif latest_user:
            message = f"I understand: {latest_user}"
        else:
            message = "How else may I assist you today?"

        return {"message": message, "tool_call": None, "confidence": 0.75}


def build_action_chain() -> ActionChain:
    """Return the action runnable."""
    return _HeuristicActionChain()

