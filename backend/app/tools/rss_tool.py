'''
从 RSS 订阅源（技术博客、新闻站）抓取最新文章。比如订阅 Hacker News、机器之心、ArXiv cs.AI 分类等。

RSS 是什么？（八股考点）

RSS 是一种标准化的"内容更新通知格式"。
网站维护者发布一篇文章，会同时更新一个 XML 文件（RSS feed）。
RSS 阅读器定期拉取这个文件，就知道有什么新内容了。

网站发布新文章
    ↓
RSS feed（XML 文件）自动更新
    ↓
我们的 RSS Tool 拉取并解析


'''
# d:\OpenResearch_Harness\backend\app\tools\rss_tool.py

from typing import Any

import feedparser

from app.tools.base import BaseTool


class RSSTool(BaseTool):
    """从 RSS 订阅源抓取最新文章。"""

    name = "rss_fetch"
    description = "从 RSS 订阅源获取最新文章"

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        feed_url = input_data.get("feed_url", "")
        max_results = input_data.get("max_results", 10)

        # 1. feedparser 自动处理 HTTP 请求 + XML 解析
        feed = feedparser.parse(feed_url)

        # 2. 检查是否解析成功
        if feed.bozo and not feed.entries:
            return {
                "items": [],
                "error": f"RSS 解析失败: {feed.bozo_exception}",
            }

        # 3. 提取文章条目
        items = []
        for entry in feed.entries[:max_results]:
            items.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", "")[:500],  # 摘要截断到 500 字
                "published_at": entry.get("published", "")[:10],
                "source_type": "rss",
            })

        return {"items": items}
