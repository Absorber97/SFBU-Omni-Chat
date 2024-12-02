from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum

class ChatMessage(TypedDict):
    role: str
    content: str

class ChatHistory(List[tuple[str, str]]):
    pass

class DiscoveryContent(TypedDict):
    summary: str
    detailed: str
    steps: str
    faq: str
    suggestions: List[str]
    followups: List[str]
    has_rag_context: bool
    status: str
    error: Optional[str]

class ChatResponse(TypedDict):
    response: str
    has_rag_context: bool
    status: str
    error: Optional[str]

class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"
    VISITOR = "visitor"

class ChatMode(str, Enum):
    CHAT = "Chat Mode"
    DISCOVERY = "Discovery Mode"

class GradioResponse(TypedDict):
    outputs: Dict[Any, Any]
    status: str
    has_rag: bool
    error: Optional[str] 