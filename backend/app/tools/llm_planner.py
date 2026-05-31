'''
原来的 planner 是硬编码的：
[topic, topic + " tutorial", topic + " 2026"]。
太死板，不会根据 topic 的实际情况拆分搜索角度。

LLM Planner 让模型自己思考：

这个 topic 涉及哪些子领域？
应该从哪些角度搜索？
该搜哪些来源？
输出结构：

用 Pydantic 约束 LLM 输出——这是面试关键点：LLM 输出不可信，必须校验。

'''
# d:\OpenResearch_Harness\backend\app\tools\llm_planner.py

from pydantic import BaseModel, Field
from app.core.llm_client import call_llm


class PlannerOutput(BaseModel):
    """LLM Planner 的结构化输出，用 Pydantic 校验。"""
    topic: str = Field(description="研究主题")
    queries: list[str] = Field(description="搜索关键词列表，3-5 个")
    sources: list[str] = Field(description="数据来源列表，可选 arxiv/github/rss")
    reasoning: str = Field(description="为什么选择这些搜索角度")


PLANNER_SYSTEM_PROMPT = """你是一个技术研究助手。你的任务是分析用户给定的主题，生成研究计划。

要求：
1. 把主题拆解成 3-5 个不同的搜索角度
2. 每个搜索角度是一个具体的关键词
3. 选择合适的数据来源（arxiv/github/rss）
4. 简要说明你为什么选择这些角度

只输出 JSON，不要输出其他内容。"""


class LLMPlanner:
    name = "llm_planner"
    description = "用 LLM 生成研究计划"

    def run(self, input_data: dict) -> dict:
        topic = input_data.get("topic", "")

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": f"主题：{topic}\n\n请生成研究计划，输出 JSON 格式：{{'topic': '...', 'queries': [...], 'sources': [...], 'reasoning': '...'}}"},
        ]

        raw_output = call_llm(messages, temperature=0.3, max_tokens=8000)

        # 用 Pydantic 校验输出
        import json
        try:
            data = json.loads(raw_output)
            result = PlannerOutput(**data)
            return result.model_dump()
        except (json.JSONDecodeError, Exception) as e:
            # LLM 输出不合法，降级到硬编码方案
            return {
                "topic": topic,
                "queries": [topic, f"{topic} tutorial", f"{topic} 2026"],
                "sources": ["arxiv", "github"],
                "reasoning": "LLM 输出解析失败，使用降级方案",
            }


llm_planner = LLMPlanner()
