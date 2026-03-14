"""
测试匹配器
"""

import pytest

# 需要先初始化数据库才能运行测试


class TestEntityMatcher:
    """测试匹配器"""

    @pytest.fixture
    def matcher(self):
        from matchina import EntityMatcher
        return EntityMatcher()

    def test_exact_match_cn(self, matcher):
        """测试中文精确匹配"""
        result = matcher.match("华为技术有限公司")
        assert result is not None
        assert len(result) > 0
        assert result[0].name_cn == "华为技术有限公司"
        assert result[0].confidence == 1.0
        assert result[0].match_type == "exact"

    def test_exact_match_en(self, matcher):
        """测试英文精确匹配"""
        result = matcher.match("Alibaba Group Holding Limited")
        assert result is not None
        assert len(result) > 0
        assert "阿里巴巴" in result[0].name_cn
        assert result[0].confidence == 1.0

    def test_alias_match(self, matcher):
        """测试别名匹配"""
        result = matcher.match("抖音")
        assert result is not None
        assert len(result) > 0
        assert "字节跳动" in result[0].name_cn
        assert result[0].confidence == 0.95
        assert result[0].match_type == "alias"

    def test_short_name(self, matcher):
        """测试简称匹配"""
        result = matcher.match("华为")
        assert result is not None
        assert len(result) > 0
        assert "华为" in result[0].name_cn

    def test_fuzzy_match(self, matcher):
        """测试模糊匹配"""
        # 轻微拼写错误（同音字）
        result = matcher.match("华威技术")
        assert result is not None
        assert len(result) > 0
        assert "华为" in result[0].name_cn
        assert result[0].confidence < 1.0
        assert result[0].match_type == "fuzzy_cn"

    def test_fuzzy_partial_match(self, matcher):
        """测试部分名称模糊匹配"""
        # 不完整名称
        result = matcher.match("腾讯科技")
        assert result is not None
        assert len(result) > 0
        assert "腾讯" in result[0].name_cn

    def test_fuzzy_english(self, matcher):
        """测试英文模糊匹配"""
        result = matcher.match("Huawei Tech")
        assert result is not None
        assert len(result) > 0
        assert result[0].confidence < 1.0

    def test_no_match(self, matcher):
        """测试无匹配"""
        result = matcher.match("不存在的公司名称12345")
        assert result == []

    def test_search(self, matcher):
        """测试搜索"""
        results = matcher.search("科技", limit=5)
        assert len(results) > 0

    def test_batch_resolve(self, matcher):
        """测试批量匹配"""
        from matchina import resolve_batch
        names = ["华为", "腾讯", "百度"]
        results = resolve_batch(names)
        assert len(results) == 3
        for _name, matches in results.items():
            assert len(matches) > 0


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

        assert elapsed < 2.0  # 100 次匹配应该在 2 秒内完成


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
