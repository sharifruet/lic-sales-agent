"""Model Context Protocol client wrappers and tool registry."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

ToolCallable = Callable[[Dict[str, Any]], Any]


class MCPClient:
    """Simple in-memory registry for agent tools."""

    def __init__(self) -> None:
        self._registry: Dict[str, ToolCallable] = {}
        self._metadata: Dict[str, str] = {}

    def register_tool(self, name: str, func: ToolCallable, *, description: Optional[str] = None) -> None:
        if not callable(func):
            raise TypeError("Tool must be callable.")
        self._registry[name] = func
        if description:
            self._metadata[name] = description

    def list_tools(self) -> List[str]:
        return list(self._registry.keys())

    def get_description(self, name: str) -> str:
        return self._metadata.get(name, "")

    def execute_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        if name not in self._registry:
            raise ValueError(f"Tool '{name}' is not registered.")
        arguments = arguments or {}
        return self._registry[name](arguments)


_client = MCPClient()


def register_tool(name: str, func: ToolCallable, *, description: Optional[str] = None) -> None:
    _client.register_tool(name, func, description=description)


def execute_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
    return _client.execute_tool(name, arguments)


def list_tools() -> List[str]:
    return _client.list_tools()


def get_tool_description(name: str) -> str:
    return _client.get_description(name)

