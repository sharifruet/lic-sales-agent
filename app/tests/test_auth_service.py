"""Tests for authentication service."""
import pytest
from datetime import datetime, timedelta
from src.services.auth_service import AuthService


def test_create_access_token():
    """Test creating access token."""
    service = AuthService()
    
    token = service.create_access_token("admin")
    
    assert token is not None
    assert isinstance(token, str)


def test_verify_token_valid():
    """Test verifying valid token."""
    service = AuthService()
    
    token = service.create_access_token("admin")
    username = service.verify_token(token)
    
    assert username == "admin"


def test_verify_token_invalid():
    """Test verifying invalid token."""
    service = AuthService()
    
    username = service.verify_token("invalid-token")
    
    assert username is None


def test_authenticate_user_valid():
    """Test authenticating valid user."""
    service = AuthService()
    
    result = service.authenticate_user("admin", "admin")
    
    assert result is True


def test_authenticate_user_invalid():
    """Test authenticating invalid user."""
    service = AuthService()
    
    result = service.authenticate_user("admin", "wrong-password")
    
    assert result is False

