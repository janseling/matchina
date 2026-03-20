# Contributing to Matchina

欢迎贡献代码、报告问题或提出建议！

## 发布前检查流程

在发布新版本之前，必须执行文档检查：

```bash
# 运行文档检查脚本
python scripts/check-docs.py
```

### 检查项目

1. **README.md** - 中文文档完整性
2. **README_en.md** - 英文文档完整性
3. **CHANGELOG.md** - 版本记录
4. **内部信息** - 无四套班子信息
5. **GitHub 链接** - 正确链接 (janseling)

### 禁止事项

- ❌ 文档结构大改动
- ❌ 删除关键章节
- ❌ 包含内部信息
- ❌ 跳过文档检查

### 允许事项

- ✅ 更新数据量
- ✅ 修正链接
- ✅ 移除敏感信息
- ✅ 增加版本记录

## 贡献流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 代码规范

- 遵循 PEP 8 风格指南
- 添加类型注解
- 编写单元测试
- 运行 `ruff check` 和 `mypy` 检查

## 测试

```bash
# 运行测试
pytest

# 类型检查
mypy matchina

# 代码检查
ruff check matchina tests
```

---

感谢你的贡献！
