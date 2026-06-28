from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserResponse


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    project_id: int
    assignee_id: Optional[int] = None
    start_date: str = ""
    end_date: str = ""
    estimated_hours: int = 0


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    estimated_hours: Optional[int] = None
    sort_order: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    project_id: int
    creator_id: int
    assignee_id: Optional[int]
    start_date: str
    end_date: str
    estimated_hours: int
    sort_order: int
    created_at: datetime
    updated_at: datetime
    creator: UserResponse
    assignee: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class TaskBatchUpdate(BaseModel):
    task_ids: list[int]
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
