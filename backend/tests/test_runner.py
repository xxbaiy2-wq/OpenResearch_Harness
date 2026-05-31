# d:\OpenResearch_Harness\backend\tests\test_runner.py

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.harness.runner import ResearchRunner
from app.models.research_task import ResearchTask
from app.models.agent_run import AgentRun
from app.models.agent_step import AgentStep
from app.models.tool_call import ToolCall
from app.models.daily_report import DailyReport


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    task = ResearchTask(
        topic="LangGraph",
        status="pending",
        created_at=datetime.now(),
    )
    session.add(task)
    session.commit()

    yield session
    session.close()


def test_runner_creates_run_and_steps(db):
    """端到端测试：Runner 执行后数据库里有 run、steps、tool_calls、report。"""

    mock_plan = {
        "topic": "LangGraph",
        "queries": ["LangGraph tutorial"],
        "sources": ["github"],
        "reasoning": "test reasoning",
    }

    mock_report = {
        "title": "LangGraph 技术雷达",
        "date": "2026-05-31",
        "total_items": 3,
        "sections": [{
            "heading": "开源项目",
            "items": [
                {
                    "title": "LangGraph",
                    "url": "https://github.com/a",
                    "summary": "LangGraph 是一个用于构建有状态多智能体应用的开源框架，基于 LangChain 构建，支持状态图定义和工作流管理，能够处理复杂的多步骤 AI 工作流场景，适用于需要长期记忆和复杂推理的应用。",
                    "why_it_matters": "它简化了复杂 AI 工作流的开发流程，通过状态管理机制大幅提高了应用的灵活性和可靠性，特别适合需要多步骤推理、人机协作和动态交互的企业级应用场景，是当前 Agent 框架的重要选择。",
                },
                {
                    "title": "LangGraph-Docs",
                    "url": "https://docs.langgraph.dev",
                    "summary": "LangGraph 官方文档提供详细的 API 参考手册、从零开始的入门教程和经过验证的最佳实践指南，帮助开发者快速上手并掌握框架的核心概念和高级用法。",
                    "why_it_matters": "官方文档是开发者学习新框架最权威、最可靠的学习资源，能够有效减少从第三方教程获取信息时可能出现的理解偏差和版本不匹配问题。",
                },
                {
                    "title": "LangGraph-Example",
                    "url": "https://github.com/c",
                    "summary": "LangGraph 实战示例代码集合，涵盖了多 Agent 协作、条件分支路由、人机协作审核和状态持久化等多种常见业务场景的完整实现方案和代码模板。",
                    "why_it_matters": "实战示例代码是开发者最直接有效的学习方式，通过模仿和修改现有示例可以大幅缩短从学习到生产环境的落地周期，提升开发效率。",
                },
            ],
        }],
    }


    # 直接 mock 工具的 run 方法，不 mock HTTP
    with patch("app.tools.llm_planner.call_llm") as mock_planner, \
         patch("app.tools.llm_summarizer.call_llm") as mock_summarizer, \
         patch("app.harness.runner.ResearchRunner._run_search") as mock_search:

        mock_planner.return_value = json.dumps(mock_plan)
        mock_summarizer.return_value = json.dumps(mock_report)

        # mock search 直接返回固定 items
        mock_search.return_value = [
            {"title": "LangGraph", "url": "https://github.com/a",
             "description": "Build resilient AI apps", "source_type": "github", "stars": 10000},
            {"title": "LangGraph-Docs", "url": "https://docs.langgraph.dev",
             "description": "Official docs", "source_type": "github", "stars": 5000},
            {"title": "LangGraph-Example", "url": "https://github.com/c",
             "description": "Example", "source_type": "github", "stars": 1000},
        ]

        runner = ResearchRunner()
        result = runner.run(db, task_id=1, topic="LangGraph")

    # ========== 验证 ==========
    run_id = result["run_id"]
    run = db.query(AgentRun).get(run_id)

    # 1. run 成功
    assert run.status == "success", f"Got {run.status}: {run.error_message}"

    # 2. 有 steps
    steps = db.query(AgentStep).filter(AgentStep.run_id == run_id).all()
    step_names = [s.step_name for s in steps]
    assert "planner" in step_names
    assert "fetch" in step_names
    assert "publish" in step_names

    # 3. 有 report
    report = db.query(DailyReport).filter(DailyReport.run_id == run_id).first()
    assert report is not None
    assert "LangGraph" in report.title

    print(f"\n✅ Run {run_id} 成功，共 {len(steps)} 个步骤，报告：{report.title}")
