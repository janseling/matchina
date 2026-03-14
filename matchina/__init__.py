"""
Matchina: 中国企业中英文名称对齐匹配库

快速匹配企业名称，支持中英文、别名、模糊搜索。

Example:
    >>> from matchina import resolve
    >>> result = resolve("华为")
    >>> print(result[0].name_cn)
    华为技术有限公司
"""

from typing import Optional

from .core.matcher import EntityMatcher, MatchResult
from .models.entity import Entity

__version__ = "0.1.0"
__all__ = ["resolve", "search", "resolve_batch", "EntityMatcher", "MatchResult", "Entity"]

# 全局 matcher 实例（懒加载）
_matcher: "Optional[EntityMatcher]" = None


def _get_matcher() -> EntityMatcher:
    """获取全局 matcher 实例（懒加载）"""
    global _matcher
    if _matcher is None:
        _matcher = EntityMatcher()
    return _matcher


def resolve(name: str, top_k: int = 5) -> list[MatchResult]:
    """
    快速匹配企业名称

    Args:
        name: 企业名称（中文或英文）
        top_k: 返回结果数量，默认 5

    Returns:
        匹配结果列表，按置信度降序排列

    Example:
        >>> resolve("阿里巴巴")
        [MatchResult(entity_id='...', name_cn='阿里巴巴集团控股有限公司', confidence=1.0)]

        >>> resolve("Tencent")
        [MatchResult(entity_id='...', name_cn='腾讯控股有限公司', confidence=1.0)]
    """
    return _get_matcher().match(name, top_k)


def search(query: str, limit: int = 10) -> list[MatchResult]:
    """
    模糊搜索企业名称

    Args:
        query: 搜索关键词
        limit: 返回结果数量，默认 10

    Returns:
        匹配结果列表

    Example:
        >>> search("科技")
        [MatchResult(name_cn='华为技术有限公司', ...), ...]
    """
    return _get_matcher().search(query, limit)


def resolve_batch(names: list[str], top_k: int = 5) -> dict[str, list[MatchResult]]:
    """
    批量匹配企业名称

    Args:
        names: 企业名称列表
        top_k: 每个名称返回结果数量，默认 5

    Returns:
        {名称：匹配结果列表}

    Example:
        >>> resolve_batch(["腾讯", "百度", "华为"])
        {"腾讯": [...], "百度": [...], "华为": [...]}
    """
    return {name: resolve(name, top_k) for name in names}
