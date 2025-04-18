from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.ticket import (
    MessageCreate,
    Ticket,
    TicketCreate,
    TicketUpdate,
    TicketWithMessages,
)
from app.core.exceptions import NotAuthorizedForTicketException, TicketNotFoundException
from app.db.models import User
from app.db.repositories.ticket_repository import TicketRepository


class TicketService:
    def __init__(self, db: AsyncSession):
        self.ticket_repository = TicketRepository(db)

    async def create_ticket(self, user: User, ticket_in: TicketCreate) -> Ticket:
        ticket_data = ticket_in.model_dump()
        ticket = await self.ticket_repository.create(
            obj_in=TicketCreate(**{**ticket_data, "user_id": user.id})
        )
        return ticket

    async def get_user_tickets(self, user: User) -> List[Ticket]:
        return await self.ticket_repository.get_user_tickets(user_id=user.id)

    async def get_ticket_with_messages(
        self, user: User, ticket_id: UUID
    ) -> TicketWithMessages:
        ticket = await self.ticket_repository.get_by_id_with_messages(ticket_id=ticket_id)
        if not ticket:
            raise TicketNotFoundException()
        
        # Check if user is authorized to access this ticket
        if str(ticket.user_id) != str(user.id) and user.role != "admin":
            raise NotAuthorizedForTicketException()
        
        return ticket

    async def update_ticket(
        self, user: User, ticket_id: UUID, ticket_update: TicketUpdate
    ) -> Ticket:
        ticket = await self.ticket_repository.get_by_id(id=ticket_id)
        if not ticket:
            raise TicketNotFoundException()
        
        # Check if user is authorized to update this ticket
        if str(ticket.user_id) != str(user.id) and user.role != "admin":
            raise NotAuthorizedForTicketException()
        
        updated_ticket = await self.ticket_repository.update(
            db_obj=ticket, obj_in=ticket_update.model_dump(exclude_unset=True)
        )
        return updated_ticket

    async def add_message(
        self, user: User, ticket_id: UUID, message_in: MessageCreate
    ):
        ticket = await self.ticket_repository.get_by_id(id=ticket_id)
        if not ticket:
            raise TicketNotFoundException()
        
        # Check if user is authorized to add message to this ticket
        if str(ticket.user_id) != str(user.id) and user.role != "admin":
            raise NotAuthorizedForTicketException()
        
        message = await self.ticket_repository.add_message(
            ticket_id=ticket_id, message_in=message_in
        )
        return message