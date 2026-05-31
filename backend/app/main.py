'''
FastAPI 启动入口
整个后端的"大门"。所有 HTTP 请求从这里进，
FastAPI 在这里启动，工具在这里注册，数据库表在这里创建。
'''
# d:\OpenResearch_Harness\backend\app\main.py

from fastapi import FastAPI
from app.core.database import Base, engine
from app.core.init_tools import register_default_tools
from app.api.routes_tasks import router as tasks_router
from app.api.routes_agent_runs import router as agent_runs_router
from app.api.routes_reports import router as reports_router
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import requests

# 1. 创建 FastAPI 应用
app = FastAPI(title="OpenResearch Harness", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

# 3. 注册工具
register_default_tools()

# 4. 注册路由
app.include_router(tasks_router, prefix="/api")
app.include_router(agent_runs_router, prefix="/api")
app.include_router(reports_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "OpenResearch Harness is running"}


def daily_auto_run():
    """每天早上 9 点自动触发所有任务。"""
    try:
        requests.post("http://localhost:8000/api/tasks/daily-run", timeout=10)
        print("[Scheduler] 每日任务已触发")
    except Exception as e:
        print(f"[Scheduler] 触发失败: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(daily_auto_run, "cron", hour=9, minute=0)  # 每天早上 9 点
scheduler.start()