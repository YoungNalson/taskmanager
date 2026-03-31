from pydantic import BaseModel
from typing import Optional
from app.models.task import PriorityEnum


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityEnum


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: PriorityEnum
    completed: bool

    class Config:
        from_attributes = True