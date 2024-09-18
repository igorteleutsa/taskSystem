from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.projects.repository import ProjectRepository
from app.projects.schemas import ProjectCreate, ProjectUpdate
from app.users.models import User


class ProjectService:
    def __init__(self, db_session: AsyncSession):
        self.repository = ProjectRepository(db_session)

    async def create_project(self, project_data: ProjectCreate, owner: User):
        """Create a new project with the current user as the owner."""
        project_data = project_data.model_dump()
        project_data["owner_id"] = owner.id
        new_project = await self.repository.create(project_data)
        return new_project

    async def update_project(
        self, project_id: int, project_data: ProjectUpdate, current_user: User
    ):
        """Update an existing project if the current user is the owner."""
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        print(current_user.__class__)
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to update this project",
            )

        updated_project = await self.repository.update(
            project_id, project_data.model_dump(exclude_unset=True)
        )
        return updated_project

    async def delete_project(self, project_id: int, current_user: User):
        """Delete a project if the current user is the owner."""
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to delete this project",
            )

        await self.repository.delete(project_id)
        return {"message": "Project deleted successfully"}

    async def get_project_by_id(self, project_id: int, current_user: User):
        """Retrieve a project by ID if the current user is the owner."""
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Check if current_user is either the owner
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to access this project",
            )

        return project

    async def get_projects_by_owner(self, owner_id: int):
        """Get all projects by a specific owner."""
        return await self.repository.get_projects_by_owner(owner_id)
