# 收集到的资料
# backend/app/models/research_item.py

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, func
from app.core.database import Base


class ResearchItem(Base):
    __tablename__ = "research_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("research_tasks.id"), nullable=False)
    source_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    summary = Column(Text, nullable=True)
    raw_content = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
