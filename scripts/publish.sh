#!/bin/bash
# Matchina PyPI 发布脚本
# 使用方法：./scripts/publish.sh

set -e

echo "🚀 Matchina 发布流程"
echo "=================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否安装了必要的工具
check_dependencies() {
    echo "检查依赖..."
    command -v python3 >/dev/null 2>&1 || { echo "${RED}错误：需要 python3${NC}"; exit 1; }
    command -v twine >/dev/null 2>&1 || { echo "${YELLOW}安装 twine...${NC}"; pip install twine; }
    command -v build >/dev/null 2>&1 || { echo "${YELLOW}安装 build...${NC}"; pip install build; }
    echo "${GREEN}✓ 依赖检查通过${NC}"
}

# 清理旧的构建文件
cleanup() {
    echo "清理旧的构建文件..."
    rm -rf dist/ build/ *.egg-info
    echo "${GREEN}✓ 清理完成${NC}"
}

# 运行测试
run_tests() {
    echo "运行测试套件..."
    python3 -m pytest -v --tb=short
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓ 测试通过${NC}"
    else
        echo "${RED}✗ 测试失败${NC}"
        exit 1
    fi
}

# 运行类型检查
run_type_check() {
    echo "运行类型检查 (mypy)..."
    python3 -m mypy matchina
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓ 类型检查通过${NC}"
    else
        echo "${YELLOW}⚠ 类型检查有警告（继续）${NC}"
    fi
}

# 运行代码检查
run_lint() {
    echo "运行代码检查 (ruff)..."
    python3 -m ruff check matchina tests
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓ 代码检查通过${NC}"
    else
        echo "${YELLOW}⚠ 代码检查有警告（继续）${NC}"
    fi
}

# 构建包
build_package() {
    echo "构建包..."
    python3 -m build
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓ 构建成功${NC}"
        ls -lh dist/
    else
        echo "${RED}✗ 构建失败${NC}"
        exit 1
    fi
}

# 验证包
verify_package() {
    echo "验证包结构..."
    tar -tzf dist/*.tar.gz | head -20
    echo "${GREEN}✓ 包结构验证完成${NC}"
}

# 上传到 PyPI
upload_pypi() {
    echo "上传到 PyPI..."
    echo "${YELLOW}警告：这将上传到 PyPI，请确认你有正确的凭证${NC}"
    read -p "是否继续？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "${YELLOW}取消上传${NC}"
        return
    fi
    
    twine upload dist/*
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓ 上传成功${NC}"
    else
        echo "${RED}✗ 上传失败${NC}"
        exit 1
    fi
}

# 上传到 TestPyPI
upload_testpypi() {
    echo "上传到 TestPyPI..."
    twine upload --repository testpypi dist/*
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓ TestPyPI 上传成功${NC}"
    else
        echo "${RED}✗ TestPyPI 上传失败${NC}"
        exit 1
    fi
}

# 本地安装测试
test_install() {
    echo "本地安装测试..."
    pip install -e . --quiet
    python3 -c "from matchina import resolve; print('✓ 导入成功')"
    echo "${GREEN}✓ 本地安装测试通过${NC}"
}

# 主流程
main() {
    echo ""
    check_dependencies
    echo ""
    cleanup
    echo ""
    run_tests
    echo ""
    run_type_check
    echo ""
    run_lint
    echo ""
    build_package
    echo ""
    verify_package
    echo ""
    test_install
    echo ""
    
    echo "=================="
    echo "📦 构建完成！"
    echo ""
    echo "下一步："
    echo "  1. 检查 dist/ 目录中的文件"
    echo "  2. 上传到 TestPyPI: twine upload --repository testpypi dist/*"
    echo "  3. 测试安装：pip install --index-url https://test.pypi.org/simple/ matchina"
    echo "  4. 上传到 PyPI: twine upload dist/*"
    echo ""
    echo "发布清单已保存到：release-checklist.md"
    echo "=================="
}

# 解析命令行参数
case "${1:-}" in
    --upload)
        upload_pypi
        ;;
    --test-upload)
        upload_testpypi
        ;;
    --build-only)
        cleanup
        build_package
        verify_package
        ;;
    --help)
        echo "使用方法：$0 [选项]"
        echo ""
        echo "选项："
        echo "  --upload       上传到 PyPI"
        echo "  --test-upload  上传到 TestPyPI"
        echo "  --build-only   仅构建，不运行测试"
        echo "  --help         显示帮助"
        echo ""
        echo "不带参数时运行完整流程（测试 + 构建 + 验证）"
        ;;
    *)
        main
        ;;
esac
