from pydantic import BaseModel
from datetime import datetime


class TaskCreate(BaseModel):
    topic: str
    description: str | None = None

# 返回给前端的响应体
class TaskOut(BaseModel):
    id: int
    topic: str
    status: str
    created_at: datetime

    # 关键：允许直接从 ORM 对象转成 schema
    # （后面路由里会用 TaskOut.model_validate(task)）
    model_config = {"from_attributes": True}
