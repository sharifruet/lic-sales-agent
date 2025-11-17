"""Pytest configuration and shared fixtures."""
import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def db_session():
    """Mock database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    session.add = Mock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session

