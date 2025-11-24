"""Action node executes interactions with the user or tools."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from chains.parsers import ActionOutput, parse_action_output
from chains.runnables import ActionChain, build_action_chain
from state.schemas import ConversationState, Message, MessageType
from tools.mcp_client import execute_tool


def _build_action_inputs(state: ConversationState) -> Dict[str, Any]:
    return {
        "plan_steps": state.plan_steps,
        "planner_rationale": state.planner_rationale,
        "retrieved_context": [doc.model_dump() for doc in state.retrieved_context],
        "current_objective": state.current_objective,
        "history": [message.model_dump() for message in state.messages],
        "pending_tool_call": state.pending_tool_call,
    }


def _append_assistant_message(state: ConversationState, action_output: ActionOutput) -> None:
    if action_output.message:
        state.messages.append(
            Message(
                role="assistant",
                content=action_output.message,
                timestamp=datetime.now(timezone.utc),
                message_type=MessageType.ASSISTANT,
                metadata={
                    "confidence": str(action_output.confidence or ""),
                },
            )
        )


def execute_action(
    state: ConversationState,
    chain: Optional[ActionChain] = None,
) -> ConversationState:
    """Run the action chain to generate assistant response or tool call."""
    action_chain = chain or build_action_chain()
    raw_output = action_chain(_build_action_inputs(state))
    action_output = parse_action_output(raw_output)

    _append_assistant_message(state, action_output)

    if action_output.tool_call:
        tool_name = action_output.tool_call.name
        arguments = action_output.tool_call.arguments or {}
        try:
            result = execute_tool(tool_name, arguments)
        except Exception as exc:  # pragma: no cover - defensive
            state.messages.append(
                Message(
                    role="system",
                    content=f"Tool '{tool_name}' failed: {exc}",
                    timestamp=datetime.now(timezone.utc),
                    message_type=MessageType.SYSTEM,
                )
            )
            state.metadata["tool_error"] = str(exc)
        else:
            state.messages.append(
                Message(
                    role="tool",
                    content=str(result),
                    timestamp=datetime.now(timezone.utc),
                    message_type=MessageType.TOOL,
                    metadata={"tool": tool_name},
                )
            )
            state.metadata["last_tool_result"] = str(result)
        finally:
            state.pending_tool_call = None
            state.metadata.pop("tool_arguments", None)
    else:
        state.pending_tool_call = None
        state.metadata.pop("tool_arguments", None)

    return state

