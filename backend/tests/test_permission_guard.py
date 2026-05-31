'''
测试哪些场景：

场景	预期
工具存在且未超限	通过
工具不存在	抛出 PermissionDenied
同一工具调用超过 5 次	第 6 次抛出 PermissionDenied
总调用超过 20 次	第 21 次抛出 PermissionDenied
reset 后计数清零	重新计数
'''
# d:\OpenResearch_Harness\backend\tests\test_permission_guard.py

import pytest
from app.harness.permission_guard import PermissionGuard, PermissionDenied
from app.harness.tool_registry import ToolRegistry, ToolSpec
from app.tools.base import BaseTool


class FakeTool(BaseTool):
    name = "fake_tool"
    description = "test"

    def run(self, input_data):
        return {}


@pytest.fixture
def guard():
    """每个测试用一个干净的 guard，并注册一个假工具。"""
    from app.harness.tool_registry import tool_registry
    tool_registry.register(FakeTool(), ToolSpec(
        name="fake_tool", description="test",
        input_schema={}, timeout_seconds=10, max_retries=2,
    ))
    return PermissionGuard()


def test_check_passes_for_registered_tool(guard):
    """工具存在时 check 不应抛异常。"""
    guard.check("fake_tool")  # 不抛异常即通过


def test_check_fails_for_unknown_tool(guard):
    """工具不存在时应抛出 PermissionDenied。"""
    with pytest.raises(PermissionDenied, match="not found"):
        guard.check("nonexistent_tool")


def test_check_fails_after_max_calls_per_tool(guard):
    """同一工具调用超过 5 次后应被拒绝。"""
    for i in range(5):
        guard.check("fake_tool")
        guard.record_call("fake_tool")

    with pytest.raises(PermissionDenied, match="exceeded max calls"):
        guard.check("fake_tool")


def test_check_fails_after_max_total_calls(guard):
    """总调用超过 20 次后应被拒绝。"""
    from app.harness.tool_registry import tool_registry

    # 注册 5 个假工具，这样轮流调用不会触发单工具限制
    for i in range(5):
        class MultiTool(BaseTool):
            name = f"tool_{i}"
            description = "test"
            def run(self, input_data):
                return {}
        tool_registry.register(MultiTool(), ToolSpec(
            name=f"tool_{i}", description="test",
            input_schema={}, timeout_seconds=10, max_retries=2,
        ))

    tools = [f"tool_{i}" for i in range(5)]

    # 每个工具调 4 次 = 20 次，刚好不超
    for i in range(20):
        tool_name = tools[i % 5]
        guard.check(tool_name)
        guard.record_call(tool_name)

    # 第 21 次应该失败
    with pytest.raises(PermissionDenied, match="exceeded max"):
        guard.check("tool_0")



def test_reset_clears_counts(guard):
    """reset 后计数清零，可以重新调用。"""
    for i in range(5):
        guard.check("fake_tool")
        guard.record_call("fake_tool")

    guard.reset()

    # reset 后应该又能正常调用
    guard.check("fake_tool")
    guard.record_call("fake_tool")
