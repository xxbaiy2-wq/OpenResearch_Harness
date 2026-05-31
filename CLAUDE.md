# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenResearch Harness is a Research Agent Harness platform — an AI tech-trend radar that automatically collects papers, open-source projects, and technical articles, then generates daily tech radar reports using LLM.

**Core concept:**
```
Research Agent completes research tasks.
Agent Harness makes it controllable, observable, verifiable, and replayable.
```

Key Harness components: Tool Registry, Permission Guard, Trace Logger, Retry Policy, State Manager, Verifier, Research Runner.

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| API Backend | FastAPI | Python 3.12, CORS enabled, APScheduler for daily tasks |
| ORM | SQLAlchemy 2.x | 7 core tables: tasks, runs, steps, tool_calls, reports, items, verification |
| Database | MySQL 8.0 | Auto-created tables via Base.metadata.create_all |
| LLM | Xiaomi Mimo API | OpenAI-compatible, configured via MIMO_API_KEY in .env |
| Frontend | React 19 + Ant Design 6 | TypeScript, react-router-dom, axios |
| Deployment | Docker Compose + Nginx | 5 services: mysql, redis, backend, frontend (build), nginx |

## Architecture

```
User → React Frontend (port 80)
          ↓
       Nginx (reverse proxy)
          ↓
       FastAPI Backend (port 8000)
          ↓
       ResearchRunner
          ├── LLMPlanner (generates search queries via Mimo API)
          ├── GithubTool / ArxivTool / RSSTool (data collection)
          ├── LLMSummarizer (generates article-style reports)
          ├── Verifier (rule-based: length, URLs, overclaim words)
          └── APScheduler (daily auto-run at 9:00 AM)
          ↓
       MySQL (agent_runs → agent_steps → tool_calls trace chain)
```

## Common Commands

```bash
# Backend development
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend development
cd frontend && npm start

# Run all tests
cd backend && pytest tests/ -v

# Run single test
cd backend && pytest tests/test_trace_logger.py -v

# Docker deployment (on server)
docker compose up -d --build

# Check service status
docker compose ps

# View backend logs
docker compose logs backend -f
```

## Key Files

- `backend/app/main.py` — FastAPI entry point, CORS, scheduler, router registration
- `backend/app/harness/runner.py` — Core orchestrator: planner → search → fetch → rank → summarize → verify → publish
- `backend/app/harness/trace_logger.py` — Writes every run/step/tool_call to MySQL (most important file)
- `backend/app/harness/verifier.py` — Rule-based report quality check
- `backend/app/tools/llm_planner.py` — LLM generates search plan with Pydantic validation
- `backend/app/tools/llm_summarizer.py` — LLM generates article-style reports
- `backend/app/core/llm_client.py` — Unified LLM call wrapper (OpenAI-compatible API)
- `frontend/src/pages/Home.tsx` — Daily radar homepage with hero section and article display
- `frontend/src/pages/AgentRunDetail.tsx` — Timeline + Tool Calls visualization
- `docker-compose.yml` — 5-service deployment configuration

## Environment Variables (.env in project root)

```
MYSQL_PASSWORD=xxx
MIMO_API_KEY=your_xiaomi_api_key
MIMO_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
DATABASE_URL=mysql+pymysql://root:password@mysql:3306/openresearch
REDIS_URL=redis://redis:6379/0
```

Note: In docker-compose, `@mysql` and `@redis` are internal service names, NOT localhost.

## Database Schema

```
research_tasks 1→N agent_runs 1→N agent_steps 1→N tool_calls
agent_runs 1→1 verification_results
agent_runs 1→1 daily_reports
research_tasks 1→N research_items
```

Task statuses: `pending`, `running`, `success`, `failed`, `verified_failed`
Run types: `normal`, `replay` (replay runs have parent_run_id)

## API Endpoints

```
POST   /api/tasks                        — Create task
GET    /api/tasks                        — List tasks
POST   /api/tasks/{id}/run               — Trigger run (sync)
POST   /api/tasks/daily-run              — Auto-trigger all tasks (scheduler)
GET    /api/agent-runs/{id}              — Run detail with steps + tool_calls
GET    /api/reports                      — List reports
GET    /api/reports/{id}                 — Report detail with items + verification
GET    /api/reports/latest/main          — Latest report for homepage
GET    /api/reports/by-date/{date}       — Report by date (YYYY-MM-DD)
GET    /api/reports/search?q=keyword     — Search research items
GET    /api/reports/weekly/{year}/{week} — Weekly summary
```

## Python Packages

Backend: `fastapi`, `uvicorn`, `sqlalchemy`, `pymysql`, `pydantic-settings`, `redis`, `openai`, `feedparser`, `apscheduler`, `pytest`, `httpx`, `cryptography`

Frontend: `react`, `react-router-dom`, `antd`, `@ant-design/icons`, `axios`, `dayjs`

## Tests (21 total)

- `test_verifier.py` (6) — Report quality rules
- `test_tool_registry.py` (4) — Tool registration and lookup
- `test_permission_guard.py` (5) — Permission and call limits
- `test_trace_logger.py` (5) — Trace logging to SQLite (in-memory)
- `test_runner.py` (1) — End-to-end with mocked LLM and tools
