from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserResponse


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    start_date: str = ""
    end_date: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    start_date: str
    end_date: str
    owner_id: int
    owner: UserResponse
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    done_count: int = 0
    member_count: int = 0
    doc_count: int = 0

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    start_date: str
    end_date: str
    owner_id: int
    owner: UserResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
