from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.lead_repository import LeadRepository
from src.services.lead_service import LeadService
from src.models.lead import Lead

router = APIRouter(prefix="/leads", tags=["leads"])


class LeadCreate(BaseModel):
    name: str
    phone: str
    nid: Optional[str] = None
    address: Optional[str] = None
    interested_policy: Optional[str] = None


@router.post("/", response_model=dict)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    service = LeadService(LeadRepository(db))
    lead: Lead = await service.create_lead(
        name=payload.name,
        phone=payload.phone,
        nid=payload.nid,
        address=payload.address,
        interested_policy=payload.interested_policy,
    )
    return {"id": lead.id}


@router.get("/", response_model=List[dict])
async def list_leads(db: AsyncSession = Depends(get_db)):
    service = LeadService(LeadRepository(db))
    leads = await service.list_leads()
    return [
        {
            "id": l.id,
            "name": l.name,
            "phone": l.phone,
            "interested_policy": l.interested_policy,
            "created_at": l.created_at,
        }
        for l in leads
    ]
