import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    sources: Optional[List[Dict]] = None
    reasoning: Optional[List[Dict[str, str]]] = None  # CHANGED: From str to list of dicts to match actual data

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str

class ChatHistoryService:
    def __init__(self, storage_dir: str = "data/conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, conversation_id: str) -> Path:
        return self.storage_dir / f"{conversation_id}.json"
    
    def save_conversation(self, conversation: Conversation) -> bool:
        try:
            conversation.updated_at = datetime.utcnow().isoformat()
            file_path = self._get_file_path(conversation.id)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation.dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        try:
            file_path = self._get_file_path(conversation_id)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Conversation(**data)
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return None
    
    def list_conversations(self) -> List[Dict]:
        conversations = []
        try:
            for file_path in sorted(self.storage_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    conversations.append({
                        "id": data["id"],
                        "title": data["title"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "message_count": len(data["messages"])
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        except Exception as e:
            print(f"Error listing conversations: {e}")
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        try:
            file_path = self._get_file_path(conversation_id)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def add_message(self, conversation_id: str, message: Message) -> bool:
        conversation = self.load_conversation(conversation_id)
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                id=conversation_id,
                title=message.content[:50] + ("..." if len(message.content) > 50 else ""),
                messages=[message],
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
        else:
            conversation.messages.append(message)
        
        return self.save_conversation(conversation)

# Global instance
chat_history_service = ChatHistoryService()