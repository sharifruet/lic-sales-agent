from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from app.src.repositories.lead_repository import LeadRepository
from app.src.services.lead_service import LeadService, LeadValidationError
from app.src.middleware.auth import get_current_user
from app.src.models.lead import LeadStatus

router = APIRouter(prefix="/leads", tags=["leads"])


class LeadCreate(BaseModel):
    name: str
    phone: str
    nid: Optional[str] = None
    address: Optional[str] = None
    interested_policy: Optional[str] = None
    email: Optional[EmailStr] = None
    conversation_id: Optional[int] = None  # Optional conversation ID for linking


class LeadOut(BaseModel):
    id: int
    name: str
    phone: str  # Will be masked for non-admin
    interested_policy: Optional[str]
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


class LeadDetail(LeadOut):
    """Full lead details with all fields (admin only)."""
    nid: Optional[str]  # Will be masked
    address: Optional[str]
    email: Optional[str]
    preferred_contact_time: Optional[str]
    notes: Optional[str]
    conversation_id: Optional[int]
    status_history: Optional[List[dict]] = None  # Status change history


class LeadUpdate(BaseModel):
    """Lead update model with all fields optional for partial updates."""
    status: Optional[str] = None
    notes: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_contact_time: Optional[str] = None
    interested_policy: Optional[str] = None


class BulkStatusUpdate(BaseModel):
    """Bulk status update model."""
    lead_ids: List[int]
    status: str
    notes: Optional[str] = None


class BulkStatusUpdateResponse(BaseModel):
    """Bulk status update response."""
    updated_count: int
    updated_lead_ids: List[int]
    status: str


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
            conversation_id=payload.conversation_id,
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


class LeadListResponse(BaseModel):
    """Response model for lead list with pagination."""
    leads: List[LeadOut]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    status: Optional[str] = None,
    interested_policy: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """
    List all leads with filtering, search, and pagination (admin only).
    
    Query Parameters:
        status: Filter by status (new, contacted, converted, not_interested)
        interested_policy: Filter by policy of interest (partial match)
        search: Search by name or email (partial match)
        start_date: Filter by created date from (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        end_date: Filter by created date to (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        page: Page number (default: 1)
        page_size: Items per page (default: 25, max: 100)
    
    Examples:
        GET /api/leads/?status=new&page=1&page_size=25
        GET /api/leads/?search=John&status=contacted
        GET /api/leads/?start_date=2024-01-01&end_date=2024-01-31
    """
    # Validate page_size
    if page_size > 100:
        page_size = 100
    if page_size < 1:
        page_size = 25
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    service = LeadService(LeadRepository(db))
    leads, total_count = await service.list_leads(
        status=status,
        interested_policy=interested_policy,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=page_size,
        offset=offset,
    )
    
    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
    
    lead_out_list = [
        {
            "id": l.id,
            "name": l.name,
            "phone": service.mask_phone(l.phone),  # Mask phone
            "interested_policy": l.interested_policy,
            "status": l.status.value if l.status else "new",
            "created_at": l.created_at.isoformat(),
        }
        for l in leads
    ]
    
    return LeadListResponse(
        leads=lead_out_list,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


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
    
    # Get status history for audit trail
    status_history = await service.get_status_history(lead.id, limit=10)
    status_history_list = [
        {
            "previous_status": h.previous_status,
            "new_status": h.new_status,
            "changed_by": h.changed_by,
            "changed_at": h.changed_at.isoformat(),
            "notes": h.notes,
        }
        for h in status_history
    ] if status_history else []
    
    return {
        "id": lead.id,
        "name": lead.name,
        "phone": phone_decrypted,  # Full phone for admin
        "nid": nid_decrypted if nid_decrypted else None,
        "address": lead.address,
        "interested_policy": lead.interested_policy,
        "status": lead.status.value if lead.status else "new",
        "email": lead.email,
        "preferred_contact_time": lead.preferred_contact_time,
        "notes": lead.notes,
        "conversation_id": lead.conversation_id,
        "created_at": lead.created_at.isoformat(),
        "status_history": status_history_list,
    }


@router.get("/export/{format}", response_model=dict)
async def export_leads(
    format: str,
    status: Optional[str] = None,
    interested_policy: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    decrypt: bool = True,  # Default to True for admin exports
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """
    Export leads to CSV or JSON format with optional filtering (admin only).
    
    Query Parameters:
        format: Export format ("csv" or "json")
        status: Filter by status (new, contacted, converted, not_interested)
        interested_policy: Filter by policy of interest (partial match)
        search: Search by name or email (partial match)
        start_date: Filter by created date from (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        end_date: Filter by created date to (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        decrypt: If True, decrypt phone/NID for admin (default: True)
    
    Examples:
        GET /api/leads/export/csv?status=new
        GET /api/leads/export/json?start_date=2024-01-01&end_date=2024-01-31&decrypt=true
    """
    if format not in ["csv", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'json'"
        )
    
    service = LeadService(LeadRepository(db))
    
    # Get leads count for history (check how many records will be exported)
    leads, record_count = await service.list_leads(
        status=status,
        interested_policy=interested_policy,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=None,  # Get all matching leads for count
        offset=None,
    )
    
    # Export leads
    content = await service.export_leads(
        format=format,
        status=status,
        interested_policy=interested_policy,
        search=search,
        start_date=start_date,
        end_date=end_date,
        decrypt=decrypt,
    )
    
    # Log export history
    from app.src.repositories.export_history_repository import ExportHistoryRepository
    from app.src.models.export_history import ExportHistory
    import json as json_lib
    
    export_repo = ExportHistoryRepository(db)
    filter_criteria = {
        "status": status,
        "interested_policy": interested_policy,
        "search": search,
        "start_date": start_date,
        "end_date": end_date,
        "decrypt": decrypt,
    }
    # Remove None values for cleaner JSON
    filter_criteria = {k: v for k, v in filter_criteria.items() if v is not None}
    
    export_history = ExportHistory(
        export_type="leads",
        format=format,
        record_count=record_count,
        filter_criteria=json_lib.dumps(filter_criteria) if filter_criteria else None,
        exported_by=current_user,
    )
    await export_repo.create(export_history)
    await db.flush()  # Flush but don't commit yet
    
    from fastapi.responses import Response
    
    content_type = "text/csv" if format == "csv" else "application/json"
    date_str = datetime.utcnow().strftime('%Y%m%d')
    filename = f"leads_export_{date_str}.{format}"
    
    await db.commit()  # Commit export history
    
    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


class ExportHistoryOut(BaseModel):
    """Export history response model."""
    id: int
    export_type: str
    format: str
    record_count: int
    filter_criteria: Optional[dict] = None
    exported_by: str
    created_at: str
    
    class Config:
        from_attributes = True


class ExportHistoryListResponse(BaseModel):
    """Response model for export history list with pagination."""
    exports: List[ExportHistoryOut]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/export/history", response_model=ExportHistoryListResponse)
async def get_export_history(
    export_type: Optional[str] = None,
    exported_by: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """
    Get export history (admin only).
    
    Query Parameters:
        export_type: Filter by export type ("leads" or "conversation")
        exported_by: Filter by user who exported
        start_date: Filter by export date from (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        end_date: Filter by export date to (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        page: Page number (default: 1)
        page_size: Items per page (default: 25, max: 100)
    
    Examples:
        GET /api/leads/export/history?export_type=leads
        GET /api/leads/export/history?exported_by=admin&page=1&page_size=25
    """
    from app.src.repositories.export_history_repository import ExportHistoryRepository
    from datetime import datetime
    import json as json_lib
    
    # Validate page_size
    if page_size > 100:
        page_size = 100
    if page_size < 1:
        page_size = 25
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
            pass
    
    export_repo = ExportHistoryRepository(db)
    exports, total_count = await export_repo.list(
        export_type=export_type,
        exported_by=exported_by,
        start_date=start_dt,
        end_date=end_dt,
        limit=page_size,
        offset=offset,
    )
    
    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
    
    # Format response
    exports_out = []
    for exp in exports:
        filter_criteria = None
        if exp.filter_criteria:
            try:
                filter_criteria = json_lib.loads(exp.filter_criteria)
            except:
                pass
        
        exports_out.append({
            "id": exp.id,
            "export_type": exp.export_type,
            "format": exp.format,
            "record_count": exp.record_count,
            "filter_criteria": filter_criteria,
            "exported_by": exp.exported_by,
            "created_at": exp.created_at.isoformat() if exp.created_at else None,
        })
    
    return ExportHistoryListResponse(
        exports=exports_out,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.put("/{lead_id}", response_model=LeadDetail)
async def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),  # Admin only
):
    """Update a lead (admin only). Supports partial updates - all fields are optional."""
    service = LeadService(LeadRepository(db))
    
    # Check if lead exists
    existing_lead = await service.get_lead(lead_id)
    if not existing_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    
    # Validate that at least one field is provided for update
    if all([
        payload.status is None,
        payload.notes is None,
        payload.email is None,
        payload.preferred_contact_time is None,
        payload.interested_policy is None,
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update",
        )
    
    # Convert status string to enum if provided
    status_enum = None
    if payload.status is not None:
        try:
            status_enum = LeadStatus(payload.status.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {payload.status}. Must be one of: {', '.join([s.value for s in LeadStatus])}",
            )
    
    try:
        # Update lead with provided fields (pass current_user for audit logging)
        updated_lead = await service.update_lead(
            lead_id=lead_id,
            status=status_enum,
            notes=payload.notes,
            email=payload.email,
            preferred_contact_time=payload.preferred_contact_time,
            interested_policy=payload.interested_policy,
            changed_by=current_user,  # For audit logging
        )
        
        if not updated_lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found",
            )
        
        await db.commit()
        await db.refresh(updated_lead)
        
        # Decrypt sensitive fields for admin
        phone_decrypted = service.encryption_service.decrypt(updated_lead.phone)
        nid_decrypted = service.encryption_service.decrypt(updated_lead.nid) if updated_lead.nid else None
        
        # Get status history for audit trail
        status_history = await service.get_status_history(lead_id, limit=10)
        status_history_list = [
            {
                "previous_status": h.previous_status,
                "new_status": h.new_status,
                "changed_by": h.changed_by,
                "changed_at": h.changed_at.isoformat(),
                "notes": h.notes,
            }
            for h in status_history
        ] if status_history else []
        
        return {
            "id": updated_lead.id,
            "name": updated_lead.name,
            "phone": phone_decrypted,  # Full phone for admin
            "nid": nid_decrypted if nid_decrypted else None,
            "address": updated_lead.address,
            "interested_policy": updated_lead.interested_policy,
            "status": updated_lead.status.value if updated_lead.status else "new",
            "email": updated_lead.email,
            "preferred_contact_time": updated_lead.preferred_contact_time,
            "notes": updated_lead.notes,
            "conversation_id": updated_lead.conversation_id,
            "created_at": updated_lead.created_at.isoformat(),
            "status_history": status_history_list,
        }
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


@router.put("/bulk-update", response_model=BulkStatusUpdateResponse)
async def bulk_update_lead_status(
    payload: BulkStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),  # Admin only
):
    """
    Bulk update status for multiple leads (admin only).
    
    Updates status for all leads in the provided list.
    Each status change is logged individually for audit trail.
    
    Request:
        {
            "lead_ids": [1, 2, 3, 4, 5],
            "status": "contacted",
            "notes": "Bulk update: All leads contacted via phone"
        }
    
    Response:
        {
            "updated_count": 5,
            "updated_lead_ids": [1, 2, 3, 4, 5],
            "status": "contacted"
        }
    """
    service = LeadService(LeadRepository(db))
    
    # Validate that lead_ids list is provided and not empty
    if not payload.lead_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="lead_ids list cannot be empty",
        )
    
    # Validate lead_ids list size (prevent too large requests)
    if len(payload.lead_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update more than 100 leads at once. Please split into multiple requests.",
        )
    
    # Remove duplicates from lead_ids
    unique_lead_ids = list(set(payload.lead_ids))
    
    # Validate status
    try:
        status_enum = LeadStatus(payload.status.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {payload.status}. Must be one of: {', '.join([s.value for s in LeadStatus])}",
        )
    
    try:
        # Bulk update status
        updated_ids = await service.bulk_update_status(
            lead_ids=unique_lead_ids,
            status=status_enum,
            changed_by=current_user,  # For audit logging
            notes=payload.notes
        )
        
        await db.commit()
        
        return BulkStatusUpdateResponse(
            updated_count=len(updated_ids),
            updated_lead_ids=updated_ids,
            status=payload.status.lower()
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating leads: {str(e)}"
        )
