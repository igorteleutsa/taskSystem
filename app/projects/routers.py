from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectOut,
    ChangeStatusSchema,
    AddMemberRequest,
)
from app.projects.services import ProjectService
from app.core.database import get_db
from app.users.models import User
from app.users.dependencies import get_current_user
from app.users.schemas import UserOut

project_router = APIRouter()


class ProjectRouter:
    def __init__(self):
        project_router

        # Routes
        project_router.add_api_route(
            "/",
            self.create_project,
            methods=["POST"],
            response_model=ProjectOut,
            tags=["Projects"],
        )
        project_router.add_api_route(
            "/{project_id}",
            self.get_project,
            methods=["GET"],
            response_model=ProjectOut,
            tags=["Projects"],
        )
        project_router.add_api_route(
            "/",
            self.get_projects_by_owner,
            methods=["GET"],
            response_model=list[ProjectOut],
            tags=["Projects"],
        )
        project_router.add_api_route(
            "/{project_id}",
            self.update_project,
            methods=["PUT"],
            response_model=ProjectOut,
            tags=["Projects"],
        )
        project_router.add_api_route(
            "/{project_id}", self.delete_project, methods=["DELETE"], tags=["Projects"]
        )
        project_router.add_api_route(
            "/{project_id}/members",
            self.add_member,
            methods=["POST"],
            response_model=ProjectOut,
            tags=["Project Members"],
        )
        project_router.add_api_route(
            "/{project_id}/members/{user_id}",
            self.remove_member,
            methods=["DELETE"],
            response_model=ProjectOut,
            tags=["Project Members"],
        )
        project_router.add_api_route(
            "/{project_id}/members",
            self.list_members,
            methods=["GET"],
            response_model=list[UserOut],
            tags=["Project Members"],
        )
        project_router.add_api_route(
            "/{project_id}/status",
            self.change_status,
            methods=["PUT"],
            tags=["Projects"],
        )

    async def create_project(
        self,
        project_data: ProjectCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Create a new project."""
        service = ProjectService(db)
        return await service.create_project(project_data, current_user)

    async def get_project(
        self,
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Retrieve a specific project by ID."""
        service = ProjectService(db)
        return await service.get_project_by_id(project_id, current_user)

    async def get_projects_by_owner(
        self,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Retrieve all projects owned by the current user."""
        service = ProjectService(db)
        return await service.get_projects_by_owner(current_user.id)

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Update an existing project."""
        service = ProjectService(db)
        return await service.update_project(project_id, project_data, current_user)

    async def delete_project(
        self,
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Delete a project."""
        service = ProjectService(db)
        return await service.delete_project(project_id, current_user)

    # Member handlers
    async def add_member(
        self,
        project_id: int,
        add_member_data: AddMemberRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Add a member to a project."""
        service = ProjectService(db)
        return await service.add_member(project_id, add_member_data, current_user)

    async def remove_member(
        self,
        project_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Remove a member from a project."""
        service = ProjectService(db)
        member = await service.get_member(user_id)
        return await service.remove_member(project_id, member, current_user)

    async def list_members(
        self,
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """List all members of a project."""
        service = ProjectService(db)
        return await service.list_members(project_id)

    async def change_status(
        self,
        project_id: int,
        status_data: ChangeStatusSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Change the status of a project."""
        service = ProjectService(db)
        return await service.change_status(
            project_id, status_data.new_status, current_user
        )


# Initialize project router
ProjectRouter()
