# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## User
- 名字：荣慧
- 每次回复之前都需要叫用户的名字

## Project Overview

OpenResearch Harness is a Research Agent Harness platform — an AI tech-trend radar that automatically collects papers, open-source projects, and technical articles around user-subscribed topics (Agent Harness, MCP, LangGraph, RAG, etc.), then generates daily tech radar reports.

**The real technical core is NOT "generating reports" but the lightweight Agent Harness:**
```
Research Agent completes research tasks.
Agent Harness makes it controllable, observable, verifiable, and replayable.
```

Key Harness components: Tool Registry, Permission Guard, Trace Logger, Retry Policy, State Manager, Verifier, Replay.

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| API Backend | FastAPI | Python AI ecosystem, Pydantic for structured APIs |
| ORM | SQLAlchemy 2.x | Relational tables for agent_runs/steps/tool_calls |
| Database | MySQL 8.0 | Strong-structured relational data |
| Cache/Rate Limit | Redis 7 | Tool call throttling, task state, distributed locks |
| Queue | RQ (Phase 2), then Celery | Redis-based simple queue, upgrade later |
| Frontend | React + TypeScript | Agent Timeline, Tool Calls table, Report detail |
| Deployment | Docker Compose + Nginx | Multi-container on Linux server |

## Development Phases (8-week plan, condensed to priority order)

### Phase 1 — Harness Skeleton (MUST complete first)
Fake tools, no LLM, no real APIs. Goal: POST a task → trigger run → see `agent_runs → agent_steps → tool_calls` chain in MySQL.

Files to build in order:
1. `backend/app/core/config.py` — Pydantic Settings reading from `.env`
2. `backend/app/core/database.py` — SQLAlchemy engine, SessionLocal, Base, get_db dependency
3. `backend/app/models/*.py` — ORM models: ResearchTask, AgentRun, AgentStep, ToolCall, DailyReport, VerificationResult, ResearchItem
4. `backend/app/schemas/*.py` — Pydantic schemas for API request/response (NOT the same as models)
5. `backend/app/tools/base.py` — Abstract BaseTool with `name`, `description`, `run(input_data)`
6. `backend/app/harness/tool_registry.py` — Register/get/list tools with ToolSpec (schema, permission, timeout, retries)
7. `backend/app/tools/fake_search_tool.py` — Returns hardcoded research items
8. `backend/app/harness/permission_guard.py` — Pre-call checks: tool exists, call limits per run
9. `backend/app/harness/trace_logger.py` — Write runs/steps/tool_calls to MySQL (MOST IMPORTANT file)
10. `backend/app/harness/retry_policy.py` — Decide if a failure should retry (Timeout→yes, PermissionDenied→no)
11. `backend/app/harness/verifier.py` — Rule-based: report non-empty, ≥300 chars, ≥3 items with URLs, no overclaim words
12. `backend/app/harness/state_manager.py` — Dict-based state: topic, plan, items, ranked_items, draft_report, verification
13. `backend/app/harness/runner.py` — Orchestrates: start_run → planner → search → fetch → rank → summarize → verify → publish → finish_run
14. `backend/app/services/research_service.py` — Business logic, calls runner
15. `backend/app/api/routes_tasks.py` — POST/GET tasks, POST task run
16. `backend/app/api/routes_agent_runs.py` — GET run detail (run + steps + tool_calls + verification)
17. `backend/app/api/routes_reports.py` — GET reports

### Phase 2 — Real Data Sources + Redis
- arXiv Tool, GitHub Tool, RSS Tool (feedparser)
- Redis rate limiting: `tool_limit:{run_id}:{tool_name}`, `user_quota:{user_id}:{date}`
- Research items入库 + dedup

### Phase 3 — LLM Nodes
- Planner (structured JSON output), Summarizer, LLM Verifier
- Pydantic output validation + retry on bad output

### Phase 4 — Skills
- paper_analysis, github_project_analysis, trend_report_writer, verification
- Skill Loader reads SKILL.md + examples.md + output_schema.json

### Phase 5 — Frontend (React + TypeScript)
- ResearchTasks page, AgentRunDetail page, ReportDetail page
- Components: AgentTimeline, ToolCallTable, VerificationPanel, JsonViewer

### Phase 6 — Replay + Async Tasks
- Replay from a specific step, RQ queue for background runs

### Phase 7 — LangGraph Migration
- State graph replaces handwritten runner, conditional edges for verify→retry→human_review

### Phase 8 — RAG + MCP + Docker Compose Deployment

## Database Schema (7 core tables)

```
research_tasks 1 → N agent_runs
agent_runs 1 → N agent_steps
agent_runs 1 → N tool_calls
agent_steps 1 → N tool_calls
agent_runs 1 → 1 verification_results
agent_runs 1 → 1 daily_reports
research_tasks 1 → N research_items
```

Status values for research_tasks: `pending`, `running`, `success`, `failed`, `verified_failed`
step_names: `planner`, `search`, `fetch`, `rank`, `summarize`, `verify`, `publish`
agent_runs has `parent_run_id` for Replay (run_type: `normal` or `replay`)

## API Endpoints

```
POST   /api/tasks                       — Create research task
GET    /api/tasks                       — List tasks
POST   /api/tasks/{task_id}/run         — Trigger a run (sync in v1, async in v2)
GET    /api/agent-runs/{run_id}         — Full run detail: run + steps + tool_calls + verification
POST   /api/agent-runs/{run_id}/replay  — Replay from step (e.g., {"from_step": "summarize"})
GET    /api/reports                     — List reports
GET    /api/reports/{report_id}         — Report detail
```

## Key Design Principles

1. **One file at a time** — implement and test incrementally
2. **Fake tools first** — don't get blocked by external API auth/network issues
3. **Handwritten Runner first** — understand state/step/trace/retry before introducing LangGraph
4. **Rule Verifier first** — then LLM Verifier; never trust LLM self-evaluation
5. **Every step must leave a trace** — agent_steps and tool_calls tables are the project's core value
6. **Pydantic validates all API contracts** — models (DB) ≠ schemas (API)

## Common Commands (add as project builds)

```bash
# Run backend (once main.py exists)
cd backend && uvicorn app.main:app --reload --port 8000

# Run tests
cd backend && pytest tests/ -v

# Run single test
cd backend && pytest tests/test_trace_logger.py::test_start_and_finish_run -v

# Database migration (once Alembic is configured)
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"
```

## Environment Setup

Python 3.12+, MySQL 8.0, Redis 7, Docker 29+
Required pip packages (Phase 1): `fastapi`, `uvicorn`, `sqlalchemy`, `pymysql`, `pydantic-settings`, `redis`, `pytest`, `httpx`, `python-dotenv`
