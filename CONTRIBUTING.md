# 贡献指南

感谢你对 Matchina 的关注！欢迎贡献代码、文档、测试或数据。

## 如何贡献

### 1. 报告问题

在 GitHub Issues 中报告 bug 或提出功能请求：
- 描述清楚问题
- 提供复现步骤
- 附上预期行为和实际行为

### 2. 提交代码

#### Fork 仓库

```bash
git clone https://github.com/YOUR_USERNAME/matchina.git
cd matchina
```

#### 创建开发环境

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -e ".[dev]"
```

#### 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-123
```

### 3. 开发流程

1. **编写代码**：遵循现有代码风格
2. **添加测试**：确保新功能有测试覆盖
3. **运行检查**：
   ```bash
   # 运行测试
   pytest
   
   # 类型检查
   mypy matchina
   
   # 代码风格检查
   ruff check matchina tests
   
   # 格式化代码
   ruff format matchina tests
   ```
4. **提交更改**：
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### 4. 提交 Pull Request

1. 推送分支到 GitHub
2. 在原始仓库创建 Pull Request
3. 描述更改内容和原因
4. 等待代码审查

### 5. 添加企业数据

如果要添加新的企业数据：

1. 在 `data/` 目录中添加数据文件
2. 更新 `matchina/data/storage.py` 加载新数据
3. 添加测试验证数据正确性
4. 在文档中说明数据来源

## 代码规范

### 命名约定

- 变量/函数：`snake_case`
- 类：`PascalCase`
- 常量：`UPPER_CASE`
- 私有方法：`_prefix`

### 文档规范

- 所有公共函数/类必须有 docstring
- 使用 Google 风格 docstring
- 包含 Example 部分

### 类型注解

- 所有函数必须有类型注解
- 使用 `typing` 模块
- 运行 mypy 确保类型正确

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构（既不修复 bug也不添加功能）
test: 添加测试
chore: 构建/工具/配置
```

示例：
```bash
git commit -m "feat: add batch processing support"
git commit -m "fix: resolve fuzzy match edge case"
git commit -m "docs: update API documentation"
```

## 测试要求

### 单元测试

- 新功能必须有单元测试
- 保持测试覆盖率
- 测试边界情况和错误处理

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_matcher.py -v

# 查看覆盖率
pytest --cov=matchina
```

## 发布流程

维护者发布新版本：

1. 更新 `CHANGELOG.md`
2. 更新版本号 `matchina/__version__.py`
3. 创建 release tag
4. 运行发布脚本
5. 上传到 PyPI

详见发布流程文档。

## 社区准则

- 尊重他人，友好交流
- 对事不对人
- 欢迎不同背景的贡献者
- 遵守开源社区最佳实践

## 联系方式

- GitHub Issues: 问题和讨论
- Email: 联系维护者

感谢你的贡献！🎉
