from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# Enum for Ticket Status
class TicketStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TicketStatus = TicketStatus.TODO
    priority: Optional[int] = Field(
        None, ge=1, le=5, description="Priority from 1 to 5"
    )


# Create Ticket Schema (for POST requests)
class TicketCreate(TicketBase):
    project_id: int


# Update Ticket Schema (for PUT requests)
class TicketUpdate(TicketBase):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None


# Executor Schema (used for adding/removing executors)
class ExecutorAssign(BaseModel):
    user_id: int


class TicketStatusUpdate(BaseModel):
    new_status: str


class TicketExecutorOut(BaseModel):
    user_id: int
    project_id: int
    model_config = ConfigDict(from_attributes=True)


# Ticket Out Schema (for returning ticket information)
class TicketOut(TicketBase):
    id: int
    project_id: int
    responsible_user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
