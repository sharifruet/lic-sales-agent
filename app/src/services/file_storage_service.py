"""File storage service for leads and conversations."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from app.src.config import settings
from app.src.models.lead import Lead
from app.src.models.conversation import Conversation
from app.src.models.message import Message


class FileStorageService:
    """Service for file-based storage of leads and conversations."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or settings.file_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.leads_path = self.storage_path / "leads"
        self.conversations_path = self.storage_path / "conversations"
        self.leads_path.mkdir(exist_ok=True)
        self.conversations_path.mkdir(exist_ok=True)
    
    def _get_daily_filename(self, prefix: str) -> str:
        """Get filename for today's data."""
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        return f"{prefix}_{date_str}.json"
    
    async def save_lead(self, lead: Lead) -> None:
        """Save lead to daily JSON file."""
        if not settings.enable_file_storage:
            return
        
        filename = self._get_daily_filename("leads")
        filepath = self.leads_path / filename
        
        # Load existing data
        leads = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                try:
                    leads = json.load(f)
                except json.JSONDecodeError:
                    leads = []
        
        # Append new lead
        lead_dict = {
            "id": lead.id,
            "name": lead.name,
            "phone": "***",  # Don't store encrypted data in files
            "nid": "***",
            "address": lead.address,
            "interested_policy": lead.interested_policy,
            "created_at": lead.created_at.isoformat(),
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        }
        
        leads.append(lead_dict)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
    
    async def save_conversation(self, conversation: Conversation, messages: List[Message]) -> None:
        """Save conversation to daily JSON file."""
        if not settings.enable_file_storage:
            return
        
        filename = self._get_daily_filename("conversations")
        filepath = self.conversations_path / filename
        
        # Load existing data
        conversations = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                try:
                    conversations = json.load(f)
                except json.JSONDecodeError:
                    conversations = []
        
        # Append new conversation
        conv_dict = {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "stage": conversation.stage,
            "message_count": conversation.message_count,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if hasattr(msg, 'created_at') else None
                }
                for msg in messages
            ],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
        }
        
        conversations.append(conv_dict)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    async def export_leads_to_csv(self, leads: List[Lead], decrypt: bool = False) -> str:
        """
        Export leads to CSV format.
        
        Args:
            leads: List of leads to export
            decrypt: If True, decrypt phone/NID for admin (requires EncryptionService)
        """
        import csv
        from io import StringIO
        from app.src.services.encryption_service import EncryptionService
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "ID", "Name", "Phone", "NID", "Email", "Address", 
            "Policy Interest", "Status", "Preferred Contact Time", "Notes",
            "Conversation ID", "Created At", "Updated At"
        ])
        
        # Data rows
        encryption_service = EncryptionService() if decrypt else None
        
        for lead in leads:
            # Handle phone
            if decrypt and encryption_service:
                try:
                    phone = encryption_service.decrypt(lead.phone)
                except:
                    phone = "***"
            else:
                phone = "***"
            
            # Handle NID
            if decrypt and encryption_service and lead.nid:
                try:
                    nid = encryption_service.decrypt(lead.nid)
                except:
                    nid = "***"
            else:
                nid = "***" if lead.nid else ""
            
            writer.writerow([
                lead.id,
                lead.name,
                phone,
                nid,
                lead.email or "",
                lead.address or "",
                lead.interested_policy or "",
                lead.status.value if lead.status else "new",
                lead.preferred_contact_time or "",
                lead.notes or "",
                lead.conversation_id or "",
                lead.created_at.isoformat() if lead.created_at else "",
                lead.updated_at.isoformat() if lead.updated_at else "",
            ])
        
        return output.getvalue()
    
    async def export_leads_to_json(self, leads: List[Lead], decrypt: bool = False) -> str:
        """
        Export leads to JSON format.
        
        Args:
            leads: List of leads to export
            decrypt: If True, decrypt phone/NID for admin (requires EncryptionService)
        """
        from app.src.services.encryption_service import EncryptionService
        
        encryption_service = EncryptionService() if decrypt else None
        
        leads_dict = []
        for lead in leads:
            # Handle phone
            if decrypt and encryption_service:
                try:
                    phone = encryption_service.decrypt(lead.phone)
                except:
                    phone = "***"
            else:
                phone = "***"
            
            # Handle NID
            if decrypt and encryption_service and lead.nid:
                try:
                    nid = encryption_service.decrypt(lead.nid)
                except:
                    nid = "***"
            else:
                nid = None
            
            lead_dict = {
                "id": lead.id,
                "name": lead.name,
                "phone": phone,
                "nid": nid,
                "email": lead.email,
                "address": lead.address,
                "interested_policy": lead.interested_policy,
                "status": lead.status.value if lead.status else "new",
                "preferred_contact_time": lead.preferred_contact_time,
                "notes": lead.notes,
                "conversation_id": lead.conversation_id,
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
                "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
            }
            leads_dict.append(lead_dict)
        
        return json.dumps(leads_dict, indent=2, ensure_ascii=False)
    
    async def export_conversation_to_text(
        self,
        conversation: Conversation,
        messages: List[Message],
        state: Optional[any] = None,
        summary: Optional[str] = None
    ) -> str:
        """Export conversation to plain text format."""
        from app.src.services.session_manager import SessionState
        
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("CONVERSATION TRANSCRIPT")
        lines.append("=" * 80)
        lines.append(f"Session ID: {conversation.session_id}")
        lines.append(f"Conversation ID: {conversation.id}")
        lines.append(f"Stage: {conversation.stage}")
        lines.append(f"Message Count: {conversation.message_count}")
        lines.append(f"Created: {conversation.created_at.isoformat() if conversation.created_at else 'N/A'}")
        lines.append("")
        
        # Customer Profile
        if state and hasattr(state, 'customer_profile'):
            lines.append("-" * 80)
            lines.append("CUSTOMER PROFILE")
            lines.append("-" * 80)
            profile = state.customer_profile
            if profile.age:
                lines.append(f"Age: {profile.age}")
            if profile.name:
                lines.append(f"Name: {profile.name}")
            if profile.purpose:
                lines.append(f"Purpose: {profile.purpose}")
            if profile.dependents:
                lines.append(f"Dependents: {profile.dependents}")
            lines.append("")
        
        # Messages
        lines.append("-" * 80)
        lines.append("CONVERSATION MESSAGES")
        lines.append("-" * 80)
        lines.append("")
        
        for msg in messages:
            role_display = "CUSTOMER" if msg.role == "user" else "AGENT"
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(msg, 'created_at') and msg.created_at else "N/A"
            lines.append(f"[{timestamp}] {role_display}:")
            lines.append(msg.content)
            lines.append("")
        
        # Summary
        if summary:
            lines.append("-" * 80)
            lines.append("CONVERSATION SUMMARY")
            lines.append("-" * 80)
            lines.append(summary)
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF TRANSCRIPT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    async def export_conversation_to_csv(
        self,
        conversation: Conversation,
        messages: List[Message],
        state: Optional[any] = None,
        summary: Optional[str] = None
    ) -> str:
        """Export conversation to CSV format."""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            "Message ID", "Timestamp", "Role", "Content"
        ])
        
        # Message rows
        for idx, msg in enumerate(messages, 1):
            timestamp = msg.created_at.isoformat() if hasattr(msg, 'created_at') and msg.created_at else ""
            role = "Customer" if msg.role == "user" else "Agent"
            # Escape content for CSV
            content = msg.content.replace('"', '""')  # Escape quotes
            writer.writerow([
                idx,
                timestamp,
                role,
                content
            ])
        
        return output.getvalue()
    
    async def export_conversation_to_pdf(
        self,
        conversation: Conversation,
        messages: List[Message],
        state: Optional[any] = None,
        summary: Optional[str] = None
    ) -> bytes:
        """
        Export conversation to PDF format.
        
        Note: This is a basic implementation. For production, consider using reportlab or weasyprint.
        """
        try:
            # Try to use reportlab if available
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("<b>CONVERSATION TRANSCRIPT</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2 * inch))
            
            # Metadata
            metadata = f"<b>Session ID:</b> {conversation.session_id}<br/>"
            metadata += f"<b>Conversation ID:</b> {conversation.id}<br/>"
            metadata += f"<b>Stage:</b> {conversation.stage}<br/>"
            metadata += f"<b>Message Count:</b> {conversation.message_count}<br/>"
            story.append(Paragraph(metadata, styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
            
            # Messages
            story.append(Paragraph("<b>CONVERSATION MESSAGES</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            for msg in messages:
                role = "CUSTOMER" if msg.role == "user" else "AGENT"
                timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(msg, 'created_at') and msg.created_at else "N/A"
                header = f"<b>[{timestamp}] {role}:</b>"
                story.append(Paragraph(header, styles['Heading3']))
                # Escape HTML in content
                content = msg.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                content = content.replace("\n", "<br/>")
                story.append(Paragraph(content, styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
            
            # Summary
            if summary:
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph("<b>CONVERSATION SUMMARY</b>", styles['Heading2']))
                summary_text = summary.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                summary_text = summary_text.replace("\n", "<br/>")
                story.append(Paragraph(summary_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        
        except ImportError:
            # Fallback: return simple text as bytes if reportlab not available
            text_content = await self.export_conversation_to_text(conversation, messages, state, summary)
            return text_content.encode('utf-8')

