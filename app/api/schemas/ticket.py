from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    content: str
    is_ai: bool = False


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: UUID
    created_at: datetime
    ticket_id: UUID
    
    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    status: Optional[str] = "open"


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    status: Optional[str] = None


class TicketInDBBase(TicketBase):
    id: UUID
    created_at: datetime
    user_id: UUID
    
    class Config:
        from_attributes = True


class Ticket(TicketInDBBase):
    pass


class TicketWithMessages(Ticket):
    messages: List[Message] = []