# Matchina

English | [中文](README.md)

A Python library for matching Chinese enterprise names in both Chinese and English. Supports exact matching, alias matching, and fuzzy search. Works offline with no network required.

## Features

- 🔍 **4-Layer Matching Strategy**: Exact → Alias → Rule-based → Fuzzy
- 🇨🇳 **Bilingual Support**: Both Chinese and English names
- 📦 **Offline Usage**: All data bundled, no network needed
- ⚡ **High Performance**: < 100ms per match
- 🐍 **Python 3.8+**: Supports Python 3.8 and above

## Installation

```bash
pip install matchina
```

## Quick Start

```python
from matchina import resolve, search, resolve_batch

# Exact match
result = resolve("华为")
print(result[0].name_cn)      # 华为技术有限公司
print(result[0].name_en)      # Huawei Technologies Co., Ltd.
print(result[0].confidence)   # 1.0

# English match
result = resolve("Alibaba")
print(result[0].name_cn)       # 阿里巴巴集团控股有限公司

# Alias match
result = resolve("抖音")
print(result[0].name_cn)       # 北京字节跳动科技有限公司
print(result[0].confidence)    # 0.95

# Batch match
names = ["腾讯", "百度", "小米", "比亚迪"]
results = resolve_batch(names)
for name, matches in results.items():
    if matches:
        print(f"{name} → {matches[0].name_cn}")

# Fuzzy search
results = search("科技", limit=5)
for r in results:
    print(f"{r.name_cn} (confidence: {r.confidence:.2f})")
```

## Matching Strategy

| Match Type | Description | Confidence |
|------------|-------------|------------|
| `exact` | Exact match | 1.0 |
| `alias` | Alias match | 0.95 |
| `rule` | Rule-based (suffix/abbreviation) | 0.85 |
| `fuzzy` | Fuzzy match (edit distance) | 0.6-0.8 |

## Data Coverage

Current version includes:

- **1132 enterprise entities**
- **112 enterprise aliases**
- Coverage: A-shares, HK stocks, US-listed Chinese companies, unicorns, notable brands

## API Reference

### `resolve(name, top_k=5)`

Match enterprise name.

**Parameters**:
- `name` (str): Enterprise name (Chinese or English)
- `top_k` (int): Number of results to return, default 5

**Returns**: `List[MatchResult]`

### `search(query, limit=10)`

Fuzzy search enterprise names.

**Parameters**:
- `query` (str): Search keyword
- `limit` (int): Number of results to return, default 10

**Returns**: `List[MatchResult]`

### `resolve_batch(names, top_k=5)`

Batch match enterprise names.

**Parameters**:
- `names` (List[str]): List of enterprise names
- `top_k` (int): Number of results per name

**Returns**: `Dict[str, List[MatchResult]]`

### `MatchResult`

Match result object.

```python
@dataclass
class MatchResult:
    entity_id: str      # Entity ID
    name_cn: str        # Chinese name
    name_en: str        # English name
    confidence: float   # Confidence score (0.0-1.0)
    aliases: List[str]  # List of aliases
    match_type: str     # Match type
```

## Example Enterprises

| Chinese Name | English Name | Aliases |
|--------------|--------------|---------|
| 华为技术有限公司 | Huawei Technologies Co., Ltd. | 华为、HUAWEI |
| 腾讯控股有限公司 | Tencent Holdings Limited | 腾讯、微信、QQ、Tencent |
| 阿里巴巴集团控股有限公司 | Alibaba Group Holding Limited | 阿里、淘宝、天猫、Alibaba |
| 北京字节跳动科技有限公司 | Beijing ByteDance Technology Co., Ltd. | 字节跳动、抖音、TikTok、今日头条 |
| 小米科技有限责任公司 | Xiaomi Technology Co., Ltd. | 小米、MI、Xiaomi |

## Development

```bash
# Clone repository
git clone https://github.com/xxx/matchina.git
cd matchina

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy matchina

# Lint
ruff check matchina
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[MIT License](LICENSE)

## Changelog

### v0.2.0 (2026-03-21)

- 🎉 Data expanded to **7825 enterprises** (100% English name completion)
- ✅ Complete A-share, HK stock, US-listed coverage
- 🔒 Code cleanup: removed data collection scripts, kept only matching algorithms
- 📊 Added 5% test samples (391 records) for quality validation
- ⚡ Match performance optimized to < 100ms

### v0.1.0 (2026-03-14)

- Initial release
- 1132 enterprise entities
- 4-layer matching strategy
- Bilingual support (Chinese/English)

---

**Matchina** - Match China, Match Enterprise Names.