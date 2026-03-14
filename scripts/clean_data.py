#!/usr/bin/env python3
"""
数据清洗脚本 - Matchina 项目名称数据清洗

对企业名称数据进行标准化、去重、格式验证

功能：
- 名称标准化（去后缀、繁简转换）
- 去重（基于模糊匹配）
- 格式验证（长度、字符集）
- 质量评分

项目：Matchina (https://github.com/xxx/matchina)
PyPI: matchina
"""

import json
import csv
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 尝试导入 opencc 用于繁简转换
try:
    from opencc import OpenCC
    OPENCC_AVAILABLE = True
except ImportError:
    OPENCC_AVAILABLE = False
    logger.warning("opencc 未安装，繁简转换功能不可用。运行：pip install opencc")


class DataCleaner:
    """数据清洗器"""
    
    # 常见公司后缀（中文）
    CN_SUFFIXES = [
        '有限公司', '有限责任公司', '股份有限公司', '集团公司',
        '集团', '公司', '厂', '店', '中心', '研究院', '研究所'
    ]
    
    # 常见公司后缀（英文）
    EN_SUFFIXES = [
        'Limited', 'Ltd.', 'Ltd', 'Co., Ltd.', 'Co. Ltd',
        'Corporation', 'Corp.', 'Corp', 'Incorporated', 'Inc.',
        'Company', 'Co.', 'Group', 'Holdings', 'Holdings Limited'
    ]
    
    # 非法字符模式（中文名称）
    CN_ILLEGAL_PATTERN = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9 ()《》""&·]')
    
    # 非法字符模式（英文名称）
    EN_ILLEGAL_PATTERN = re.compile(r'[^a-zA-Z0-9 .,&\'\-()]')
    
    def __init__(self, input_dir: str = "data", output_dir: str = "data/cleaned"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化繁简转换器
        if OPENCC_AVAILABLE:
            self.cc_t2s = OpenCC('t2s')  # 繁体转简体
            self.cc_s2t = OpenCC('s2t')  # 简体转繁体
        
    def load_data(self, input_file: str) -> List[Dict[str, Any]]:
        """加载 JSON 或 CSV 数据"""
        input_path = self.input_dir / input_file
        
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
    
    def normalize_chinese_name(self, name: str) -> str:
        """
        标准化中文名称
        
        - 繁简转换（转为简体）
        - 去除首尾空格
        - 统一全角/半角
        """
        if not name:
            return ""
        
        # 去除首尾空格
        name = name.strip()
        
        # 繁简转换（如果 opencc 可用）
        if OPENCC_AVAILABLE:
            name = self.cc_t2s.convert(name)
        
        # 全角转半角（数字和字母）
        name = unicodedata.normalize('NFKC', name)
        
        return name
    
    def normalize_english_name(self, name: str) -> str:
        """
        标准化英文名称
        
        - 统一大小写格式
        - 去除多余空格
        - 标准化标点
        """
        if not name:
            return ""
        
        # 去除首尾空格
        name = name.strip()
        
        # 多个空格转为一个
        name = re.sub(r'\s+', ' ', name)
        
        # 标准化标点空格
        name = re.sub(r'\s*,\s*', ', ', name)
        name = re.sub(r'\s*\.\s*', '. ', name)
        
        # 首字母大写（除非是全大写官方格式）
        if name.isupper() and len(name) > 3:
            # 保持全大写（可能是官方证券简称）
            return name
        else:
            # 标题化（每个单词首字母大写）
            return name.title()
    
    def remove_suffix(self, name: str, language: str = 'cn') -> str:
        """
        去除公司后缀
        
        Args:
            name: 公司全称
            language: 'cn' 或 'en'
            
        Returns:
            去除后缀后的名称
        """
        if not name:
            return ""
        
        if language == 'cn':
            for suffix in sorted(self.CN_SUFFIXES, key=len, reverse=True):
                if name.endswith(suffix):
                    return name[:-len(suffix)]
        elif language == 'en':
            for suffix in sorted(self.EN_SUFFIXES, key=len, reverse=True):
                if name.upper().endswith(suffix.upper()):
                    # 找到后缀位置并移除
                    idx = name.upper().rfind(suffix.upper())
                    return name[:idx].strip()
        
        return name
    
    def validate_format(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证记录格式
        
        Returns:
            (是否通过验证，错误列表)
        """
        errors = []
        
        # 验证中文名称
        cn_name = record.get('name_cn_full', '')
        if cn_name:
            # 长度检查
            if len(cn_name) < 5 or len(cn_name) > 50:
                errors.append(f"中文名称长度异常：{len(cn_name)} (应在 5-50 之间)")
            
            # 字符集检查
            if self.CN_ILLEGAL_PATTERN.search(cn_name):
                errors.append(f"中文名称包含非法字符")
        
        # 验证英文名称
        en_name = record.get('name_en_full', '')
        if en_name:
            # 长度检查
            if len(en_name) < 5 or len(en_name) > 100:
                errors.append(f"英文名称长度异常：{len(en_name)} (应在 5-100 之间)")
            
            # 字符集检查
            if self.EN_ILLEGAL_PATTERN.search(en_name):
                errors.append(f"英文名称包含非法字符")
        
        # 验证企业 ID
        if not record.get('company_id'):
            errors.append("企业 ID 缺失")
        
        # 验证数据来源
        if not record.get('data_source'):
            errors.append("数据来源缺失")
        
        return len(errors) == 0, errors
    
    def calculate_quality_score(self, record: Dict[str, Any]) -> float:
        """
        计算数据质量评分
        
        基于：
        - 质量等级（L1-L4）
        - 数据源可信度
        - 字段完整性
        """
        base_score = 0.5
        
        # 质量等级加分
        quality_levels = {
            'L1': 0.3,  # 官方匹配
            'L2': 0.2,  # 证券匹配
            'L3': 0.15, # 市场公认
            'L4': 0.05  # 推测匹配
        }
        level = record.get('quality_level', 'L4')
        base_score += quality_levels.get(level, 0.05)
        
        # 数据源可信度加分
        trusted_sources = ['SEC EDGAR', 'HKEX 披露易', 'AkShare', '国家企业信用信息公示系统']
        if record.get('data_source') in trusted_sources:
            base_score += 0.1
        
        # 字段完整性加分
        required_fields = ['name_cn_full', 'name_en_full', 'company_id', 'data_source']
        optional_fields = ['name_short', 'stock_code', 'stock_exchange']
        
        for field in required_fields:
            if record.get(field):
                base_score += 0.05
        
        for field in optional_fields:
            if record.get(field):
                base_score += 0.02
        
        return min(base_score, 1.0)
    
    def deduplicate(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去重
        
        使用规则：
        - 企业 ID 完全相同 → 合并
        - 中文名称相似度>95% → 视为重复
        - 保留质量评分更高的记录
        """
        if not records:
            return []
        
        # 按企业 ID 分组
        id_map = {}
        for record in records:
            company_id = record.get('company_id', '')
            if company_id:
                if company_id not in id_map:
                    id_map[company_id] = []
                id_map[company_id].append(record)
        
        # 每个 ID 保留质量最好的记录
        deduped_by_id = []
        for company_id, dup_records in id_map.items():
            if len(dup_records) == 1:
                deduped_by_id.append(dup_records[0])
            else:
                # 按质量评分排序，保留最好的
                sorted_records = sorted(
                    dup_records,
                    key=lambda r: r.get('confidence_score', 0),
                    reverse=True
                )
                deduped_by_id.append(sorted_records[0])
                logger.info(f"企业 {company_id} 去重：保留 {len(sorted_records[0])} 条，丢弃 {len(dup_records)-1} 条")
        
        # 进一步基于名称模糊去重
        final_records = self._fuzzy_dedup(deduped_by_id)
        
        return final_records
    
    def _fuzzy_dedup(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于名称模糊匹配去重
        
        使用 Levenshtein 距离或简单字符串匹配
        """
        if not records:
            return []
        
        # 尝试导入 fuzzywuzzy
        try:
            from fuzzywuzzy import fuzz
            FUZZ_AVAILABLE = True
        except ImportError:
            FUZZ_AVAILABLE = False
            logger.warning("fuzzywuzzy 未安装，使用简单字符串匹配")
        
        deduped = []
        seen_names = set()
        
        for record in sorted(records, key=lambda r: r.get('confidence_score', 0), reverse=True):
            cn_name = self.normalize_chinese_name(record.get('name_cn_full', ''))
            en_name = self.normalize_english_name(record.get('name_en_full', ''))
            
            name_key = f"{cn_name}|{en_name}"
            
            if name_key in seen_names:
                logger.info(f"跳过重复记录：{cn_name}")
                continue
            
            # 如果没有 fuzzywuzzy，使用精确匹配
            if FUZZ_AVAILABLE:
                # 检查是否与已有记录高度相似
                is_duplicate = False
                for seen_key in seen_names:
                    seen_cn = seen_key.split('|')[0]
                    similarity = fuzz.ratio(cn_name, seen_cn)
                    if similarity > 95:
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
            
            seen_names.add(name_key)
            deduped.append(record)
        
        return deduped
    
    def clean(self, input_file: str, output_file: str = "cleaned_data.json") -> List[Dict[str, Any]]:
        """
        执行完整清洗流程
        
        Args:
            input_file: 输入文件名
            output_file: 输出文件名
            
        Returns:
            清洗后的数据
        """
        logger.info(f"开始清洗数据：{input_file}")
        
        # 加载数据
        records = self.load_data(input_file)
        if not records:
            return []
        
        logger.info(f"加载 {len(records)} 条记录")
        
        # 1. 格式验证
        valid_records = []
        for record in records:
            is_valid, errors = self.validate_format(record)
            if is_valid:
                valid_records.append(record)
            else:
                logger.warning(f"记录格式验证失败：{errors}")
                # 添加错误信息到记录
                record['validation_errors'] = errors
                record['is_valid'] = False
        
        logger.info(f"格式验证通过：{len(valid_records)}/{len(records)}")
        
        # 2. 名称标准化
        for record in valid_records:
            record['name_cn_full'] = self.normalize_chinese_name(record.get('name_cn_full', ''))
            record['name_en_full'] = self.normalize_english_name(record.get('name_en_full', ''))
            
            # 生成简称（如果没有）
            if not record.get('name_short'):
                cn_name = record['name_cn_full']
                record['name_short'] = self.remove_suffix(cn_name, 'cn')
        
        # 3. 计算质量评分
        for record in valid_records:
            record['quality_score'] = self.calculate_quality_score(record)
        
        # 4. 去重
        deduped_records = self.deduplicate(valid_records)
        logger.info(f"去重后剩余：{len(deduped_records)} 条记录")
        
        # 5. 添加清洗元数据
        for record in deduped_records:
            record['cleaned_at'] = datetime.now().isoformat()
            record['cleaned_version'] = '1.0'
        
        # 保存结果
        output_path = self.output_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(deduped_records, f, ensure_ascii=False, indent=2)
        
        logger.info(f"清洗完成，保存到 {output_path}")
        
        # 生成清洗报告
        self._generate_cleaning_report(records, valid_records, deduped_records, output_path)
        
        return deduped_records
    
    def _generate_cleaning_report(self, original: List, valid: List, deduped: List, output_path: Path):
        """生成清洗报告"""
        report = {
            "summary": {
                "original_count": len(original),
                "valid_count": len(valid),
                "deduped_count": len(deduped),
                "validation_rate": f"{len(valid)/len(original)*100:.1f}%" if original else "0%",
                "dedup_rate": f"{len(deduped)/len(valid)*100:.1f}%" if valid else "0%"
            },
            "quality_distribution": {},
            "data_sources": {},
            "cleaned_at": datetime.now().isoformat(),
            "output_file": str(output_path)
        }
        
        # 质量等级分布
        for record in deduped:
            level = record.get('quality_level', 'unknown')
            report['quality_distribution'][level] = report['quality_distribution'].get(level, 0) + 1
        
        # 数据源分布
        for record in deduped:
            source = record.get('data_source', 'unknown')
            report['data_sources'][source] = report['data_sources'].get(source, 0) + 1
        
        # 保存报告
        report_path = self.output_dir / "cleaning_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"清洗报告保存到 {report_path}")


def main():
    """主函数 - 测试数据清洗"""
    print("=" * 60)
    print("企业名称数据清洗脚本")
    print("=" * 60)
    
    # 创建清洗器
    cleaner = DataCleaner()
    
    # 查找输入文件
    input_files = list(cleaner.input_dir.glob("collected_data.*"))
    if not input_files:
        print("\n⚠️ 未找到采集数据文件")
        print("   请先运行：python scripts/collect_data.py")
        return
    
    input_file = input_files[0].name
    print(f"\n📂 输入文件：{input_file}")
    
    # 执行清洗
    cleaned_data = cleaner.clean(input_file)
    
    if cleaned_data:
        print(f"\n✅ 清洗完成!")
        print(f"   - 原始记录：{len(cleaner.load_data(input_file))}")
        print(f"   - 清洗后：{len(cleaned_data)}")
        
        # 显示质量分布
        quality_dist = {}
        for record in cleaned_data:
            level = record.get('quality_level', 'unknown')
            quality_dist[level] = quality_dist.get(level, 0) + 1
        
        print("\n📊 质量等级分布:")
        for level, count in sorted(quality_dist.items()):
            print(f"   {level}: {count} 条")
        
        # 显示数据源分布
        source_dist = {}
        for record in cleaned_data:
            source = record.get('data_source', 'unknown')
            source_dist[source] = source_dist.get(source, 0) + 1
        
        print("\n📊 数据源分布:")
        for source, count in sorted(source_dist.items()):
            print(f"   {source}: {count} 条")
    else:
        print("\n⚠️ 清洗后无数据，请检查输入文件")


if __name__ == "__main__":
    main()
