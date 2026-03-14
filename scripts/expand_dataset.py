#!/usr/bin/env python3
"""大规模数据扩展脚本 - Matchina 项目 目标：1000+ 实体"""
import sqlite3
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    db_path = Path.home() / "Projects" / "matchina" / "data" / "entities.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS entities (id TEXT PRIMARY KEY, name_cn TEXT NOT NULL, name_en TEXT, name_short_cn TEXT, name_short_en TEXT, status TEXT);
    CREATE TABLE IF NOT EXISTS aliases (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id TEXT NOT NULL, alias TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_name_cn ON entities(name_cn);
    CREATE INDEX IF NOT EXISTS idx_alias ON aliases(alias);
    """)
    conn.commit()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM entities")
    current = cursor.fetchone()[0]
    logger.info(f"当前实体：{current}")
    
    entities = []
    # A 股核心
    a_core = [("贵州茅台","Kweich