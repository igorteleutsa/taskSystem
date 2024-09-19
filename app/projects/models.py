from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    Enum as SqlEnum,
    Integer,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel
from enum import Enum


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Project(BaseModel):
    __tablename__ = "projects"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SqlEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False
    )

    # Foreign key to relate projects to their owners or creators (assuming 1 owner per project)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to User (owner/creator of the project)
    owner = relationship("User", back_populates="owned_projects")
    project_memberships = relationship(
        "ProjectMember", back_populates="project", overlaps="members,projects"
    )
    members = relationship(
        "User", secondary="project_members", back_populates="projects"
    )
    tickets = relationship(
        "Ticket", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectMember(BaseModel):
    __tablename__ = "project_members"
    id = None

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)

    # Relationships to User and Project models
    user = relationship(
        "User", back_populates="project_memberships", overlaps="projects,members"
    )

    project = relationship(
        "Project", back_populates="project_memberships", overlaps="members,projects"
    )
    assigned_tickets = relationship("TicketExecutor", back_populates="project_member")
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_user_project"),
    )
