from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.lead_repository import LeadRepository
from src.services.lead_service import LeadService, LeadValidationError
from src.middleware.auth import get_current_user

router = APIRouter(prefix="/leads", tags=["leads"])


class LeadCreate(BaseModel):
    name: str
    phone: str
    nid: Optional[str] = None
    address: Optional[str] = None
    interested_policy: Optional[str] = None
    email: Optional[EmailStr] = None


class LeadOut(BaseModel):
    id: int
    name: str
    phone: str  # Will be masked for non-admin
    interested_policy: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class LeadDetail(LeadOut):
    """Full lead details with all fields (admin only)."""
    nid: Optional[str]  # Will be masked
    address: Optional[str]
    email: Optional[str]


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    """Create a new lead (public endpoint for customers)."""
    service = LeadService(LeadRepository(db))
    try:
        lead = await service.create_lead(
            name=payload.name,
            phone=payload.phone,
            nid=payload.nid,
            address=payload.address,
            interested_policy=payload.interested_policy,
            email=payload.email,
        )
        return {"id": lead.id, "message": "Lead created successfully"}
    except LeadValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": e.errors}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[LeadOut])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """List all leads (admin only)."""
    service = LeadService(LeadRepository(db))
    leads = await service.list_leads()
    return [
        {
            "id": l.id,
            "name": l.name,
            "phone": service.mask_phone(l.phone),  # Mask phone
            "interested_policy": l.interested_policy,
            "created_at": l.created_at.isoformat(),
        }
        for l in leads
    ]


@router.get("/{lead_id}", response_model=LeadDetail)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """Get lead details by ID (admin only)."""
    service = LeadService(LeadRepository(db))
    lead = await service.get_lead(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Decrypt sensitive fields for admin
    phone_decrypted = service.encryption_service.decrypt(lead.phone)
    nid_decrypted = service.encryption_service.decrypt(lead.nid) if lead.nid else None
    
    return {
        "id": lead.id,
        "name": lead.name,
        "phone": phone_decrypted,  # Full phone for admin
        "nid": nid_decrypted if nid_decrypted else None,
        "address": lead.address,
        "interested_policy": lead.interested_policy,
        "created_at": lead.created_at.isoformat(),
    }


@router.get("/export/{format}", response_model=dict)
async def export_leads(
    format: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """Export leads to CSV or JSON format (admin only)."""
    if format not in ["csv", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'json'"
        )
    
    service = LeadService(LeadRepository(db))
    content = await service.export_leads(format)
    
    from fastapi.responses import Response
    
    content_type = "text/csv" if format == "csv" else "application/json"
    filename = f"leads_export_{datetime.utcnow().strftime('%Y%m%d')}.{format}"
    
    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
