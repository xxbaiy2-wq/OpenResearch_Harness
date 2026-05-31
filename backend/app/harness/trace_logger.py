from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session
from app.models.agent_run import AgentRun
from app.models.agent_step import AgentStep
from app.models.tool_call import ToolCall


class TraceLogger:
    """把 Agent 的每一步执行记录写入 MySQL。"""

    # ---- Run 级别 ----

    def start_run(self, db: Session, task_id: int, input_data: dict | None = None,
                  parent_run_id: int | None = None, run_type: str = "normal") -> int:
        """开始一次 run，返回 run_id。"""
        run = AgentRun(
            task_id=task_id,
            status="running",
            input_json=input_data,
            parent_run_id=parent_run_id,
            run_type=run_type,
            started_at=datetime.now(),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id

    def finish_run(self, db: Session, run_id: int, output_data: dict | None = None) -> None:
        """标记 run 成功完成。"""
        run = db.query(AgentRun).get(run_id)
        run.status = "success"
        run.output_json = output_data
        run.finished_at = datetime.now()
        run.total_latency_ms = int(
            (run.finished_at - run.started_at).total_seconds() * 1000
        )
        db.commit()

    def fail_run(self, db: Session, run_id: int, error_message: str) -> None:
        """标记 run 失败。"""
        run = db.query(AgentRun).get(run_id)
        run.status = "failed"
        run.error_message = error_message
        run.finished_at = datetime.now()
        run.total_latency_ms = int(
            (run.finished_at - run.started_at).total_seconds() * 1000
        )
        db.commit()

    # ---- Step 级别 ----

    def start_step(self, db: Session, run_id: int, step_index: int,
                   step_name: str, input_data: dict | None = None) -> int:
        """开始一个步骤，返回 step_id。"""
        step = AgentStep(
            run_id=run_id,
            step_index=step_index,
            step_name=step_name,
            status="running",
            input_json=input_data,
            started_at=datetime.now(),
        )
        db.add(step)
        db.commit()
        db.refresh(step)
        return step.id

    def finish_step(self, db: Session, step_id: int, output_data: dict | None = None) -> None:
        """标记步骤成功。"""
        step = db.query(AgentStep).get(step_id)
        step.status = "success"
        step.output_json = output_data
        step.finished_at = datetime.now()
        step.latency_ms = int(
            (step.finished_at - step.started_at).total_seconds() * 1000
        )
        db.commit()

    def fail_step(self, db: Session, step_id: int, error_message: str) -> None:
        """标记步骤失败。"""
        step = db.query(AgentStep).get(step_id)
        step.status = "failed"
        step.error_message = error_message
        step.finished_at = datetime.now()
        step.latency_ms = int(
            (step.finished_at - step.started_at).total_seconds() * 1000
        )
        db.commit()

    # ---- Tool Call 级别 ----

    def log_tool_call(
        self,
        db: Session,
        run_id: int,
        step_id: int | None,
        tool_name: str,
        input_data: dict | None,
        output_data: dict | None,
        status: str,
        error_message: str | None = None,
        latency_ms: int = 0,
        retry_count: int = 0,
    ) -> int:
        """记录一次工具调用，返回 tool_call_id。"""
        tc = ToolCall(
            run_id=run_id,
            step_id=step_id,
            tool_name=tool_name,
            input_json=input_data,
            output_json=output_data,
            status=status,
            error_message=error_message,
            latency_ms=latency_ms,
            retry_count=retry_count,
            created_at=datetime.now(),
        )
        db.add(tc)
        db.commit()
        db.refresh(tc)
        return tc.id


# 全局实例
trace_logger = TraceLogger()
