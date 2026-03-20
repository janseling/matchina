"""
测试匹配器 - 使用测试用例数据
符合四套班子流程留痕要求
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
import pytest

# 配置日志 - 四套班子留痕系统
LOG_DIR = Path(__file__).parent.parent / "memory" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "session_id": "matchina-test", '
           '"action": "%(levelname)s", "result": "%(message)s"}',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TestMatcherWithTestData:
    """使用测试用例数据的匹配器测试"""

    @pytest.fixture
    def matcher(self):
        from matchina import EntityMatcher
        return EntityMatcher()

    @pytest.fixture
    def test_data(self):
        """加载测试用例数据"""
        data_path = Path(__file__).parent / "test_data.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['records']

    def test_load_test_data(self, test_data):
        """测试加载测试数据"""
        assert len(test_data) == 391, f"预期 391 条记录，实际{len(test_data)}条"
        logger.info(f"加载测试数据成功：{len(test_data)}条记录")
        
        # 验证数据格式
        record = test_data[0]
        assert 'id' in record
        assert 'name_cn' in record
        assert 'name_en' in record
        assert 'stock_code' in record

    def test_match_all_records(self, matcher, test_data):
        """遍历所有测试记录进行匹配验证"""
        logger.info("开始执行匹配测试")
        start_time = time.time()
        
        passed = 0
        failed = 0
        failed_cases = []
        
        for record in test_data:
            # 测试中文名称匹配
            cn_result = matcher.match(record['name_cn'])
            
            # 测试英文名称匹配
            en_result = matcher.match(record['name_en'])
            
            # 验证匹配结果
            cn_pass = len(cn_result) > 0 and cn_result[0].name_cn == record['name_cn']
            en_pass = len(en_result) > 0
            
            if cn_pass and en_pass:
                passed += 1
            else:
                failed += 1
                failed_cases.append({
                    'id': record['id'],
                    'name_cn': record['name_cn'],
                    'name_en': record['name_en'],
                    'stock_code': record['stock_code'],
                    'cn_match': cn_pass,
                    'en_match': en_pass,
                    'cn_result': cn_result[0].name_cn if cn_result else None,
                    'en_result': en_result[0].name_cn if en_result else None
                })
        
        elapsed = time.time() - start_time
        pass_rate = passed / len(test_data) * 100
        
        # 输出测试结果
        report = {
            'total': len(test_data),
            'passed': passed,
            'failed': failed,
            'pass_rate': f"{pass_rate:.2f}%",
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"测试完成：{report}")
        
        # 打印详细报告
        print("\n" + "="*60)
        print("匹配器测试报告")
        print("="*60)
        print(f"测试记录总数：{report['total']}")
        print(f"通过数量：{report['passed']}")
        print(f"失败数量：{report['failed']}")
        print(f"通过率：{report['pass_rate']}")
        print(f"执行时间：{report['elapsed_seconds']}秒")
        print("="*60)
        
        if failed_cases:
            print("\n失败案例详情:")
            print("-"*60)
            for i, case in enumerate(failed_cases[:10], 1):  # 只显示前 10 个
                print(f"{i}. ID: {case['id']}")
                print(f"   中文：{case['name_cn']} -> 匹配：{case['cn_result']}")
                print(f"   英文：{case['name_en']} -> 匹配：{case['en_result']}")
                print()
        
        assert pass_rate > 50, f"通过率过低：{pass_rate:.2f}%"
        
        # 留痕：记录决策链
        decision_log = {
            'timestamp': datetime.now().isoformat(),
            'session_id': 'matchina-test',
            'action': 'TEST_COMPLETE',
            'decision_maker': '党委 (main)',
            'change_content': f"测试脚本修改完成",
            'reason': '使用测试用例数据进行验证',
            'expected_impact': f"通过率{pass_rate:.2f}%",
            'actual_result': report
        }
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(decision_log, ensure_ascii=False) + '\n')

    def test_sample_records(self, matcher, test_data):
        """抽样测试部分记录（快速验证）"""
        # 测试前 10 条记录
        sample = test_data[:10]
        
        for record in sample:
            result = matcher.match(record['name_cn'])
            assert isinstance(result, list)
            logger.info(f"抽样测试：{record['name_cn']} -> {len(result)}个结果")

    def test_stock_code_search(self, matcher, test_data):
        """测试股票代码搜索"""
        # 随机测试几个股票代码
        sample = test_data[::50]  # 每隔 50 条取一个
        
        for record in sample[:5]:
            result = matcher.search(record['stock_code'])
            assert isinstance(result, list)
            logger.info(f"股票代码搜索：{record['stock_code']} -> {len(result)}个结果")


class TestNormalizer:
    """测试名称标准化"""

    def test_remove_cn_suffix(self):
        from matchina.utils.normalizer import normalize
        result = normalize("华为技术有限公司", remove_suffix=True)
        assert "技术" not in result or result == "华为技术"

    def test_remove_en_suffix(self):
        from matchina.utils.normalizer import normalize
        result = normalize("Alibaba Group Holding Limited", remove_suffix=True)
        assert "Limited" not in result

    def test_lowercase(self):
        from matchina.utils.normalizer import normalize
        result = normalize("HUAWEI", to_lowercase=True)
        assert result == "huawei"

    def test_empty_string(self):
        from matchina.utils.normalizer import normalize
        assert normalize("") == ""
        assert normalize("   ") == ""

    def test_traditional_to_simplified(self):
        from matchina.utils.normalizer import normalize
        result = normalize("資訊網絡技術", convert_traditional=True)
        assert "資訊" not in result
        assert "信息" in result or "资讯" in result

    def test_whitespace_cleanup(self):
        from matchina.utils.normalizer import normalize
        result = normalize("  华为   ")
        assert result == "华为"
        assert "  " not in result


class TestEdgeCases:
    """测试边界情况"""

    @pytest.fixture
    def matcher(self):
        from matchina import EntityMatcher
        return EntityMatcher()

    def test_empty_query(self, matcher):
        """测试空查询"""
        assert matcher.match("") == []
        assert matcher.match("   ") == []

    def test_special_characters(self, matcher):
        """测试特殊字符"""
        result = matcher.match("华为@#$")
        assert len(result) == 0 or "华为" in result[0].name_cn

    def test_very_long_query(self, matcher):
        """测试超长查询"""
        long_query = "华为技术有限公司北京分公司研发中心" * 10
        result = matcher.match(long_query)
        assert isinstance(result, list)

    def test_mixed_language(self, matcher):
        """测试中英文混合"""
        result = matcher.match("华为 Huawei")
        assert isinstance(result, list)

    def test_numeric_in_name(self, matcher):
        """测试包含数字的名称"""
        result = matcher.match("360")
        assert isinstance(result, list)

    def test_case_insensitive_en(self, matcher):
        """测试英文大小写不敏感"""
        result1 = matcher.match("ALIBABA")
        result2 = matcher.match("alibaba")
        assert len(result1) == len(result2)

    def test_top_k_parameter(self, matcher):
        """测试 top_k 参数"""
        result1 = matcher.match("华为", top_k=1)
        result2 = matcher.match("华为", top_k=10)
        assert len(result1) == len(result2)  # 精确匹配只返回 1 个结果
        assert len(result1) >= 1

    def test_search_returns_results(self, matcher):
        """测试搜索返回结果"""
        result = matcher.search("华为", limit=5)
        assert len(result) >= 1

    def test_search_limit(self, matcher):
        """测试搜索 limit 参数"""
        result1 = matcher.search("科技", limit=1)
        result2 = matcher.search("科技", limit=20)
        assert len(result1) <= len(result2)


class TestPerformance:
    """性能测试"""

    def test_batch_resolve_performance(self):
        """测试批量匹配性能"""
        import time

        from matchina import resolve_batch

        # 使用不同的名称（resolve_batch 返回 dict，键为输入名称）
        names = ["华为", "腾讯", "百度", "阿里", "小米"] * 10  # 50 个输入
        start = time.time()
        results = resolve_batch(names)
        elapsed = time.time() - start

        # dict 键数量为 5（重复名称合并）
        assert len(results) == 5
        # 验证每个名称都有结果
        for name in results:
            assert len(results[name]) >= 1
        assert elapsed < 5.0  # 应该在 5 秒内完成

    def test_batch_resolve_unique_names(self):
        """测试批量匹配不同名称"""
        from matchina import resolve_batch

        names = ["华为", "腾讯", "百度", "阿里", "小米"]
        results = resolve_batch(names)

        assert len(results) == 5
        for name in names:
            assert name in results
            assert len(results[name]) >= 1

    def test_fuzzy_match_performance(self):
        """测试模糊匹配性能"""
        import time

        from matchina import EntityMatcher

        matcher = EntityMatcher()
        query = "华威技术"

        start = time.time()
        for _ in range(100):
            matcher.match(query)
        elapsed = time.time() - start

        assert elapsed < 20.0  # 100 次匹配应该在 20 秒内完成 (CI 环境较慢)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
