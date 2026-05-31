from pydantic import BaseModel
from datetime import datetime
# 报告

class ReportOut(BaseModel):
    id: int
    task_id: int
    run_id: int
    title: str
    content: str
    status: str
    created_at: datetime
    published_at: datetime | None = None

    model_config = {"from_attributes": True}
