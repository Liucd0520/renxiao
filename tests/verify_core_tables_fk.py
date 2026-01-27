#!/usr/bin/env python3
"""
验证核心表的外键关系

检查 Neo4j 数据库中核心业务表是否有外键连接
"""

import os
import sys

# 直接导入 neo4j，避免 FlagEmbedding 依赖
try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ neo4j 包未安装，请运行: pip install neo4j")
    sys.exit(1)

# Neo4j 连接配置
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://172.31.24.111:7689")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "12345678")

# 关系权重
RELATION_WEIGHTS = {
    "IS": 1.0,
    "MOSTLYIS": 0.2,
}

# 核心业务表
CORE_TABLES = [
    "t_bz_config_ci_ne_root",  # 设备表
    "event_history",           # 事件历史表
    "t_bz_config_customer",    # 客户表
]


def main():
    print("=" * 60)
    print("Neo4j 核心表外键关系验证")
    print("=" * 60)
    
    # 初始化驱动
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        # 验证连接
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()
            if record["test"] == 1:
                print("✅ Neo4j 连接成功")
            else:
                print("❌ Neo4j 连接验证失败")
                return
    except Exception as e:
        print(f"❌ Neo4j 连接失败: {e}")
        return
    
    # 1. 获取图统计信息
    print("\n" + "-" * 40)
    print("1. 图统计信息")
    print("-" * 40)
    
    with driver.session() as session:
        # 表数量
        result = session.run("MATCH (t:Table) RETURN count(t) AS cnt")
        table_count = result.single()["cnt"]
        
        # IS 关系数量
        result = session.run("MATCH ()-[r:IS]-() RETURN count(r)/2 AS cnt")
        is_count = result.single()["cnt"]
        
        # MOSTLYIS 关系数量
        result = session.run("MATCH ()-[r:MOSTLYIS]-() RETURN count(r)/2 AS cnt")
        mostlyis_count = result.single()["cnt"]
        
        print(f"   表总数: {table_count}")
        print(f"   IS 关系: {is_count}")
        print(f"   MOSTLYIS 关系: {mostlyis_count}")
    
    # 2. 检查核心表是否存在
    print("\n" + "-" * 40)
    print("2. 核心表存在性检查")
    print("-" * 40)
    
    with driver.session() as session:
        result = session.run("MATCH (t:Table) RETURN t.name AS name")
        all_tables = set(record["name"] for record in result)
        
        for table in CORE_TABLES:
            if table in all_tables:
                print(f"   ✅ {table} - 存在")
            else:
                print(f"   ❌ {table} - 不存在！")
    
    # 3. 检查核心表的度信息
    print("\n" + "-" * 40)
    print("3. 核心表度信息（外键连接数）")
    print("-" * 40)
    
    with driver.session() as session:
        query = """
        MATCH (t:Table)
        WHERE t.name IN $tables
        OPTIONAL MATCH (t)-[r1:IS]-(other1:Table)
        OPTIONAL MATCH (t)-[r2:MOSTLYIS]-(other2:Table)
        WITH t.name AS name,
             count(DISTINCT other1) AS is_count,
             count(DISTINCT other2) AS mostlyis_count
        RETURN name, is_count, mostlyis_count
        """
        result = session.run(query, {"tables": CORE_TABLES})
        
        for record in result:
            name = record["name"]
            is_count = record["is_count"]
            mostlyis_count = record["mostlyis_count"]
            total = is_count + mostlyis_count
            
            print(f"   {name}:")
            print(f"      IS 连接: {is_count}")
            print(f"      MOSTLYIS 连接: {mostlyis_count}")
            print(f"      总连接: {total}")
            
            if total == 0:
                print(f"      ⚠️ 这是一个孤立表！")
    
    # 4. 检查核心表之间的关系
    print("\n" + "-" * 40)
    print("4. 核心表之间的关系")
    print("-" * 40)
    
    with driver.session() as session:
        query = """
        MATCH (t1:Table)-[r:IS|MOSTLYIS]-(t2:Table)
        WHERE t1.name IN $tables AND t2.name IN $tables
        RETURN DISTINCT t1.name AS source, type(r) AS rel_type, t2.name AS target
        """
        result = session.run(query, {"tables": CORE_TABLES})
        records = list(result)
        
        if records:
            for record in records:
                print(f"   {record['source']} --[{record['rel_type']}]--> {record['target']}")
        else:
            print("   ⚠️ 核心表之间没有任何外键关系！")
    
    # 5. 检查核心表连接的其他表
    print("\n" + "-" * 40)
    print("5. 核心表连接的邻居表（1-hop）")
    print("-" * 40)
    
    with driver.session() as session:
        for table in CORE_TABLES:
            query = """
            MATCH (t:Table {name: $table})-[r:IS|MOSTLYIS]-(neighbor:Table)
            RETURN DISTINCT neighbor.name AS neighbor, type(r) AS rel_type
            """
            result = session.run(query, {"table": table})
            records = list(result)
            
            print(f"\n   {table}:")
            if records:
                print(f"      邻居数量: {len(records)}")
                for record in records[:10]:
                    print(f"      - {record['neighbor']} (via {record['rel_type']})")
                if len(records) > 10:
                    print(f"      ... 还有 {len(records) - 10} 个")
            else:
                print(f"      ⚠️ 没有连接的邻居表！（孤立表）")
    
    # 6. 直接执行 Cypher 查询验证
    print("\n" + "-" * 40)
    print("6. 直接 Cypher 查询验证（报告中建议的查询）")
    print("-" * 40)
    
    with driver.session() as session:
        query = """
        MATCH (t:Table)-[r:IS|MOSTLYIS]-(other:Table)
        WHERE t.name IN ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
        RETURN t.name AS source, type(r) AS rel_type, other.name AS target
        LIMIT 50
        """
        result = session.run(query)
        records = list(result)
        
        if records:
            print(f"   找到 {len(records)} 条关系:")
            for record in records:
                print(f"      {record['source']} --[{record['rel_type']}]--> {record['target']}")
        else:
            print("   ⚠️ 没有找到任何关系！")
            print("   这验证了报告中的结论：核心表在 Neo4j 中确实没有外键数据！")
    
    # 7. 查找哪些表有最多的外键连接
    print("\n" + "-" * 40)
    print("7. 外键连接最多的 Top 10 表（看看数据库里有什么）")
    print("-" * 40)
    
    with driver.session() as session:
        query = """
        MATCH (t:Table)
        OPTIONAL MATCH (t)-[r1:IS]-(other1:Table)
        OPTIONAL MATCH (t)-[r2:MOSTLYIS]-(other2:Table)
        WITH t.name AS name,
             count(DISTINCT other1) AS is_count,
             count(DISTINCT other2) AS mostlyis_count
        WITH name, is_count, mostlyis_count, is_count + mostlyis_count AS total
        WHERE total > 0
        RETURN name, is_count, mostlyis_count, total
        ORDER BY total DESC
        LIMIT 10
        """
        result = session.run(query)
        
        for i, record in enumerate(result, 1):
            print(f"   {i}. {record['name']}: {record['total']} 连接 (IS={record['is_count']}, MOSTLYIS={record['mostlyis_count']})")
    
    # 8. 检查是否有任何 IS 关系
    print("\n" + "-" * 40)
    print("8. 查看一些 IS 关系示例（精确外键）")
    print("-" * 40)
    
    with driver.session() as session:
        query = """
        MATCH (t1:Table)-[r:IS]-(t2:Table)
        RETURN DISTINCT t1.name AS source, t2.name AS target
        LIMIT 10
        """
        result = session.run(query)
        records = list(result)
        
        if records:
            print(f"   找到的 IS 关系示例:")
            for record in records:
                print(f"      {record['source']} <--> {record['target']}")
        else:
            print("   ⚠️ 没有 IS 关系！")
    
    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)
    
    driver.close()


if __name__ == "__main__":
    main()
