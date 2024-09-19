from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    DateTime,
    func,
    Enum as SqlEnum,
    CheckConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel
from enum import Enum


# Enum for ticket status
class TicketStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# Class-based model for the many-to-many relationship between tickets and executors
class TicketExecutor(BaseModel):
    __tablename__ = "ticket_executors"

    ticket_id = Column(
        Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "project_id"],
            ["project_members.user_id", "project_members.project_id"],
            ondelete="CASCADE",
        ),
    )

    # Relationships
    ticket = relationship("Ticket", back_populates="executors")
    project_member = relationship("ProjectMember", back_populates="assigned_tickets")


class Ticket(BaseModel):
    __tablename__ = "tickets"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Responsible user (ForeignKey to users table)
    responsible_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    responsible_user = relationship(
        "User", back_populates="responsible_tickets", foreign_keys=[responsible_user_id]
    )

    # Many-to-many relationship with executors (Users)
    executors = relationship(
        "TicketExecutor", back_populates="ticket", cascade="all, delete-orphan"
    )

    # Status and priority
    status = Column(SqlEnum(TicketStatus), default=TicketStatus.TODO, nullable=False)
    priority = Column(Integer, nullable=False, default=3)

    # Each ticket belongs to a project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="tickets")

    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <= 5", name="priority_check"),
    )
