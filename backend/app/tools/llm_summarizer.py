'''
原来的 summarizer 是模板拼接，生成的报告像流水账。LLM Summarizer 让模型理解每个 item 的价值，生成有结构、有洞察的技术报告。
'''
# d:\OpenResearch_Harness\backend\app\tools\llm_summarizer.py

from pydantic import BaseModel, Field
from app.core.llm_client import call_llm
from datetime import datetime


class ItemSummary(BaseModel):
    title: str = Field(description="项目或论文名称")
    url: str = Field(default="", description="链接")
    source_type: str = Field(default="", description="来源类型")
    summary: str = Field(description="一句话摘要")
    why_it_matters: str = Field(description="为什么值得关注")



class Section(BaseModel):
    heading: str = Field(description="板块标题")
    content: str = Field(description="完整段落内容，200-400字的连贯文章")


class ReportOutput(BaseModel):
    title: str = Field(description="文章标题")
    date: str = Field(default="", description="日期")
    sections: list[Section] = Field(default=[], description="文章板块")



SUMMARIZER_SYSTEM_PROMPT = """你是一个资深技术博主，每天写一篇「每日5分钟了解前沿」技术速递。

要求：
1. 把收集到的资料融合成一篇流畅的中文文章，不要罗列式输出
2. 开头写一段导语（100字左右），说明今天这个领域的动态概况
3. 每个重要项目/论文单独一个小节，用自然段落介绍，包含技术细节和实际价值
4. 结尾写一段总结展望（100字左右）
5. 语言专业但可读，面向有2-3年经验的开发者
6. 不要用"颠覆""革命性"等夸大词
7. JSON 的 key 必须用英文（title, date, total_items, sections, heading, items, summary, why_it_matters）
7. 只输出 JSON：{"title": "文章标题", "date": "日期", "sections": [{"heading": "板块标题", "content": "完整段落内容"}]}

注意：sections里的content是完整的中文段落，不是要点列表。"""


class LLMSummarizer:
    name = "llm_summarizer"
    description = "用 LLM 从收集到的资料生成结构化报告"

    def run(self, input_data: dict) -> dict:
        items = input_data.get("items", [])
        topic = input_data.get("topic", "")

        # 把 items 压缩成文本，避免 token 超限
        items_text = ""
        for i, item in enumerate(items[:10], 1):
            title = item.get("title") or item.get("name") or "无标题"
            url = item.get("url", "")
            summary = item.get("abstract") or item.get("description") or item.get("summary", "")
            source = item.get("source_type", "unknown")
            items_text += f"\n[{i}] {title}\n来源: {source}\n链接: {url}\n摘要: {summary[:300]}\n"

        messages = [
            {"role": "system", "content": SUMMARIZER_SYSTEM_PROMPT},
            {"role": "user", "content": f"主题：{topic}\n\n收集到以下 {len(items)} 条资料：\n{items_text}\n\n请生成结构化报告 JSON。"},
        ]

        raw_output = call_llm(messages, temperature=0.4, max_tokens=8000)

        import json
        try:
            data = json.loads(raw_output)
            result = ReportOutput(**data)
            # 补上 LLM 没输出的字段
            if not result.date:
                result.date = datetime.now().strftime("%Y-%m-%d")
            if not result.total_items:
                result.total_items = len(items)
            return result.model_dump()

        except (json.JSONDecodeError, Exception) as e:
            # 降级：生成最简单的文本报告
            print(f"DEBUG: {type(e).__name__}: {e}")  # 加这一行调试 LLM 输出错误
            sections_text = "\n".join(
                f"- {item.get('title') or item.get('name', '无标题')}: {item.get('url', '')}"
                for item in items[:10]
            )
            return {
                "title": f"{topic} 技术雷达",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_items": len(items),
                "raw_content": f"LLM 解析失败，以下是原始列表：\n{sections_text}",
            }


llm_summarizer = LLMSummarizer()
