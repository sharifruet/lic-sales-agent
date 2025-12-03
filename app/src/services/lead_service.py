from typing import List, Optional
from app.src.models.lead import Lead, LeadStatus
from app.src.repositories.lead_repository import LeadRepository
from app.src.services.validation_service import ValidationService
from app.src.services.encryption_service import EncryptionService
from app.src.services.file_storage_service import FileStorageService


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
                         email: Optional[str] = None, conversation_id: Optional[int] = None) -> Lead:
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
            email=email.strip() if email else None,
            status=LeadStatus.NEW,  # Set initial status
            conversation_id=conversation_id,  # Link to conversation if provided
        )
        saved_lead = await self.repo.create(lead)
        
        # Save to file storage (async, fire and forget)
        try:
            await self.file_storage.save_lead(saved_lead)
        except Exception:
            pass  # Don't fail if file storage fails
        
        return saved_lead

    async def list_leads(
        self,
        status: Optional[str] = None,
        interested_policy: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[List[Lead], int]:
        """
        List leads with filtering, search, and pagination.
        
        Returns:
            Tuple of (leads list, total count)
        """
        return await self.repo.list(
            status=status,
            interested_policy=interested_policy,
            search=search,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    
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
    
    async def export_leads(
        self,
        format: str = "csv",
        status: Optional[str] = None,
        interested_policy: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        decrypt: bool = False,
    ) -> str:
        """
        Export leads to specified format with optional filtering.
        
        Args:
            format: Export format ("csv" or "json")
            status: Filter by status
            interested_policy: Filter by policy
            search: Search by name or email
            start_date: Filter by created date from
            end_date: Filter by created date to
            decrypt: If True, decrypt phone/NID for admin (default: False for security)
        
        Returns:
            Exported data as string
        """
        leads, _ = await self.list_leads(
            status=status,
            interested_policy=interested_policy,
            search=search,
            start_date=start_date,
            end_date=end_date,
            limit=None,  # Export all matching leads
            offset=None,
        )
        
        if format == "csv":
            return await self.file_storage.export_leads_to_csv(leads, decrypt=decrypt)
        elif format == "json":
            return await self.file_storage.export_leads_to_json(leads, decrypt=decrypt)
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def update_lead(
        self,
        lead_id: int,
        status: Optional[LeadStatus] = None,
        notes: Optional[str] = None,
        email: Optional[str] = None,
        preferred_contact_time: Optional[str] = None,
        interested_policy: Optional[str] = None,
        changed_by: Optional[str] = None,
    ) -> Optional[Lead]:
        """Update lead with partial updates (admin only)."""
        # Get existing lead to track status changes
        existing_lead = await self.repo.find_by_id(lead_id)
        if not existing_lead:
            return None
        
        previous_status = existing_lead.status.value if existing_lead.status else None
        
        # Validate status if provided
        if status is not None:
            if not isinstance(status, LeadStatus):
                try:
                    status = LeadStatus(status)
                except ValueError:
                    raise ValueError(
                        f"Invalid status: {status}. Must be one of: "
                        f"{', '.join([s.value for s in LeadStatus])}"
                    )
        
        # Validate email if provided
        if email is not None:
            email = email.strip()
            if email:
                validation_result = self.validation_service.validate_email(email)
                if not validation_result.is_valid:
                    raise LeadValidationError(validation_result.errors)
            else:
                email = None
        
        # Build updates dict
        updates = {}
        if status is not None:
            updates["status"] = status
        if notes is not None:
            updates["notes"] = notes.strip() if notes.strip() else None
        if email is not None:
            updates["email"] = email
        if preferred_contact_time is not None:
            updates["preferred_contact_time"] = (
                preferred_contact_time.strip() if preferred_contact_time.strip() else None
            )
        if interested_policy is not None:
            updates["interested_policy"] = (
                interested_policy.strip() if interested_policy.strip() else None
            )
        
        # At least one field must be provided
        if not updates:
            raise ValueError("At least one field must be provided for update")
        
        # Update lead
        updated_lead = await self.repo.update(lead_id, updates)
        
        # Log status change if status was updated
        if status is not None and changed_by:
            new_status_value = status.value if isinstance(status, LeadStatus) else status
            if previous_status != new_status_value:
                # Use notes for status history if status changed
                # Notes can serve dual purpose: lead notes AND status change reason
                status_change_notes = notes.strip() if notes else None
                await self.repo.add_status_history(
                    lead_id=lead_id,
                    previous_status=previous_status,
                    new_status=new_status_value,
                    changed_by=changed_by,
                    notes=status_change_notes
                )
        
        return updated_lead

    async def get_status_history(self, lead_id: int, limit: Optional[int] = None) -> List:
        """Get status change history for a lead."""
        return await self.repo.get_status_history(lead_id, limit)

    async def bulk_update_status(
        self,
        lead_ids: List[int],
        status: LeadStatus,
        changed_by: str,
        notes: Optional[str] = None
    ) -> List[int]:
        """
        Bulk update status for multiple leads.
        
        Args:
            lead_ids: List of lead IDs to update
            status: New status (LeadStatus enum)
            changed_by: User/admin who made the change
            notes: Optional notes for status change
        
        Returns:
            List of successfully updated lead IDs
        """
        # Validate status
        if not isinstance(status, LeadStatus):
            try:
                status = LeadStatus(status)
            except ValueError:
                raise ValueError(
                    f"Invalid status: {status}. Must be one of: "
                    f"{', '.join([s.value for s in LeadStatus])}"
                )
        
        # Bulk update status and log changes
        updated_ids = await self.repo.bulk_update_status(
            lead_ids=lead_ids,
            new_status=status.value,
            changed_by=changed_by,
            notes=notes.strip() if notes else None
        )
        
        return updated_ids
