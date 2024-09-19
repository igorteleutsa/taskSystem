from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rabbitmq import get_rabbitmq_connection
from app.tickets.models import Ticket, TicketExecutor
from app.tickets.repository import TicketRepository
from app.tickets.schemas import (
    TicketCreate,
    TicketUpdate,
    ExecutorAssign,
    TicketStatus,
    TicketStatusUpdate,
)
from app.users.schemas import UserOut
from app.users.services import UserService
from app.projects.services import ProjectService
from app.users.models import User


class TicketService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ticket_repository = TicketRepository(db)
        self.user_service = UserService(db)
        self.project_service = ProjectService(db)

    async def get_ticket_by_id(self, ticket_id: int):
        """Retrieve a ticket by ID if the current user is the member of the project"""
        # Retrieve the ticket from the repository
        ticket = await self.ticket_repository.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found."
            )

        return ticket

    async def create_ticket(
        self, ticket_data: TicketCreate, current_user: User
    ) -> Ticket:
        # Verify the project exists
        project = await self.project_service.get_project_by_id(
            ticket_data.project_id, current_user
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Create the ticket
        ticket_obj = await self.ticket_repository.create(
            {
                "title": ticket_data.title,
                "description": ticket_data.description,
                "status": ticket_data.status,
                "priority": ticket_data.priority,
                "project_id": ticket_data.project_id,
                "responsible_user_id": current_user.id,  # Assign current user as responsible user
            }
        )

        return ticket_obj

    async def update_ticket(
        self, ticket_id: int, ticket_data: TicketUpdate, current_user: User
    ) -> Ticket:
        ticket = await self.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
            )

        # Update ticket data
        updated_data = ticket_data.model_dump(exclude_unset=True)
        updated_ticket = await self.ticket_repository.update(ticket_id, updated_data)

        return updated_ticket

    async def delete_ticket(self, ticket_id: int, current_user: User) -> None:
        ticket = await self.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
            )
        await self.ticket_repository.delete(ticket_id)

    async def add_executor(
        self, ticket_id: int, executor_data: ExecutorAssign, current_user: User
    ) -> Ticket:
        ticket = await self.get_ticket_by_id(ticket_id)

        # Verify the user exists
        executor = await self.user_service.get_user_by_id(executor_data.user_id)
        if not executor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Add executor to ticket
        await self.ticket_repository.add_executor(
            ticket_id, ticket.project_id, executor.id
        )

        return ticket

    async def remove_executor(
        self, ticket_id: int, executor_data: ExecutorAssign, current_user: User
    ) -> Ticket:
        ticket = await self.get_ticket_by_id(ticket_id)

        # Verify the user exists
        executor = await self.user_service.get_user_by_id(executor_data.user_id)
        if not executor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Remove executor from ticket
        await self.ticket_repository.remove_executor(ticket_id, executor.id)

        return ticket

    async def list_tickets(self, project_id: int, current_user: User) -> list[Ticket]:
        project = await self.project_service.get_project_by_id(project_id, current_user)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        return await self.ticket_repository.get_all()

    async def change_ticket_status(
        self, ticket_id: int, status_data: TicketStatusUpdate, current_user: User
    ) -> Ticket:
        ticket = await self.get_ticket_by_id(ticket_id)

        # Validate the new status
        if status_data.new_status not in ["todo", "in_progress", "done"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
            )

        # Change the ticket status
        updated_ticket = await self.ticket_repository.update(
            ticket_id, {"status": status_data.new_status}
        )
        rabbitmq = await get_rabbitmq_connection()

        # Prepare RabbitMQ message
        message_body = {
            "ticket_id": ticket.id,
            "new_status": status_data.new_status,
            "updated_by": current_user.email,
            "timestamp": str(datetime.now()),
        }

        # Send RabbitMQ message
        await rabbitmq.send_message(
            queue_name="ticket_updates", message_body=message_body
        )

        return updated_ticket

    async def list_executors(self, ticket_id: int, current_user: User) -> list[UserOut]:
        """List all executors of a ticket."""
        # Retrieve the ticket
        ticket = await self.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found."
            )

        # Retrieve executors from the repository
        executors = await self.ticket_repository.get_ticket_executors(ticket_id)
        if not executors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No executors found for this ticket.",
            )

        # Convert executors to UserOut schema
        return [UserOut.model_validate(executor) for executor in executors]
