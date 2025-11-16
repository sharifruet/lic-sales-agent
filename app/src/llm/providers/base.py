from typing import Optional
from pydantic import BaseModel
import httpx
from src.config import settings


class LLMRequest(BaseModel):
    prompt: str
    temperature: float = settings.llm_temperature
    max_tokens: int = settings.llm_max_tokens


class OllamaProvider:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
