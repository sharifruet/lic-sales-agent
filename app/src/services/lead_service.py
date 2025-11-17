from typing import List, Optional
from src.models.lead import Lead
from src.repositories.lead_repository import LeadRepository
from src.services.validation_service import ValidationService
from src.services.encryption_service import EncryptionService
from src.services.file_storage_service import FileStorageService


class LeadValidationError(Exception):
    """Raised when lead validation fails."""
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")


class LeadService:
    def __init__(self, repo: LeadRepository):
        self.repo = repo
        self.validation_service = ValidationService()
        self.encryption_service = EncryptionService()
        self.file_storage = FileStorageService()

    async def create_lead(self, name: str, phone: str, nid: Optional[str] = None, 
                         address: Optional[str] = None, interested_policy: Optional[str] = None,
                         email: Optional[str] = None) -> Lead:
        # Validate lead data
        validation_result = self.validation_service.validate_lead_data(
            name=name, phone=phone, nid=nid, address=address, email=email
        )
        if not validation_result.is_valid:
            raise LeadValidationError(validation_result.errors)
        
        # Normalize phone number
        phone_result = self.validation_service.validate_phone_number(phone)
        phone_normalized = phone_result.normalized or phone.strip()
        
        # Encrypt sensitive data
        phone_encrypted = self.encryption_service.encrypt(phone_normalized)
        nid_encrypted = self.encryption_service.encrypt(nid.strip()) if nid else None
        
        # Check for duplicates
        existing = await self.repo.find_by_phone(phone_encrypted)
        if existing:
            raise ValueError(f"Lead with phone {phone_normalized[:3]}*** already exists")
        
        lead = Lead(
            name=name.strip(),
            phone=phone_encrypted,  # Store encrypted
            nid=nid_encrypted,  # Store encrypted
            address=address.strip() if address else None,
            interested_policy=interested_policy.strip() if interested_policy else None,
        )
        saved_lead = await self.repo.create(lead)
        
        # Save to file storage (async, fire and forget)
        try:
            await self.file_storage.save_lead(saved_lead)
        except Exception:
            pass  # Don't fail if file storage fails
        
        return saved_lead

    async def list_leads(self) -> List[Lead]:
        return await self.repo.list()
    
    async def get_lead(self, lead_id: int) -> Optional[Lead]:
        return await self.repo.find_by_id(lead_id)
    
    def mask_phone(self, encrypted_phone: str) -> str:
        """Mask phone number for display (decrypt and mask)."""
        try:
            phone = self.encryption_service.decrypt(encrypted_phone)
            if len(phone) > 4:
                return f"{phone[:3]}***{phone[-4:]}"
            return "***"
        except:
            return "***"
    
    async def export_leads(self, format: str = "csv") -> str:
        """Export leads to specified format."""
        leads = await self.list_leads()
        if format == "csv":
            return await self.file_storage.export_leads_to_csv(leads)
        elif format == "json":
            return await self.file_storage.export_leads_to_json(leads)
        else:
            raise ValueError(f"Unsupported format: {format}")
