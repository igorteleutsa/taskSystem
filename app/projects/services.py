from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.projects.repository import ProjectRepository
from app.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectOut,
    ProjectStatus,
    AddMemberRequest,
)
from app.users.models import User
from app.users.schemas import UserOut
from app.users.services import UserService


class ProjectService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
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

    async def get_member(self, user_id: int) -> User:
        """Fetch a user by ID using the UserService."""
        user_service = UserService(self.db_session)
        member = await user_service.get_user_by_id(user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return member

    async def add_member(
        self, project_id: int, add_member_data: AddMemberRequest, current_user: User
    ) -> ProjectOut:
        """Add a member to a project."""

        project = await self.repository.get_by_id(project_id)

        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to add members to this project.",
            )
        user_service = UserService(self.db_session)
        # Get the user ID from the request body data
        member = await user_service.get_user_by_id(add_member_data.user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        # Add the member to the project
        return await self.repository.add_member(project_id, member.id)

    async def remove_member(
        self, project_id: int, member: User, current_user: User
    ) -> ProjectOut:
        """Remove a member from a project."""
        project = await self.repository.get_by_id(project_id)

        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to remove members from this project.",
            )

        await self.repository.remove_member(project_id, member.id)
        await self.db_session.refresh(project)
        return project

    async def list_members(self, project_id: int) -> list[UserOut]:
        """List all members of a project."""
        return await self.repository.get_project_members(project_id)

    async def change_status(
        self, project_id: int, new_status: ProjectStatus, current_user: User
    ) -> ProjectOut:
        """Change the status of a project."""
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found."
            )
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to change the status of this project.",
            )

        return await self.repository.change_project_status(project_id, new_status)
