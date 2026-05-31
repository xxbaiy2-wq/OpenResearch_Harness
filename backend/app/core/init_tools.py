# d:\OpenResearch_Harness\backend\app\core\init_tools.py

from app.harness.tool_registry import tool_registry, ToolSpec
from app.tools.arxiv_tool import ArxivTool
from app.tools.github_tool import GithubTool
from app.tools.rss_tool import RSSTool


def register_default_tools():
    """注册所有内置工具到全局 tool_registry。"""

    arxiv = ArxivTool()
    tool_registry.register(arxiv, ToolSpec(
        name=arxiv.name,
        description=arxiv.description,
        input_schema={"query": "str", "max_results": "int"},
        timeout_seconds=15,
        max_retries=2,
    ))

    github = GithubTool()
    tool_registry.register(github, ToolSpec(
        name=github.name,
        description=github.description,
        input_schema={"query": "str", "max_results": "int"},
        timeout_seconds=15,
        max_retries=2,
    ))

    rss = RSSTool()
    tool_registry.register(rss, ToolSpec(
        name=rss.name,
        description=rss.description,
        input_schema={"feed_url": "str", "max_results": "int"},
        timeout_seconds=15,
        max_retries=1,
    ))
