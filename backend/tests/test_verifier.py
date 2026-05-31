#verifier 是纯逻辑，不依赖数据库、不依赖网络，最容易测试
# d:\OpenResearch_Harness\backend\tests\test_verifier.py

import pytest
from app.harness.verifier import Verifier


@pytest.fixture
def verifier():
    return Verifier()


def test_verifier_passes_valid_report(verifier):
    """正常报告应该通过验证。"""
    content = "这是一个正常的技术报告。" * 50  # 约250字
    content += "更多内容来凑够300字。继续补充内容。更多内容。"
    items = [
        {"title": "A", "url": "https://a.com"},
        {"title": "B", "url": "https://b.com"},
        {"title": "C", "url": "https://c.com"},
    ]
    result = verifier.verify(content, items)
    assert result.passed is True
    assert result.score == 100
    assert result.problems == []


def test_verifier_rejects_empty_report(verifier):
    """空报告应该被拒绝。"""
    result = verifier.verify("", [])
    assert result.passed is False
    assert any(p["type"] == "empty_report" for p in result.problems)


def test_verifier_rejects_short_report(verifier):
    """长度不足300字应该被拒绝。"""
    content = "太短了"  # 只有几个字
    items = [
        {"title": "A", "url": "https://a.com"},
        {"title": "B", "url": "https://b.com"},
        {"title": "C", "url": "https://c.com"},
    ]
    result = verifier.verify(content, items)
    assert result.passed is False
    assert any(p["type"] == "too_short" for p in result.problems)


def test_verifier_rejects_insufficient_items(verifier):
    """items 不足 3 个应该被拒绝。"""
    content = "这是一个正常的技术报告。" * 50
    items = [{"title": "A", "url": "https://a.com"}]  # 只有1个
    result = verifier.verify(content, items)
    assert result.passed is False
    assert any(p["type"] == "insufficient_items" for p in result.problems)


def test_verifier_rejects_missing_url(verifier):
    """item 缺少 URL 应该被拒绝。"""
    content = "这是一个正常的技术报告。" * 50
    items = [
        {"title": "A", "url": "https://a.com"},
        {"title": "B", "url": None},       # 没有 URL
        {"title": "C", "url": "https://c.com"},
    ]
    result = verifier.verify(content, items)
    assert result.passed is False
    assert any(p["type"] == "missing_url" for p in result.problems)


def test_verifier_rejects_overclaim(verifier):
    """报告含夸大词应该被拒绝。"""
    content = "这项技术是革命性的，将彻底取代现有方案。" * 30
    items = [
        {"title": "A", "url": "https://a.com"},
        {"title": "B", "url": "https://b.com"},
        {"title": "C", "url": "https://c.com"},
    ]
    result = verifier.verify(content, items)
    assert result.passed is False
    assert any(p["type"] == "overclaim" for p in result.problems)
