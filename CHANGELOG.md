# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2026-04-09

### Added
- 港股数据完善：2742 条港股数据补全简称 (100% 中文简称, 98% 英文简称)
- 数据库同步：matchina-engine → matchina 数据同步流程

### Changed
- 版本从 0.2.3 升级到 0.2.4

## [0.2.3] - 2026-03-21

### Changed
- 删除 GitHub Actions CI 配置
- 清理测试文件中的内部架构代码
- 简化测试文件结构

## [0.2.2] - 2026-03-21

### Fixed
- 恢复完整 README 文档结构 (特性/安装/API/示例)
- 修复文档链接 (xxx → janseling)
- 移除内部架构信息
- 清理敏感代码 (爬虫/清洗脚本)

### Changed
- 版本从 0.2.1 升级到 0.2.2

## [0.2.1] - 2026-03-21

### Fixed
- 修复文档链接 (xxx → janseling)
- 移除内部架构信息
- 清理敏感代码 (爬虫/清洗脚本)

### Changed
- 版本从 0.2.0 升级到 0.2.1

## [0.2.0] - 2026-03-21

### Added
- 7825 家企业实体数据库
- 模糊匹配算法 (Jaro-Winkler + 拼音)
- 股票代码搜索
- 繁简转换支持
- PyPI 发布 (pip install matchina)

### Changed
- 版本从 0.1.x 升级到 0.2.0
