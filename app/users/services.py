from sqlalchemy.ext.asyncio import AsyncSession
from app.users.repository import UserRepository
from app.users.utils import hash_password, verify_password
from app.users.schemas import UserCreate, UserOut, UserUpdate
from app.users.models import User
from fastapi import HTTPException, status


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.repository = UserRepository(db_session)

    async def create_user(self, user_data: UserCreate) -> UserOut:
        """Create a new user with hashed password."""
        # Check if user already exists
        existing_user = await self.repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )

        # Hash the user's password
        hashed_password = hash_password(user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]  # Remove raw password after hashing

        # Create the user
        new_user = await self.repository.create(user_dict)
        return UserOut.from_orm(new_user)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user by verifying email and password."""
        user = await self.repository.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def get_user_by_id(self, user_id: int) -> UserOut:
        """Fetch user information by user ID."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        return UserOut.from_orm(user)

    async def get_users_by_role(self, role: str) -> list[UserOut]:
        """Fetch a list of users by their role."""
        users = await self.repository.get_user_by_role(role)
        return [UserOut.from_orm(user) for user in users]

    async def update_user(self, user_id: int, user_update_data: UserUpdate) -> UserOut:
        """Update an existing user's details."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        # If password is being updated, hash it
        update_data = user_update_data.model_dump(
            exclude_unset=True
        )  # Only update fields that are provided
        if update_data.get("password"):
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        updated_user = await self.repository.update(user_id, update_data)
        return UserOut.from_orm(updated_user)

    async def delete_user(self, user_id: int) -> None:
        """Delete a user by their ID."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        await self.repository.delete(user_id)
        return (
            None  # Returning None for consistency, could also return an empty response
        )
