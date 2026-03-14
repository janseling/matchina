"""
初始化数据库脚本

生成 entities.db 数据库文件
"""

import sqlite3
from pathlib import Path


def create_database(db_path: str) -> None:
    """创建数据库表结构"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 企业实体表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            name_cn TEXT NOT NULL,
            name_en TEXT,
            name_short_cn TEXT,
            name_short_en TEXT,
            status TEXT
        )
    """)

    # 别名表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT NOT NULL,
            alias TEXT NOT NULL,
            FOREIGN KEY (entity_id) REFERENCES entities(id)
        )
    """)

    # 索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_name_cn ON entities(name_cn)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_name_en ON entities(name_en)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alias ON aliases(alias)")

    conn.commit()
    conn.close()


def insert_sample_data(db_path: str) -> None:
    """插入示例数据"""

    # 示例数据：知名出海企业
    entities = [
        # 互联网巨头
        ("alibaba", "阿里巴巴集团控股有限公司", "Alibaba Group Holding Limited", "阿里巴巴", "Alibaba", "active"),
        ("tencent", "腾讯控股有限公司", "Tencent Holdings Limited", "腾讯", "Tencent", "active"),
        ("bytedance", "北京字节跳动科技有限公司", "Beijing ByteDance Technology Co., Ltd.", "字节跳动", "ByteDance", "active"),
        ("baidu", "百度在线网络技术（北京）有限公司", "Baidu Online Network Technology (Beijing) Co., Ltd.", "百度", "Baidu", "active"),
        ("jd", "北京京东世纪贸易有限公司", "Beijing Jingdong Century Trading Co., Ltd.", "京东", "JD.com", "active"),
        ("meituan", "北京三快在线科技有限公司", "Beijing SanKuai Online Technology Co., Ltd.", "美团", "Meituan", "active"),
        ("pinduoduo", "上海寻梦信息技术有限公司", "Shanghai Xunmeng Information Technology Co., Ltd.", "拼多多", "Pinduoduo", "active"),

        # 硬件/电子
        ("huawei", "华为技术有限公司", "Huawei Technologies Co., Ltd.", "华为", "Huawei", "active"),
        ("xiaomi", "小米科技有限责任公司", "Xiaomi Technology Co., Ltd.", "小米", "Xiaomi", "active"),
        ("oppo", "广东欧珀移动通信有限公司", "Guangdong OPPO Mobile Telecommunications Corp., Ltd.", "OPPO", "OPPO", "active"),
        ("vivo", "广东步步高通信科技有限公司", "Guangdong Vivo Mobile Communication Co., Ltd.", "vivo", "vivo", "active"),
        ("lenovo", "联想控股股份有限公司", "Lenovo Group Limited", "联想", "Lenovo", "active"),
        ("zte", "中兴通讯股份有限公司", "ZTE Corporation", "中兴", "ZTE", "active"),

        # 新能源汽车
        ("byd", "比亚迪股份有限公司", "BYD Company Limited", "比亚迪", "BYD", "active"),
        ("nio", "上海蔚来汽车有限公司", "NIO Inc.", "蔚来", "NIO", "active"),
        ("xpeng", "广州小鹏汽车科技有限公司", "XPeng Inc.", "小鹏", "XPeng", "active"),
        ("li_auto", "北京车和家信息技术有限公司", "Li Auto Inc.", "理想汽车", "Li Auto", "active"),

        # 跨境电商
        ("shein", "南京希音电子商务有限公司", "SHEIN", "SHEIN", "SHEIN", "active"),
        ("temu", "拼多多海外版", "Temu", "Temu", "Temu", "active"),
        ("shopee", "深圳市虾皮信息科技有限公司", "Shopee", "Shopee", "Shopee", "active"),
        ("lazada", "来赞达", "Lazada Group", "Lazada", "Lazada", "active"),

        # 游戏
        ("netease", "广州网易计算机系统有限公司", "NetEase, Inc.", "网易", "NetEase", "active"),
        ("taptap", "易玩（上海）网络科技有限公司", "TapTap", "TapTap", "TapTap", "active"),
        ("mihoyo", "上海米哈游网络科技股份有限公司", "miHoYo Co., Ltd.", "米哈游", "miHoYo", "active"),

        # 金融科技
        ("ant_group", "蚂蚁科技集团股份有限公司", "Ant Group Co., Ltd.", "蚂蚁集团", "Ant Group", "active"),
        ("lufax", "陆金所控股有限公司", "Lufax Holding Ltd.", "陆金所", "Lufax", "active"),

        # 物流
        ("sf_express", "顺丰控股股份有限公司", "SF Express Co., Ltd.", "顺丰", "SF Express", "active"),
        ("jd_logistics", "京东物流股份有限公司", "JD Logistics, Inc.", "京东物流", "JD Logistics", "active"),

        # 其他知名企业
        ("didi", "北京小桔科技有限公司", "Beijing Xiaoju Technology Co., Ltd.", "滴滴", "DiDi", "active"),
        ("trip", "携程集团", "Trip.com Group Limited", "携程", "Trip.com", "active"),
        ("bilibili", "上海哔哩哔哩科技有限公司", "Bilibili Inc.", "哔哩哔哩", "Bilibili", "active"),
        ("kuaishou", "北京快手科技有限公司", "Kuaishou Technology", "快手", "Kuaishou", "active"),
    ]

    # 别名数据
    aliases = [
        # 阿里巴巴
        ("alibaba", "阿里"),
        ("alibaba", "淘宝"),
        ("alibaba", "天猫"),
        ("alibaba", "Alibaba"),
        ("alibaba", "阿里巴巴集团"),
        
        # 腾讯
        ("tencent", "腾讯科技"),
        ("tencent", "QQ"),
        ("tencent", "微信"),
        ("tencent", "WeChat"),
        ("tencent", "Tencent"),
        
        # 字节跳动
        ("bytedance", "抖音"),
        ("bytedance", "TikTok"),
        ("bytedance", "今日头条"),
        ("bytedance", "ByteDance"),
        
        # 百度
        ("baidu", "Baidu"),
        ("baidu", "百度搜索"),
        
        # 京东
        ("jd", "京东商城"),
        ("jd", "JD"),
        ("jd", "京东集团"),
        
        # 拼多多
        ("pinduoduo", "PDD"),
        
        # 华为
        ("huawei", "华为科技"),
        ("huawei", "HUAWEI"),
        
        # 小米
        ("xiaomi", "小米手机"),
        ("xiaomi", "MI"),
        
        # OPPO
        ("oppo", "OPPO手机"),
        
        # vivo
        ("vivo", "vivo手机"),
        
        # 比亚迪
        ("byd", "比亚迪汽车"),
        
        # 蔚来
        ("nio", "蔚来汽车"),
        
        # 小鹏
        ("xpeng", "小鹏汽车"),
        
        # 理想
        ("li_auto", "理想"),
        
        # SHEIN
        ("shein", "希音"),
        
        # 网易
        ("netease", "网易游戏"),
        
        # 米哈游
        ("mihoyo", "原神"),
        ("mihoyo", "Honkai"),
        
        # 蚂蚁集团
        ("ant_group", "支付宝"),
        ("ant_group", "Alipay"),
        ("ant_group", "蚂蚁金服"),
        
        # 顺丰
        ("sf_express", "顺丰快递"),
        ("sf_express", "SF"),
        
        # 滴滴
        ("didi", "滴滴出行"),
        ("didi", "DiDi"),
        ("didi", "滴滴打车"),
        
        # 携程
        ("trip", "携程旅行"),
        ("trip", "Ctrip"),
        
        # 哔哩哔哩
        ("bilibili", "B站"),
        ("bilibili", "Bilibili"),
        ("bilibili", "哔哩"),
        
        # 快手
        ("kuaishou", "快手短视频"),
    ]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 插入实体
    cursor.executemany(
        "INSERT OR REPLACE INTO entities (id, name_cn, name_en, name_short_cn, name_short_en, status) VALUES (?, ?, ?, ?, ?, ?)",
        entities,
    )

    # 插入别名
    cursor.executemany(
        "INSERT INTO aliases (entity_id, alias) VALUES (?, ?)",
        aliases,
    )

    conn.commit()
    conn.close()

    print(f"已插入 {len(entities)} 个实体")
    print(f"已插入 {len(aliases)} 个别名")


def main():
    """主函数"""
    # 数据库路径
    db_path = Path(__file__).parent.parent / "data" / "entities.db"

    # 确保目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建数据库
    print(f"创建数据库: {db_path}")
    create_database(str(db_path))

    # 插入示例数据
    print("插入示例数据...")
    insert_sample_data(str(db_path))

    print("完成！")


if __name__ == "__main__":
    main()