from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.users.models import User
from app.core.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by their email."""
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_user_by_role(self, role: str) -> list[User]:
        """Fetch users by their role (e.g., admin, manager)."""
        query = select(User).where(User.role == role)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    # You can add more user-specific methods here as needed
