from sqlalchemy import Column, String, Boolean, Enum as SqlEnum
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"  # Example of another role


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.USER)

    # Relationship with projects (as owner)
    owned_projects = relationship(
        "Project", back_populates="owner", cascade="all, delete-orphan"
    )

    # Relationship with projects as a member (many-to-many via ProjectMember class)
    project_memberships = relationship(
        "ProjectMember", back_populates="user", overlaps="projects,members"
    )
    projects = relationship(
        "Project", secondary="project_members", back_populates="members"
    )
