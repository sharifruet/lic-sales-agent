from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.policy_repository import PolicyRepository
from src.services.policy_service import PolicyService


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


def _service(db: AsyncSession) -> PolicyService:
    return PolicyService(PolicyRepository(db))


@router.get("/", response_model=List[PolicyOut])
async def list_policies(db: AsyncSession = Depends(get_db)):
    service = _service(db)
    policies = await service.list_policies()
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
async def create_policy(payload: PolicyCreate, db: AsyncSession = Depends(get_db)):
    service = _service(db)
    policy = await service.create_policy(
        name=payload.name,
        provider=payload.provider,
        coverage_amount=payload.coverage_amount,
        monthly_premium=payload.monthly_premium,
        term_years=payload.term_years,
        medical_exam_required=payload.medical_exam_required,
    )
    return policy


