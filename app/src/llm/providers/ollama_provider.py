"""Ollama LLM provider implementation."""
from typing import List, Dict, Any, Optional
import json
import httpx

from src.llm.providers.llm_provider import (
    LLMProvider,
    LLMConfig,
    LLMResponse,
    Message,
    Intent,
)
from src.config import settings


class OllamaProvider(LLMProvider):
    """Ollama provider implementation."""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.client = httpx.AsyncClient(timeout=settings.llm_timeout)
    
    async def generate_response(
        self,
        messages: List[Message],
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Generate response using Ollama API."""
        if config is None:
            config = LLMConfig(
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
        
        try:
            # Format messages for Ollama (simple prompt format)
            prompt = self._format_messages_for_ollama(messages)
            
            # Call Ollama API
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {
                        "temperature": config.temperature,
                        "num_predict": config.max_tokens,
                        "top_p": config.top_p,
                    },
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data.get("response", ""),
                model=self.model,
                tokens_used=data.get("eval_count", 0),
                finish_reason="stop"
            )
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _format_messages_for_ollama(self, messages: List[Message]) -> str:
        """Format messages for Ollama (converts to simple prompt format)."""
        formatted = []
        
        for msg in messages:
            if msg.role == "system":
                formatted.append(f"System: {msg.content}")
            elif msg.role == "user":
                formatted.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                formatted.append(f"Assistant: {msg.content}")
        
        # Add final prompt for assistant response
        formatted.append("Assistant:")
        
        return "\n\n".join(formatted)
    
    async def classify_intent(self, message: str) -> Intent:
        """Classify intent using Ollama."""
        prompt = f"""Classify the intent of this message: "{message}"

Possible intents: greeting, question, objection, interest, exit, information_request, policy_comparison

Respond with only the intent name."""
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {"temperature": 0.1, "num_predict": 10},
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            intent_str = data.get("response", "").strip().lower()
            
            try:
                return Intent(intent_str)
            except ValueError:
                return Intent.UNKNOWN
        except Exception:
            return Intent.UNKNOWN
    
    async def extract_entities(
        self,
        message: str,
        entity_types: List[str]
    ) -> Dict[str, Any]:
        """Extract entities using Ollama."""
        prompt = f"""Extract the following from this message: "{message}"

Extract: {', '.join(entity_types)}

Return JSON format with extracted values or null if not found."""
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {"temperature": 0.1, "num_predict": 200},
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "")
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {}
        except Exception:
            return {}

