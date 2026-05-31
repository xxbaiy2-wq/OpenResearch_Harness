# 所有工具的统一模板
from abc import ABC, abstractmethod
# Abstract Base Class，抽象基类
from typing import Any


class BaseTool(ABC):
    """所有工具的基类。定义统一接口，Runner 不需要关心工具内部怎么实现。"""

    name: str
    description: str

    # "子类必须自己实现这个方法"
    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行工具，接收输入字典，返回输出字典。"""
        pass

'''
为什么需要这个？（八股考点：多态）
Runner 调用工具时不需要知道具体是 arXiv 还是 GitHub：
tool = tool_registry.get_tool("fake_search")
result = tool.run({"topic": "Agent Harness"})  # 任何工具都这样调用

'''