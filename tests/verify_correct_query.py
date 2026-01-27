#!/usr/bin/env python3
"""
修正版验证脚本 - 通过 Column 关系推导 Table 关系

外键关系数据模型:
  Table A --[COLUMN]--> Column A --[IS/MOSTLYIS]--> Column B <--[COLUMN]-- Table B
  
所以要找 Table 之间的外键关系，需要通过 Column 节点中转
"""

import os
from neo4j import GraphDatabase

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


def main():
    print("=" * 70)
    print("修正版验证：通过 Column 关系推导 Table 之间的外键")
    print("=" * 70)
    
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    
    with driver.session() as session:
        
        # 1. 正确的查询方式：通过 Column 推导 Table 关系
        print("\n" + "-" * 50)
        print("1. 通过 Column 推导所有 Table 之间的外键关系")
        print("-" * 50)
        
        query = """
        MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
        WHERE t1 <> t2
        RETURN DISTINCT t1.name AS table1, c1.name AS col1, 
               type(r) AS rel_type, c2.name AS col2, t2.name AS table2
        LIMIT 30
        """
        result = session.run(query)
        records = list(result)
        
        if records:
            print(f"   找到 {len(records)} 条 Table 间关系（通过 Column）:")
            for r in records:
                print(f"   {r['table1']}.{r['col1']} --[{r['rel_type']}]--> {r['table2']}.{r['col2']}")
        else:
            print("   ⚠️ 没有找到任何 Table 间的关系！")
        
        # 2. 统计有多少对 Table 有外键关系
        print("\n" + "-" * 50)
        print("2. 统计有外键关系的 Table 对数量")
        print("-" * 50)
        
        query = """
        MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
        WHERE t1 <> t2
        WITH DISTINCT t1.name AS t1_name, t2.name AS t2_name, type(r) AS rel
        RETURN rel, count(*) AS cnt
        """
        result = session.run(query)
        for r in result:
            print(f"   {r['rel']} 关系: {r['cnt']} 对 Table")
        
        # 3. 检查核心表是否有外键关系（正确的查询方式）
        print("\n" + "-" * 50)
        print("3. 核心表的外键关系（正确查询方式）")
        print("-" * 50)
        
        for table in CORE_TABLES:
            query = """
            MATCH (t1:Table {name: $table})-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
            WHERE t1 <> t2
            RETURN DISTINCT t2.name AS related_table, c1.name AS col1, 
                   type(r) AS rel_type, c2.name AS col2
            """
            result = session.run(query, {"table": table})
            records = list(result)
            
            print(f"\n   {table}:")
            if records:
                print(f"      找到 {len(records)} 个相关表:")
                for r in records:
                    print(f"      --> {r['related_table']} (通过 {r['col1']} --[{r['rel_type']}]--> {r['col2']})")
            else:
                print(f"      ⚠️ 没有通过 Column 找到任何外键关系！")
        
        # 4. 检查核心表之间是否有外键关系
        print("\n" + "-" * 50)
        print("4. 核心表之间的外键关系")
        print("-" * 50)
        
        query = """
        MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
        WHERE t1.name IN $tables AND t2.name IN $tables AND t1 <> t2
        RETURN DISTINCT t1.name AS table1, c1.name AS col1, 
               type(r) AS rel_type, c2.name AS col2, t2.name AS table2
        """
        result = session.run(query, {"tables": CORE_TABLES})
        records = list(result)
        
        if records:
            print(f"   核心表之间的关系:")
            for r in records:
                print(f"   {r['table1']}.{r['col1']} --[{r['rel_type']}]--> {r['table2']}.{r['col2']}")
        else:
            print("   ⚠️ 核心表之间没有外键关系！")
        
        # 5. 找出连接最多的 Table
        print("\n" + "-" * 50)
        print("5. 外键连接最多的 Top 15 表")
        print("-" * 50)
        
        query = """
        MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
        WHERE t1 <> t2
        WITH t1.name AS table_name, count(DISTINCT t2) AS connection_count
        RETURN table_name, connection_count
        ORDER BY connection_count DESC
        LIMIT 15
        """
        result = session.run(query)
        
        for i, r in enumerate(result, 1):
            print(f"   {i}. {r['table_name']}: {r['connection_count']} 个相关表")
        
        # 6. 检查 neo4j_client.py 中的查询是否正确
        print("\n" + "-" * 50)
        print("6. 对比：neo4j_client.py 的查询 vs 正确查询")
        print("-" * 50)
        
        # neo4j_client.py 中的查询（错误的方式）
        print("\n   [错误的查询] - 直接查 Table 之间的关系:")
        query_wrong = """
        MATCH (t1:Table)-[r:IS|MOSTLYIS]-(t2:Table)
        RETURN count(*) AS cnt
        """
        result = session.run(query_wrong)
        cnt = result.single()["cnt"]
        print(f"   结果: {cnt} 条")
        
        # 正确的查询
        print("\n   [正确的查询] - 通过 Column 推导 Table 关系:")
        query_correct = """
        MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
        WHERE t1 <> t2
        RETURN count(DISTINCT [t1.name, t2.name]) AS cnt
        """
        result = session.run(query_correct)
        cnt = result.single()["cnt"]
        print(f"   结果: {cnt} 对 Table 有外键关系")
    
    print("\n" + "=" * 70)
    print("诊断结论")
    print("=" * 70)
    print("""
  问题根源: neo4j_client.py 的查询方式是错误的！
  
  错误: MATCH (t1:Table)-[r:IS|MOSTLYIS]-(t2:Table)
  正确: MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
  
  外键关系存储在 Column 节点之间，需要通过 Column 来推导 Table 关系。
    """)
    
    driver.close()


if __name__ == "__main__":
    main()
