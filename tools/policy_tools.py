"""Sample policy-related tools used during development."""

from __future__ import annotations

from typing import Any, Dict

from tools.mcp_client import list_tools, register_tool

POLICY_DB: Dict[str, Dict[str, Any]] = {
    "term_basic": {
        "name": "Basic Term Life",
        "duration_years": 20,
        "monthly_premium": 25.0,
        "description": "Affordable coverage for a fixed 20 year period.",
    },
    "whole_classic": {
        "name": "Classic Whole Life",
        "duration_years": "lifetime",
        "monthly_premium": 75.0,
        "description": "Lifetime coverage with cash value growth.",
    },
}


def lookup_policy(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Return policy details based on a policy identifier."""
    policy_id = arguments.get("policy_id")
    if not policy_id:
        raise ValueError("policy_id argument is required.")
    if policy_id not in POLICY_DB:
        raise ValueError(f"Unknown policy_id '{policy_id}'.")
    return POLICY_DB[policy_id]


def list_policy_ids(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return available policy identifiers."""
    return {"policies": list(POLICY_DB.keys())}


def register_default_tools() -> None:
    """Register default development tools."""
    if "lookup_policy" not in list_tools():
        register_tool(
            "lookup_policy",
            lookup_policy,
            description="Retrieve policy details by policy_id.",
        )
    if "list_policies" not in list_tools():
        register_tool(
            "list_policies",
            list_policy_ids,
            description="List available policy identifiers.",
        )

