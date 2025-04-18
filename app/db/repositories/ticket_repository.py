from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Message, Ticket, User
from app.db.repositories.base import BaseRepository
from app.api.schemas.ticket import MessageCreate, TicketCreate, TicketUpdate


class TicketRepository(BaseRepository[Ticket, TicketCreate, TicketUpdate]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Ticket)

    async def get_by_id_with_messages(self, ticket_id: UUID) -> Optional[Ticket]:
        stmt = (
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(selectinload(Ticket.messages))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_tickets(self, user_id: UUID) -> List[Ticket]:
        stmt = select(Ticket).where(Ticket.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add_message(self, ticket_id: UUID, message_in: MessageCreate) -> Message:
        message = Message(
            content=message_in.content,
            is_ai=message_in.is_ai,
            ticket_id=ticket_id,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message