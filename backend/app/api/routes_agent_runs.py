# d:\OpenResearch_Harness\backend\app\api\routes_agent_runs.py
# 调一次 GET 就能看到 Agent 的完整执行轨迹。
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.agent_run import AgentRun
from app.models.agent_step import AgentStep
from app.models.tool_call import ToolCall
from app.models.verification_result import VerificationResult
from app.schemas.agent import RunDetail, RunOut, StepOut, ToolCallOut, VerificationOut

router = APIRouter(prefix="/agent-runs", tags=["agent-runs"])


@router.get("/{run_id}", response_model=RunDetail)
def get_run_detail(run_id: int, db: Session = Depends(get_db)):
    """获取一次 run 的完整详情：run + steps + tool_calls + verification。"""
    run = db.query(AgentRun).get(run_id)
    if not run:
        return {"error": "Run not found"}

    steps = (
        db.query(AgentStep)
        .filter(AgentStep.run_id == run_id)
        .order_by(AgentStep.step_index)
        .all()
    )

    tool_calls = (
        db.query(ToolCall)
        .filter(ToolCall.run_id == run_id)
        .order_by(ToolCall.created_at)
        .all()
    )

    verification = (
        db.query(VerificationResult)
        .filter(VerificationResult.run_id == run_id)
        .first()
    )

    return RunDetail(
        run=run,
        steps=steps,
        tool_calls=tool_calls,
        verification=verification,
    )
