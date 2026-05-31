'''
测试哪些场景：

场景	预期
注册工具后能 get_tool 找到	返回工具实例
查找不存在的工具	抛出 ValueError
get_spec 返回正确的 ToolSpec	spec.name 匹配
list_tools 返回所有已注册工具	数量正确
'''
# d:\OpenResearch_Harness\backend\tests\test_tool_registry.py

import pytest
from app.harness.tool_registry import ToolRegistry, ToolSpec
from app.tools.base import BaseTool


class FakeTool(BaseTool):
    name = "fake_tool"
    description = "A fake tool for testing"

    def run(self, input_data):
        return {"result": "fake"}


@pytest.fixture
def registry():
    """每个测试用一个干净的 registry。"""
    reg = ToolRegistry()
    tool = FakeTool()
    reg.register(tool, ToolSpec(
        name=tool.name,
        description=tool.description,
        input_schema={"query": "str"},
        timeout_seconds=10,
        max_retries=2,
    ))
    return reg


def test_get_tool_returns_registered_tool(registry):
    """注册后能通过 get_tool 找到。"""
    tool = registry.get_tool("fake_tool")
    assert tool.name == "fake_tool"
    assert tool.run({"query": "test"}) == {"result": "fake"}


def test_get_unknown_tool_raises_error(registry):
    """查找不存在的工具应抛出 ValueError。"""
    with pytest.raises(ValueError, match="not found"):
        registry.get_tool("nonexistent_tool")


def test_get_spec_returns_correct_metadata(registry):
    """get_spec 返回工具的元信息。"""
    spec = registry.get_spec("fake_tool")
    assert spec.name == "fake_tool"
    assert spec.timeout_seconds == 10
    assert spec.max_retries == 2


def test_list_tools_returns_all_tools(registry):
    """list_tools 返回所有已注册工具。"""
    tools = registry.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "fake_tool"
