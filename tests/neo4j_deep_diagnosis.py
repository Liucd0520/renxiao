#!/usr/bin/env python3
"""
深度检查 Neo4j 数据库状态
"""

import os
from neo4j import GraphDatabase

# Neo4j 连接配置
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://172.31.24.111:7689")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "12345678")

def main():
    print("=" * 60)
    print("Neo4j 深度诊断")
    print("=" * 60)
    
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    
    with driver.session() as session:
        # 1. 检查所有节点类型
        print("\n1. 节点类型统计")
        print("-" * 40)
        result = session.run("CALL db.labels() YIELD label RETURN label")
        labels = [r["label"] for r in result]
        print(f"   节点类型: {labels}")
        
        for label in labels:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) AS cnt")
            cnt = result.single()["cnt"]
            print(f"   - {label}: {cnt} 个")
        
        # 2. 检查所有关系类型
        print("\n2. 关系类型统计")
        print("-" * 40)
        result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        rel_types = [r["relationshipType"] for r in result]
        print(f"   关系类型: {rel_types}")
        
        for rel_type in rel_types:
            result = session.run(f"MATCH ()-[r:{rel_type}]-() RETURN count(r)/2 AS cnt")
            cnt = result.single()["cnt"]
            print(f"   - {rel_type}: {cnt} 条")
        
        # 3. 检查 IS 和 MOSTLYIS 关系连接的是什么类型的节点
        print("\n3. IS/MOSTLYIS 关系连接的节点类型")
        print("-" * 40)
        
        for rel_type in ["IS", "MOSTLYIS"]:
            query = f"""
            MATCH (a)-[r:{rel_type}]-(b)
            RETURN DISTINCT labels(a) AS label_a, labels(b) AS label_b
            LIMIT 5
            """
            result = session.run(query)
            records = list(result)
            if records:
                print(f"   {rel_type}:")
                for r in records:
                    print(f"      {r['label_a']} <--> {r['label_b']}")
            else:
                print(f"   {rel_type}: 没有关系")
        
        # 4. 查看一些实际的关系数据
        print("\n4. 查看一些实际的关系（任意类型）")
        print("-" * 40)
        
        query = """
        MATCH (a)-[r]-(b)
        RETURN labels(a) AS label_a, a.name AS name_a, type(r) AS rel, labels(b) AS label_b, b.name AS name_b
        LIMIT 20
        """
        result = session.run(query)
        records = list(result)
        
        if records:
            for r in records:
                print(f"   ({r['label_a']})'{r['name_a']}' --[{r['rel']}]--> ({r['label_b']})'{r['name_b']}'")
        else:
            print("   ⚠️ 数据库中没有任何关系！")
        
        # 5. 检查 Table 节点
        print("\n5. 随机查看 10 个 Table 节点")
        print("-" * 40)
        
        query = """
        MATCH (t:Table)
        RETURN t.name AS name
        LIMIT 10
        """
        result = session.run(query)
        for r in result:
            print(f"   - {r['name']}")
        
        # 6. 检查 Column 节点以及它们与 Table 的关系
        print("\n6. 检查 Column 和 Table 的关系")
        print("-" * 40)
        
        query = """
        MATCH (t:Table)-[r]-(c:Column)
        RETURN t.name AS table_name, type(r) AS rel, c.name AS column_name
        LIMIT 10
        """
        result = session.run(query)
        records = list(result)
        
        if records:
            for r in records:
                print(f"   {r['table_name']} --[{r['rel']}]--> {r['column_name']}")
        else:
            print("   ⚠️ Table 和 Column 之间没有关系！")
        
        # 7. 检查 IS/MOSTLYIS 是否在 Column 之间
        print("\n7. 检查 IS/MOSTLYIS 是否存在于 Column 节点之间")
        print("-" * 40)
        
        query = """
        MATCH (c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)
        RETURN c1.name AS col1, type(r) AS rel, c2.name AS col2
        LIMIT 10
        """
        result = session.run(query)
        records = list(result)
        
        if records:
            print("   IS/MOSTLYIS 关系存在于 Column 之间:")
            for r in records:
                print(f"   {r['col1']} --[{r['rel']}]--> {r['col2']}")
        else:
            print("   Column 之间也没有 IS/MOSTLYIS 关系")
        
        # 8. 全面搜索 IS/MOSTLYIS 关系
        print("\n8. 全面搜索 IS/MOSTLYIS 关系")
        print("-" * 40)
        
        for rel_type in ["IS", "MOSTLYIS"]:
            query = f"""
            MATCH (a)-[r:{rel_type}]-(b)
            RETURN labels(a) AS label_a, a.name AS name_a, labels(b) AS label_b, b.name AS name_b
            LIMIT 5
            """
            result = session.run(query)
            records = list(result)
            
            print(f"\n   {rel_type} 关系:")
            if records:
                for r in records:
                    print(f"      ({r['label_a']})'{r['name_a']}' <--> ({r['label_b']})'{r['name_b']}'")
            else:
                print(f"      ⚠️ 没有找到任何 {rel_type} 关系！")
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    
    driver.close()


if __name__ == "__main__":
    main()
