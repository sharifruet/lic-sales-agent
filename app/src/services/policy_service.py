from typing import List

from src.models.policy import Policy
from src.repositories.policy_repository import PolicyRepository


class PolicyService:
    """Service layer for policy management and simple matching."""

    def __init__(self, repo: PolicyRepository):
        self.repo = repo

    async def list_policies(self) -> List[Policy]:
        return await self.repo.list()

    async def get_policy(self, policy_id: int) -> Policy | None:
        return await self.repo.find_by_id(policy_id)

    async def create_policy(
        self,
        name: str,
        provider: str,
        coverage_amount: int,
        monthly_premium: float,
        term_years: int,
        medical_exam_required: bool,
    ) -> Policy:
        policy = Policy(
            name=name,
            provider=provider,
            coverage_amount=coverage_amount,
            monthly_premium=monthly_premium,
            term_years=term_years,
            medical_exam_required=medical_exam_required,
        )
        return await self.repo.create(policy)


