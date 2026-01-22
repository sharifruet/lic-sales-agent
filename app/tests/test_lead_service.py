"""Tests for lead service."""
import pytest
from unittest.mock import Mock, AsyncMock

from src.services.lead_service import LeadService, LeadValidationError
from src.repositories.lead_repository import LeadRepository
from src.models.lead import Lead


@pytest.mark.asyncio
async def test_create_lead_valid(db_session):
    """Test creating a valid lead."""
    repo = LeadRepository(db_session)
    service = LeadService(repo)
    
    # Mock repository
    mock_lead = Lead(
        id=1,
        name="John Doe",
        phone="+1234567890",
        nid=None,
        address="123 Main St",
        interested_policy="term-life-20yr"
    )
    db_session.flush = AsyncMock()
    
    # Create lead
    lead = await service.create_lead(
        name="John Doe",
        phone="+1234567890",
        address="123 Main St",
        interested_policy="term-life-20yr"
    )
    
    assert lead is not None
    assert lead.name == "John Doe"


@pytest.mark.asyncio
async def test_create_lead_invalid_phone(db_session):
    """Test creating lead with invalid phone number."""
    repo = LeadRepository(db_session)
    service = LeadService(repo)
    
    with pytest.raises(LeadValidationError) as exc_info:
        await service.create_lead(
            name="John Doe",
            phone="123",  # Invalid phone
            address="123 Main St"
        )
    
    assert len(exc_info.value.errors) > 0


@pytest.mark.asyncio
async def test_create_lead_duplicate(db_session):
    """Test creating duplicate lead."""
    repo = LeadRepository(db_session)
    service = LeadService(repo)
    
    # Mock existing lead
    existing_lead = Lead(id=1, name="John", phone="+1234567890")
    repo.find_by_phone = AsyncMock(return_value=existing_lead)
    
    with pytest.raises(ValueError):
        await service.create_lead(
            name="John Doe",
            phone="+1234567890",
            address="123 Main St"
        )


@pytest.mark.asyncio
async def test_list_leads(db_session):
    """Test listing leads."""
    repo = LeadRepository(db_session)
    service = LeadService(repo)
    
    # Mock repository list
    mock_leads = [
        Lead(id=1, name="John", phone="+1234567890"),
        Lead(id=2, name="Jane", phone="+0987654321"),
    ]
    repo.list = AsyncMock(return_value=mock_leads)
    
    leads = await service.list_leads()
    
    assert len(leads) == 2
    assert leads[0].name == "John"


@pytest.fixture
async def db_session():
    """Mock database session."""
    session = AsyncMock()
    session.add = Mock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session

