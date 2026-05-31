# OpenResearch Harness：AI 技术趋势雷达与 Agent 运行验证平台开发实施手册 v1.0

> 适用对象：代码基础较薄、但希望真正掌握后端工程 + Agent Harness 的研究生 / 求职者。  
> 项目目标：不做“AI 资讯套壳”，而是做一个能上线、能自用、能面试讲深的 Agent 工程化项目。  
> 推荐开发方式：你自己按文件实现，AI 只做解释、review、局部修复和测试辅助。

---

## 0. 这份文档怎么用

这不是一份“复制粘贴即可完成项目”的代码生成说明，而是一份带训练轮的工程实施手册。你应该按下面方式使用：

1. 每次只实现一个文件，不要同时开很多文件。
2. 每个文件写之前先读“为什么要写它”。
3. 每个文件写完后跑一次最小测试。
4. 遇到错误时先自己定位，再让 AI 解释报错。
5. 不让 AI 一次生成整个项目，只让 AI 做局部 review、补测试、解释错误。
6. 每天写一小段开发日志：今天实现了什么、为什么这么做、遇到什么问题、如何解决。

本项目最重要的学习目标不是“会用某个库”，而是理解下面这句话：

```text
真实 Agent 系统最大的问题不是能不能生成内容，而是能不能被控制、观测、验证和恢复。
```

---

## 1. 项目一句话定位

OpenResearch Harness 是一个面向 AI 开发者的技术趋势雷达平台。它会围绕用户订阅的主题，例如 Agent Harness、MCP、LangGraph、RAG、Agent Skills 等，自动收集论文、开源项目和技术文章，生成每日技术雷达报告。

但项目真正的技术核心不是“生成日报”，而是实现一个轻量级 Agent Harness：

```text
Research Agent 负责完成研究任务。
Agent Harness 负责让它可控、可观测、可验证、可回放。
```

---

## 2. 为什么这个项目不是普通 AI 新闻总结

普通 AI 新闻总结通常是：

```text
抓取内容 -> 丢给 LLM -> 生成摘要 -> 展示页面
```

这个项目应该是：

```text
创建研究任务
-> Planner 生成研究计划
-> Tool Registry 查找可用工具
-> Permission Guard 检查工具调用权限和预算
-> Search / arXiv / GitHub / RSS 工具收集证据
-> State Manager 保存中间状态
-> Trace Logger 记录每一步输入输出
-> Summarizer 生成结构化报告
-> Verifier 检查来源、新鲜度、重复、夸大表达
-> Retry Policy 处理失败和重试
-> Human Review 决定是否发布
-> Replay 支持从失败步骤重跑
-> Report 页面公开展示
```

所以你面试时不要说“我做了一个 AI 新闻总结网站”，而要说：

```text
我做了一个面向技术研究任务的 Research Agent Harness。它把研究型 Agent 的计划、工具调用、状态、验证、重试、日志和回放全部工程化，解决 Agent 输出不可控、不可追踪、难验证、失败难复现的问题。
```

---

## 3. 用户场景与产品价值

### 3.1 目标用户

| 用户 | 需求 | 项目提供的价值 |
|---|---|---|
| AI 应用开发求职者 | 想跟上 Agent/RAG/MCP 新技术 | 每天生成技术雷达，降低信息筛选成本 |
| 后端开发求职者 | 想做一个有真实后端架构的项目 | 项目包含 MySQL、Redis、异步任务、部署、日志、限流 |
| 研究生 | 想追踪论文和开源趋势 | 自动追踪 arXiv、GitHub、技术博客 |
| 面试官 | 想确认项目是不是套壳 | 可展示 Agent 执行轨迹、tool calls、verification、replay |

### 3.2 第一版用户故事

```text
作为一个 AI 应用开发求职者，
我想订阅“Agent Harness / MCP / LangGraph”等主题，
系统每天帮我收集相关论文、开源项目和技术动态，
并生成带来源、带验证结果、可追溯生成过程的技术雷达报告，
这样我能持续学习前沿，也能把项目作为真实上线作品展示。
```

---

## 4. MVP 范围

### 4.1 第一版必须做

| 模块 | 必须做到什么 |
|---|---|
| 研究任务 | 能创建 topic，例如 “Agent Harness” |
| Runner | 能手动触发一次完整 research flow |
| Fake Tools | 先用假工具跑通流程，避免一开始被外部 API 卡死 |
| Trace | agent_runs、agent_steps、tool_calls 必须落库 |
| Verifier | 能基于规则通过或拒绝报告 |
| Report | 能生成一份简单日报 |
| 前端 | 至少能看到任务列表、报告详情、Agent Timeline、Tool Calls |
| 部署 | 最终能用 Docker Compose 在 Linux 服务器运行 |

### 4.2 第一版暂时不做

```text
复杂登录注册
支付系统
多租户权限
复杂爬虫
复杂推荐算法
一开始就接很多数据源
一开始就上 LangGraph
一开始就做 MCP
一开始就做复杂 RAG
```

原因：你代码基础较薄，第一目标是理解 Harness 骨架。先把“可控、可观测、可验证”跑通，再逐步加真实工具、LLM、Skills、LangGraph、RAG、MCP。

---

## 5. 技术栈总览

| 层级 | 技术 | 第一版是否使用 | 何时引入 | 为什么合适 |
|---|---|---:|---|---|
| API 后端 | FastAPI | 是 | 第 1 天 | Python AI 生态好，类型提示和 Pydantic 适合结构化 API |
| ORM | SQLAlchemy | 是 | 第 1-2 天 | 关系型表多，便于从 Python 操作 MySQL |
| 数据库 | MySQL | 是 | 第 1 周 | Agent run、step、tool_call 是强结构化关系数据 |
| 缓存/限流 | Redis | 是 | 第 1-2 周 | 做工具调用限流、任务状态、热点报告缓存 |
| 队列 | RQ | 第二版 | 第 3-4 周 | 学习成本低，适合把长任务放后台 |
| 队列升级 | Celery | 可选 | 项目稳定后 | 更适合复杂定时任务和分布式 worker |
| Agent 流程 | 手写 Runner | 是 | 第 1 周 | 帮你理解状态、步骤、trace、重试 |
| Agent 图编排 | LangGraph | 后期 | 手写 Runner 跑通后 | 流程有状态、分支、恢复、human-in-the-loop，才值得引入 |
| LLM 适配 | OpenAI/DeepSeek/Qwen 任一 | 第二版 | Harness 跑通后 | 用于 Planner、Summarizer、Verifier |
| Skills | 自研轻量版 Skills | 第二/三版 | LLM 节点稳定后 | 把论文分析、项目分析、报告生成等经验模块化 |
| RAG | Chroma/FAISS | 后期 | 有历史报告后 | 查询历史趋势、做重复检测 |
| MCP | Python MCP SDK | 后期 | 内部工具稳定后 | 把平台能力暴露给外部 Agent 客户端 |
| 前端 | React + TypeScript | 是 | 第 4 周 | 展示执行时间线、日志表格、报告详情 |
| 部署 | Docker Compose + Nginx + Linux | 是 | 第 6 周 | 多容器服务部署简单，适合轻量服务器 |

---

## 6. 技术选择依据：不是为了堆技术

### 6.1 为什么用 FastAPI

FastAPI 是基于标准 Python 类型提示构建 API 的现代 Web 框架，适合 Python AI 应用后端。项目里有大量结构化输入输出，例如创建任务、查询 Agent Run、返回 tool calls、提交 replay 请求，FastAPI + Pydantic 能帮助你明确 API 合约。

不用 Flask 的原因：Flask 更轻，但你需要自己补很多类型校验、OpenAPI 文档、依赖注入约束。  
不用 Spring Boot 作为第一版的原因：本项目核心 AI 生态在 Python，第一阶段重点是 Harness，不应该让 Java 后端配置增加学习负担。

### 6.2 为什么用 MySQL

Agent Harness 会产生大量结构化记录：

```text
research_tasks -> agent_runs -> agent_steps -> tool_calls -> verification_results -> daily_reports
```

这些对象之间有明确关系，适合关系型数据库。MySQL 还能让你在面试中展开讲表设计、索引、事务和查询优化。

不用 MongoDB 的原因：项目不是无结构文档存储，核心数据有强关系。如果 tool_calls 和 agent_steps 没有关系表，后续就很难做 Timeline、Replay 和失败归因。

### 6.3 为什么用 Redis

Redis 在项目里承担 Harness 的控制功能，而不是简单缓存：

```text
工具调用限流：tool_limit:{run_id}:{tool_name}
用户每日任务配额：user_quota:{user_id}:{date}
任务状态缓存：task_status:{task_id}
热门日报缓存：report_cache:{report_id}
分布式锁：lock:daily_report:{topic}:{date}
```

没有 Redis 也可以完成 demo，但一旦要上线，Agent 可能重复调用搜索工具、重复生成报告、请求过多导致接口被封。Redis 解决的是执行预算和并发控制问题。

### 6.4 为什么先 RQ 后 Celery

第一版后台任务可以先同步执行，第二版再上 RQ。RQ 是基于 Redis 的简单 Python 队列，学习成本低，适合你先把耗时 research run 放到后台。

Celery 更强，但也更重。等你有定时日报、多 worker、任务路由、失败重试监控等需求后，再升级 Celery 更合理。

### 6.5 为什么一开始不直接用 LangGraph

LangGraph 适合有状态、多步骤、条件分支、恢复和 human-in-the-loop 的 agent workflow。但你现在代码基础薄，如果第一天就用 LangGraph，很容易变成“会照教程调库”，却不理解它解决了什么问题。

所以顺序应该是：

```text
先手写 Runner -> 理解 state/step/trace/retry -> 再迁移 LangGraph
```

最终引入 LangGraph 的真实原因是：

```text
plan -> search -> fetch -> rank -> summarize -> verify -> publish
```

这个流程天然有状态流转；verify 失败后要回到 summarize；连续失败后要 human_review；后续 replay 和 time travel 需要保存状态。这时 LangGraph 是合适的，不是硬加。

### 6.6 为什么用 Skills

Skills 不应该第一天就上。它适合在 LLM 节点稳定后引入，用来沉淀重复任务经验。

本项目里适合做成 Skills 的任务：

```text
Paper Analysis Skill：如何判断论文价值
GitHub Project Analysis Skill：如何判断开源项目价值
Trend Report Writer Skill：如何组织日报
Verification Skill：如何检查夸大、缺来源、重复
```

Skills 是“经验包”，Tools 是“动作”，Harness 是“控制系统”。

### 6.7 为什么后期做 MCP

MCP 的价值是把系统能力标准化暴露给外部 Agent 客户端。第一版没必要做 MCP，因为你的内部工具还不稳定。

当你已经有 search_research_items、generate_daily_report、explain_concept、query_trend_history 这些内部工具后，再包装成 MCP tools 就很自然。

### 6.8 为什么后期做 RAG

RAG 不应该第一天做。RAG 的真实用途是：

```text
查询历史报告
判断今天内容和历史内容是否重复
根据过去一个月趋势回答用户问题
辅助 Verifier 判断 novelty
```

没有历史数据时做 RAG 是空的；先有 reports 和 research_items，再做 RAG 更合理。

### 6.9 为什么用 Docker Compose

项目至少包含：

```text
backend
frontend
mysql
redis
worker
nginx
```

Docker Compose 可以用一个 YAML 管理多容器服务、网络、环境变量和 volumes，适合轻量服务器部署。

---

## 7. 总体架构

### 7.1 第一版架构

```text
React Frontend
    |
    v
FastAPI Backend
    |
    v
Research Service
    |
    v
Handwritten Harness Runner
    |-- Tool Registry
    |-- Permission Guard
    |-- Trace Logger
    |-- Retry Policy
    |-- State Manager
    |-- Rule-based Verifier
    |
    v
Fake Tools
    |-- fake_search_tool
    |-- fake_fetch_tool
    |-- fake_summarize_tool
    |
    v
MySQL + Redis
```

### 7.2 完整版架构

```text
React + TypeScript Dashboard
    |
    v
Nginx Reverse Proxy
    |
    v
FastAPI API Gateway
    |-----------------------------|
    v                             v
Research Service              Agent Run Service
    |                             |
    v                             v
RQ / Celery Worker           Trace Query APIs
    |
    v
LangGraph Research Workflow
    |-- Planner Node
    |-- Search Node
    |-- Fetch Node
    |-- Rank Node
    |-- Summarize Node
    |-- Verify Node
    |-- Publish Node
    |
    v
Harness Layer
    |-- Tool Registry
    |-- Permission Guard
    |-- Skill Loader
    |-- Trace Logger
    |-- Retry Policy
    |-- Replay Manager
    |
    v
Tools
    |-- arXiv Tool
    |-- GitHub Tool
    |-- RSS Tool
    |-- RAG Retriever
    |-- MCP Tool Adapter
    |
    v
MySQL + Redis + Vector Store
```

---

## 8. 核心业务流程

### 8.1 创建研究任务

```text
用户输入 topic = "Agent Harness"
后端创建 research_tasks 记录
状态为 pending
```

### 8.2 执行研究任务

```text
用户点击 Run
后端创建 agent_run
Runner 开始执行
每一步都创建 agent_step
每次工具调用都创建 tool_call
Verifier 生成 verification_result
通过后生成 daily_report
```

### 8.3 查看执行过程

前端 AgentRunDetail 页面请求：

```http
GET /api/agent-runs/{run_id}
```

展示：

```text
Run 基本信息
Step Timeline
Tool Calls
Verification Result
错误信息
耗时统计
```

### 8.4 Replay

```text
用户选择从 summarize 步骤重跑
系统读取 summarize 上一步的 output_json
创建 parent_run_id = 原始 run_id 的新 replay run
从 summarize 继续执行
比较两次结果
```

---

## 9. 数据库设计

### 9.1 表关系

```text
research_tasks 1 -> N agent_runs
agent_runs 1 -> N agent_steps
agent_runs 1 -> N tool_calls
agent_steps 1 -> N tool_calls
agent_runs 1 -> 1 verification_results
agent_runs 1 -> 1 daily_reports
research_tasks 1 -> N research_items
```

### 9.2 research_tasks

```sql
CREATE TABLE research_tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    topic VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

状态：

```text
pending：已创建但未运行
running：正在运行
success：运行成功
failed：运行失败
verified_failed：Verifier 未通过
```

### 9.3 agent_runs

```sql
CREATE TABLE agent_runs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_json JSON,
    output_json JSON,
    error_message TEXT,
    started_at DATETIME NOT NULL,
    finished_at DATETIME,
    total_latency_ms INT,
    total_tokens INT DEFAULT 0,
    parent_run_id BIGINT,
    run_type VARCHAR(50) DEFAULT 'normal',
    FOREIGN KEY (task_id) REFERENCES research_tasks(id)
);
```

parent_run_id 用于 Replay。run_type 可以是 normal 或 replay。

### 9.4 agent_steps

```sql
CREATE TABLE agent_steps (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    run_id BIGINT NOT NULL,
    step_index INT NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_json JSON,
    output_json JSON,
    error_message TEXT,
    latency_ms INT,
    started_at DATETIME NOT NULL,
    finished_at DATETIME,
    FOREIGN KEY (run_id) REFERENCES agent_runs(id)
);
```

step_name：

```text
planner
search
fetch
rank
summarize
verify
publish
```

### 9.5 tool_calls

```sql
CREATE TABLE tool_calls (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    run_id BIGINT NOT NULL,
    step_id BIGINT,
    tool_name VARCHAR(100) NOT NULL,
    input_json JSON,
    output_json JSON,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    latency_ms INT,
    retry_count INT DEFAULT 0,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (run_id) REFERENCES agent_runs(id),
    FOREIGN KEY (step_id) REFERENCES agent_steps(id)
);
```

这是项目中最重要的表之一。它体现你理解 Agent 不是黑盒：每次工具调用都要记录输入、输出、耗时、错误和重试次数。

### 9.6 research_items

```sql
CREATE TABLE research_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id BIGINT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    summary TEXT,
    raw_content TEXT,
    published_at DATETIME,
    score FLOAT DEFAULT 0,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (task_id) REFERENCES research_tasks(id)
);
```

### 9.7 verification_results

```sql
CREATE TABLE verification_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    run_id BIGINT NOT NULL,
    report_id BIGINT,
    passed BOOLEAN NOT NULL,
    score INT NOT NULL,
    problems_json JSON,
    action VARCHAR(50),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (run_id) REFERENCES agent_runs(id)
);
```

### 9.8 daily_reports

```sql
CREATE TABLE daily_reports (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id BIGINT NOT NULL,
    run_id BIGINT NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    created_at DATETIME NOT NULL,
    published_at DATETIME,
    FOREIGN KEY (task_id) REFERENCES research_tasks(id),
    FOREIGN KEY (run_id) REFERENCES agent_runs(id)
);
```

### 9.9 skills 与 skill_usages：第二阶段再加

```sql
CREATE TABLE skills (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    path VARCHAR(500) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL
);
```

```sql
CREATE TABLE skill_usages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    run_id BIGINT NOT NULL,
    step_id BIGINT,
    skill_name VARCHAR(100) NOT NULL,
    skill_version VARCHAR(50),
    input_json JSON,
    output_json JSON,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (run_id) REFERENCES agent_runs(id),
    FOREIGN KEY (step_id) REFERENCES agent_steps(id)
);
```

---

## 10. 项目目录结构

```text
openresearch-harness/
  backend/
    app/
      main.py

      api/
        routes_tasks.py
        routes_reports.py
        routes_agent_runs.py
        routes_replay.py

      core/
        config.py
        database.py
        redis_client.py
        logging.py

      models/
        research_task.py
        research_item.py
        daily_report.py
        agent_run.py
        agent_step.py
        tool_call.py
        verification_result.py
        skill.py

      schemas/
        research_task.py
        research_item.py
        daily_report.py
        agent.py
        tool.py
        verification.py
        replay.py

      harness/
        runner.py
        tool_registry.py
        permission_guard.py
        trace_logger.py
        retry_policy.py
        state_manager.py
        verifier.py
        replay.py
        skill_loader.py

      tools/
        base.py
        fake_search_tool.py
        fake_fetch_tool.py
        fake_summarize_tool.py
        arxiv_tool.py
        github_tool.py
        rss_tool.py

      skills/
        paper_analysis/
          SKILL.md
          examples.md
          output_schema.json

        github_project_analysis/
          SKILL.md
          examples.md
          output_schema.json

        trend_report_writer/
          SKILL.md
          examples.md
          output_schema.json

        verification/
          SKILL.md
          rules.json
          examples.md

      services/
        research_service.py
        report_service.py
        agent_run_service.py
        item_service.py

      workers/
        queue.py
        tasks.py

    tests/
      test_tool_registry.py
      test_permission_guard.py
      test_trace_logger.py
      test_runner.py
      test_verifier.py
      test_replay.py

  frontend/
    src/
      pages/
        Dashboard.tsx
        ResearchTasks.tsx
        AgentRunDetail.tsx
        ReportDetail.tsx

      components/
        AgentTimeline.tsx
        ToolCallTable.tsx
        VerificationPanel.tsx
        ReportCard.tsx
        JsonViewer.tsx

  docker-compose.yml
  README.md
  .env.example
```

---

## 11. 第一阶段：一个文件一个文件实现

### 11.1 core/config.py

目标：统一读取环境变量。

你要实现：

```text
DATABASE_URL
REDIS_URL
APP_ENV
LLM_API_KEY，后期再用
```

建议结构：

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
```

你要理解：配置不能写死。部署到服务器时，数据库地址和密钥都应该来自环境变量。

自测：

```text
临时 print(settings.database_url)，确认能从 .env 读取。
```

AI 辅助问法：

```text
我正在写 FastAPI 项目的 config.py。请帮我检查 pydantic-settings 的用法是否正确，不要帮我生成整个项目。
```

### 11.2 core/database.py

目标：创建 SQLAlchemy 连接。

你要实现：

```text
engine
SessionLocal
Base
get_db
```

关键理解：

```text
engine 负责数据库连接池。
SessionLocal 负责创建每次请求的数据库会话。
Base 是所有 ORM 模型的基类。
get_db 是 FastAPI 依赖注入，用完 session 后关闭。
```

### 11.3 models/*.py

目标：定义 ORM 表。

先写这些模型：

```text
ResearchTask
AgentRun
AgentStep
ToolCall
DailyReport
VerificationResult
ResearchItem
```

注意：

```text
不要把所有模型都塞进一个超大文件。
每个表一个文件，方便维护。
```

每个模型至少包含：

```text
id
业务字段
created_at
updated_at，部分表需要
```

### 11.4 schemas/*.py

目标：定义 API 输入输出，不等于数据库表。

你要理解：

```text
ORM Model 是数据库结构。
Pydantic Schema 是 API 合约。
```

例如：

```python
class ResearchTaskCreate(BaseModel):
    topic: str
    description: str | None = None

class ResearchTaskOut(BaseModel):
    id: int
    topic: str
    status: str
```

### 11.5 tools/base.py

目标：统一所有工具的接口。

建议：

```python
from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        pass
```

你要理解：Runner 不应该关心工具内部怎么实现。Runner 只知道工具有 name 和 run 方法。

### 11.6 harness/tool_registry.py

目标：注册和查找工具。

核心类：

```python
class ToolSpec(BaseModel):
    name: str
    description: str
    input_schema: dict
    permission_level: str = "normal"
    timeout_seconds: int = 10
    max_retries: int = 2
```

核心方法：

```text
register(tool, spec)
get_tool(name)
get_spec(name)
list_tools()
```

你要理解：工具不是普通函数。真实 Agent 系统里的工具要有 schema、描述、权限、超时、重试策略。

### 11.7 tools/fake_search_tool.py

目标：返回假 research items，先跑通流程。

输入：

```json
{
  "topic": "Agent Harness"
}
```

输出：

```json
{
  "items": [
    {
      "title": "What is Agent Harness",
      "url": "https://example.com/agent-harness",
      "source_type": "fake",
      "summary": "Agent Harness controls tool use, tracing, verification and replay."
    }
  ]
}
```

为什么先用 fake tool：

```text
你第一阶段要验证 Harness，不要被 arXiv/GitHub API 的网络问题、鉴权问题、字段问题卡住。
```

### 11.8 harness/permission_guard.py

目标：工具调用前做检查。

第一版规则：

```text
工具必须存在。
一次 run 最多调用 20 次工具。
同一个工具一次 run 最多调用 5 次。
输入必须是 dict。
```

第二版加 Redis：

```text
tool_limit:{run_id}:{tool_name}
user_quota:{user_id}:{date}
```

你要理解：Permission Guard 是 Agent 的刹车系统。

### 11.9 harness/trace_logger.py

目标：将 Agent 执行过程写入 MySQL。

必须有这些方法：

```text
start_run(task_id, input_data) -> run_id
finish_run(run_id, output_data)
fail_run(run_id, error_message)

start_step(run_id, step_name, input_data) -> step_id
finish_step(step_id, output_data)
fail_step(step_id, error_message)

log_tool_call(run_id, step_id, tool_name, input_data, output_data, status, error_message, latency_ms, retry_count)
```

这是项目最重要的文件。你要慢慢写，不要让 AI 一次生成。

你要理解：

```text
没有 Trace Logger，Agent 就是黑盒。
有了 Trace Logger，Agent 每一步都能被看见、排查、回放。
```

### 11.10 harness/retry_policy.py

目标：判断失败是否应该重试。

第一版规则：

| 错误类型 | 是否重试 | 原因 |
|---|---:|---|
| TimeoutError | 是 | 外部服务临时失败 |
| JSONParseError | 是 | LLM 输出格式可能偶发错误 |
| VerifierFailed | 是，最多一次 | 可回到 summarize 重写 |
| PermissionDenied | 否 | 权限错误重试无意义 |
| ToolNotFound | 否 | 配置错误重试无意义 |

你要理解：不是所有失败都该重试。乱重试会导致成本更高、错误更难定位。

### 11.11 harness/verifier.py

目标：第一版用规则检查报告。

规则：

```text
报告不能为空。
报告长度不能低于 300 字。
至少包含 3 个 research_items。
每个 item 必须有 url。
标题和报告不能包含过度夸大词。
```

夸大词：

```text
颠覆
彻底取代
革命性
史无前例
完全改变
```

输出：

```json
{
  "passed": false,
  "score": 70,
  "problems": [
    {
      "type": "missing_source",
      "message": "第 2 条内容缺少来源 URL"
    }
  ],
  "action": "revise"
}
```

你要理解：Verifier 不是为了让 Agent 更聪明，而是为了让 Agent 输出更可靠。

### 11.12 harness/state_manager.py

目标：维护 run 的中间状态。

第一版可以用 dict：

```python
state = {
    "task_id": task_id,
    "topic": topic,
    "plan": [],
    "items": [],
    "ranked_items": [],
    "draft_report": None,
    "verification": None,
    "final_report": None
}
```

你要理解：Agent 不是一次性 prompt。多步骤任务必须有状态。

### 11.13 harness/runner.py

目标：串起完整流程。

第一版流程：

```text
start_run
planner step
search step
fetch step
rank step
summarize step
verify step
publish step
finish_run
```

伪代码：

```python
class ResearchRunner:
    def run(self, task_id: int):
        run_id = trace_logger.start_run(task_id, input_data)
        state = create_initial_state(task_id)

        try:
            self.run_planner(run_id, state)
            self.run_search(run_id, state)
            self.run_fetch(run_id, state)
            self.run_rank(run_id, state)
            self.run_summarize(run_id, state)
            self.run_verify(run_id, state)

            if not state["verification"]["passed"]:
                trace_logger.fail_run(run_id, "verification failed")
                return

            self.run_publish(run_id, state)
            trace_logger.finish_run(run_id, state["final_report"])
        except Exception as e:
            trace_logger.fail_run(run_id, str(e))
```

你要注意：这只是伪代码。你应该按方法拆分实现，写完一个 step 测一次。

### 11.14 services/research_service.py

目标：处理任务创建、任务状态更新、调用 Runner。

它不要包含工具细节，只做业务编排。

### 11.15 services/report_service.py

目标：创建和查询 daily_reports。

### 11.16 api/routes_tasks.py

接口：

```http
POST /api/tasks
GET /api/tasks
POST /api/tasks/{task_id}/run
```

第一版 run 可以同步执行，后续改成 RQ 异步。

### 11.17 api/routes_agent_runs.py

接口：

```http
GET /api/agent-runs/{run_id}
```

返回：

```json
{
  "run": {},
  "steps": [],
  "tool_calls": [],
  "verification": {}
}
```

### 11.18 api/routes_reports.py

接口：

```http
GET /api/reports/{report_id}
GET /api/reports
```

---

## 12. 前端页面设计

第一版前端不要追求美观，重点展示 Harness。

### 12.1 ResearchTasks 页面

显示：

```text
任务 ID
Topic
Status
Created At
Run 按钮
查看 Runs 按钮
```

### 12.2 AgentRunDetail 页面

这是最重要页面。

显示：

```text
Run 状态
总耗时
错误信息
Step Timeline
Tool Calls
Verification Result
```

### 12.3 AgentTimeline 组件

每个 step 显示：

```text
step_name
status
latency_ms
started_at
finished_at
展开后显示 input_json / output_json / error_message
```

### 12.4 ToolCallTable 组件

每条 tool call 显示：

```text
tool_name
status
latency_ms
retry_count
input_json
output_json
error_message
```

### 12.5 ReportDetail 页面

显示：

```text
报告标题
报告正文
来源列表
Verifier 分数
生成它的 run_id
```

---

## 13. API 设计

### 13.1 创建任务

```http
POST /api/tasks
```

请求：

```json
{
  "topic": "Agent Harness",
  "description": "追踪 Agent Harness 相关论文、项目和技术动态"
}
```

响应：

```json
{
  "id": 1,
  "topic": "Agent Harness",
  "status": "pending"
}
```

### 13.2 触发任务

```http
POST /api/tasks/{task_id}/run
```

响应：

```json
{
  "run_id": 1001,
  "status": "running"
}
```

### 13.3 查询 Run 详情

```http
GET /api/agent-runs/{run_id}
```

响应：

```json
{
  "run": {
    "id": 1001,
    "status": "success"
  },
  "steps": [],
  "tool_calls": [],
  "verification": {}
}
```

### 13.4 Replay

```http
POST /api/agent-runs/{run_id}/replay
```

请求：

```json
{
  "from_step": "summarize"
}
```

---

## 14. 第二阶段：接真实数据源

第一版 fake flow 跑通后，再接真实来源。

### 14.1 arXiv Tool

输入：

```json
{
  "query": "agent harness",
  "max_results": 5
}
```

输出：

```json
{
  "items": [
    {
      "title": "",
      "url": "",
      "authors": [],
      "abstract": "",
      "published_at": ""
    }
  ]
}
```

注意：不要把 arXiv 返回结果直接丢给 LLM。先结构化、入库、去重。

### 14.2 GitHub Tool

输入：

```json
{
  "query": "langgraph agent",
  "max_results": 5
}
```

输出：

```json
{
  "items": [
    {
      "name": "",
      "url": "",
      "description": "",
      "stars": 0,
      "language": "",
      "updated_at": ""
    }
  ]
}
```

### 14.3 RSS Tool

输入：

```json
{
  "feed_url": "",
  "max_results": 10
}
```

输出：

```json
{
  "items": [
    {
      "title": "",
      "url": "",
      "published_at": "",
      "summary": ""
    }
  ]
}
```

---

## 15. 第三阶段：接 LLM

先接三个节点：

```text
Planner
Summarizer
Verifier
```

### 15.1 Planner

输入：

```json
{
  "topic": "Agent Harness"
}
```

输出必须是结构化 JSON：

```json
{
  "topic": "Agent Harness",
  "queries": [
    "agent harness engineering",
    "agent observability tool tracing",
    "agent verification replay"
  ],
  "sources": ["arxiv", "github", "rss"]
}
```

### 15.2 Summarizer

输入：

```json
{
  "items": []
}
```

输出：

```json
{
  "title": "今日 Agent Harness 技术雷达",
  "sections": [
    {
      "heading": "新论文",
      "items": [
        {
          "title": "",
          "summary": "",
          "why_it_matters": "",
          "source_url": ""
        }
      ]
    }
  ]
}
```

### 15.3 LLM 输出必须校验

用 Pydantic 校验输出。如果校验失败：

```text
记录 agent_step 失败
按 Retry Policy 重试
超过次数则 fail_run
```

这一步很重要。你要真正感受到：LLM 不是可靠函数，Harness 必须约束它。

---

## 16. 第四阶段：Skills

### 16.1 Skills 的定位

Skills 不是工具，也不是工作流框架。它是任务经验包。

```text
Tool：执行一个外部动作，例如 search_arxiv。
Skill：告诉 Agent 如何完成一类专业任务，例如如何分析论文价值。
Harness：控制工具、状态、日志、重试和验证。
LangGraph：管理多步骤流程和条件分支。
```

### 16.2 推荐 4 个 Skills

| Skill | 作用 | 何时使用 |
|---|---|---|
| paper_analysis | 分析论文价值 | 拿到 arXiv 论文后 |
| github_project_analysis | 分析开源项目价值 | 拿到 GitHub repo 后 |
| trend_report_writer | 生成日报结构 | Summarizer 节点 |
| verification | 检查报告质量 | Verifier 节点 |

### 16.3 Skill 目录结构

```text
skills/paper_analysis/
  SKILL.md
  examples.md
  output_schema.json
```

### 16.4 SKILL.md 示例

```text
# Paper Analysis Skill

## Purpose
用于分析 AI Agent / RAG / MCP / LangGraph 相关论文是否值得进入日报。

## When to use
当 Research Agent 获取到论文标题、摘要、发布时间和 URL 后使用。

## Input
- title
- abstract
- authors
- published_at
- url

## Output
必须输出：
- core_problem
- method
- contribution
- limitation
- relevance_score
- why_it_matters

## Quality Criteria
- 不夸大论文贡献
- 必须指出局限
- 必须说明和用户 topic 的关系
```

### 16.5 Skill Loader

文件：

```text
harness/skill_loader.py
```

职责：

```text
读取 SKILL.md
读取 examples.md
读取 output_schema.json
记录 skill_usages
把 skill instruction 拼入对应节点的 prompt
```

---

## 17. 第五阶段：引入 LangGraph

### 17.1 什么时候引入

只有当你已经完成这些后再引入：

```text
手写 Runner 跑通
Trace Logger 可用
Verifier 可用
Retry Policy 可用
至少一个真实工具可用
```

### 17.2 为什么此时引入合理

因为你的流程已经变成状态图：

```text
plan -> search -> fetch -> rank -> summarize -> verify -> publish
```

并且有条件分支：

```text
verify passed -> publish
verify failed and retry_count < 1 -> summarize
verify failed and retry_count >= 1 -> human_review
```

LangGraph 的价值在于表达这种状态流、分支、持久化和恢复，而不是替代你的 Harness。

### 17.3 LangGraph 状态示例

```python
class ResearchState(TypedDict):
    task_id: int
    topic: str
    plan: dict
    items: list[dict]
    ranked_items: list[dict]
    draft_report: dict | None
    verification: dict | None
    final_report: dict | None
    retry_count: int
```

### 17.4 LangGraph 节点

```text
plan_node
search_node
fetch_node
rank_node
summarize_node
verify_node
publish_node
human_review_node
```

注意：即使用 LangGraph，Tool Registry、Permission Guard、Trace Logger、Verifier 仍然保留。LangGraph 管流程，Harness 管控制。

---

## 18. 第六阶段：Replay

### 18.1 为什么 Replay 重要

Replay 能说明你不是只做展示，而是真的能排查 Agent 问题。

如果某次 run 在 summarize 失败，你不应该只能重新跑全部流程。你可以从 summarize 重新执行。

### 18.2 第一版 Replay 规则

```text
输入 run_id 和 from_step
找到 from_step 的上一步 output_json
创建新的 replay run
parent_run_id 指向原始 run
从 from_step 继续执行
```

### 18.3 数据依赖

Replay 成立的前提是：

```text
每个 step 的 input_json 和 output_json 都已经保存。
```

这也是 agent_steps 表的价值。

---

## 19. 第七阶段：RAG

### 19.1 RAG 的真实用途

```text
查询历史报告
回答过去一个月技术趋势
判断今天内容是否和历史重复
为 Verifier 提供 novelty evidence
```

### 19.2 第一版 RAG 数据源

```text
daily_reports.content
research_items.title + summary + raw_content
verification_results.problems_json
```

### 19.3 不要过早做 RAG

没有历史数据时做 RAG 没意义。至少先积累 20-50 条 reports/items，再做检索。

---

## 20. 第八阶段：MCP

### 20.1 MCP 的真实用途

等内部工具稳定后，把它们暴露给外部 Agent 客户端：

```text
search_research_items
query_trend_history
generate_daily_report
explain_concept
```

### 20.2 为什么不是第一阶段做

第一阶段你的工具还没稳定。过早做 MCP 会变成协议 demo，而不是解决真实问题。

### 20.3 MCP 和内部 Tool Registry 的关系

```text
内部 Tool Registry：给自己的 Research Agent 用。
MCP Server：把一部分稳定工具暴露给外部客户端。
```

---

## 21. Redis 设计

### 21.1 工具调用限流

Key：

```text
tool_limit:{run_id}:{tool_name}
```

规则：

```text
每次工具调用前 INCR
如果超过阈值则拒绝
设置 EXPIRE 防止 key 永久存在
```

### 21.2 用户每日配额

```text
user_quota:{user_id}:{date}
```

### 21.3 分布式锁

```text
lock:daily_report:{topic}:{date}
```

用途：防止同一个主题一天重复生成多次日报。

### 21.4 任务状态缓存

```text
task_status:{task_id}
```

前端可以轮询这个状态。

---

## 22. 异步任务设计

第一版可以同步执行。

第二版引入 RQ：

```text
POST /api/tasks/{task_id}/run
-> enqueue run_research_task(task_id)
-> 立即返回 job_id
-> 前端轮询 job status
```

后续升级 Celery：

```text
每日定时生成
失败重试
多 worker
任务监控
```

---

## 23. 测试计划

你至少要写这些测试：

```text
test_tool_registry_register_and_get
test_tool_registry_unknown_tool
test_permission_guard_blocks_unknown_tool
test_permission_guard_blocks_too_many_calls
test_trace_logger_start_and_finish_run
test_trace_logger_records_step
test_trace_logger_records_tool_call
test_verifier_rejects_missing_url
test_verifier_rejects_overclaim
test_runner_creates_agent_run_steps_tool_calls
```

测试不是形式主义。它能防止你后面改 Runner 时把 trace 搞坏。

---

## 24. 部署方案

### 24.1 Docker Compose 服务

```text
backend
frontend
mysql
redis
worker
nginx
```

### 24.2 docker-compose.yml 大致结构

```yaml
services:
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: example
      MYSQL_DATABASE: openresearch
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7

  backend:
    build: ./backend
    depends_on:
      - mysql
      - redis
    env_file:
      - .env

  frontend:
    build: ./frontend

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    depends_on:
      - backend
      - frontend

volumes:
  mysql_data:
```

### 24.3 服务器部署目标

```text
能通过公网 IP 或域名访问
能创建任务
能生成报告
能查看 Agent Timeline
能查看 Tool Calls
```

---

## 25. AI 辅助开发规则

### 25.1 允许 AI 做什么

```text
解释报错
帮你 review 一个文件
帮你写单元测试
帮你比较两种设计
帮你检查 SQLAlchemy 写法
帮你解释 FastAPI 依赖注入
帮你优化某个函数
```

### 25.2 不允许 AI 做什么

```text
一次生成完整后端
一次生成完整前端
一次生成整个项目
直接复制不理解的代码
让 AI 替你做所有架构决策
```

### 25.3 推荐问 AI 的模板

```text
我正在实现 openresearch-harness 的 harness/trace_logger.py。
这个文件的职责是记录 agent_runs、agent_steps、tool_calls。
我现在只想实现 start_run 和 finish_run。
请你先解释这两个方法应该做什么，然后 review 我的代码，不要生成整个项目。
```

```text
这是我写的 permission_guard.py。
我想检查同一个 run 中同一个工具最多调用 5 次。
请你帮我找逻辑漏洞，并给出 2 个 pytest 测试。
```

```text
我的 Runner 在 verify step 失败后没有正确 fail_run。
这是报错和相关代码。
请你解释原因，指出我应该检查哪些变量，不要重写整个 runner.py。
```

---

## 26. 每个文件写之前必须回答的 5 个问题

```text
1. 这个文件解决什么问题？
2. 输入是什么？
3. 输出是什么？
4. 出错怎么办？
5. 它和 Harness 的关系是什么？
```

例：trace_logger.py

```text
1. 解决 Agent 黑盒问题。
2. 输入 run、step、tool_call 的执行信息。
3. 输出 MySQL 中结构化 trace 记录。
4. 写入失败时记录错误，不允许静默失败。
5. 它让 Agent 可观测、可回放、可排查。
```

---

## 27. 8 周开发计划

### 第 1 周：Harness 骨架

目标：不用 LLM，不用真实数据源，跑通 fake flow。

完成：

```text
FastAPI 启动
MySQL 连接
ORM Models
Schemas
Tool Registry
Permission Guard
Trace Logger
Rule Verifier
Fake Tools
ResearchRunner
基础 API
```

验收：

```text
触发一次任务后，MySQL 中能看到 agent_run、agent_steps、tool_calls。
```

### 第 2 周：真实数据源 + Redis

完成：

```text
arXiv Tool
GitHub Tool
RSS Tool，可选
Redis 工具调用限流
Research Items 入库
```

验收：

```text
真实抓取至少两个来源，items 入库，tool_calls 有记录。
```

### 第 3 周：LLM 节点

完成：

```text
Planner
Summarizer
LLM Verifier
Pydantic Schema 校验
LLM 输出失败重试
```

验收：

```text
LLM 输出不合法时能记录失败并重试。
```

### 第 4 周：Skills

完成：

```text
paper_analysis skill
github_project_analysis skill
trend_report_writer skill
verification skill
skill_loader
skill_usages 记录
```

验收：

```text
每次 summarize 或 verify 能看到使用了哪个 skill。
```

### 第 5 周：前端可视化

完成：

```text
ResearchTasks 页面
ReportDetail 页面
AgentRunDetail 页面
AgentTimeline 组件
ToolCallTable 组件
VerificationPanel 组件
```

验收：

```text
面试官打开页面能看到一次 Agent 是怎么运行的。
```

### 第 6 周：Replay + 异步任务

完成：

```text
Replay API
从指定 step 重跑
RQ 异步任务
任务状态轮询
```

验收：

```text
某个失败 run 可以从 summarize 重新执行。
```

### 第 7 周：LangGraph 迁移

完成：

```text
ResearchState
LangGraph nodes
conditional edges
verify failed -> summarize
human_review 节点
```

验收：

```text
同样的流程由 LangGraph 执行，但仍然复用 Harness。
```

### 第 8 周：RAG + MCP + 部署

完成：

```text
历史报告向量化
query_trend_history
MCP Server 初版
Docker Compose
Nginx
Linux 上线
```

验收：

```text
公网可访问，能生成报告，能查历史趋势。
```

---

## 28. 项目完成度分级

### 及格版

```text
Fake tools
手写 Runner
MySQL trace
规则 Verifier
简单报告
简单前端
```

### 良好版

```text
真实 arXiv/GitHub 工具
Redis 限流
LLM Planner/Summarizer
Agent Timeline 页面
Tool Calls 页面
```

### 优秀版

```text
Skills
Replay
RQ 异步任务
LangGraph
Docker Compose 上线
```

### 很强版

```text
RAG 历史趋势查询
MCP Server
Human Review
成本统计
失败归因统计
公开日报页面
```

---

## 29. 面试讲法

### 29.1 一分钟介绍

```text
我做了一个 OpenResearch Harness，表面上是 AI 技术趋势雷达，底层是一个 Research Agent 的运行控制系统。系统会根据用户订阅主题调用 arXiv、GitHub、RSS 等工具收集信息，再生成带来源的技术雷达报告。项目重点是自研轻量级 Agent Harness：我实现了 Tool Registry、Permission Guard、Trace Logger、Retry Policy、Verifier、Replay 和 Skills Loader，用来解决 Agent 工具调用不可控、执行过程不可观测、生成结果难验证、失败后难恢复的问题。
```

### 29.2 面试官问：是不是主要写 prompt？

回答：

```text
不是。Prompt 只是 Planner、Summarizer、Verifier 的一部分。项目更重要的是运行控制层。我记录每个 step 的输入输出、每次工具调用的参数和耗时，用 Redis 控制工具调用预算，用 Verifier 检查引用和夸大表达，用 Replay 从失败步骤恢复。所以它不是 prompt 项目，而是 Agent 工程化项目。
```

### 29.3 面试官问：为什么用 LangGraph？

回答：

```text
我不是一开始就用 LangGraph，而是先手写 Runner。等流程稳定后发现这个任务天然是状态图：plan、search、fetch、rank、summarize、verify、publish，每个节点都有状态输入输出，verify 后还有条件分支，失败后需要恢复和人工审核。所以后期引入 LangGraph 是为了解决状态流转、条件分支和持久化问题，不是为了堆技术。
```

### 29.4 面试官问：Redis 用在哪里？

回答：

```text
Redis 主要用于 Harness 控制层，包括工具调用限流、用户每日配额、任务状态缓存、热门日报缓存和分布式锁。比如同一个 run 中同一个工具最多调用 5 次，避免 Agent 重复搜索导致成本失控。
```

### 29.5 面试官问：Skills 是什么作用？

回答：

```text
Skills 是可复用的任务经验包，不是工具。比如论文分析、GitHub 项目分析、趋势报告生成和验证规则，这些任务会反复出现。我把它们沉淀成 SKILL.md + examples + schema，并通过 Harness 记录每次 Skill 使用，方便版本化和审计。
```

---

## 30. 常见坑

### 30.1 一开始功能做太大

错误：

```text
第一天就想接 arXiv、GitHub、RAG、MCP、LangGraph、React。
```

正确：

```text
第一周只跑通 fake flow 和 trace。
```

### 30.2 把工具写成普通函数

错误：

```text
随便写 search() 函数让 Agent 调。
```

正确：

```text
每个工具都有 ToolSpec、input_schema、timeout、permission、retry。
```

### 30.3 不记录中间状态

错误：

```text
失败了只知道报错，不知道哪一步错。
```

正确：

```text
每个 step 的 input_json、output_json、status、error_message 都落库。
```

### 30.4 Verifier 全靠 LLM

错误：

```text
让 LLM 自己判断是否可靠。
```

正确：

```text
规则 Verifier + LLM Verifier 结合。先检查 URL、长度、来源、新鲜度、重复、夸大词。
```

### 30.5 技术为了简历硬加

错误：

```text
因为简历想写 MCP，所以强行第一天做 MCP。
```

正确：

```text
内部工具稳定后，再把它们暴露成 MCP tools。
```

---

## 31. 推荐依赖版本策略

第一版建议固定大版本，避免每次安装出来不同结果。

```text
Python 3.11+
FastAPI
Uvicorn
SQLAlchemy 2.x
Alembic
PyMySQL 或 mysqlclient
Pydantic v2
pydantic-settings
redis-py
pytest
httpx
python-dotenv
```

第二阶段加入：

```text
rq
feedparser
requests 或 httpx
```

第三阶段加入：

```text
openai 或对应模型 SDK
langchain-core，可选
```

第七阶段加入：

```text
langgraph
```

第八阶段加入：

```text
chromadb 或 faiss-cpu
mcp
```

---

## 32. 参考资料与技术依据

以下资料用于支撑技术选型，开发前建议至少浏览一遍，不需要全部深入阅读。

1. FastAPI 官方文档：FastAPI 是基于 Python 类型提示构建 API 的现代高性能框架。  
   https://fastapi.tiangolo.com/

2. FastAPI async/await 官方说明：用于理解异步代码、并发和 IO 型请求处理。  
   https://fastapi.tiangolo.com/async/

3. Redis INCR 官方文档：包含 rate limiter 模式，适合本项目的工具调用限流。  
   https://redis.io/docs/latest/commands/incr/

4. RQ 官方文档：RQ 是基于 Redis 的简单 Python 后台任务队列。  
   https://python-rq.org/

5. Celery 官方文档：Celery 是分布式任务队列，支持实时处理和任务调度。  
   https://docs.celeryq.dev/

6. Docker Compose 官方文档：用于定义和运行多容器应用。  
   https://docs.docker.com/compose/

7. LangGraph 官方介绍：用于构建有状态 Agent 和 workflow。  
   https://www.langchain.com/langgraph

8. LangGraph Persistence 文档：说明 checkpoints、human-in-the-loop、time travel debugging、fault-tolerant execution。  
   https://docs.langchain.com/oss/python/langgraph/persistence

9. MCP 官方规范：MCP Server 可以提供 Resources、Prompts、Tools。  
   https://modelcontextprotocol.io/specification/2025-11-25

10. Anthropic Agent Skills 工程文章：Skill 是包含 SKILL.md、脚本和资源的目录，用于扩展 Agent 能力。  
    https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

11. Anthropic Skills GitHub 仓库：Skills 是 instructions、scripts、resources 组成的文件夹，Claude 会动态加载。  
    https://github.com/anthropics/skills

---

## 33. 最后提醒

你代码基础薄，不代表不能做。这个项目的正确姿势是：

```text
慢一点，一个文件一个文件写。
先 fake flow，再真实工具。
先手写 Runner，再 LangGraph。
先规则 Verifier，再 LLM Verifier。
先内部工具，再 MCP。
先有历史报告，再 RAG。
```

只要你把 agent_runs、agent_steps、tool_calls、verification_results 这几张表真正跑通，并能在前端展示一次 Agent 的完整运行轨迹，这个项目就已经不是普通套壳项目了。

项目成功的标准不是用了多少技术，而是你能不能回答：

```text
这个技术解决了什么真实问题？
不用它会怎样？
我在哪里遇到了问题？
我是怎么定位和解决的？
```

做到这一点，你就真的学会了。
