from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from app.src.repositories.policy_repository import PolicyRepository
from app.src.services.policy_service import PolicyService
from app.src.middleware.auth import get_current_user


router = APIRouter(prefix="/policies", tags=["policies"])


class PolicyOut(BaseModel):
    id: int
    name: str
    provider: str
    coverage_amount: int
    monthly_premium: float
    term_years: int
    medical_exam_required: bool

    class Config:
        from_attributes = True


class PolicyCreate(BaseModel):
    name: str = Field(..., max_length=120)
    provider: str = Field(..., max_length=120)
    coverage_amount: int = Field(..., ge=10000)
    monthly_premium: float = Field(..., gt=0)
    term_years: int = Field(..., ge=1)
    medical_exam_required: bool = False


class PolicyUpdate(BaseModel):
    """Policy update model with all fields optional for partial updates."""
    name: Optional[str] = Field(None, max_length=120)
    provider: Optional[str] = Field(None, max_length=120)
    coverage_amount: Optional[int] = Field(None, ge=10000)
    monthly_premium: Optional[float] = Field(None, gt=0)
    term_years: Optional[int] = Field(None, ge=1)
    medical_exam_required: Optional[bool] = None


def _service(db: AsyncSession) -> PolicyService:
    return PolicyService(PolicyRepository(db))


@router.get("/", response_model=List[PolicyOut])
async def list_policies(
    provider: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all policies, optionally filtered by provider or searched by name.
    
    Query Parameters:
        provider: Optional provider name to filter by (can be partial match)
        search: Optional policy name to search for (can be partial match)
    
    Examples:
        GET /api/policies/ - List all policies
        GET /api/policies/?provider=Company%20A - List policies from Company A
        GET /api/policies/?search=Term%20Life - Search for policies with "Term Life" in name
        GET /api/policies/?provider=Company%20A&search=Term - Filter by provider and search by name
    """
    service = _service(db)
    policies = await service.list_policies(provider=provider, search=search)
    return policies


@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    service = _service(db)
    policy = await service.get_policy(policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    return policy


@router.post("/", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
async def create_policy(
    payload: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),  # Admin only
):
    """Create a new policy (admin only)."""
    service = _service(db)
    policy = await service.create_policy(
        name=payload.name,
        provider=payload.provider,
        coverage_amount=payload.coverage_amount,
        monthly_premium=payload.monthly_premium,
        term_years=payload.term_years,
        medical_exam_required=payload.medical_exam_required,
    )
    await db.commit()
    await db.refresh(policy)
    return policy


@router.put("/{policy_id}", response_model=PolicyOut)
async def update_policy(
    policy_id: int,
    payload: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),  # Admin only
):
    """Update a policy (admin only). Supports partial updates - all fields are optional."""
    service = _service(db)
    
    # Check if policy exists
    existing_policy = await service.get_policy(policy_id)
    if not existing_policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    # Validate that at least one field is provided for update
    if all([
        payload.name is None,
        payload.provider is None,
        payload.coverage_amount is None,
        payload.monthly_premium is None,
        payload.term_years is None,
        payload.medical_exam_required is None,
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update",
        )
    
    # Check for name uniqueness if name is being updated
    if payload.name is not None and payload.name != existing_policy.name:
        repo = PolicyRepository(db)
        existing_with_name = await repo.find_by_name(payload.name)
        if existing_with_name and existing_with_name.id != policy_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Policy with name '{payload.name}' already exists",
            )
    
    # Update policy with provided fields
    updated_policy = await service.update_policy(
        policy_id=policy_id,
        name=payload.name,
        provider=payload.provider,
        coverage_amount=payload.coverage_amount,
        monthly_premium=payload.monthly_premium,
        term_years=payload.term_years,
        medical_exam_required=payload.medical_exam_required,
    )
    
    if not updated_policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    await db.commit()
    await db.refresh(updated_policy)
    return updated_policy


class PolicyComparisonRequest(BaseModel):
    """Request model for policy comparison."""
    policy_ids: List[int] = Field(..., min_items=2, max_items=10, description="List of policy IDs to compare (2-10 policies)")


class PolicyComparisonResponse(BaseModel):
    """Response model for policy comparison."""
    policies: List[dict]
    comparison_points: dict
    summary: Optional[str] = None  # Optional comparison summary


@router.post("/compare", response_model=PolicyComparisonResponse)
async def compare_policies(
    payload: PolicyComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple policies side-by-side (public endpoint).
    
    Compares 2-10 policies and returns structured comparison data.
    
    Request:
        {
            "policy_ids": [1, 2, 3]
        }
    
    Response:
        {
            "policies": [
                {
                    "id": 1,
                    "name": "Term Life 20-Year",
                    "provider": "Company A",
                    "coverage_amount": 500000,
                    "monthly_premium": 50.00,
                    "term_years": 20,
                    "medical_exam_required": false
                },
                ...
            ],
            "comparison_points": {
                "coverage_range": {"min": 100000, "max": 1000000},
                "premium_range": {"min": 30.00, "max": 100.00},
                "term_range": {"min": 10, "max": 30},
                "medical_exam_required_count": 1
            },
            "summary": "Comparison of 3 policies..."
        }
    """
    service = _service(db)
    
    # Validate policy IDs
    if len(payload.policy_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 policies are required for comparison"
        )
    
    if len(payload.policy_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot compare more than 10 policies at once"
        )
    
    # Remove duplicates
    unique_ids = list(set(payload.policy_ids))
    
    try:
        comparison = await service.compare_policies(unique_ids)
        
        # Generate summary (optional, can be enhanced with LLM)
        summary = f"Comparison of {len(comparison['policies'])} policies: "
        summary += ", ".join([p['name'] for p in comparison['policies']])
        
        return PolicyComparisonResponse(
            policies=comparison['policies'],
            comparison_points=comparison['comparison_points'],
            summary=summary
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing policies: {str(e)}"
        )


@router.get("/competitors", response_model=List[PolicyOut])
async def list_competitor_policies(
    exclude_provider: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """
    List all competitor policies (admin only).
    
    Returns policies from providers other than the company.
    
    Query Parameters:
        exclude_provider: Optional provider name to exclude (defaults to company name from config)
    
    Examples:
        GET /api/policies/competitors - List all non-company policies
        GET /api/policies/competitors?exclude_provider=Company%20A - Exclude specific provider
    """
    service = _service(db)
    policies = await service.list_competitor_policies(exclude_provider=exclude_provider)
    return policies


@router.get("/company", response_model=List[PolicyOut])
async def list_company_policies(
    company_provider: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all company policies (public endpoint).
    
    Returns policies from the company itself (not competitors).
    
    Query Parameters:
        company_provider: Optional company provider name (defaults to company name from config)
    
    Examples:
        GET /api/policies/company - List all company policies
        GET /api/policies/company?company_provider=Company%20A - List policies for specific provider
    """
    service = _service(db)
    policies = await service.list_company_policies(company_provider=company_provider)
    return policies


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: int,
    soft_delete: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),  # Admin only
):
    """
    Delete or deactivate a policy (admin only).
    
    Query Parameters:
        soft_delete: If True, performs soft delete (marks as inactive); if False, hard deletes (default: True)
    
    Note:
        - Soft delete is recommended to preserve data integrity
        - Hard delete will permanently remove the policy from the database
        - Before deletion, check if policy is referenced by any leads
    
    Examples:
        DELETE /api/policies/1 - Soft delete policy (default)
        DELETE /api/policies/1?soft_delete=false - Hard delete policy
    """
    service = _service(db)
    
    # Check if policy exists
    existing_policy = await service.get_policy(policy_id)
    if not existing_policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    # TODO: Check if policy is referenced by leads before deletion
    # This should prevent deletion if policy is in use
    
    # Delete policy
    success = await service.delete_policy(policy_id, soft_delete=soft_delete)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    await db.commit()
    
    return {
        "message": "Policy deleted successfully" if not soft_delete else "Policy deactivated successfully",
        "policy_id": policy_id,
        "soft_delete": soft_delete,
    }


