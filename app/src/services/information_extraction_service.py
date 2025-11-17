"""Information Extraction service for extracting structured data from messages."""
from typing import Dict, List, Any, Optional
from src.llm.providers.llm_provider import LLMProvider
import re


class InformationExtractionService:
    """Service for extracting structured information from natural language."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def extract_information(
        self,
        message: str,
        context: Dict,
        entity_types: List[str] = None
    ) -> Dict[str, Any]:
        """Extract structured information from natural language."""
        if entity_types is None:
            entity_types = ["age", "phone", "name", "address", "email"]
        
        extracted = {}
        
        # Use LLM for entity extraction
        try:
            llm_extracted = await self.llm_provider.extract_entities(
                message,
                entity_types
            )
            extracted.update(llm_extracted)
        except Exception:
            # Fallback to regex patterns
            extracted = self._extract_with_regex(message, entity_types)
        
        return extracted
    
    def _extract_with_regex(self, message: str, entity_types: List[str]) -> Dict:
        """Fallback regex-based extraction."""
        extracted = {}
        
        # Age extraction
        if "age" in entity_types:
            age_pattern = r'\b(\d{2})\s*(?:years?\s*old|age|aged)|\b(?:age|aged)\s*(\d{2})\b'
            age_match = re.search(age_pattern, message.lower())
            if age_match:
                age = int(age_match.group(1) or age_match.group(2))
                if 18 <= age <= 100:
                    extracted["age"] = age
        
        # Phone extraction
        if "phone" in entity_types:
            phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
            phone_match = re.search(phone_pattern, message)
            if phone_match:
                extracted["phone"] = phone_match.group(0)
        
        # Email extraction
        if "email" in entity_types:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, message)
            if email_match:
                extracted["email"] = email_match.group(0)
        
        # Name extraction (simple: look for capitalized words)
        if "name" in entity_types:
            # Look for patterns like "I'm John" or "My name is John"
            name_patterns = [
                r"(?:i'?m|my name is|call me|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
                r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s+here|speaking)"
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, message, re.IGNORECASE)
                if name_match:
                    extracted["name"] = name_match.group(1)
                    break
        
        return extracted
    
    def sanitize_input(self, message: str) -> str:
        """Sanitize user input."""
        # Remove potentially harmful characters
        sanitized = message.strip()
        
        # Remove excessive whitespace
        sanitized = " ".join(sanitized.split())
        
        # Limit length
        if len(sanitized) > 2000:
            sanitized = sanitized[:2000]
        
        return sanitized

