"""Tests for validation service."""
import pytest
from src.services.validation_service import ValidationService


def test_validate_phone_number_valid():
    """Test validating valid phone numbers."""
    service = ValidationService()
    
    # Test international format
    result = service.validate_phone_number("+1234567890")
    assert result.is_valid is True
    assert result.normalized == "+1234567890"
    
    # Test with spaces/dashes
    result = service.validate_phone_number("+1 (234) 567-890")
    assert result.is_valid is True


def test_validate_phone_number_invalid():
    """Test validating invalid phone numbers."""
    service = ValidationService()
    
    # Too short
    result = service.validate_phone_number("123")
    assert result.is_valid is False
    
    # Invalid format
    result = service.validate_phone_number("abc")
    assert result.is_valid is False


def test_validate_nid_valid():
    """Test validating valid NID."""
    service = ValidationService()
    
    # Default format
    result = service.validate_nid("12345678")
    assert result.is_valid is True
    
    # US SSN format
    result = service.validate_nid("123456789", country="US")
    assert result.is_valid is True


def test_validate_nid_invalid():
    """Test validating invalid NID."""
    service = ValidationService()
    
    # Too short
    result = service.validate_nid("123")
    assert result.is_valid is False


def test_validate_email_valid():
    """Test validating valid email."""
    service = ValidationService()
    
    result = service.validate_email("test@example.com")
    assert result.is_valid is True
    assert result.normalized == "test@example.com"


def test_validate_email_invalid():
    """Test validating invalid email."""
    service = ValidationService()
    
    result = service.validate_email("invalid-email")
    assert result.is_valid is False


def test_validate_lead_data_complete():
    """Test validating complete lead data."""
    service = ValidationService()
    
    result = service.validate_lead_data(
        name="John Doe",
        phone="+1234567890",
        nid="123456789",
        address="123 Main St",
        email="john@example.com"
    )
    
    assert result.is_valid is True


def test_validate_lead_data_incomplete():
    """Test validating incomplete lead data."""
    service = ValidationService()
    
    result = service.validate_lead_data(
        name="J",  # Too short
        phone="123",  # Invalid
        address="123"  # Too short
    )
    
    assert result.is_valid is False
    assert len(result.errors) > 0

