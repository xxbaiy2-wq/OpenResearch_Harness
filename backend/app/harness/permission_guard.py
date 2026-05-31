from app.harness.tool_registry import tool_registry


class PermissionDenied(Exception):
    """权限检查不通过时抛出"""
    pass


class PermissionGuard:
    """工具调用前的安全检查：工具是否存在、调用次数是否超限。"""

    MAX_CALLS_PER_RUN = 20       # 一次 run 最多调 20 次工具
    MAX_CALLS_PER_TOOL = 5       # 同一个工具最多调 5 次

    def __init__(self):
        self._tool_counts: dict[str, int] = {}  # {tool_name: 调用次数}

    def check(self, tool_name: str) -> None:
        # 1. 工具必须存在
        try:
            tool_registry.get_tool(tool_name)
        except ValueError:
            raise PermissionDenied(f"Tool '{tool_name}' not found in registry")

        # 2. 单个工具调用次数限制
        count = self._tool_counts.get(tool_name, 0)
        if count >= self.MAX_CALLS_PER_TOOL:
            raise PermissionDenied(
                f"Tool '{tool_name}' exceeded max calls ({self.MAX_CALLS_PER_TOOL})"
            )

        # 3. 总调用次数限制
        total = sum(self._tool_counts.values())
        if total >= self.MAX_CALLS_PER_RUN:
            raise PermissionDenied(
                f"Total tool calls exceeded max ({self.MAX_CALLS_PER_RUN})"
            )

    def record_call(self, tool_name: str) -> None:
        """工具调用成功后记录次数"""
        self._tool_counts[tool_name] = self._tool_counts.get(tool_name, 0) + 1

    def reset(self) -> None:
        """每次新 run 开始时清零"""
        self._tool_counts.clear()
