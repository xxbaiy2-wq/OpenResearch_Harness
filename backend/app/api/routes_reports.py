from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.daily_report import DailyReport
from app.models.research_item import ResearchItem
from app.schemas.report import ReportOut
from app.models.verification_result import VerificationResult

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportOut])
def list_reports(db: Session = Depends(get_db)):
    """列出所有报告。"""
    return db.query(DailyReport).order_by(DailyReport.id.desc()).all()

@router.get("/search")
def search_items(q: str = "", db: Session = Depends(get_db)):
    """按关键词搜索历史收集的技术内容。"""
    if not q:
        return {"query": q, "count": 0, "items": []}

    items = (
        db.query(ResearchItem)
        .filter(
            ResearchItem.title.ilike(f"%{q}%")
            | ResearchItem.summary.ilike(f"%{q}%")
        )
        .order_by(ResearchItem.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "query": q,
        "count": len(items),
        "items": [
            {"id": i.id, "title": i.title, "url": i.url, "source_type": i.source_type, "summary": i.summary}
            for i in items
        ],
    }


@router.get("/latest/main")
def get_latest_report(db: Session = Depends(get_db)):
    """获取最新一篇报告，用于首页展示。"""
    report = db.query(DailyReport).order_by(DailyReport.id.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="暂无报告")

    from app.models.research_item import ResearchItem
    items = db.query(ResearchItem).filter(ResearchItem.task_id == report.task_id).all()

    return {
        "report": {
            "id": report.id,
            "title": report.title,
            "content": report.content,
            "run_id": report.run_id,
            "created_at": str(report.created_at),
        },
        "items": [
            {"title": i.title, "url": i.url, "source_type": i.source_type, "summary": i.summary}
            for i in items
        ],
    }

@router.get("/by-date/{date}")
def get_report_by_date(date: str, db: Session = Depends(get_db)):
    """按日期获取报告，date 格式：2026-05-31。"""
    # 查找当天 00:00 到 23:59 之间创建的报告
    start = datetime.strptime(date, "%Y-%m-%d")
    from datetime import timedelta
    end = start + timedelta(days=1)

    report = (
        db.query(DailyReport)
        .filter(DailyReport.created_at >= start, DailyReport.created_at < end)
        .order_by(DailyReport.id.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail=f"{date} 没有报告")

    from app.models.research_item import ResearchItem
    items = db.query(ResearchItem).filter(ResearchItem.task_id == report.task_id).all()

    return {
        "report": {
            "id": report.id,
            "title": report.title,
            "content": report.content,
            "run_id": report.run_id,
            "created_at": str(report.created_at),
        },
        "items": [
            {"title": i.title, "url": i.url, "source_type": i.source_type, "summary": i.summary}
            for i in items
        ],
    }

@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """获取单篇报告详情。"""
    report = db.query(DailyReport).get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

from app.models.research_item import ResearchItem
from sqlalchemy import func

@router.get("/weekly/{year}/{week}")
def get_weekly_report(year: int, week: int, db: Session = Depends(get_db)):
    """获取某一周的汇总报告。"""
    from datetime import date
    # 计算周的起止日期
    start = date.fromisocalendar(year, week, 1)
    end = start + timedelta(days=7)

    # 查找这一周的所有 report
    reports = (
        db.query(DailyReport)
        .filter(DailyReport.created_at >= start, DailyReport.created_at < end)
        .order_by(DailyReport.created_at.asc())
        .all()
    )
    if not reports:
        raise HTTPException(status_code=404, detail=f"{year}年第{week}周没有报告")

    # 汇总这一周的所有 research_items
    report_ids = [r.id for r in reports]
    items = (
        db.query(ResearchItem)
        .filter(ResearchItem.task_id.in_(
            db.query(DailyReport.task_id).filter(DailyReport.id.in_(report_ids))
        ))
        .all()
    )

    # 按来源统计
    source_count = {}
    for item in items:
        s = item.source_type or "unknown"
        source_count[s] = source_count.get(s, 0) + 1

    return {
        "year": year,
        "week": week,
        "report_count": len(reports),
        "item_count": len(items),
        "source_stats": source_count,
        "daily_reports": [
            {"id": r.id, "title": r.title, "created_at": str(r.created_at)[:10]}
            for r in reports
        ],
    }

from fastapi import BackgroundTasks

def run_task_background(task_id: int):
    """后台执行任务（不阻塞 HTTP 请求）。"""
    from app.core.database import SessionLocal
    from app.models.research_task import ResearchTask
    from app.harness.runner import research_runner

    db = SessionLocal()
    try:
        task = db.query(ResearchTask).get(task_id)
        if task:
            task.status = "running"
            db.commit()
            result = research_runner.run(db, task_id, task.topic)
            task.status = result["status"]
            db.commit()
    finally:
        db.close()


@router.post("/daily-run")
def daily_run(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """触发所有 pending 任务执行一次，用于每日定时。"""
    from app.models.research_task import ResearchTask
    tasks = db.query(ResearchTask).filter(ResearchTask.status.in_(["pending", "success"])).all()
    for task in tasks:
        background_tasks.add_task(run_task_background, task.id)
    return {"message": f"已触发 {len(tasks)} 个任务", "task_ids": [t.id for t in tasks]}


