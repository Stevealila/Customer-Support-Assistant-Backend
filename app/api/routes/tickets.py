from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.ticket import (
    Message,
    MessageCreate,
    Ticket,
    TicketCreate,
    TicketUpdate,
    TicketWithMessages,
)
from app.core.dependencies import get_current_active_user
from app.db.base import get_db
from app.db.models import User
from app.services.ai_service import AIService
from app.services.ticket_service import TicketService

router = APIRouter()


@router.get("/", response_model=List[Ticket])
async def get_tickets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tickets for the current user.
    """
    ticket_service = TicketService(db)
    tickets = await ticket_service.get_user_tickets(user=current_user)
    return tickets


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_in: TicketCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new ticket.
    """
    ticket_service = TicketService(db)
    ticket = await ticket_service.create_ticket(user=current_user, ticket_in=ticket_in)
    return ticket


@router.get("/{ticket_id}", response_model=TicketWithMessages)
async def get_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific ticket with its messages.
    """
    ticket_service = TicketService(db)
    ticket = await ticket_service.get_ticket_with_messages(
        user=current_user, ticket_id=ticket_id
    )
    return ticket


@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_update: TicketUpdate,
    ticket_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a ticket.
    """
    ticket_service = TicketService(db)
    ticket = await ticket_service.update_ticket(
        user=current_user, ticket_id=ticket_id, ticket_update=ticket_update
    )
    return ticket


@router.post("/{ticket_id}/messages", response_model=Message)
async def add_message(
    message_in: MessageCreate,
    ticket_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a message to a ticket.
    """
    ticket_service = TicketService(db)
    message = await ticket_service.add_message(
        user=current_user, ticket_id=ticket_id, message_in=message_in
    )
    return message


@router.get("/{ticket_id}/ai-response")
async def stream_ai_response(
    ticket_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream an AI response for the latest customer message.
    """
    ticket_service = TicketService(db)
    ticket = await ticket_service.get_ticket_with_messages(
        user=current_user, ticket_id=ticket_id
    )
    
    if not ticket.messages:
        return StreamingResponse(
            content=iter([b"No messages in this ticket to respond to."]),
            media_type="text/event-stream",
        )
    
    # Get the latest customer message
    customer_messages = [msg for msg in ticket.messages if not msg.is_ai]
    if not customer_messages:
        return StreamingResponse(
            content=iter([b"No customer messages to respond to."]),
            media_type="text/event-stream",
        )
    
    latest_message = customer_messages[-1].content
    
    # Prepare message history (exclude the latest message)
    message_history = [
        {"content": msg.content, "is_ai": msg.is_ai}
        for msg in ticket.messages
        if msg.id != customer_messages[-1].id
    ]
    
    # Generate AI response
    ai_service = AIService()
    
    async def generate():
        full_response = ""
        async for text_chunk in ai_service.generate_response_stream(
            ticket_description=ticket.description,
            message_history=message_history,
            latest_message=latest_message,
        ):
            full_response += text_chunk
            yield f"data: {text_chunk}\n\n"
        
        # After response generation, save it to the database
        ai_message = MessageCreate(content=full_response, is_ai=True)
        await ticket_service.add_message(
            user=current_user, ticket_id=ticket_id, message_in=ai_message
        )
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        content=generate(),
        media_type="text/event-stream",
    )