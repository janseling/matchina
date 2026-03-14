"""
使用示例
"""

from cn_entity_resolver import resolve, search, resolve_batch


def main():
    print("=" * 60)
    print("cn-entity-resolver 使用示例")
    print("=" * 60)

    # 1. 精确匹配
    print("\n1. 精确匹配")
    print("-" * 40)

    result = resolve("华为技术有限公司")
    if result:
        print(f"输入: 华为技术有限公司")
        print(f"匹配: {result[0].name_cn}")
        print(f"英文: {result[0].name_en}")
        print(f"置信度: {result[0].confidence}")
        print(f"匹配类型: {result[0].match_type}")

    # 2. 英文匹配
    print("\n2. 英文匹配")
    print("-" * 40)

    result = resolve("Alibaba")
    if result:
        print(f"输入: Alibaba")
        print(f"匹配: {result[0].name_cn}")
        print(f"英文: {result[0].name_en}")
        print(f"置信度: {result[0].confidence}")

    # 3. 别名匹配
    print("\n3. 别名匹配")
    print("-" * 40)

    result = resolve("抖音")
    if result:
        print(f"输入: 抖音")
        print(f"匹配: {result[0].name_cn}")
        print(f"置信度: {result[0].confidence}")
        print(f"匹配类型: {result[0].match_type}")

    result = resolve("微信")
    if result:
        print(f"输入: 微信")
        print(f"匹配: {result[0].name_cn}")
        print(f"置信度: {result[0].confidence}")

    # 4. 批量匹配
    print("\n4. 批量匹配")
    print("-" * 40)

    names = ["腾讯", "百度", "小米", "比亚迪", "蔚来"]
    results = resolve_batch(names)

    for name, matches in results.items():
        if matches:
            print(f"{name} → {matches[0].name_cn} (置信度: {matches[0].confidence:.2f})")
        else:
            print(f"{name} → 无匹配")

    # 5. 模糊搜索
    print("\n5. 模糊搜索")
    print("-" * 40)

    results = search("科技", limit=5)
    for r in results:
        print(f"{r.name_cn} (置信度: {r.confidence:.2f})")

    print("\n" + "=" * 60)
    print("示例完成")


if __name__ == "__main__":
    main()