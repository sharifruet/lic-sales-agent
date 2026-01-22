"""Tests for tool integrations."""

import pytest

from tools import register_default_tools
from tools.mcp_client import execute_tool, list_tools, register_tool


def test_register_and_execute_custom_tool() -> None:
    def echo(arguments):
        return {"echo": arguments.get("value")}

    register_tool("echo_tool", echo, description="Echo back the provided value.")
    result = execute_tool("echo_tool", {"value": "hello"})
    assert result == {"echo": "hello"}
    assert "echo_tool" in list_tools()


def test_default_policy_tools_available() -> None:
    register_default_tools()
    assert "lookup_policy" in list_tools()
    payload = execute_tool("lookup_policy", {"policy_id": "term_basic"})
    assert payload["name"] == "Basic Term Life"


def test_execute_unknown_tool_raises() -> None:
    with pytest.raises(ValueError):
        execute_tool("non_existent_tool", {})
