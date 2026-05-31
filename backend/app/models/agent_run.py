# backend/app/models/agent_run.py
'''
执行链（agent_runs → agent_steps → tool_calls）
这三张表是项目最核心的表，记录 Agent 每次运行的完整轨迹。

AgentRun（一次完整的执行）
用户点击"Run"按钮后，系统创建一条 agent_run，记录从开始到结束的全过程。
'''
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, func
from app.core.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("research_tasks.id"), nullable=False)
    status = Column(String(50), nullable=False, default="running")
    input_json = Column(JSON, nullable=True)
    output_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
    # 总耗时，面试展示性能分析能力
    total_latency_ms = Column(Integer, nullable=True)
    total_tokens = Column(Integer, default=0)
    # Replay 用的：如果是从某个步骤重跑，指向原始 run
    parent_run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=True)
    run_type = Column(String(50), nullable=False, default="normal")
