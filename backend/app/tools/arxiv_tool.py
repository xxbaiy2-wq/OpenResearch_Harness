'''
从 arXiv 论文库搜索相关论文，获取标题、摘要、作者、链接等信息。

arXiv API 是什么？（八股考点）

arXiv 提供了一个公开的 REST API，不需要注册、不需要 token，用 HTTP 请求就能搜论文：

为什么用 urllib 而不是 requests？

你可能会问，requests 更好用啊。
是的，但 urllib 是 Python 标准库，不需额外安装
项目第一版追求精简，能少一个依赖就少一个。

'''
# d:\OpenResearch_Harness\backend\app\tools\arxiv_tool.py

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

from app.tools.base import BaseTool


ARXIV_API_URL = "http://export.arxiv.org/api/query"

# XML 命名空间，arXiv 返回的 XML 用这个命名空间
ATOM_NS = "http://www.w3.org/2005/Atom"


class ArxivTool(BaseTool):
    """从 arXiv 搜索论文。"""

    name = "arxiv_search"
    description = "搜索 arXiv 论文，返回标题、摘要、作者和链接"

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 5)

        # 1. 构造请求 URL
        # 参数拼成 URL 查询字符串
        # 如 search_query=all:agent+harness&max_results=5
        params = urllib.parse.urlencode({
            "search_query": f"all:{query}",
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        })
        url = f"{ARXIV_API_URL}?{params}"

        # 2. 发起 HTTP 请求
        with urllib.request.urlopen(url, timeout=60) as response:
            xml_data = response.read().decode("utf-8")

        # 3. 解析 XML
        root = ET.fromstring(xml_data)
        items = []

        for entry in root.findall(f"{{{ATOM_NS}}}entry"):
            # 提取论文 ID（arxiv URL）
            arxiv_id_el = entry.find(f"{{{ATOM_NS}}}id")
            arxiv_url = arxiv_id_el.text if arxiv_id_el is not None else ""

            # 提取标题（去掉多余的换行和空格）
            title_el = entry.find(f"{{{ATOM_NS}}}title")
            title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""

            # 提取摘要
            summary_el = entry.find(f"{{{ATOM_NS}}}summary")
            abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None else ""

            # 提取作者列表
            authors = []
            for author_el in entry.findall(f"{{{ATOM_NS}}}author"):
                name_el = author_el.find(f"{{{ATOM_NS}}}name")
                if name_el is not None:
                    authors.append(name_el.text)

            # 提取发布时间
            published_el = entry.find(f"{{{ATOM_NS}}}published")
            published_at = ""
            if published_el is not None and published_el.text:
                try:
                    dt = datetime.fromisoformat(published_el.text.replace("Z", "+00:00"))
                    published_at = dt.strftime("%Y-%m-%d")
                except ValueError:
                    published_at = published_el.text[:10]

            items.append({
                "title": title,
                "url": arxiv_url,
                "authors": authors,
                "abstract": abstract,
                "published_at": published_at,
                "source_type": "arxiv",
            })

        return {"items": items}
