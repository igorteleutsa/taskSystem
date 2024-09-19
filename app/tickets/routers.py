from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.tickets.schemas import (
    TicketCreate,
    TicketUpdate,
    ExecutorAssign,
    TicketOut,
    TicketStatusUpdate,
)
from app.tickets.services import TicketService
from app.users.dependencies import get_current_user, roles_required
from app.core.database import get_db

# Create the router instance
from app.users.schemas import UserOut

ticket_router = APIRouter()


class TicketRouter:
    def __init__(self):
        ticket_router.add_api_route(
            "/",
            self.create_ticket,
            methods=["POST"],
            response_model=TicketOut,
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/{ticket_id}",
            self.get_ticket,
            methods=["GET"],
            response_model=TicketOut,
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/{ticket_id}",
            self.update_ticket,
            methods=["PUT"],
            response_model=TicketOut,
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/{ticket_id}",
            self.delete_ticket,
            methods=["DELETE"],
            dependencies=[Depends(roles_required("admin", "manager"))],
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/{ticket_id}/executors",
            self.add_executor,
            methods=["POST"],
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/{ticket_id}/executors/{executor_id}",
            self.remove_executor,
            methods=["DELETE"],
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/{ticket_id}/status",
            self.change_status,
            methods=["PUT"],
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/list/{project_id}",
            self.list_tickets,
            methods=["GET"],
            response_model=list[TicketOut],
            tags=["Tickets"],
        )
        ticket_router.add_api_route(
            "/{ticket_id}/executors",
            self.list_executors,
            methods=["GET"],
            response_model=list[UserOut],
            tags=["Tickets"],
        )

    async def create_ticket(
        self,
        ticket_data: TicketCreate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        """Create a new ticket."""
        service = TicketService(db)
        return await service.create_ticket(ticket_data, current_user)

    async def get_ticket(self, ticket_id: int, db: AsyncSession = Depends(get_db)):
        """Retrieve a specific ticket by ID."""
        service = TicketService(db)
        return await service.get_ticket_by_id(ticket_id)

    async def update_ticket(
        self,
        ticket_id: int,
        ticket_data: TicketUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        """Update a specific ticket by ID."""
        service = TicketService(db)
        return await service.update_ticket(ticket_id, ticket_data, current_user)

    async def delete_ticket(
        self,
        ticket_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        """Delete a specific ticket by ID."""
        service = TicketService(db)
        return await service.delete_ticket(ticket_id, current_user)

    async def add_executor(
        self,
        ticket_id: int,
        executor_data: ExecutorAssign,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        """Add an executor to the ticket."""
        service = TicketService(db)
        return await service.add_executor(ticket_id, executor_data, current_user)

    async def remove_executor(
        self,
        ticket_id: int,
        executor_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        """Remove an executor from the ticket."""
        service = TicketService(db)
        executor_data = ExecutorAssign(user_id=executor_id)
        return await service.remove_executor(ticket_id, executor_data, current_user)

    async def change_status(
        self,
        ticket_id: int,
        status_data: TicketStatusUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        """Change the status of a specific ticket."""
        service = TicketService(db)
        return await service.change_ticket_status(ticket_id, status_data, current_user)

    async def list_tickets(
        self,
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        """List all tickets for a project."""
        service = TicketService(db)
        return await service.list_tickets(project_id, current_user)

    async def list_executors(
        self,
        ticket_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ) -> list[UserOut]:
        """List all executors of a specific ticket."""
        service = TicketService(db)
        return await service.list_executors(ticket_id, current_user)


# Initialize the ticket router
TicketRouter()
