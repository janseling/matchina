"""
测试匹配器 - 使用测试用例数据
符合四套班子流程留痕要求
"""

import json
import logging
import time
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


@pytest.fixture
def matcher():
    """全局 matcher fixture"""
    from matchina import EntityMatcher
    return EntityMatcher()


@pytest.fixture
def test_data():
    """全局 test_data fixture"""
    data_path = Path(__file__).parent / "test_data.json"
    with open(data_path, encoding='utf-8') as f:
        data = json.load(f)
    return data['records']


class TestMatcherWithTestData:
    """使用测试用例数据的匹配器测试"""

    def test_load_test_data(self, test_data):
        """测试加载测试数据"""
        assert len(test_data) == 391, f"预期 391 条记录，实际{len(test_data)}条"
        logger.info(f"加载测试数据成功：{len(test_data)}条记录")

        # 验证数据格式
        assert 'id' in test_data[0]
        assert 'name_cn' in test_data[0]
        assert 'name_en' in test_data[0]
        assert 'stock_code' in test_data[0]

    def test_match_all_records(self, matcher, test_data):
        """测试匹配所有记录"""
        for record in test_data:
            result = matcher.match(record['name_cn'])
            assert len(result) > 0, f"无法匹配：{record['name_cn']}"

    def test_sample_records(self, matcher, test_data):
        """测试抽样记录匹配 - 验证能匹配到结果"""
        samples = test_data[:10]
        for record in samples:
            result = matcher.match(record['name_cn'])
            assert len(result) > 0, f"无法匹配：{record['name_cn']}"

    def test_stock_code_search(self, matcher, test_data):
        """测试股票代码搜索 - 部分代码可匹配"""
        matched = 0
        for record in test_data[:50]:  # 只测试前 50 条
            if record.get('stock_code'):
                result = matcher.match(record['stock_code'])
                if len(result) > 0:
                    matched += 1
        assert matched > 0, "股票代码完全无法匹配"


class TestNormalizer:
    """标准化函数测试"""

    def test_remove_cn_suffix(self):
        """测试中文后缀移除"""
        from matchina.utils.normalizer import normalize

        assert normalize("腾讯科技有限公司") == "腾讯科技"
        assert normalize("阿里巴巴集团") == "阿里巴巴"

    def test_remove_en_suffix(self):
        """测试英文后缀移除"""
        from matchina.utils.normalizer import normalize

        assert normalize("Tencent Ltd.") == "Tencent"
        assert normalize("Alibaba Group") == "Alibaba"

    def test_lowercase(self):
        """测试小写转换"""
        from matchina.utils.normalizer import normalize

        assert normalize("TENCENT", to_lowercase=True) == "tencent"

    def test_empty_string(self):
        """测试空字符串"""
        from matchina.utils.normalizer import normalize

        assert normalize("") == ""

    def test_traditional_to_simplified(self):
        """测试繁体转简体"""
        from matchina.utils.normalizer import normalize

        assert normalize("騰訊") == "腾讯"

    def test_whitespace_cleanup(self):
        """测试空白字符清理"""
        from matchina.utils.normalizer import normalize

        assert normalize("  腾讯  \n") == "腾讯"


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_query(self, matcher):
        """测试空查询"""
        result = matcher.match("")
        assert len(result) == 0

    def test_special_characters(self, matcher):
        """测试特殊字符"""
        result = matcher.match("@#$%")
        assert len(result) == 0

    def test_very_long_query(self, matcher):
        """测试超长查询"""
        long_query = "这是一个非常非常非常非常非常非常非常非常非常非常长的公司名称"
        result = matcher.match(long_query)
        assert len(result) == 0

    def test_mixed_language(self, matcher):
        """测试混合语言"""
        result = matcher.match("腾讯 Tencent")
        assert len(result) > 0

    def test_numeric_in_name(self, matcher):
        """测试名称中的数字"""
        result = matcher.match("360")
        assert len(result) > 0

    def test_case_insensitive_en(self, matcher):
        """测试英文大小写不敏感"""
        result1 = matcher.match("Tencent")
        result2 = matcher.match("tencent")
        assert result1[0].entity_id == result2[0].entity_id

    def test_top_k_parameter(self, matcher):
        """测试 top_k 参数"""
        result1 = matcher.match("科技", top_k=5)
        result2 = matcher.match("科技", top_k=10)
        assert len(result1) <= len(result2)

    def test_search_returns_results(self, matcher):
        """测试搜索返回结果"""
        result = matcher.search("科技")
        assert len(result) > 0

    def test_search_limit(self, matcher):
        """测试搜索限制"""
        result = matcher.search("科技", limit=5)
        assert len(result) <= 5


class TestPerformance:
    """性能测试"""

    def test_batch_resolve_performance(self, matcher, test_data):
        """测试批量匹配性能"""
        import time

        names = [r['name_cn'] for r in test_data[:100]]
        start = time.time()
        for name in names:
            matcher.match(name)
        elapsed = time.time() - start

        assert elapsed < 20.0  # 100 次匹配应该在 20 秒内完成 (CI 环境较慢)

    def test_batch_resolve_unique_names(self, matcher, test_data):
        """测试批量匹配唯一名称"""
        import time

        unique_names = list(set([r['name_cn'] for r in test_data[:100]]))
        start = time.time()
        for name in unique_names:
            matcher.match(name)
        elapsed = time.time() - start

        assert elapsed < 20.0

    def test_fuzzy_match_performance(self, matcher):
        """测试模糊匹配性能"""
        import time

        matcher = EntityMatcher()
        query = "华威技术"

        start = time.time()
        for _ in range(100):
            matcher.match(query)
        elapsed = time.time() - start

        assert elapsed < 20.0  # 100 次匹配应该在 20 秒内完成 (CI 环境较慢)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
