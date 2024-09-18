from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from multipart.exceptions import DecodeError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.settings import settings
from app.users.models import User
from app.users.utils import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     return verify_access_token(token)


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("id")
        if user_id is None:
            raise credentials_exception
        token_data = {
            "id": user_id,
            "role": payload.get("role"),
        }  # Add other fields if necessary
    except JWTError:
        raise credentials_exception

    user = await db.get(User, int(token_data["id"]))
    if user is None:
        raise credentials_exception

    return user


def roles_required(*required_roles: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.role
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker
