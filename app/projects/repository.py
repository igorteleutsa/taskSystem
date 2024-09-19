from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.base_repository import BaseRepository
from app.projects.models import Project, ProjectMember
from app.users.models import User


class ProjectRepository(BaseRepository):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Project, db_session)

    async def get_projects_by_owner(self, owner_id: int):
        """Retrieve all projects by the owner"""
        return await self.db_session.execute(
            self.model.query.filter_by(owner_id=owner_id)
        )

    async def add_member(self, project_id: int, user_id: int) -> None:
        """Add a member to a project."""
        project_member = ProjectMember(user_id=user_id, project_id=project_id)
        self.db_session.add(project_member)
        await self.db_session.commit()
        return await self.get_by_id(project_id)

    async def remove_member(self, project_id: int, user_id: int) -> None:
        """Remove a member from a project."""
        result = await self.db_session.execute(
            select(ProjectMember).where(
                ProjectMember.user_id == user_id, ProjectMember.project_id == project_id
            )
        )
        project_member = result.scalars().first()
        if not project_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found in the project.",
            )

        await self.db_session.delete(project_member)
        await self.db_session.commit()
        return await self.get_by_id(project_id)

    async def get_project_members(self, project_id: int):
        """Retrieve members of a project."""
        project = await self.db_session.execute(
            select(Project)
            .options(joinedload(Project.members))  # Eagerly load members
            .where(Project.id == project_id)
        )
        project = project.scalars().first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        return project.members

    async def change_project_status(self, project_id: int, new_status: str) -> Project:
        """Update the status of a project."""
        project = await self.get_by_id(project_id)
        project.status = new_status
        await self.db_session.commit()
        return await self.get_by_id(project_id)

    async def get_project_member(self, project_id: int, user_id: int) -> ProjectMember:
        """Retrieve a project member by project ID and user ID."""
        result = await self.db_session.execute(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .where(ProjectMember.user_id == user_id)
        )
        return result.scalars().first()
