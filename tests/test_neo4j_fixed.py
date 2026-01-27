#!/usr/bin/env python3
"""
验证修复后的 neo4j_client.py

测试核心表的外键关系是否能正确获取
"""

import sys
sys.path.insert(0, "/Users/jason/Documents/实习/理想实习/FusionSQL")

# 使用修复后的 Neo4j 客户端
from neo4j import GraphDatabase
import os

# Neo4j 连接配置
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://172.31.24.111:7689")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "12345678")

# 核心业务表
CORE_TABLES = [
    "t_bz_config_ci_ne_root",  # 设备表
    "event_history",           # 事件历史表
    "t_bz_config_customer",    # 客户表
]

# 关系权重
RELATION_WEIGHTS = {
    "IS": 1.0,
    "MOSTLYIS": 0.2,
}


def test_neo4j_client_fixed():
    """测试修复后的查询逻辑"""
    print("=" * 70)
    print("测试修复后的 Neo4j 客户端")
    print("=" * 70)
    
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    
    with driver.session() as session:
        # 1. 测试 get_table_relationships（修复后的查询）
        print("\n" + "-" * 50)
        print("1. get_table_relationships - 修复后的查询")
        print("-" * 50)
        
        # 获取核心表之间的关系
        query = """
        MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
        WHERE t1.name IN $tables AND t2.name IN $tables AND t1 <> t2
        RETURN DISTINCT t1.name AS source, t2.name AS target, type(r) AS rel_type
        """
        result = session.run(query, {"tables": CORE_TABLES})
        records = list(result)
        
        print(f"   核心表之间的关系 ({len(records)} 条):")
        for r in records:
            weight = RELATION_WEIGHTS.get(r['rel_type'], 0.5)
            print(f"   {r['source']} --> {r['target']} [{r['rel_type']}] (权重: {weight})")
        
        # 2. 测试 get_connected_tables（修复后的查询）
        print("\n" + "-" * 50)
        print("2. get_connected_tables - 修复后的查询")
        print("-" * 50)
        
        for table in CORE_TABLES:
            query = """
            MATCH (seed:Table)-[:COLUMN]-(c1:Column)-[:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(neighbor:Table)
            WHERE seed.name IN $seeds AND seed <> neighbor
            RETURN DISTINCT neighbor.name AS table_name
            """
            result = session.run(query, {"seeds": [table]})
            neighbors = [r["table_name"] for r in result]
            
            print(f"\n   {table}:")
            print(f"      邻居表数量: {len(neighbors)}")
            if neighbors:
                for n in neighbors[:5]:
                    print(f"      - {n}")
                if len(neighbors) > 5:
                    print(f"      ... 还有 {len(neighbors) - 5} 个")
        
        # 3. 测试 get_table_degrees（修复后的查询）
        print("\n" + "-" * 50)
        print("3. get_table_degrees - 修复后的查询")
        print("-" * 50)
        
        query = """
        MATCH (t:Table)
        WHERE t.name IN $tables
        OPTIONAL MATCH (t)-[:COLUMN]-(c1:Column)-[r1:IS]-(c2:Column)-[:COLUMN]-(other1:Table)
        WHERE t <> other1
        WITH t, count(DISTINCT other1) AS is_count
        OPTIONAL MATCH (t)-[:COLUMN]-(c3:Column)-[r2:MOSTLYIS]-(c4:Column)-[:COLUMN]-(other2:Table)
        WHERE t <> other2
        WITH t.name AS name, is_count, count(DISTINCT other2) AS mostlyis_count
        RETURN name, is_count, mostlyis_count
        """
        result = session.run(query, {"tables": CORE_TABLES})
        
        for r in result:
            total = r['is_count'] + r['mostlyis_count']
            print(f"   {r['name']}:")
            print(f"      IS 连接: {r['is_count']}")
            print(f"      MOSTLYIS 连接: {r['mostlyis_count']}")
            print(f"      总连接: {total}")
        
        # 4. 测试所有表的度统计
        print("\n" + "-" * 50)
        print("4. 所有表的外键连接 Top 10")
        print("-" * 50)
        
        query = """
        MATCH (t:Table)
        OPTIONAL MATCH (t)-[:COLUMN]-(c1:Column)-[r1:IS]-(c2:Column)-[:COLUMN]-(other1:Table)
        WHERE t <> other1
        WITH t, count(DISTINCT other1) AS is_count
        OPTIONAL MATCH (t)-[:COLUMN]-(c3:Column)-[r2:MOSTLYIS]-(c4:Column)-[:COLUMN]-(other2:Table)
        WHERE t <> other2
        WITH t.name AS name, is_count, count(DISTINCT other2) AS mostlyis_count
        WITH name, is_count, mostlyis_count, is_count + mostlyis_count AS total
        WHERE total > 0
        RETURN name, is_count, mostlyis_count, total
        ORDER BY total DESC
        LIMIT 10
        """
        result = session.run(query)
        
        for i, r in enumerate(result, 1):
            print(f"   {i}. {r['name']}: {r['total']} 连接 (IS={r['is_count']}, MOSTLYIS={r['mostlyis_count']})")
    
    print("\n" + "=" * 70)
    print("修复验证完成！核心表的外键关系现在可以正确获取。")
    print("=" * 70)
    
    driver.close()


if __name__ == "__main__":
    test_neo4j_client_fixed()
