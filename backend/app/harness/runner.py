'''
最重要的文件：runner.py
文件路径： d:\OpenResearch_Harness\backend\app\harness\runner.py
解决什么问题：
Runner 是整个系统的指挥官。它按顺序执行 7 个步骤，每一步都调用 trace_logger 记录，中间结果存到 state_manager，失败时根据 retry_policy 决定是否重试。

执行流程图：
start_run (trace_logger)
    ↓
[step 0] planner   → 从 topic 生成搜索 query 列表
    ↓
[step 1] search    → 用 arxiv/github 工具搜索，收集 items
    ↓
[step 2] fetch     → 获取详细内容（第一版直接透传 items）
    ↓
[step 3] rank      → 按 stars/时间 排序 items
    ↓
[step 4] summarize → 从 ranked_items 生成报告草稿
    ↓
[step 5] verify    → 规则检查报告质量
    ↓           ↓
  通过？      不通过？
    ↓           ↓
[step 6] publish   回到 summarize 重试（最多1次）
    ↓
finish_run (trace_logger)
'''
# d:\OpenResearch_Harness\backend\app\harness\runner.py

from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session

from app.harness.trace_logger import trace_logger
from app.harness.state_manager import StateManager
from app.harness.retry_policy import RetryDecision
from app.harness.verifier import verifier
from app.harness.tool_registry import tool_registry
from app.harness.permission_guard import PermissionGuard
from app.models.daily_report import DailyReport
from app.models.research_item import ResearchItem
from app.tools.llm_summarizer import llm_summarizer
from app.tools.llm_planner import llm_planner
from app.tools.llm_summarizer import llm_summarizer


# 步骤定义：(step_index, step_name)
STEPS = [
    (0, "planner"),
    (1, "search"),
    (2, "fetch"),
    (3, "rank"),
    (4, "summarize"),
    (5, "verify"),
    (6, "publish"),
]


class ResearchRunner:
    """Research Agent 的执行引擎。串起所有步骤，记录 trace，处理失败和重试。"""

    def __init__(self):
        self.state = StateManager()
        self.guard = PermissionGuard()

    def run(self, db: Session, task_id: int, topic: str) -> dict:
        """执行一次完整的 research flow，返回结果字典。"""

        # ========== 0. 初始化 ==========
        self.state.init_state(task_id, topic)
        self.guard.reset()
        run_id = trace_logger.start_run(
            db, task_id,
            input_data={"topic": topic},
        )

        try:
            # ========== 1. Planner ==========
            plan = self._run_planner(db, run_id, topic)

            # ========== 2. Search ==========
            items = self._run_search(db, run_id, plan)

            # ========== 3. Fetch ==========
            items = self._run_fetch(db, run_id, items)

            # ========== 4. Rank ==========
            ranked_items = self._run_rank(db, run_id, items)

            # ========== 5. Summarize ==========
            draft_report = self._run_summarize(db, run_id, ranked_items)

            # ========== 6. Verify ==========
            verification = self._run_verify(db, run_id, draft_report, ranked_items)


            # 判断验证是否通过
            if not verification.get("passed"):
                # 验证失败，尝试重跑 summarize
                from app.harness.retry_policy import retry_policy
                decision = retry_policy.should_retry("VerifierFailed", run_id)

                if decision.should_retry:
                    # 重跑 summarize
                    draft_report = self._run_summarize(db, run_id, ranked_items)
                    verification = self._run_verify(db, run_id, draft_report, items)

                if not verification.get("passed"):
                    trace_logger.fail_run(db, run_id, f"验证失败: {verification.get('problems')}")
                    return {"run_id": run_id, "status": "verified_failed"}

            # ========== 7. Publish ==========
            self._run_publish(db, run_id, task_id, draft_report, items)

            # ========== 8. 完成 ==========
            trace_logger.finish_run(db, run_id, self.state.get_all())
            return {"run_id": run_id, "status": "success"}

        except Exception as e:
            trace_logger.fail_run(db, run_id, str(e))
            return {"run_id": run_id, "status": "failed", "error": str(e)}

    # ---- 各步骤的具体实现 ----

    def _run_planner(self, db: Session, run_id: int, topic: str) -> dict:
        step_id = trace_logger.start_step(
            db, run_id, step_index=0, step_name="planner",
            input_data={"topic": topic},
        )
        try:
            plan = llm_planner.run({"topic": topic})
            self.state.set("plan", plan)
            trace_logger.finish_step(db, step_id, plan)
            return plan
        except Exception as e:
            trace_logger.fail_step(db, step_id, str(e))
            raise


    def _run_search(self, db: Session, run_id: int, plan: dict) -> list[dict]:
        step_id = trace_logger.start_step(
            db, run_id, step_index=1, step_name="search",
            input_data=plan,
        )

        all_items = []

        # 搜索 GitHub
        try:
            github_tool = tool_registry.get_tool("github_search")
            for query in plan.get("queries", []):
                self.guard.check("github_search")

                import time
                start = time.time()
                try:
                    result = github_tool.run({"query": query, "max_results": 5})
                    latency = int((time.time() - start) * 1000)
                    all_items.extend(result.get("items", []))
                    self.guard.record_call("github_search")

                    # ★ 记录成功的 tool_call
                    trace_logger.log_tool_call(
                        db=db, run_id=run_id, step_id=step_id,
                        tool_name="github_search",
                        input_data={"query": query, "max_results": 5},
                        output_data={"item_count": len(result.get("items", []))},
                        status="success",
                        latency_ms=latency,
                    )
                except Exception as e:
                    latency = int((time.time() - start) * 1000)
                    trace_logger.log_tool_call(
                        db=db, run_id=run_id, step_id=step_id,
                        tool_name="github_search",
                        input_data={"query": query, "max_results": 5},
                        output_data=None,
                        status="failed",
                        error_message=str(e),
                        latency_ms=latency,
                    )
        except Exception as e:
            pass

        # 搜索 arXiv
        try:
            arxiv_tool = tool_registry.get_tool("arxiv_search")
            for query in plan.get("queries", []):
                self.guard.check("arxiv_search")

                start = time.time()
                try:
                    result = arxiv_tool.run({"query": query, "max_results": 5})
                    latency = int((time.time() - start) * 1000)
                    all_items.extend(result.get("items", []))
                    self.guard.record_call("arxiv_search")

                    trace_logger.log_tool_call(
                        db=db, run_id=run_id, step_id=step_id,
                        tool_name="arxiv_search",
                        input_data={"query": query, "max_results": 5},
                        output_data={"item_count": len(result.get("items", []))},
                        status="success",
                        latency_ms=latency,
                    )
                except Exception as e:
                    latency = int((time.time() - start) * 1000)
                    trace_logger.log_tool_call(
                        db=db, run_id=run_id, step_id=step_id,
                        tool_name="arxiv_search",
                        input_data={"query": query, "max_results": 5},
                        output_data=None,
                        status="failed",
                        error_message=str(e),
                        latency_ms=latency,
                    )
        except Exception as e:
            pass

        self.state.set("items", all_items)
        trace_logger.finish_step(db, step_id, {"item_count": len(all_items)})
        return all_items



    def _run_fetch(self, db: Session, run_id: int, items: list[dict]) -> list[dict]:
        """Fetch：获取详细内容。第一版直接透传。"""
        step_id = trace_logger.start_step(
            db, run_id, step_index=2, step_name="fetch",
            input_data={"item_count": len(items)},
        )
        # 后续版本：根据 URL 抓取完整内容
        trace_logger.finish_step(db, step_id, {"fetched": len(items)})
        return items

    def _run_rank(self, db: Session, run_id: int, items: list[dict]) -> list[dict]:
        """Rank：对 items 排序。"""
        step_id = trace_logger.start_step(
            db, run_id, step_index=3, step_name="rank",
            input_data={"item_count": len(items)},
        )

        try:
            # 按 stars 数降序排（GitHub 有 stars，arXiv 没有所以为 0）
            ranked = sorted(items, key=lambda x: x.get("stars", 0), reverse=True)
            self.state.set("ranked_items", ranked)
            trace_logger.finish_step(db, step_id, {"ranked_count": len(ranked)})
            return ranked
        except Exception as e:
            trace_logger.fail_step(db, step_id, str(e))
            raise

    def _run_summarize(self, db: Session, run_id: int, items: list[dict]) -> dict:
        step_id = trace_logger.start_step(
            db, run_id, step_index=4, step_name="summarize",
            input_data={"item_count": len(items)},
        )
        try:
            topic = self.state.get("topic")
            result = llm_summarizer.run({"topic": topic, "items": items})
            self.state.set("draft_report", result)
            trace_logger.finish_step(db, step_id, {"title": result.get("title")})
            return result
        except Exception as e:
            trace_logger.fail_step(db, step_id, str(e))
            raise


    def _run_verify(self, db: Session, run_id: int,
                report_data: dict, items: list[dict]) -> dict:
        step_id = trace_logger.start_step(
            db, run_id, step_index=5, step_name="verify",
            input_data=report_data,
        )
        try:
            # 如果有 sections（正常报告），从 sections 拼内容
            if report_data.get("sections"):
                content = report_data.get("title", "")
                for section in report_data["sections"]:
                    content += " " + section.get("heading", "")
                    for item in section.get("items", []):
                        content += " " + item.get("summary", "")
                        content += " " + item.get("why_it_matters", "")
            # 如果是降级报告，用 raw_content
            elif report_data.get("raw_content"):
                content = report_data["raw_content"]
            else:
                content = report_data.get("title", "")

            result = verifier.verify(content, items)
            verification_data = result.to_dict()
            self.state.set("verification", verification_data)
            trace_logger.finish_step(db, step_id, verification_data)
            return verification_data
        except Exception as e:
            trace_logger.fail_step(db, step_id, str(e))
            raise



    def _run_publish(self, db: Session, run_id: int, task_id: int,
                 report_data: dict, items: list[dict]) -> int:
        step_id = trace_logger.start_step(
            db, run_id, step_index=6, step_name="publish",
            input_data={"report_title": report_data.get("title", "")},
        )
        try:
            topic = self.state.get("topic")

            for item in items:
                ri = ResearchItem(
                    task_id=task_id,
                    source_type=item.get("source_type", "unknown"),
                    title=item.get("title") or item.get("name", ""),
                    url=item.get("url"),
                    summary=(item.get("abstract") or item.get("description") or item.get("summary", "")),
                )
                db.add(ri)

            # 把 report_data 转成 JSON 字符串存入 content
            import json
            content = json.dumps(report_data, ensure_ascii=False, indent=2)

            report = DailyReport(
                task_id=task_id,
                run_id=run_id,
                title=report_data.get("title", f"{topic} 技术雷达"),
                content=content,
                status="draft",
                created_at=datetime.now(),
            )
            db.add(report)
            db.commit()
            db.refresh(report)

            self.state.set("final_report", {"report_id": report.id})
            trace_logger.finish_step(db, step_id, {"report_id": report.id})
            return report.id
        except Exception as e:
            trace_logger.fail_step(db, step_id, str(e))
            raise


# 全局实例
research_runner = ResearchRunner()
