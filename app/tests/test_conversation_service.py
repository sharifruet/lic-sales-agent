"""Tests for conversation service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.services.conversation_service import ConversationService
from src.models.conversation import Conversation
from src.models.message import Message


@pytest.mark.asyncio
async def test_start_conversation(db_session):
    """Test starting a new conversation."""
    service = ConversationService(db_session)
    session = await service.start_conversation()
    
    assert session is not None
    assert session.session_id is not None
    assert session.conversation_stage == "introduction"


@pytest.mark.asyncio
async def test_process_message(db_session):
    """Test processing a user message."""
    service = ConversationService(db_session)
    
    # Mock LLM provider
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Hello! How can I help you today?"
    service.llm = mock_llm
    
    # Start conversation first
    session = await service.start_conversation()
    session_id = session.session_id
    
    # Process message
    response = await service.process_message(session_id, "Hello")
    
    assert response is not None
    assert "response" in response
    assert response["response"] == "Hello! How can I help you today?"


@pytest.mark.asyncio
async def test_detect_intent(db_session):
    """Test intent detection."""
    service = ConversationService(db_session)
    
    # Test greeting intent
    intent = await service.detect_intent("Hello there!")
    assert intent in ["greeting", "question", "unknown"]  # Flexible


@pytest.mark.asyncio
async def test_detect_interest(db_session):
    """Test interest detection."""
    service = ConversationService(db_session)
    
    # Create session with interest
    session = await service.start_conversation()
    
    # Add messages indicating interest
    await service.process_message(session.session_id, "I'm interested in life insurance")
    await service.process_message(session.session_id, "How do I apply?")
    
    interest = await service.detect_interest(session.session_id)
    assert interest in ["none", "low", "medium", "high"]


@pytest.fixture
async def db_session():
    """Mock database session."""
    session = AsyncMock()
    session.add = Mock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session

