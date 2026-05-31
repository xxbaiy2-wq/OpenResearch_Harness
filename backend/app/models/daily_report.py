# backend/app/models/daily_report.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from app.core.database import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("research_tasks.id"), nullable=False)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    # status: "draft" 草稿, "published" 已发布
    status = Column(String(50), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    published_at = Column(DateTime, nullable=True)
