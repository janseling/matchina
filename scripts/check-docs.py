#!/usr/bin/env python3
"""
Matchina 发布前文档检查脚本
符合四套班子流程规范
"""

import sys
from pathlib import Path

def check_readme(path: Path) -> bool:
    """检查 README 完整性"""
    if not path.exists():
        print(f"❌ {path} 不存在")
        return False
    
    content = path.read_text(encoding='utf-8')
    
    # 必检章节
    required_sections = [
        "## 特性",
        "## 安装",
        "## 快速开始",
        "## API",
        "## 数据覆盖",
    ]
    
    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)
    
    if missing:
        print(f"❌ {path.name} 缺失章节: {missing}")
        return False
    
    print(f"✅ {path.name} 完整性检查通过")
    return True

def check_changelog(path: Path) -> bool:
    """检查 CHANGELOG 版本记录"""
    if not path.exists():
        print(f"❌ {path} 不存在")
        return False
    
    content = path.read_text(encoding='utf-8')
    
    if "## [0.2." not in content:
        print(f"❌ {path.name} 缺少新版本记录")
        return False
    
    print(f"✅ {path.name} 版本记录检查通过")
    return True

def check_internal_info(paths: list) -> bool:
    """检查内部信息（四套班子）"""
    forbidden_keywords = [
        "四套班子",
        "党委",
        "人大",
        "政府",
        "政协",
        "留痕系统",
    ]
    
    found = []
    for path in paths:
        if not path.exists():
            continue
        content = path.read_text(encoding='utf-8')
        for keyword in forbidden_keywords:
            if keyword in content:
                found.append((path.name, keyword))
    
    if found:
        print(f"❌ 发现内部信息: {found}")
        return False
    
    print(f"✅ 内部信息检查通过")
    return True

def check_github_link(paths: list) -> bool:
    """检查 GitHub 链接"""
    wrong_link = "github.com/xxx"
    correct_link = "github.com/janseling"
    
    found = []
    for path in paths:
        if not path.exists():
            continue
        content = path.read_text(encoding='utf-8')
        if wrong_link in content:
            found.append(path.name)
    
    if found:
        print(f"❌ 错误 GitHub 链接 ({wrong_link}) 在: {found}")
        return False
    
    print(f"✅ GitHub 链接检查通过")
    return True

def main():
    """主检查流程"""
    print("="*60)
    print("Matchina 发布前文档检查")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    # 检查列表
    checks = [
        ("README.md", check_readme, [project_root / "README.md"]),
        ("README_en.md", check_readme, [project_root / "README_en.md"]),
        ("CHANGELOG.md", check_changelog, [project_root / "CHANGELOG.md"]),
        ("内部信息", check_internal_info, [
            project_root / "README.md",
            project_root / "README_en.md",
            project_root / "CHANGELOG.md",
        ]),
        ("GitHub 链接", check_github_link, [
            project_root / "README.md",
            project_root / "README_en.md",
            project_root / "pyproject.toml",
        ]),
    ]
    
    passed = 0
    failed = 0
    
    for name, check_func, paths in checks:
        if check_func(*paths):
            passed += 1
        else:
            failed += 1
    
    print("="*60)
    print(f"检查结果：{passed} 通过，{failed} 失败")
    print("="*60)
    
    if failed > 0:
        print("❌ 发布前检查失败，请修复后再提交")
        sys.exit(1)
    else:
        print("✅ 发布前检查通过，可以提交")
        sys.exit(0)

if __name__ == "__main__":
    main()
