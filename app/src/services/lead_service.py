from typing import List, Optional
from src.models.lead import Lead
from src.repositories.lead_repository import LeadRepository


class LeadService:
    def __init__(self, repo: LeadRepository):
        self.repo = repo

    async def create_lead(self, name: str, phone: str, nid: Optional[str] = None, address: Optional[str] = None,
                          interested_policy: Optional[str] = None) -> Lead:
        # basic normalization
        phone_normalized = phone.strip()
        lead = Lead(
            name=name.strip(),
            phone=phone_normalized,
            nid=nid.strip() if nid else None,
            address=address.strip() if address else None,
            interested_policy=interested_policy.strip() if interested_policy else None,
        )
        return await self.repo.create(lead)

    async def list_leads(self) -> List[Lead]:
        return await self.repo.list()
