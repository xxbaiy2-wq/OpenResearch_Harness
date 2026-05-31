# 工具的"登记簿"
from pydantic import BaseModel
from typing import Any
from app.tools.base import BaseTool

# 工具本身只管执行，工具的权限、超时、重试策略由 Spec 管，职责分离
class ToolSpec(BaseModel):
    """工具的元信息：描述、权限、超时、重试策略。"""
    name: str
    description: str
    input_schema: dict
    permission_level: str = "normal"
    timeout_seconds: int = 10
    max_retries: int = 2


# 所有地方共享同一个注册中心，不用传来传去
class ToolRegistry:
    """工具注册中心。所有工具在这里登记，Runner 从这里查找。"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._specs: dict[str, ToolSpec] = {}

    def register(self, tool: BaseTool, spec: ToolSpec):
        self._tools[tool.name] = tool
        self._specs[tool.name] = spec

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        return self._tools[name]

    def get_spec(self, name: str) -> ToolSpec:
        if name not in self._specs:
            raise ValueError(f"Spec for tool '{name}' not found")
        return self._specs[name]

    def list_tools(self) -> list[ToolSpec]:
        return list(self._specs.values())


# 全局实例，整个项目共享一个注册中心
tool_registry = ToolRegistry()
