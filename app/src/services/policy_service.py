from typing import List, Optional

from src.models.policy import Policy
from src.repositories.policy_repository import PolicyRepository
from src.config import settings


class PolicyService:
    """Service layer for policy management and simple matching."""

    def __init__(self, repo: PolicyRepository):
        self.repo = repo

    async def list_policies(
        self,
        provider: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Policy]:
        """
        List policies, optionally filtered by provider or searched by name.
        
        Args:
            provider: Filter by provider name (partial match)
            search: Search by policy name (partial match)
        """
        return await self.repo.list(provider=provider, search=search)
    
    async def delete_policy(self, policy_id: int, soft_delete: bool = True) -> bool:
        """
        Delete or deactivate a policy.
        
        Args:
            policy_id: Policy ID to delete/deactivate
            soft_delete: If True, marks as inactive; if False, hard deletes (default: True)
        
        Returns:
            True if successful, False if policy not found
        
        Note:
            For soft delete to work properly, the Policy model should have an is_active field.
            Currently, this performs a hard delete but logs a warning about soft delete.
        """
        # TODO: Check if policy is referenced by leads before deletion
        # For now, we'll allow deletion but this should be checked
        
        return await self.repo.delete(policy_id, soft_delete=soft_delete)

    async def list_competitor_policies(self, exclude_provider: Optional[str] = None) -> List[Policy]:
        """
        List all competitor policies (non-company policies).
        
        Args:
            exclude_provider: Provider name to exclude (typically company name).
                            If None, uses settings.company_name.
                            Can be partial match (case-insensitive).
        
        Returns:
            List of policies that are not from the company
        """
        exclude_name = (exclude_provider or settings.company_name).lower()
        
        all_policies = await self.repo.list()
        # Filter out company policies (case-insensitive partial match)
        competitor_policies = [
            p for p in all_policies
            if exclude_name not in p.provider.lower()
        ]
        
        return competitor_policies

    async def list_company_policies(self, company_provider: Optional[str] = None) -> List[Policy]:
        """
        List all company policies.
        
        Args:
            company_provider: Company provider name. If None, uses settings.company_name
        
        Returns:
            List of policies from the company
        """
        company_name = company_provider or settings.company_name
        # Use exact match for company policies
        return await self.repo.find_by_provider(company_name, exact_match=True)

    async def compare_policies(self, policy_ids: List[int]) -> dict:
        """
        Compare multiple policies side-by-side.
        
        Args:
            policy_ids: List of policy IDs to compare
        
        Returns:
            Dictionary with comparison data
        """
        policies = []
        for policy_id in policy_ids:
            policy = await self.repo.find_by_id(policy_id)
            if policy:
                policies.append(policy)
        
        if len(policies) < 2:
            raise ValueError("At least 2 policies are required for comparison")
        
        # Build comparison data
        comparison = {
            "policies": [
                {
                    "id": p.id,
                    "name": p.name,
                    "provider": p.provider,
                    "coverage_amount": p.coverage_amount,
                    "monthly_premium": float(p.monthly_premium),
                    "term_years": p.term_years,
                    "medical_exam_required": p.medical_exam_required,
                }
                for p in policies
            ],
            "comparison_points": {
                "coverage_range": {
                    "min": min(p.coverage_amount for p in policies),
                    "max": max(p.coverage_amount for p in policies),
                },
                "premium_range": {
                    "min": float(min(p.monthly_premium for p in policies)),
                    "max": float(max(p.monthly_premium for p in policies)),
                },
                "term_range": {
                    "min": min(p.term_years for p in policies),
                    "max": max(p.term_years for p in policies),
                },
                "medical_exam_required_count": sum(1 for p in policies if p.medical_exam_required),
            }
        }
        
        return comparison

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

    async def update_policy(
        self,
        policy_id: int,
        name: str = None,
        provider: str = None,
        coverage_amount: int = None,
        monthly_premium: float = None,
        term_years: int = None,
        medical_exam_required: bool = None,
    ) -> Policy | None:
        """Update policy with partial updates."""
        updates = {}
        if name is not None:
            updates["name"] = name
        if provider is not None:
            updates["provider"] = provider
        if coverage_amount is not None:
            updates["coverage_amount"] = coverage_amount
        if monthly_premium is not None:
            updates["monthly_premium"] = monthly_premium
        if term_years is not None:
            updates["term_years"] = term_years
        if medical_exam_required is not None:
            updates["medical_exam_required"] = medical_exam_required
        
        return await self.repo.update(policy_id, updates)


