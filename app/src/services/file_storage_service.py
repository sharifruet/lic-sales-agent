"""File storage service for leads and conversations."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from src.config import settings
from src.models.lead import Lead
from src.models.conversation import Conversation
from src.models.message import Message


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
    
    async def export_leads_to_csv(self, leads: List[Lead]) -> str:
        """Export leads to CSV format."""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "ID", "Name", "Phone", "Address", 
            "Policy Interest", "Created At"
        ])
        
        # Data rows (phone/nid masked)
        for lead in leads:
            writer.writerow([
                lead.id,
                lead.name,
                "***",  # Masked
                lead.address or "",
                lead.interested_policy or "",
                lead.created_at.isoformat() if lead.created_at else "",
            ])
        
        return output.getvalue()
    
    async def export_leads_to_json(self, leads: List[Lead]) -> str:
        """Export leads to JSON format."""
        leads_dict = [
            {
                "id": lead.id,
                "name": lead.name,
                "phone": "***",  # Masked
                "address": lead.address,
                "interested_policy": lead.interested_policy,
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
            }
            for lead in leads
        ]
        return json.dumps(leads_dict, indent=2, ensure_ascii=False)

