"""Response Filter for safety and compliance following LLM Integration Design."""
from typing import List


class ResponseFilter:
    """Filters LLM responses for safety and compliance."""
    
    # Blocked phrases from LLM Integration Design Document
    BLOCKED_PHRASES = [
        # False promises
        "guaranteed approval",
        "guaranteed coverage",
        "no questions asked",
        "instant approval",
        
        # Aggressive sales
        "must buy now",
        "limited time only",
        "act immediately",
        "don't miss out",
        "must buy",
        "act now or lose",
        
        # Medical claims
        "will cure",
        "medical advice",
        "diagnose",
        
        # Financial guarantees
        "guaranteed returns",
        "risk-free",
        "no risk",
    ]
    
    PROHIBITED_CONTENT = [
        "discrimination",
        "illegal advice",
        "false claims",
        "misleading information"
    ]
    
    def filter_response(self, response: str) -> str:
        """Filter LLM response for safety and compliance."""
        filtered = response
        
        # Remove blocked phrases
        for phrase in self.BLOCKED_PHRASES:
            if phrase.lower() in filtered.lower():
                # Replace with empty string or safe alternative
                filtered = filtered.replace(phrase, "").replace(phrase.lower(), "")
                # Log filtering action (could add logging here)
        
        # Check for prohibited content
        response_lower = filtered.lower()
        for content in self.PROHIBITED_CONTENT:
            if content in response_lower:
                # Flag for review or replace with safe default
                return "I apologize, but I can't provide that type of information. Let me help you with something else."
        
        # Ensure transparency about AI nature if needed
        if "I am" in filtered and "human" in filtered.lower():
            # Correct if LLM claims to be human
            filtered = filtered.replace("I am human", "I am an AI assistant")
            filtered = filtered.replace("i am human", "I am an AI assistant")
        
        # Remove excessive whitespace
        filtered = " ".join(filtered.split())
        
        return filtered.strip()
    
    def validate_response(self, response: str) -> bool:
        """Validate response meets quality standards."""
        if not response or len(response.strip()) < 5:
            return False
        
        # Check for blocked phrases
        response_lower = response.lower()
        for phrase in self.BLOCKED_PHRASES:
            if phrase in response_lower:
                return False
        
        # Check for prohibited content
        for content in self.PROHIBITED_CONTENT:
            if content in response_lower:
                return False
        
        return True
    
    def check_brand_safety(self, response: str) -> bool:
        """Check if response meets brand safety standards."""
        # Check for competitor bashing
        competitor_keywords = ["competitor", "other company", "they're worse"]
        if any(keyword in response.lower() for keyword in competitor_keywords):
            return False
        
        # Check for false claims
        false_claim_keywords = ["guaranteed", "always", "never fails"]
        if any(keyword in response.lower() for keyword in false_claim_keywords):
            # Context-dependent, but flag for review
            pass
        
        return True
