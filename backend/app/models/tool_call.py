# backend/app/models/tool_call.py
'''
ToolCall（每次工具调用）
角色： 一个步骤里可能调用多次工具
（比如 search 步骤调用 arXiv + GitHub）
每次调用一条记录。
'''
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, func
from app.core.database import Base


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    # 外键指向 agent_step，知道这次调用属于哪个步骤
    step_id = Column(Integer, ForeignKey("agent_steps.id"), nullable=True)
    tool_name = Column(String(100), nullable=False)
    input_json = Column(JSON, nullable=True)
    output_json = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
