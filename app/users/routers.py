from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.users.schemas import UserCreate, UserOut, UserUpdate
from app.users.services import UserService
from app.users.dependencies import get_current_user, roles_required
from app.users.utils import create_access_token
from app.core.database import get_db

# Create the router instance
user_router = APIRouter()


class UserRouter:
    def __init__(self):
        user_router.add_api_route(
            "/signup",
            self.signup,
            methods=["POST"],
            response_model=UserOut,
            tags=["Auth"],
        )
        user_router.add_api_route("/login", self.login, methods=["POST"], tags=["Auth"])
        user_router.add_api_route(
            "/me", self.get_me, methods=["GET"], response_model=UserOut, tags=["Users"]
        )
        user_router.add_api_route(
            "/",
            self.get_users,
            methods=["GET"],
            dependencies=[Depends(roles_required("admin", "manager"))],
            response_model=list[UserOut],
            tags=["Users"],
        )
        user_router.add_api_route(
            "/{user_id}",
            self.get_user_by_id,
            methods=["GET"],
            dependencies=[Depends(roles_required("admin", "manager"))],
            response_model=UserOut,
            tags=["Users"],
        )
        user_router.add_api_route(
            "/update",
            self.update_user,
            methods=["PUT"],
            response_model=UserOut,
            tags=["Users"],
        )
        user_router.add_api_route(
            "/update/{user_id}",
            self.update_user,
            methods=["PUT"],
            dependencies=[Depends(roles_required("admin"))],
            response_model=UserOut,
            tags=["Users"],
        )

        user_router.add_api_route(
            "/{user_id}",
            self.delete_user,
            methods=["DELETE"],
            dependencies=[Depends(roles_required("admin"))],
            tags=["Users"],
        )

    async def signup(self, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
        """Create a new user account."""
        service = UserService(db)
        return await service.create_user(user_data)

    async def login(
        self,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
    ):
        """Authenticate a user and return a JWT token."""
        service = UserService(db)
        user = await service.authenticate_user(form_data.username, form_data.password)

        # Create JWT token after successful authentication
        access_token = create_access_token(
            data={"sub": user.email, "id": user.id, "role": user.role}
        )
        return {"access_token": access_token, "token_type": "Bearer"}

    async def get_me(self, current_user: dict = Depends(get_current_user)):
        """Return the current user's profile."""
        return current_user

    async def update_user(
        self,
        user_update_data: UserUpdate,
        user_id: int | None = None,
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """
        Update the current user's profile, or if user_id is provided (admin role), update another user's profile.
        """
        service = UserService(db)

        # If an admin provides a user_id, they can update another user's profile
        if user_id is not None:
            return await service.update_user(user_id, user_update_data)

        # If no user_id is provided, the user is updating their own profile
        return await service.update_user(current_user["id"], user_update_data)

    async def get_users(self, db: AsyncSession = Depends(get_db)):
        """Admin or Manager: Get a list of all users."""
        service = UserService(db)
        return await service.get_users_by_role(
            "admin"
        ) + await service.get_users_by_role("manager")

    async def get_user_by_id(self, user_id: int, db: AsyncSession = Depends(get_db)):
        """Admin or Manager: Get a user by their ID."""
        service = UserService(db)
        return await service.get_user_by_id(user_id)

    async def delete_user(self, user_id: int, db: AsyncSession = Depends(get_db)):
        """Admin-only: Delete a user by ID."""
        service = UserService(db)
        await service.delete_user(user_id)
        return {"message": "User deleted successfully"}


UserRouter()
