from typing import Optional

from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.tickets.models import Ticket, TicketExecutor
from app.core.base_repository import BaseRepository
from sqlalchemy.future import select

from app.users.models import User


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Ticket, db_session)

    async def add_executor(self, ticket_id: int, project_id: int, user_id: int) -> None:
        """Add an executor (user) to a ticket."""
        ticket_executor = TicketExecutor(
            ticket_id=ticket_id, project_id=project_id, user_id=user_id
        )
        self.db_session.add(ticket_executor)
        await self.db_session.commit()

    async def remove_executor(self, ticket_id: int, user_id: int) -> None:
        """Remove an executor (user) from a ticket."""
        query = (
            delete(TicketExecutor)
            .where(TicketExecutor.ticket_id == ticket_id)
            .where(TicketExecutor.user_id == user_id)
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.commit()

    async def get_ticket_executors(self, ticket_id: int) -> list[int]:
        """Get all executors (user IDs) for a specific ticket."""
        query = select(TicketExecutor.user_id).where(
            TicketExecutor.ticket_id == ticket_id
        )
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_by_project(self, project_id: int) -> list[Ticket]:
        """Retrieve all tickets for a specific project."""
        query = select(Ticket).where(Ticket.project_id == project_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def change_status(self, ticket_id: int, new_status: str) -> Ticket:
        """Change the status of a ticket."""
        query = (
            update(Ticket)
            .where(Ticket.id == ticket_id)
            .values(status=new_status)
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.commit()
        return await self.get_by_id(ticket_id)

    async def get_ticket_executors(self, ticket_id: int) -> list[User]:
        """Retrieve all executors for a given ticket."""
        result = await self.db_session.execute(
            select(User)
            .join(TicketExecutor, TicketExecutor.user_id == User.id)
            .where(TicketExecutor.ticket_id == ticket_id)
        )
        return result.scalars().all()
