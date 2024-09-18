from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.projects.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.projects.services import ProjectService
from app.core.database import get_db
from app.users.models import User
from app.users.dependencies import get_current_user


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


# Initialize project router
ProjectRouter()
