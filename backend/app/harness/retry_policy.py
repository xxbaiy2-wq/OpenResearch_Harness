# 工具调用或某个步骤失败了，该不该重试？不是所有失败都该重试——乱重试会浪费成本、掩盖真正的问题。
'''
重试规则设计：

错误类型	是否重试	为什么
超时（TimeoutError）	✅ 是	外部服务临时不稳定，重试可能成功
LLM 输出格式错误（JSONParseError）	✅ 是	LLM 偶尔输出不规范，重试可能正常
验证不通过（VerifierFailed）	✅ 是，最多1次	回到 summarize 步骤重写
工具不存在（ToolNotFound）	❌ 否	配置错误，重试也没用
权限拒绝（PermissionDenied）	❌ 否	重试不会改变权限
'''
# d:\OpenResearch_Harness\backend\app\harness\retry_policy.py


class RetryDecision:
    """重试决策的结果。"""

    def __init__(self, should_retry: bool, reason: str = ""):
        self.should_retry = should_retry
        self.reason = reason


class RetryPolicy:
    """判断一次失败是否应该重试。"""

    # 允许重试的错误类型
    RETRYABLE_ERRORS = {
        "TimeoutError": "外部服务临时不可用，重试可能成功",
        "JSONParseError": "LLM 输出格式错误，重试可能正常",
        "ConnectionError": "网络连接问题，重试可能恢复",
    }

    # 验证失败的特殊处理：可以重跑 summarize
    VERIFY_FAIL_MAX_RETRY = 1

    def __init__(self):
        self._verify_retry_count: dict[int, int] = {}  # {run_id: 已重试次数}

    def should_retry(self, error_type: str, run_id: int | None = None) -> RetryDecision:
        """核心方法：给定错误类型和 run_id，返回是否应该重试。"""

        # 1. 可重试的错误类型
        if error_type in self.RETRYABLE_ERRORS:
            return RetryDecision(
                should_retry=True,
                reason=self.RETRYABLE_ERRORS[error_type],
            )

        # 2. 验证失败的特殊逻辑
        if error_type == "VerifierFailed":
            if run_id is None:
                return RetryDecision(False, "缺少 run_id，无法判断")
            count = self._verify_retry_count.get(run_id, 0)
            if count < self.VERIFY_FAIL_MAX_RETRY:
                self._verify_retry_count[run_id] = count + 1
                return RetryDecision(
                    should_retry=True,
                    reason=f"验证失败第{count + 1}次重试，回到 summarize 重写",
                )
            return RetryDecision(
                False, f"验证失败已重试 {self.VERIFY_FAIL_MAX_RETRY} 次，不再重试",
            )

        # 3. 其他错误一律不重试
        return RetryDecision(False, f"错误类型 '{error_type}' 不在可重试列表中")


# 全局实例
retry_policy = RetryPolicy()
