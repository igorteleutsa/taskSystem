from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"


class UserBase(BaseModel):
    email: EmailStr
    name: str
    surname: str
    is_active: bool = True
    role: UserRole = UserRole.USER  # Use Enum for roles


class UserCreate(UserBase):
    password: str  # Raw password for hashing


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None  # The raw password, if updating
    name: str | None = None
    surname: str | None = None
    is_active: bool | None = None
    role: str | None = None


class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
