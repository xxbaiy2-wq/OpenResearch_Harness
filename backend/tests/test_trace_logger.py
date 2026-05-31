'''
这个测试需要数据库。 用 SQLite 内存数据库测试，不依赖 MySQL，测试更快、更独立。

测试哪些场景：

场景	预期
start_run 创建记录，返回 run_id	run.status = "running"
finish_run 更新状态为 success	run.status = "success"
fail_run 更新状态为 failed	run.status = "failed", 有 error_message
start_step 记录步骤	step.step_name 正确
log_tool_call 记录工具调用	tc.tool_name 正确
'''
# d:\OpenResearch_Harness\backend\tests\test_trace_logger.py

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.harness.trace_logger import TraceLogger
from app.models.agent_run import AgentRun
from app.models.agent_step import AgentStep
from app.models.tool_call import ToolCall
from app.models.research_task import ResearchTask


@pytest.fixture
def db():
    """用 SQLite 内存数据库做测试，不依赖 MySQL。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 先创建一个 research_task（外键依赖）
    task = ResearchTask(
        topic="test",
        status="pending",
        created_at=datetime.now(),
    )
    session.add(task)
    session.commit()

    yield session
    session.close()


@pytest.fixture
def logger():
    return TraceLogger()


def test_start_and_finish_run(logger, db):
    """start_run 创建记录，finish_run 标记成功。"""
    run_id = logger.start_run(db, task_id=1, input_data={"topic": "test"})
    assert run_id is not None

    run = db.query(AgentRun).get(run_id)
    assert run.status == "running"
    assert run.input_json == {"topic": "test"}

    logger.finish_run(db, run_id, output_data={"result": "ok"})
    run = db.query(AgentRun).get(run_id)
    assert run.status == "success"
    assert run.finished_at is not None
    assert run.total_latency_ms is not None


def test_fail_run(logger, db):
    """fail_run 标记失败并记录错误信息。"""
    run_id = logger.start_run(db, task_id=1)
    logger.fail_run(db, run_id, "Something went wrong")

    run = db.query(AgentRun).get(run_id)
    assert run.status == "failed"
    assert run.error_message == "Something went wrong"


def test_start_and_finish_step(logger, db):
    """start_step 记录步骤，finish_step 标记完成。"""
    run_id = logger.start_run(db, task_id=1)
    step_id = logger.start_step(db, run_id, step_index=0, step_name="planner")

    step = db.query(AgentStep).get(step_id)
    assert step.step_name == "planner"
    assert step.step_index == 0
    assert step.status == "running"

    logger.finish_step(db, step_id, output_data={"queries": ["a", "b"]})
    step = db.query(AgentStep).get(step_id)
    assert step.status == "success"
    assert step.output_json == {"queries": ["a", "b"]}


def test_log_tool_call(logger, db):
    """log_tool_call 记录工具调用。"""
    run_id = logger.start_run(db, task_id=1)
    tc_id = logger.log_tool_call(
        db=db, run_id=run_id, step_id=None,
        tool_name="github_search",
        input_data={"query": "test"},
        output_data={"items": [{"title": "a"}]},
        status="success",
        latency_ms=500,
    )

    tc = db.query(ToolCall).get(tc_id)
    assert tc.tool_name == "github_search"
    assert tc.input_json == {"query": "test"}
    assert tc.status == "success"
    assert tc.latency_ms == 500


def test_step_records_latency(logger, db):
    """finish_step 应该计算 latency_ms。"""
    run_id = logger.start_run(db, task_id=1)
    step_id = logger.start_step(db, run_id, step_index=0, step_name="planner")

    import time
    time.sleep(0.1)  # 等待 100ms

    logger.finish_step(db, step_id)
    step = db.query(AgentStep).get(step_id)
    assert step.latency_ms >= 100  # 至少 100ms
