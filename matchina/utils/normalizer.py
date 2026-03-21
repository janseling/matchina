"""
名称标准化工具
"""

import re

# 常见公司后缀（中文）
CN_SUFFIXES = [
    "有限公司", "有限责任公司", "股份有限公司", "集团", "公司",
    "控股有限公司", "控股集团", "技术有限公司", "科技有限公司",
    "网络技术有限公司", "信息技术有限公司", "互联网有限公司",
]

# 常见公司后缀（英文）
EN_SUFFIXES = [
    "Co., Ltd.", "Co.,Ltd.", "Co. Ltd.", "Co Ltd",
    "Ltd.", "Ltd", "Limited",
    "Inc.", "Inc", "Incorporated",
    "Corp.", "Corp", "Corporation",
    "LLC", "L.L.C.",
    "Group", "Holdings", "Holdings Ltd.",
    "Technology", "Technologies", "Tech",
    "International", "Intl",
]

# 繁简转换表（常用字）
TRADITIONAL_TO_SIMPLIFIED = {
    "集團": "集团", "有限公司": "有限公司",  # 相同
    "資訊": "资讯", "網絡": "网络", "技術": "技术",
    "電子": "电子", "電腦": "电脑", "通訊": "通讯",
}


def normalize(
    name: str,
    remove_suffix: bool = True,
    to_lowercase: bool = False,
    convert_traditional: bool = True,
) -> str:
    """
    标准化企业名称

    Args:
        name: 原始名称
        remove_suffix: 是否移除公司后缀
        to_lowercase: 是否转小写
        convert_traditional: 是否繁简转换

    Returns:
        标准化后的名称
    """
    if not name:
        return ""

    result = name.strip()

    # 繁简转换
    if convert_traditional:
        result = _convert_traditional(result)

    # 移除公司后缀
    if remove_suffix:
        result = _remove_suffixes(result)

    # 转小写
    if to_lowercase:
        result = result.lower()

    # 移除多余空格
    result = " ".join(result.split())

    return result


def _convert_traditional(text: str) -> str:
    """繁简转换"""
    for trad, simp in TRADITIONAL_TO_SIMPLIFIED.items():
        text = text.replace(trad, simp)
    return text


def _remove_suffixes(name: str) -> str:
    """移除公司后缀"""
    result = name

    # 中文后缀
    for suffix in CN_SUFFIXES:
        if result.endswith(suffix):
            result = result[: -len(suffix)]
            break

    # 英文后缀（不区分大小写）
    name_lower = result.lower()
    for suffix in EN_SUFFIXES:
        if name_lower.endswith(suffix.lower()):
            result = result[: -len(suffix)]
            break

    return result.strip()


def normalize_for_comparison(name: str) -> str:
    """
    用于比较的标准化

    更激进的标准化，用于匹配比较
    """
    if not name:
        return ""

    result = normalize(name, remove_suffix=True, to_lowercase=True)

    # 移除标点
    result = re.sub(r"[^\w\s]", "", result)

    # 移除空格
    result = result.replace(" ", "")

    return result


def extract_keywords(name: str) -> list[str]:
    """
    提取名称中的关键词

    Args:
        name: 企业名称

    Returns:
        关键词列表
    """
    normalized = normalize(name, remove_suffix=True)
    # 简单分词：按空格和常见分隔符
    words = re.split(r"[\s\-_]+", normalized)
    return [w for w in words if w and len(w) > 1]
words if w and len(w) > 1]
 return [w for w in words if w and len(w) > 1]
