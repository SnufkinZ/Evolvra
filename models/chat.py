from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    message_id: str
    content: str
    circumstance: str   # Context or situation of the message, such as "Goal page", "Task page" or "Chat page"
    timestamp: datetime = datetime.utcnow()