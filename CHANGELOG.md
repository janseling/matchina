# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-21

### Added
- 🎉 **7825 家企业实体** (100% 中文名 - 英文名对齐完成)
- A 股、港股、中概股、独角兽、知名企业完整覆盖
- 5% 测试用例 (391 条) 用于质量验证
- 测试覆盖率提升

### Changed
- 🔒 **代码规范化**: 移除数据采集脚本，仅保留匹配算法
- 数据量从 1132 提升至 7825 家企业 (+591%)
- 测试用例从手动编写升级为数据驱动
- 匹配性能优化 < 100ms

### Removed
- 数据采集脚本
- 临时目录和备份文件

### Security
- 敏感代码移至私有项目
- 开源项目仅保留匹配算法和数据
- 日志目录加入 `.gitignore`

### Fixed
- 数据完整性验证 (100% 英文名补全)
- 测试用例随机种子固定 (可复现)

---

## [0.1.0] - 2026-03-14

## [0.1.0] - 2026-03-14

### Added
- 四层匹配策略（精确匹配、别名匹配、规则匹配、模糊匹配）
- 中英文企业名称匹配支持
- 别名/简称识别
- 批量匹配功能 `resolve_batch()`
- 模糊搜索功能 `search()`
- 完整的类型注解和 mypy 支持
- 约 30+ 企业数据（中文、英文、别名）
- 单元测试覆盖核心功能
- MIT 许可证

### Technical Stack
- Python 3.8+
- pytest 测试框架
- mypy 类型检查
- ruff 代码检查
- setuptools 构建系统

### Data Format
- SQLite 数据库存储企业数据
- JSON 别名映射表
- 离线数据，无需网络连接

### API
- `resolve(name, top_k=5)` - 单个名称匹配
- `search(query, limit=10)` - 模糊搜索
- `resolve_batch(names, top_k=5)` - 批量匹配
- `EntityMatcher` 类接口
- `Entity` 数据模型
- `MatchResult` 结果对象

### Performance
- 批量匹配优化
- 懒加载全局 matcher 实例
- 缓存匹配结果

### Documentation
- 快速开始指南
- API 文档
- 示例代码
- 匹配策略说明

---

## Version History

- **0.1.0** (2026-03-14) - Initial release (Matchina)

---

## Upcoming

### Planned Features
- 更多企业数据（目标 100+）
- 拼音匹配支持
- 行业分类过滤
- 置信度阈值配置
- 自定义数据加载
- 性能优化（缓存、索引）

### Future Considerations
- 异步 API 支持
- 增量数据更新
- 企业关联关系
- 行业知识图谱
