"""Legacy base provider - use llm_provider.py and ollama_provider.py instead."""
# This file is kept for backward compatibility
# New code should use src.llm.providers.ollama_provider.OllamaProvider

from app.src.llm.providers.ollama_provider import OllamaProvider

__all__ = ["OllamaProvider"]
