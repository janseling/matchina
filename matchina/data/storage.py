"""
数据存储模块
"""

import sqlite3
from pathlib import Path
from typing import Optional

from ..models.entity import Entity


class DataStorage:
    """SQLite 数据存储"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据存储

        Args:
            db_path: 数据库路径，默认使用包内数据
        """
        if db_path is None:
            # 使用包内数据
            db_path = str(Path(__file__).parent / "entities.db")

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        """获取数据库连接（懒加载）"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """根据 ID 获取实体"""
        cursor = self.conn.execute(
            "SELECT * FROM entities WHERE id = ?", (entity_id,)
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_entity(row)
        return None

    def get_entity_by_name_cn(self, name: str) -> Optional[Entity]:
        """根据中文名精确匹配"""
        cursor = self.conn.execute(
            "SELECT * FROM entities WHERE name_cn = ? OR name_short_cn = ?",
            (name, name),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_entity(row)
        return None

    def get_entity_by_name_en(self, name: str) -> Optional[Entity]:
        """根据英文名精确匹配"""
        name_lower = name.lower()
        cursor = self.conn.execute(
            "SELECT * FROM entities WHERE LOWER(name_en) = ? OR LOWER(name_short_en) = ?",
            (name_lower, name_lower),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_entity(row)
        return None

    def get_entity_by_alias(self, alias: str) -> Optional[Entity]:
        """根据别名匹配"""
        cursor = self.conn.execute(
            """
            SELECT e.* FROM entities e
            JOIN aliases a ON e.id = a.entity_id
            WHERE a.alias = ?
            """,
            (alias,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_entity(row)
        return None

    def search_entities(self, query: str, limit: int = 10) -> list[Entity]:
        """模糊搜索"""
        cursor = self.conn.execute(
            """
            SELECT * FROM entities
            WHERE name_cn LIKE ? OR name_en LIKE ? OR name_short_cn LIKE ? OR name_short_en LIKE ?
            LIMIT ?
            """,
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_all_names(self) -> list[tuple[str, str, str]]:
        """获取所有名称（用于模糊匹配）"""
        cursor = self.conn.execute(
            "SELECT id, name_cn, name_en FROM entities"
        )
        return [(row["id"], row["name_cn"], row["name_en"]) for row in cursor.fetchall()]

    def get_aliases(self, entity_id: str) -> list[str]:
        """获取实体的所有别名"""
        cursor = self.conn.execute(
            "SELECT alias FROM aliases WHERE entity_id = ?", (entity_id,)
        )
        return [row["alias"] for row in cursor.fetchall()]

    def _row_to_entity(self, row: sqlite3.Row) -> Entity:
        """数据库行转实体对象"""
        return Entity(
            id=row["id"],
            name_cn=row["name_cn"],
            name_en=row["name_en"] if "name_en" in row.keys() else None,
            name_short_cn=row["name_short_cn"] if "name_short_cn" in row.keys() else None,
            name_short_en=row["name_short_en"] if "name_short_en" in row.keys() else None,
            status=row["status"] if "status" in row.keys() else None,
        )

    def close(self) -> None:
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "DataStorage":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
