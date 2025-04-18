from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel


class User(BaseModel):
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    tickets = relationship("Ticket", back_populates="user")


class Ticket(BaseModel):
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="open")
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket", cascade="all, delete")


class Message(BaseModel):
    content = Column(Text)
    is_ai = Column(Boolean, default=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("ticket.id"))
    ticket = relationship("Ticket", back_populates="messages")