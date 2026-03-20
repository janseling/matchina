"""
匹配策略实现

四层匹配：
1. ExactStrategy: 精确匹配（置信度 1.0）
2. AliasStrategy: 别名查表（置信度 0.95）
3. RuleStrategy: 规则匹配（置信度 0.85）
4. FuzzyStrategy: 模糊匹配（置信度 0.6-0.8）
"""

from abc import ABC, abstractmethod

from ..data.storage import DataStorage
from ..models.entity import MatchResult
from ..utils.normalizer import normalize, normalize_for_comparison


class BaseStrategy(ABC):
    """匹配策略基类"""

    @abstractmethod
    def match(self, query: str, storage: DataStorage) -> MatchResult | None:
        """
        执行匹配

        Args:
            query: 待匹配名称
            storage: 数据存储

        Returns:
            匹配结果，无匹配返回 None
        """
        pass


class ExactStrategy(BaseStrategy):
    """
    Layer 1: 精确匹配

    完全相等或标准化后相等
    置信度: 1.0
    """

    def match(self, query: str, storage: DataStorage) -> Optional[MatchResult]:
        # 中文精确匹配
        entity = storage.get_entity_by_name_cn(query)
        if entity:
            return MatchResult(
                entity_id=entity.id,
                name_cn=entity.name_cn,
                name_en=entity.name_en,
                confidence=1.0,
                aliases=entity.aliases,
                match_type="exact",
            )

        # 英文精确匹配（忽略大小写）
        entity = storage.get_entity_by_name_en(query)
        if entity:
            return MatchResult(
                entity_id=entity.id,
                name_cn=entity.name_cn,
                name_en=entity.name_en,
                confidence=1.0,
                aliases=entity.aliases,
                match_type="exact",
            )

        # 标准化后匹配
        normalized = normalize(query)
        entity = storage.get_entity_by_name_cn(normalized)
        if entity:
            return MatchResult(
                entity_id=entity.id,
                name_cn=entity.name_cn,
                name_en=entity.name_en,
                confidence=0.98,
                aliases=entity.aliases,
                match_type="exact_normalized",
            )

        return None


class AliasStrategy(BaseStrategy):
    """
    Layer 2: 别名查表

    预计算的别名映射
    置信度: 0.95
    """

    def match(self, query: str, storage: DataStorage) -> Optional[MatchResult]:
        # 直接别名匹配
        entity = storage.get_entity_by_alias(query)
        if entity:
            return MatchResult(
                entity_id=entity.id,
                name_cn=entity.name_cn,
                name_en=entity.name_en,
                confidence=0.95,
                aliases=entity.aliases,
                match_type="alias",
            )

        # 标准化后别名匹配
        normalized = normalize(query)
        entity = storage.get_entity_by_alias(normalized)
        if entity:
            return MatchResult(
                entity_id=entity.id,
                name_cn=entity.name_cn,
                name_en=entity.name_en,
                confidence=0.93,
                aliases=entity.aliases,
                match_type="alias_normalized",
            )

        return None


class RuleStrategy(BaseStrategy):
    """
    Layer 3: 规则匹配

    基于启发式规则：
    - 公司后缀移除后匹配
    - 常见缩写展开
    - 拼音匹配

    置信度: 0.85
    """

    # 常见缩写映射
    ABBREVIATIONS = {
        "ali": "alibaba",
        "tenc": "tencent",
        "baidu": "baidu",
        "byted": "bytedance",
        "jd": "jd.com",
        "hw": "huawei",
        "xm": "xiaomi",
    }

    def match(self, query: str, storage: DataStorage) -> Optional[MatchResult]:
        normalized = normalize(query, remove_suffix=True)

        # 移除后缀后匹配
        entity = storage.get_entity_by_name_cn(normalized)
        if entity:
            return MatchResult(
                entity_id=entity.id,
                name_cn=entity.name_cn,
                name_en=entity.name_en,
                confidence=0.85,
                aliases=entity.aliases,
                match_type="rule_suffix_removed",
            )

        entity = storage.get_entity_by_name_en(normalized)
        if entity:
            return MatchResult(
                entity_id=entity.id,
                name_cn=entity.name_cn,
                name_en=entity.name_en,
                confidence=0.85,
                aliases=entity.aliases,
                match_type="rule_suffix_removed",
            )

        # 缩写展开
        query_lower = query.lower().strip()
        if query_lower in self.ABBREVIATIONS:
            expanded = self.ABBREVIATIONS[query_lower]
            entity = storage.get_entity_by_name_en(expanded)
            if entity:
                return MatchResult(
                    entity_id=entity.id,
                    name_cn=entity.name_cn,
                    name_en=entity.name_en,
                    confidence=0.80,
                    aliases=entity.aliases,
                    match_type="rule_abbreviation",
                )

        return None


class FuzzyStrategy(BaseStrategy):
    """
    Layer 4: 模糊匹配

    基于编辑距离的相似度匹配
    置信度: 0.6 - 0.8
    """

    def __init__(self, threshold: float = 0.75):
        """
        Args:
            threshold: 相似度阈值，默认 0.75
        """
        self.threshold = threshold

    def match(self, query: str, storage: DataStorage) -> Optional[MatchResult]:
        # 获取所有名称
        all_names = storage.get_all_names()
        if not all_names:
            return None

        query_normalized = normalize_for_comparison(query)
        if not query_normalized:
            return None

        # 计算相似度
        best_match = None
        best_score = 0.0

        for entity_id, name_cn, name_en in all_names:
            # 中文匹配
            if name_cn:
                cn_normalized = normalize_for_comparison(name_cn)
                score = self._similarity(query_normalized, cn_normalized)
                if score > best_score and score >= self.threshold:
                    best_score = score
                    entity = storage.get_entity_by_id(entity_id)
                    if entity:
                        best_match = MatchResult(
                            entity_id=entity.id,
                            name_cn=entity.name_cn,
                            name_en=entity.name_en,
                            confidence=score,
                            aliases=entity.aliases,
                            match_type="fuzzy_cn",
                        )

            # 英文匹配
            if name_en:
                en_normalized = normalize_for_comparison(name_en)
                score = self._similarity(query_normalized, en_normalized)
                if score > best_score and score >= self.threshold:
                    best_score = score
                    entity = storage.get_entity_by_id(entity_id)
                    if entity:
                        best_match = MatchResult(
                            entity_id=entity.id,
                            name_cn=entity.name_cn,
                            name_en=entity.name_en,
                            confidence=score,
                            aliases=entity.aliases,
                            match_type="fuzzy_en",
                        )

        return best_match

    def _similarity(self, s1: str, s2: str) -> float:
        """
        计算相似度

        使用优化的编辑距离算法（Jaro-Winkler 改进版）
        """
        if not s1 or not s2:
            return 0.0

        # 快速路径：完全相等
        if s1 == s2:
            return 1.0

        # 长度差异过大，直接返回低分
        len_ratio = min(len(s1), len(s2)) / max(len(s1), len(s2))
        if len_ratio < 0.5:
            return 0.0

        # 编辑距离
        distance = self._levenshtein_distance_optimized(s1, s2)
        max_len = max(len(s1), len(s2))

        if max_len == 0:
            return 1.0

        similarity = 1.0 - (distance / max_len)

        # 长度差异惩罚
        adjusted_similarity = similarity * len_ratio

        return adjusted_similarity

    def _levenshtein_distance_optimized(self, s1: str, s2: str) -> int:
        """
        优化的编辑距离计算

        使用空间优化版本，只保留两行
        """
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return len(s1)

        # 只保留两行，节省空间
        previous_row: list[int] = list(range(len(s2) + 1))
        current_row: list[int] = [0] * (len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row[0] = i + 1
            for j, c2 in enumerate(s2):
                # 插入、删除、替换的代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row[j + 1] = min(insertions, deletions, substitutions)
            # 交换行引用，避免复制
            previous_row, current_row = current_row, previous_row

        return previous_row[-1]
