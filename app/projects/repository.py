from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_repository import BaseRepository
from app.projects.models import Project


class ProjectRepository(BaseRepository):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Project, db_session)

    async def get_projects_by_owner(self, owner_id: int):
        """Retrieve all projects by the owner"""
        return await self.db_session.execute(
            self.model.query.filter_by(owner_id=owner_id)
        )
