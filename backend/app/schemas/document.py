from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserResponse


class DocumentCreate(BaseModel):
    title: str
    doc_type: str = "markdown"
    content: str = ""
    project_id: int


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    doc_type: str
    content: str
    file_path: str
    file_name: str
    file_size: int
    project_id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    creator: UserResponse

    model_config = {"from_attributes": True}
