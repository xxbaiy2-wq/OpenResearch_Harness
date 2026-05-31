'''
第二组：结果（verification + report + items）
VerificationResult（验证结果）
'''
# backend/app/models/verification_result.py

from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime, func
from app.core.database import Base


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False, unique=True)
    report_id = Column(Integer, nullable=True)
    passed = Column(Boolean, nullable=False)
    score = Column(Integer, nullable=False)
    problems_json = Column(JSON, nullable=True)
    # 建议操作（"revise" 重写, "human_review" 人工审）
    action = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
