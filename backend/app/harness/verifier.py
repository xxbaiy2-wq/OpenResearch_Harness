'''
报告生成后，不能直接发布。需要检查报告质量——长度够不够、有没有来源链接、有没有夸大用词。
检查规则：

规则	要求	不通过的问题类型
报告不能为空	content ≠ ""	empty_report
报告长度 ≥ 300 字	len(content) ≥ 300	too_short
至少包含 3 个 research items	len(items) ≥ 3	insufficient_items
每个 item 必须有 URL	item.url ≠ None	missing_url
不能有夸大词	不含"颠覆""革命性"等	overclaim
'''

# d:\OpenResearch_Harness\backend\app\harness\verifier.py

# 夸大词列表
OVERCLAIM_WORDS = ["颠覆", "彻底取代", "革命性", "史无前例", "完全改变"]


class VerificationResult:
    """验证结果。"""

    def __init__(self, passed: bool, score: int, problems: list[dict], action: str):
        self.passed = passed       # 是否通过
        self.score = score         # 0-100 分
        self.problems = problems   # 不通过的具体原因列表
        self.action = action       # 建议操作: "pass" / "revise" / "human_review"

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "score": self.score,
            "problems": self.problems,
            "action": self.action,
        }


class Verifier:
    """基于规则检查报告质量。"""

    def verify(self, report_content: str, items: list[dict]) -> VerificationResult:
        problems: list[dict] = []
        score = 100

        # 规则1：报告不能为空
        if not report_content or not report_content.strip():
            problems.append({"type": "empty_report", "message": "报告内容为空"})
            score -= 50

        # 规则2：长度 ≥ 300 字
        if len(report_content) < 300:
            problems.append({
                "type": "too_short",
                "message": f"报告长度 {len(report_content)} 字，不足 300 字",
            })
            score -= 20

        # 规则3：至少 3 个 items
        if len(items) < 3:
            problems.append({
                "type": "insufficient_items",
                "message": f"只有 {len(items)} 条内容，不足 3 条",
            })
            score -= 20

        # 规则4：每个 item 必须有 URL
        for i, item in enumerate(items):
            if not item.get("url"):
                problems.append({
                    "type": "missing_url",
                    "message": f"第 {i + 1} 条内容缺少来源 URL",
                })
                score -= 10

        # 规则5：不能有夸大词
        for word in OVERCLAIM_WORDS:
            if word in report_content:
                problems.append({
                    "type": "overclaim",
                    "message": f"报告中包含夸大词：'{word}'",
                })
                score -= 15
                break  # 有一个夸大词就够了，不重复扣

        score = max(score, 0)  # 最低 0 分

        passed = len(problems) == 0
        if not passed:
            action = "revise"
        else:
            action = "pass"

        return VerificationResult(
            passed=passed,
            score=score,
            problems=problems,
            action=action,
        )


# 全局实例
verifier = Verifier()
