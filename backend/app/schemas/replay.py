from pydantic import BaseModel
# replay请求

class ReplayRequest(BaseModel):
    from_step: str   # 例如 "summarize"，从这一步开始重跑
