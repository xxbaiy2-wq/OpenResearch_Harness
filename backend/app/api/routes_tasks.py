# d:\OpenResearch_Harness\backend\app\api\routes_tasks.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.research_task import ResearchTask
from app.schemas.task import TaskCreate, TaskOut
from app.harness.runner import research_runner
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    """创建一个研究任务。"""
    task = ResearchTask(
        topic=body.topic,
        description=body.description,
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    """列出所有任务。"""
    tasks = db.query(ResearchTask).order_by(ResearchTask.id.desc()).all()
    return tasks


@router.post("/{task_id}/run")
def run_task(task_id: int, db: Session = Depends(get_db)):
    """触发一次研究任务执行。"""
    task = db.query(ResearchTask).get(task_id)
    if not task:
        return {"error": "Task not found"}

    task.status = "running"
    db.commit()

    # 同步执行（第二版改成异步）
    result = research_runner.run(db, task_id, task.topic)

    task.status = result["status"]
    db.commit()

    return result
