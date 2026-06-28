from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), default="")
    avatar = Column(String(255), default="")
    role = Column(String(20), default="member")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    documents = relationship("Document", back_populates="creator")
