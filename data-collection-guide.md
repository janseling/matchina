# Matchina 数据采集使用指南

本指南说明如何使用 Matchina 项目的数据采集脚本从公开数据源采集企业中英文名称数据。

**项目**: Matchina (原 cn-entity-resolver)  
**PyPI**: `matchina`  
**导入**: `from matchina import resolve, search`

---

## 一、快速开始

### 1.1 安装依赖

```bash
cd ~/Projects/matchina

# 安装核心依赖
pip install akshare opencc fuzzywuzzy python-Levenshtein

# 或使用项目依赖（如果已配置）
pip install -e .
```

### 1.2 数据采集流程

```bash
# 1. 采集数据（从 AkShare、港交所、SEC EDGAR）
python scripts/collect_data.py

# 2. 清洗数据（标准化、去重、验证）
python scripts/clean_data.py

# 3. 导入数据库（SQLite）
python scripts/import_to_db.py
```

---

## 二、脚本说明

### 2.1 collect_data.py - 数据采集脚本

从多个公开数据源采集企业中英文名称数据。

**支持数据源**:
- **AkShare**: A 股上市公司（完全免费，开源）
- **港交所披露易**: 港股上市公司（官方公开）
- **SEC EDGAR**: 美股中概股（官方公开）

**输出格式**:
```json
{
  "company_id": "H00700",
  "name_cn_full": "腾讯控股有限公司",
  "name_en_full": "Tencent Holdings Limited",
  "name_short": "腾讯",
  "stock_code": "00700.HK",
  "stock_exchange": "HKEX",
  "data_source": "HKEX 披露易",
  "quality_level": "L1",
  "confidence_score": 1.0,
  "collected_at": "2026-03-14T19:00:00"
}
```

**使用方法**:
```bash
# 测试模式（每个数据源采集 5 条）
python scripts/collect_data.py

# 生产模式（修改脚本中的 limit_per_source 参数）
# 编辑 collect_data.py，修改：
# collector.collect_all(limit_per_source=100)
```

**输出文件**:
- `data/collected_data.json` - JSON 格式原始数据
- `data/collected_data.csv` - CSV 格式原始数据

### 2.2 clean_data.py - 数据清洗脚本

对采集的原始数据进行清洗和标准化。

**功能**:
- ✅ **名称标准化**: 繁简转换、去除首尾空格、统一格式
- ✅ **去后缀**: 自动识别并去除公司后缀（有限公司、Limited 等）
- ✅ **格式验证**: 检查长度、字符集、必填字段
- ✅ **去重**: 基于企业 ID 和模糊匹配去重
- ✅ **质量评分**: 计算数据可信度评分

**质量等级**:
| 等级 | 说明 | 来源 |
|------|------|------|
| L1 | 官方匹配 | 年报/官网明确披露 |
| L2 | 证券匹配 | 交易所披露 |
| L3 | 市场公认 | 多家权威媒体一致 |
| L4 | 推测匹配 | 音译/意译，需人工审核 |

**使用方法**:
```bash
python scripts/clean_data.py
```

**输出文件**:
- `data/cleaned/cleaned_data.json` - 清洗后的数据
- `data/cleaned/cleaning_report.json` - 清洗报告（统计信息）

### 2.3 import_to_db.py - 数据导入脚本

将清洗后的数据导入 SQLite 数据库。

**功能**:
- ✅ 创建数据库表结构
- ✅ 批量导入记录
- ✅ 增量更新（比较更新时间）
- ✅ 版本管理
- ✅ 统计查询

**数据库表**:
- `companies` - 企业基本信息
- `company_aliases` - 企业别名/简称
- `data_versions` - 数据版本记录

**使用方法**:
```bash
python scripts/import_to_db.py
```

**输出文件**:
- `data/matchina.db` - SQLite 数据库

---

## 三、数据源详解

### 3.1 AkShare（A 股）

**特点**:
- 完全开源免费，无需 API key
- 覆盖全部 A 股上市公司（约 5000 家）
- 实时更新

**代码示例**:
```python
import akshare as ak

# 获取 A 股上市公司列表
stock_df = ak.stock_info_a_code_name()

# 获取公司详细信息
# 注意：需要调用更详细的 API 获取英文名
```

**字段映射**:
- 股票代码 → `stock_code`
- 公司全称 → `name_cn_full`
- 英文名称 → `name_en_full`（需补充）

### 3.2 港交所披露易（港股）

**特点**:
- 官方公开数据，权威性高
- 覆盖全部港股上市公司（约 2500 家）
- 包含中英文官方名称

**访问方式**:
- 网站：https://www.hkexnews.hk
- 需要 HTML 解析或 API 封装

**字段映射**:
- 股票代码 → `stock_code` (00700.HK 格式)
- 公司中文名称 → `name_cn_full`
- 公司英文名称 → `name_en_full`

### 3.3 SEC EDGAR（中概股）

**特点**:
- 美国 SEC 官方数据
- 覆盖全部美股上市公司
- 中概股有中文名称披露

**访问方式**:
- API: https://www.sec.gov/edgar
- 需要遵守速率限制（<10 请求/秒）

**字段映射**:
- 股票代码 → `stock_code` (BABA, JD, PDD 等)
- 注册名称 → `name_en_full`
- 中文名称 → `name_cn_full`（需从年报提取）

---

## 四、数据质量标准

### 4.1 名称格式规范

**中文名称**:
- 长度：5-50 字符
- 字符集：中文汉字、字母、数字、空格、`（）《》""、&`
- 示例：`腾讯控股有限公司`

**英文名称**:
- 长度：5-100 字符
- 字符集：A-Z、a-z、0-9、空格、`.,&-'()`
- 格式：首字母大写（除非全大写是官方格式）
- 示例：`Tencent Holdings Limited`

### 4.2 验证规则

```python
# 格式验证
is_valid, errors = validate_format(record)

# 长度检查
5 <= len(cn_name) <= 50
5 <= len(en_name) <= 100

# 字符集检查
CN_ILLEGAL_PATTERN = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9 ()《》""&·]')
EN_ILLEGAL_PATTERN = re.compile(r'[^a-zA-Z0-9 .,&\'\-()]')
```

### 4.3 可信度评分

| 来源 | 可信度 | 权重 |
|------|--------|------|
| 官方年报/招股书 | ⭐⭐⭐⭐⭐ | 1.0 |
| 交易所披露 | ⭐⭐⭐⭐⭐ | 1.0 |
| 公司官网 | ⭐⭐⭐⭐ | 0.9 |
| 维基百科（有引用） | ⭐⭐⭐⭐ | 0.8 |
| 权威媒体报道 | ⭐⭐⭐ | 0.7 |

---

## 五、合规性说明

### 5.1 合规数据源

✅ **推荐使用**:
- AkShare（开源 MIT 协议）
- 港交所披露易（官方公开）
- SEC EDGAR（官方公开）
- 公司官网/年报（公开披露）
- 维基百科（CC-BY-SA）

### 5.2 使用限制

❌ **禁止**:
- 绕过付费墙/登录验证爬取数据
- 违反 robots.txt 的大规模爬取
- 将商业数据库数据转售或二次分发
- 未注明来源的版权内容

### 5.3 最佳实践

1. **设置请求延迟**: `<1 请求/秒`
2. **注明数据来源**: 尤其是榜单、报告
3. **遵守 robots.txt**: 检查网站爬取协议
4. **仅存储企业名称**: 不涉及经营数据、财务数据
5. **建立 takedown 机制**: 收到投诉及时删除

---

## 六、输出数据 Schema

### 6.1 企业记录

```json
{
  "company_id": "H00700",
  "name_cn_full": "腾讯控股有限公司",
  "name_cn_short": "腾讯控股",
  "name_en_full": "Tencent Holdings Limited",
  "name_en_short": "TENCENT",
  "stock_code": "00700.HK",
  "stock_exchange": "HKEX",
  "data_source": "HKEX 披露易",
  "quality_level": "L1",
  "confidence_score": 1.0,
  "quality_score": 0.95,
  "version": "1.0",
  "collected_at": "2026-03-14T19:00:00",
  "cleaned_at": "2026-03-14T19:30:00"
}
```

### 6.2 别名记录

```json
{
  "company_id": "H00700",
  "alias_type": "别名",
  "alias_name": "腾讯",
  "language": "zh",
  "source": "媒体报道",
  "confidence_score": 0.7
}
```

---

## 七、常见问题

### Q1: 采集速度慢怎么办？

**A**: 请求延迟是合规要求，建议：
- 使用多线程采集（注意速率限制）
- 批量采集而非单条请求
- 夜间低峰期采集

### Q2: 英文名为空怎么办？

**A**: AkShare 部分数据缺少英文名，建议：
- 从公司官网补充
- 从年报/招股书提取
- 使用音译规则生成（标记为 L4）

### Q3: 如何验证数据质量？

**A**: 查看清洗报告：
```bash
cat data/cleaned/cleaning_report.json
```

关注：
- 质量等级分布（L1 占比越高越好）
- 数据源分布（官方源占比）
- 验证通过率

### Q4: 数据库如何查询？

**A**: 使用 SQLite 命令：
```bash
sqlite3 data/matchina.db

# 查询所有企业
SELECT * FROM companies LIMIT 10;

# 按质量等级筛选
SELECT * FROM companies WHERE quality_level = 'L1';

# 搜索企业
SELECT * FROM companies WHERE name_cn_full LIKE '%腾讯%';
```

---

## 八、扩展开发

### 8.1 添加新数据源

1. 在 `collect_data.py` 中添加新方法：
```python
def collect_from_new_source(self, limit: int = 10) -> List[Dict]:
    """采集新数据源"""
    # 实现采集逻辑
    pass
```

2. 在 `collect_all()` 中调用新方法

3. 更新数据源合规性评估

### 8.2 添加新清洗规则

1. 在 `clean_data.py` 中添加新方法：
```python
def new_normalization(self, name: str) -> str:
    """新标准化规则"""
    pass
```

2. 在 `clean()` 流程中调用

### 8.3 导出到其他格式

```python
# 导出到 CSV
importer.export_to_csv("data/export.csv")

# 导出到 Excel
importer.export_to_excel("data/export.xlsx")
```

---

## 九、版本管理

### 9.1 数据版本

- 版本号：`vYYYYMMDD-NNN` 格式
- 每次导入创建新版本记录
- 保留至少 3 个历史版本

### 9.2 回滚机制

```bash
# 查看版本列表
sqlite3 data/matchina.db "SELECT * FROM data_versions ORDER BY created_at DESC"

# 回滚到指定版本（需要实现）
python scripts/rollback.py --version v20260314-001
```

---

## 十、贡献指南

### 10.1 数据贡献

1. Fork 项目
2. 添加新数据源或清洗规则
3. 运行测试确保质量
4. 提交 PR

### 10.2 错误报告

- 使用 GitHub Issues
- 提供企业名称和错误详情
- 附上数据来源链接

### 10.3 许可证

- 代码：MIT License
- 数据：ODbL (Open Database License)

---

**文档版本**: v1.0  
**更新日期**: 2026-03-14  
**项目**: Matchina  
**许可证**: CC-BY 4.0
