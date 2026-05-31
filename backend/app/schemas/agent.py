from pydantic import BaseModel
from datetime import datetime
from typing import Any
# run相关

class RunOut(BaseModel):
    id: int
    task_id: int
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    total_latency_ms: int | None = None
    error_message: str | None = None
    run_type: str

    model_config = {"from_attributes": True}


class StepOut(BaseModel):
    id: int
    step_index: int
    step_name: str
    status: str
    # JSON 类型在 Pydantic 里用 dict 表示
    input_json: dict | None = None
    output_json: dict | None = None
    error_message: str | None = None
    latency_ms: int | None = None
    started_at: datetime
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}


class ToolCallOut(BaseModel):
    id: int
    tool_name: str
    status: str
    input_json: dict | None = None
    output_json: dict | None = None
    error_message: str | None = None
    latency_ms: int | None = None
    retry_count: int

    model_config = {"from_attributes": True}


class VerificationOut(BaseModel):
    id: int
    passed: bool
    score: int
    problems_json: list | None = None
    action: str | None = None

    model_config = {"from_attributes": True}

# 这是组合 schema，GET /api/agent-runs/{id} 的完整响应
# 包含 run、steps、tool_calls、verification 四部分
class RunDetail(BaseModel):
    run: RunOut
    steps: list[StepOut]
    tool_calls: list[ToolCallOut]
    verification: VerificationOut | None = None
