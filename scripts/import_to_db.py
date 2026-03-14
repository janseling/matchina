#!/usr/bin/env python3
"""
数据导入脚本 - Matchina 项目

将清洗后的数据导入 SQLite 数据库

功能：
- 从 JSON/CSV 导入到 SQLite
- 支持增量更新
- 创建索引优化查询
- 数据版本管理

项目：Matchina (https://github.com/xxx/matchina)
PyPI: matchina
"""

import json
import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseImporter:
    """数据库导入器"""
    
    # 数据库表结构
    TABLE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS companies (
        company_id TEXT PRIMARY KEY,
        name_cn_full TEXT NOT NULL,
        name_cn_short TEXT,
        name_en_full TEXT NOT NULL,
        name_en_short TEXT,
        stock_code TEXT,
        stock_exchange TEXT,
        data_source TEXT,
        quality_level TEXT,
        confidence_score REAL,
        quality_score REAL,
        version TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS company_aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id TEXT NOT NULL,
        alias_type TEXT NOT NULL,
        alias_name TEXT NOT NULL,
        language TEXT NOT NULL,
        source TEXT,
        confidence_score REAL,
        created_at TEXT,
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
    );
    
    CREATE TABLE IF NOT EXISTS data_versions (
        version TEXT PRIMARY KEY,
        description TEXT,
        record_count INTEGER,
        created_at TEXT,
        source_files TEXT
    );
    
    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_cn_name ON companies(name_cn_full);
    CREATE INDEX IF NOT EXISTS idx_en_name ON companies(name_en_full);
    CREATE INDEX IF NOT EXISTS idx_stock_code ON companies(stock_code);
    CREATE INDEX IF NOT EXISTS idx_quality_level ON companies(quality_level);
    """
    
    def __init__(self, db_path: str = "data/matchina.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"已连接数据库：{self.db_path}")
        
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def initialize_schema(self):
        """初始化数据库表结构"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.executescript(self.TABLE_SCHEMA)
        self.conn.commit()
        logger.info("数据库表结构初始化完成")
    
    def load_data(self, input_file: str) -> List[Dict[str, Any]]:
        """加载 JSON 或 CSV 数据"""
        input_path = Path(input_file)
        
        if not input_path.exists():
            logger.error(f"文件不存在：{input_path}")
            return []
        
        if input_path.suffix == '.json':
            with open(input_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif input_path.suffix == '.csv':
            with open(input_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        else:
            logger.error(f"不支持的文件格式：{input_path.suffix}")
            return []
    
    def insert_company(self, record: Dict[str, Any]) -> bool:
        """
        插入或更新企业记录
        
        使用 UPSERT 模式（INSERT OR REPLACE）
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # 准备数据
        now = datetime.now().isoformat()
        
        sql = """
        INSERT OR REPLACE INTO companies (
            company_id, name_cn_full, name_cn_short, name_en_full, name_en_short,
            stock_code, stock_exchange, data_source, quality_level, 
            confidence_score, quality_score, version, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            record.get('company_id', ''),
            record.get('name_cn_full', ''),
            record.get('name_short', ''),
            record.get('name_en_full', ''),
            record.get('name_en_short', ''),
            record.get('stock_code', ''),
            record.get('stock_exchange', ''),
            record.get('data_source', ''),
            record.get('quality_level', ''),
            float(record.get('confidence_score', 0)),
            float(record.get('quality_score', 0)),
            record.get('cleaned_version', '1.0'),
            now,
            now
        )
        
        try:
            cursor.execute(sql, values)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"插入记录失败：{e}")
            return False
    
    def insert_alias(self, company_id: str, alias_type: str, 
                     alias_name: str, language: str, 
                     source: str = "", confidence: float = 0.5) -> bool:
        """插入企业别名"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        sql = """
        INSERT INTO company_aliases (
            company_id, alias_type, alias_name, language, source, confidence_score, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            company_id,
            alias_type,
            alias_name,
            language,
            source,
            confidence,
            datetime.now().isoformat()
        )
        
        try:
            cursor.execute(sql, values)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"插入别名失败：{e}")
            return False
    
    def import_records(self, records: List[Dict[str, Any]], 
                       batch_size: int = 100) -> int:
        """
        批量导入记录
        
        Args:
            records: 记录列表
            batch_size: 批量大小
            
        Returns:
            成功导入的记录数
        """
        if not self.conn:
            self.connect()
        
        success_count = 0
        cursor = self.conn.cursor()
        
        logger.info(f"开始导入 {len(records)} 条记录...")
        
        for i, record in enumerate(records):
            if self.insert_company(record):
                success_count += 1
                
                # 处理别名（如果有）
                if record.get('name_cn_alias'):
                    for alias in record['name_cn_alias']:
                        self.insert_alias(
                            record['company_id'],
                            '别名',
                            alias,
                            'zh',
                            record.get('data_source', ''),
                            record.get('confidence_score', 0.5)
                        )
                
                if record.get('name_en_alias'):
                    for alias in record['name_en_alias']:
                        self.insert_alias(
                            record['company_id'],
                            '别名',
                            alias,
                            'en',
                            record.get('data_source', ''),
                            record.get('confidence_score', 0.5)
                        )
            
            # 进度日志
            if (i + 1) % batch_size == 0:
                logger.info(f"已导入 {i + 1}/{len(records)} 条记录")
        
        logger.info(f"导入完成：{success_count}/{len(records)} 条记录成功")
        return success_count
    
    def incremental_update(self, new_records: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        增量更新
        
        比较新数据与现有数据，只插入/更新有变化的记录
        
        Returns:
            统计信息：新增、更新、跳过
        """
        if not self.conn:
            self.connect()
        
        stats = {'inserted': 0, 'updated': 0, 'skipped': 0}
        cursor = self.conn.cursor()
        
        for record in new_records:
            company_id = record.get('company_id')
            
            # 检查是否已存在
            cursor.execute(
                "SELECT company_id, updated_at FROM companies WHERE company_id = ?",
                (company_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # 比较更新时间
                existing_time = existing['updated_at'] or ''
                new_time = record.get('cleaned_at', '')
                
                if new_time > existing_time:
                    # 更新
                    if self.insert_company(record):
                        stats['updated'] += 1
                        logger.debug(f"更新记录：{company_id}")
                    else:
                        stats['skipped'] += 1
                else:
                    stats['skipped'] += 1
                    logger.debug(f"跳过记录（已是最新）：{company_id}")
            else:
                # 插入
                if self.insert_company(record):
                    stats['inserted'] += 1
                    logger.debug(f"新增记录：{company_id}")
                else:
                    stats['skipped'] += 1
        
        logger.info(f"增量更新完成：新增 {stats['inserted']}, 更新 {stats['updated']}, 跳过 {stats['skipped']}")
        return stats
    
    def create_version_record(self, version: str, records: List[Dict], 
                              source_files: str):
        """创建版本记录"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        sql = """
        INSERT INTO data_versions (version, description, record_count, created_at, source_files)
        VALUES (?, ?, ?, ?, ?)
        """
        
        values = (
            version,
            f"导入 {len(records)} 条企业记录",
            len(records),
            datetime.now().isoformat(),
            source_files
        )
        
        cursor.execute(sql, values)
        self.conn.commit()
        logger.info(f"版本记录已创建：{version}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        stats = {}
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) as count FROM companies")
        stats['total_companies'] = cursor.fetchone()['count']
        
        # 按质量等级分布
        cursor.execute("""
            SELECT quality_level, COUNT(*) as count 
            FROM companies 
            WHERE quality_level IS NOT NULL 
            GROUP BY quality_level
        """)
        stats['quality_distribution'] = {
            row['quality_level']: row['count'] 
            for row in cursor.fetchall()
        }
        
        # 按数据源分布
        cursor.execute("""
            SELECT data_source, COUNT(*) as count 
            FROM companies 
            WHERE data_source IS NOT NULL 
            GROUP BY data_source
        """)
        stats['source_distribution'] = {
            row['data_source']: row['count'] 
            for row in cursor.fetchall()
        }
        
        # 按交易所分布
        cursor.execute("""
            SELECT stock_exchange, COUNT(*) as count 
            FROM companies 
            WHERE stock_exchange IS NOT NULL 
            GROUP BY stock_exchange
        """)
        stats['exchange_distribution'] = {
            row['stock_exchange']: row['count'] 
            for row in cursor.fetchall()
        }
        
        # 别名总数
        cursor.execute("SELECT COUNT(*) as count FROM company_aliases")
        stats['total_aliases'] = cursor.fetchone()['count']
        
        # 版本信息
        cursor.execute("""
            SELECT version, record_count, created_at 
            FROM data_versions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        latest_version = cursor.fetchone()
        stats['latest_version'] = latest_version['version'] if latest_version else None
        stats['latest_version_count'] = latest_version['record_count'] if latest_version else 0
        
        return stats
    
    def export_to_json(self, output_file: str = "data/export.json"):
        """导出数据库到 JSON"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM companies")
        
        records = []
        for row in cursor.fetchall():
            records.append(dict(row))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已导出到 {output_file}")
        return output_file


def main():
    """主函数 - 测试数据导入"""
    print("=" * 60)
    print("Matchina 数据导入脚本")
    print("=" * 60)
    
    # 创建导入器
    importer = DatabaseImporter()
    
    # 初始化数据库
    print("\n📇 初始化数据库...")
    importer.initialize_schema()
    
    # 查找清洗后的数据文件
    cleaned_files = list(Path("data/cleaned").glob("cleaned_data.*"))
    if not cleaned_files:
        print("\n⚠️ 未找到清洗后的数据文件")
        print("   请先运行：python scripts/clean_data.py")
        importer.close()
        return
    
    input_file = cleaned_files[0]
    print(f"📂 输入文件：{input_file}")
    
    # 加载数据
    records = importer.load_data(str(input_file))
    print(f"📊 加载 {len(records)} 条记录")
    
    # 导入数据
    print("\n⏳ 开始导入数据...")
    success_count = importer.import_records(records)
    
    # 创建版本记录
    version = f"v{datetime.now().strftime('%Y%m%d')}-001"
    importer.create_version_record(version, records, str(input_file))
    
    # 显示统计信息
    print("\n📈 数据库统计:")
    stats = importer.get_stats()
    print(f"   - 总企业数：{stats.get('total_companies', 0)}")
    print(f"   - 最新版本：{stats.get('latest_version', 'N/A')}")
    print(f"   - 别名总数：{stats.get('total_aliases', 0)}")
    
    if stats.get('quality_distribution'):
        print("\n   质量等级分布:")
        for level, count in sorted(stats['quality_distribution'].items()):
            print(f"      {level}: {count}")
    
    if stats.get('source_distribution'):
        print("\n   数据源分布:")
        for source, count in sorted(stats['source_distribution'].items()):
            print(f"      {source}: {count}")
    
    # 关闭连接
    importer.close()
    
    print("\n✅ 导入完成!")
    print(f"   数据库位置：{importer.db_path.absolute()}")


if __name__ == "__main__":
    main()
