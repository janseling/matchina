# Matchina

[English](README_en.md) | 中文

中国企业中英文名称对齐匹配库。支持精确匹配、别名匹配、模糊搜索，离线使用，无需网络。

## 特性

- 🔍 **四层匹配策略**：精确匹配 → 别名匹配 → 规则匹配 → 模糊匹配
- 🇨🇳 **中英文支持**：同时支持中文和英文名称
- 📦 **离线使用**：所有数据打包在库内，无需网络
- ⚡ **高性能**：单次匹配 < 100ms
- 🐍 **Python 3.8+**：支持 Python 3.8 及以上版本

## 安装

```bash
pip install matchina
```

## 快速开始

```python
from matchina import resolve, search, resolve_batch

# 精确匹配
result = resolve("华为")
print(result[0].name_cn)      # 华为技术有限公司
print(result[0].name_en)      # Huawei Technologies Co., Ltd.
print(result[0].confidence)   # 1.0

# 英文匹配
result = resolve("Alibaba")
print(result[0].name_cn)       # 阿里巴巴集团控股有限公司

# 别名匹配
result = resolve("抖音")
print(result[0].name_cn)       # 北京字节跳动科技有限公司
print(result[0].confidence)    # 0.95

# 批量匹配
names = ["腾讯", "百度", "小米", "比亚迪"]
results = resolve_batch(names)
for name, matches in results.items():
    if matches:
        print(f"{name} → {matches[0].name_cn}")

# 模糊搜索
results = search("科技", limit=5)
for r in results:
    print(f"{r.name_cn} (置信度：{r.confidence:.2f})")
```

## 匹配策略

| 匹配类型 | 说明 | 置信度 |
|----------|------|--------|
| `exact` | 完全匹配 | 1.0 |
| `alias` | 别名匹配 | 0.95 |
| `rule` | 规则匹配（后缀/缩写） | 0.85 |
| `fuzzy` | 模糊匹配（编辑距离） | 0.6-0.8 |

## 数据覆盖

当前版本包含：

- **7825 家企业实体** ✅ (100% 中文名 - 英文名对齐)
- **A 股上市公司**: 完整覆盖
- **港股上市公司**: 完整覆盖
- **中概股**: SEC EDGAR 数据
- **独角兽品牌**: 手动验证
- **知名企业**: 手动验证

## API 文档

### `resolve(name, top_k=5)`

匹配企业名称。

**参数**:
- `name` (str): 企业名称（中文或英文）
- `top_k` (int): 返回结果数量，默认 5

**返回**: `List[MatchResult]`

### `search(query, limit=10)`

模糊搜索企业名称。

**参数**:
- `query` (str): 搜索关键词
- `limit` (int): 返回结果数量，默认 10

**返回**: `List[MatchResult]`

### `resolve_batch(names, top_k=5)`

批量匹配企业名称。

**参数**:
- `names` (List[str]): 企业名称列表
- `top_k` (int): 每个名称返回结果数量

**返回**: `Dict[str, List[MatchResult]]`

### `MatchResult`

匹配结果对象。

```python
@dataclass
class MatchResult:
    entity_id: str      # 实体 ID
    name_cn: str        # 中文名称
    name_en: str        # 英文名称
    confidence: float   # 置信度 (0.0-1.0)
    aliases: List[str]  # 别名列表
    match_type: str     # 匹配类型
```

## 示例企业

| 中文名 | 英文名 | 别名 |
|--------|--------|------|
| 华为技术有限公司 | Huawei Technologies Co., Ltd. | 华为、HUAWEI |
| 腾讯控股有限公司 | Tencent Holdings Limited | 腾讯、微信、QQ、Tencent |
| 阿里巴巴集团控股有限公司 | Alibaba Group Holding Limited | 阿里、淘宝、天猫、Alibaba |
| 北京字节跳动科技有限公司 | Beijing ByteDance Technology Co., Ltd. | 字节跳动、抖音、TikTok、今日头条 |
| 小米科技有限责任公司 | Xiaomi Technology Co., Ltd. | 小米、MI、Xiaomi |

## 开发

```bash
# 克隆仓库
git clone https://github.com/janseling/matchina.git
cd matchina

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 类型检查
mypy matchina

# 代码检查
ruff check matchina
```

## 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)

## 更新日志

### v0.2.1 (2026-03-21)

- 🎉 数据量提升至 **7825 家企业** (100% 英文名补全)
- ✅ A 股、港股、中概股完整覆盖
- 🔒 代码规范化：移除数据采集脚本，仅保留匹配算法
- 📊 新增 5% 测试用例 (391 条) 用于质量验证
- ⚡ 匹配性能优化 < 100ms

### v0.1.0 (2026-03-14)

- 首次发布
- 支持 1132 家企业实体
- 四层匹配策略
- 中英文支持

---

**Matchina** - Match China, Match Enterprise Names.
