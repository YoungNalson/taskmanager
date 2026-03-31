from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.db.base import Base
import enum


class PriorityEnum(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    priority = Column(Enum(PriorityEnum), nullable=False)
    completed = Column(Boolean, default=False)