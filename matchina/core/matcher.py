"""
企业实体匹配器

整合四层匹配策略，按置信度降序返回结果。
"""

from typing import Optional

from ..data.storage import DataStorage
from ..models.entity import MatchResult
from .strategies import AliasStrategy, ExactStrategy, FuzzyStrategy, RuleStrategy


class EntityMatcher:
    """
    企业实体匹配器

    使用四层匹配策略：
    1. ExactStrategy: 精确匹配（置信度 1.0）
    2. AliasStrategy: 别名查表（置信度 0.95）
    3. RuleStrategy: 规则匹配（置信度 0.85）
    4. FuzzyStrategy: 模糊匹配（置信度 0.6-0.8）

    Example:
        >>> matcher = EntityMatcher()
        >>> results = matcher.match("华为")
        >>> print(results[0].name_cn)
        华为技术有限公司
    """

    def __init__(self, db_path: Optional[str] = None, fuzzy_threshold: float = 0.75):
        """
        初始化匹配器

        Args:
            db_path: 数据库路径，默认使用包内数据
            fuzzy_threshold: 模糊匹配阈值，默认 0.75
        """
        self.storage = DataStorage(db_path)

        # 初始化策略（按优先级排序）
        self.strategies = [
            ExactStrategy(),
            AliasStrategy(),
            RuleStrategy(),
            FuzzyStrategy(threshold=fuzzy_threshold),
        ]

    def match(self, query: str, top_k: int = 5) -> list[MatchResult]:
        """
        匹配企业名称

        Args:
            query: 企业名称（中文或英文）
            top_k: 返回结果数量，默认 5

        Returns:
            匹配结果列表，按置信度降序排列
        """
        if not query or not query.strip():
            return []

        # 尝试各策略（按优先级）
        for strategy in self.strategies:
            result = strategy.match(query.strip(), self.storage)
            if result:
                return [result]

        # 无匹配，返回空列表
        return []

    def search(self, query: str, limit: int = 10) -> list[MatchResult]:
        """
        模糊搜索企业名称

        Args:
            query: 搜索关键词
            limit: 返回结果数量，默认 10

        Returns:
            匹配结果列表
        """
        if not query or not query.strip():
            return []

        # 使用模糊搜索
        entities = self.storage.search_entities(query.strip(), limit)

        results = []
        for entity in entities:
            results.append(
                MatchResult(
                    entity_id=entity.id,
                    name_cn=entity.name_cn,
                    name_en=entity.name_en,
                    confidence=0.6,  # 搜索结果默认置信度较低
                    aliases=entity.aliases,
                    match_type="search",
                )
            )

        return results

    def close(self) -> None:
        """关闭数据库连接"""
        self.storage.close()

    def __enter__(self) -> "EntityMatcher":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
