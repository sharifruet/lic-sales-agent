"""Validation service for lead data and other inputs."""
import re
from typing import Optional
from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Result of validation."""
    is_valid: bool
    errors: list[str] = []
    normalized: Optional[str] = None


class ValidationService:
    """Service for validating lead data and inputs."""
    
    def validate_phone_number(self, phone: str) -> ValidationResult:
        """Validate phone number format."""
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-\(\)]', '', phone.strip())
        
        # Check if starts with + (international format)
        if cleaned.startswith('+'):
            # E.164 format: + followed by 1-15 digits
            if re.match(r'^\+\d{1,15}$', cleaned):
                return ValidationResult(is_valid=True, normalized=cleaned)
            return ValidationResult(
                is_valid=False,
                errors=["Phone number must be in international format: +1234567890"]
            )
        else:
            # Allow digits only (10-15 digits)
            if re.match(r'^\d{10,15}$', cleaned):
                # Add + prefix for normalization
                normalized = f"+{cleaned}"
                return ValidationResult(is_valid=True, normalized=normalized)
            return ValidationResult(
                is_valid=False,
                errors=["Phone number must be 10-15 digits. Include country code: +1234567890"]
            )
    
    def validate_nid(self, nid: str, country: str = "default") -> ValidationResult:
        """Validate National ID format (country-specific)."""
        # Remove spaces and hyphens
        cleaned = nid.strip().replace(" ", "").replace("-", "")
        
        # Country-specific validation
        if country == "US":
            # SSN format: 9 digits
            if len(cleaned) == 9 and cleaned.isdigit():
                return ValidationResult(is_valid=True, normalized=cleaned)
            return ValidationResult(
                is_valid=False,
                errors=["Invalid SSN format. Must be 9 digits."]
            )
        elif country == "BD":
            # Bangladesh NID: 10 or 13 digits
            if len(cleaned) in [10, 13] and cleaned.isdigit():
                return ValidationResult(is_valid=True, normalized=cleaned)
            return ValidationResult(
                is_valid=False,
                errors=["Invalid Bangladesh NID format. Must be 10 or 13 digits."]
            )
        else:
            # Default: alphanumeric, 8-20 characters
            if 8 <= len(cleaned) <= 20 and (cleaned.isalnum() or cleaned.replace("-", "").replace("_", "").isalnum()):
                return ValidationResult(is_valid=True, normalized=cleaned)
            return ValidationResult(
                is_valid=False,
                errors=["Invalid NID format. Must be 8-20 alphanumeric characters."]
            )
    
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email format."""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if re.match(pattern, email.strip()):
            return ValidationResult(is_valid=True, normalized=email.strip().lower())
        return ValidationResult(
            is_valid=False,
            errors=["Invalid email format."]
        )
    
    def validate_lead_data(self, name: str, phone: str, nid: Optional[str] = None, 
                          address: Optional[str] = None, email: Optional[str] = None) -> ValidationResult:
        """Validate complete lead data."""
        errors = []
        
        # Validate name
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters.")
        
        # Validate phone
        phone_result = self.validate_phone_number(phone)
        if not phone_result.is_valid:
            errors.extend(phone_result.errors)
        
        # Validate NID if provided
        if nid:
            nid_result = self.validate_nid(nid)
            if not nid_result.is_valid:
                errors.extend(nid_result.errors)
        
        # Validate email if provided
        if email:
            email_result = self.validate_email(email)
            if not email_result.is_valid:
                errors.extend(email_result.errors)
        
        # Validate address if provided
        if address and len(address.strip()) < 5:
            errors.append("Address must be at least 5 characters.")
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        
        return ValidationResult(is_valid=True)

