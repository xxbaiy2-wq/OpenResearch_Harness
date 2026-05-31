'''
从 GitHub 搜索开源项目，获取仓库名、描述、星标数、语言等信息。
'''
# d:\OpenResearch_Harness\backend\app\tools\github_tool.py
# urllib.parse.quote 是把中文或空格转成 URL 安全的编码，比如 "agent harness" → "agent%20harness"。
import urllib.request
import json
from typing import Any

from app.tools.base import BaseTool


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


class GithubTool(BaseTool):
    """从 GitHub 搜索开源仓库。"""

    name = "github_search"
    description = "搜索 GitHub 开源仓库，返回名称、描述、星标数和链接"

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 5)

        # 1. 构造请求
        params = f"q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page={max_results}"
        url = f"{GITHUB_SEARCH_URL}?{params}"

        request = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github.v3+json",
            # "Authorization": "Bearer YOUR_TOKEN",  # 有 token 时取消注释
        })

        # 2. 发起请求
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        # 3. 提取结果
        items = []
        for repo in data.get("items", []):
            items.append({
                "name": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "description": repo.get("description", ""),
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language", ""),
                "updated_at": (repo.get("updated_at", "") or "")[:10],
                "source_type": "github",
            })

        return {"items": items}

