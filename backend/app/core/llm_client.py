'''
项目里有多个地方要调 LLM（Planner、Summarizer、Verifier）。
如果每个地方都自己写 OpenAI(api_key=..., base_url=...)，
改配置时要改好几个地方。封装成一个客户端，所有地方统一调用。
'''
# d:\OpenResearch_Harness\backend\app\core\llm_client.py

from openai import OpenAI
from app.core.config import settings


def get_llm_client() -> OpenAI:
    """创建 LLM 客户端。统一从 settings 读配置。"""
    return OpenAI(
        api_key=settings.mimo_api_key,
        base_url=settings.mimo_base_url,
    )


def call_llm(messages: list[dict], temperature: float = 0.3, max_tokens: int = 8000) -> str:
    """调用 LLM，返回文本结果。所有 LLM 调用都走这里。"""
    client = get_llm_client()
    response = client.chat.completions.create(
        model=settings.mimo_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
