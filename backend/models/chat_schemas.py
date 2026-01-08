from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class MessageCreate(BaseModel):
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    reasoning: Optional[List[Dict[str, str]]] = None  # Changed to specific type for safety (matches orchestrator output)

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str
    sources: Optional[List[Dict]] = None
    reasoning: Optional[List[Dict[str, str]]] = None  # CHANGED: From str to list of dicts for consistency

class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int

class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: List[MessageResponse]
    created_at: str
    updated_at: str

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationList(BaseModel):
    conversations: List[ConversationSummary]
    total: int