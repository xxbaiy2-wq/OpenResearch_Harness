# backend/app/models/agent_step.py
'''
AgentStep（一次执行中的每个步骤）
角色： 一个 run 里有 7 个步骤
（planner → search → fetch → rank → summarize → verify → publish）
每个步骤一条记录。
'''
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, func
from app.core.database import Base


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="running")
    input_json = Column(JSON, nullable=True)
    output_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
