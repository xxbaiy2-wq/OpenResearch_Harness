'''
Agent 执行是一个多步骤流程（planner → search → fetch → rank → summarize → verify → publish）。每一步的输出是下一步的输入，所以需要一个地方临时存放中间结果。

类比：就像工厂流水线，上一个工序做好的半成品放到传送带上，下一个工序接着做。

状态字段解释：

字段	什么时候写入	下一步怎么用
topic	创建 run 时传入	planner 用它生成搜索计划
plan	planner 步骤完成后	search 步骤用 plan 里的 query 去搜索
items	search 步骤完成后	rank 步骤对 items 排序
ranked_items	rank 步骤完成后	summarize 用它生成报告
draft_report	summarize 步骤完成后	verify 检查 draft_report 的质量
verification	verify 步骤完成后	runner 根据 verification 决定走 publish 还是重跑
final_report	publish 步骤完成后	写入数据库 daily_reports 表

'''

# d:\OpenResearch_Harness\backend\app\harness\state_manager.py
# 为什么用 dict 而不是 class？

# 用 dict	用 class
# 简单、灵活、新增字段不用改类定义	需要预先定义所有字段
# 面试可以说"第一版用 dict 验证流程，后续可以迁移到 TypedDict 或 Pydantic"	一开始就过度设计

class StateManager:
    """管理一次 run 的中间状态。用 dict 存储，简单直接。"""

    def __init__(self):
        self.state: dict = {}

    def init_state(self, task_id: int, topic: str) -> None:
        """初始化状态，每次新 run 调用一次。"""
        self.state = {
            "task_id": task_id,
            "topic": topic,
            "plan": None,           # planner 输出
            "items": [],            # search 输出
            "ranked_items": [],     # rank 输出
            "draft_report": None,   # summarize 输出
            "verification": None,   # verify 输出
            "final_report": None,   # publish 输出
        }

    def get(self, key: str):
        """读取某个状态值。"""
        return self.state.get(key)

    def set(self, key: str, value) -> None:
        """更新某个状态值。"""
        self.state[key] = value

    def get_all(self) -> dict:
        """获取完整状态，用于 finish_run 写入 output_json。"""
        return dict(self.state)


# 全局实例
state_manager = StateManager()
