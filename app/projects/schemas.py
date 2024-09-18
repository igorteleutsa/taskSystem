from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ProjectBase(BaseModel):
    title: str = Field(..., max_length=255, description="Title of the project")
    description: Optional[str] = Field(
        None, description="Optional description of the project"
    )
    status: Optional[ProjectStatus] = Field(
        ProjectStatus.ACTIVE, description="Status of the project"
    )


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""

    pass


class ProjectUpdate(ProjectBase):
    """Schema for updating an existing project."""

    title: Optional[str] = Field(None, description="Title of the project")
    description: Optional[str] = Field(
        None, description="Optional description of the project"
    )
    status: Optional[ProjectStatus] = Field(None, description="Status of the project")


class ProjectOut(ProjectBase):
    """Response schema for project details."""

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
