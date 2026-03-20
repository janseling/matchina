"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Entity:
    """企业实体"""

    id: str
    name_cn: str
    name_en: Optional[str] = None
    name_short_cn: Optional[str] = None
    name_short_en: Optional[str] = None
    aliases: list[str] = field(default_factory=list)
    status: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "name_short_cn": self.name_short_cn,
            "name_short_en": self.name_short_en,
            "aliases": self.aliases,
            "status": self.status,
        }


@dataclass
class MatchResult:
    """匹配结果"""

    entity_id: str
    name_cn: str
    name_en: Optional[str]
    confidence: float  # 0.0 - 1.0
    aliases: List[str] = field(default_factory=list)
    match_type: str = "unknown"  # exact, alias, rule, fuzzy

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "confidence": self.confidence,
            "aliases": self.aliases,
            "match_type": self.match_type,
        }

    def __repr__(self) -> str:
        return f"MatchResult({self.name_cn}, conf={self.confidence:.2f}, type={self.match_type})"
pe})"
