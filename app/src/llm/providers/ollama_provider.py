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
        # Increase timeout for Ollama - it can be slow, especially on first request
        self.client = httpx.AsyncClient(timeout=120.0)  # 2 minutes for Ollama
    
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
        
        # Format messages for Ollama (simple prompt format)
        prompt = self._format_messages_for_ollama(messages)
        
        # Retry network call with exponential backoff (AC-022.7: Network retry with backoff)
        from src.services.retry_service import RetryService, RetryConfig
        retry_service = RetryService(RetryConfig(max_attempts=3, initial_delay=1.0, max_delay=10.0))
        
        async def _call_ollama_api():
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
                },
                timeout=120.0  # 2 minute timeout for Ollama (can be slow)
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data.get("response", ""),
                model=self.model,
                tokens_used=data.get("eval_count", 0),
                finish_reason="stop"
            )
        
        try:
            import httpx
            return await retry_service.retry_with_backoff(
                _call_ollama_api,
                operation_name="Ollama API call",
                retryable_exceptions=[httpx.ReadTimeout, httpx.ConnectTimeout, httpx.TimeoutException],
                non_retryable_exceptions=[]
            )
        except Exception as e:
            # Raise as LLMAPIError for proper error handling
            from src.middleware.error_handler import LLMAPIError
            raise LLMAPIError(f"Ollama API error after retries: {str(e)}")
    
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
        
        # Retry network call with exponential backoff (AC-022.7)
        from src.services.retry_service import RetryService, RetryConfig
        retry_service = RetryService(RetryConfig(max_attempts=3, initial_delay=1.0, max_delay=10.0))
        
        async def _classify_intent_api():
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {"temperature": 0.1, "num_predict": 10},
                    "stream": False
                },
                timeout=60.0  # 60 second timeout for intent classification (Ollama can be slow)
            )
            response.raise_for_status()
            data = response.json()
            intent_str = data.get("response", "").strip().lower()
            
            try:
                return Intent(intent_str)
            except ValueError:
                return Intent.UNKNOWN
        
        try:
            import httpx
            return await retry_service.retry_with_backoff(
                _classify_intent_api,
                operation_name="Ollama intent classification",
                retryable_exceptions=[httpx.ReadTimeout, httpx.ConnectTimeout, httpx.TimeoutException],
                non_retryable_exceptions=[]
            )
        except Exception:
            # Fallback to default intent
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

