#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预计算图缓存脚本

计算并缓存全局度中心性和 PageRank，避免在线计算开销。

使用方法:
    python scripts/precompute_graph_cache.py
"""

import sys
import os

# 添加项目根目录到 path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fusionsql.graph_optimizer import Neo4jClient, GraphCache


def main():
    print("=" * 60)
    print("图缓存预计算")
    print("=" * 60)

    # 1. 连接 Neo4j
    print("\n[1/4] 连接 Neo4j...")
    client = Neo4jClient()

    if not client.verify_connection():
        print("❌ Neo4j 连接失败！请检查配置。")
        sys.exit(1)
    print("✅ Neo4j 连接成功")

    # 2. 获取图统计信息
    print("\n[2/4] 获取图统计信息...")
    stats = client.get_graph_stats()
    print(f"   表数量: {stats['tables']}")
    print(f"   IS 关系: {stats['is_relations']}")
    print(f"   MOSTLYIS 关系: {stats['mostlyis_relations']}")

    # 3. 预计算
    print("\n[3/4] 预计算全局指标...")
    cache = GraphCache()
    result = cache.precompute_global_metrics(client)

    # 4. 验证
    print("\n[4/4] 验证缓存...")
    if cache.is_valid():
        print(f"✅ 缓存有效")
        print(f"   缓存路径: {cache.cache_path}")
        print(f"   表数量: {cache.get_table_count()}")

        # 显示一些示例
        print("\n   示例 PageRank 值:")
        pageranks = result.get("global_pagerank", {})
        sorted_pr = sorted(pageranks.items(), key=lambda x: x[1], reverse=True)
        for table, pr in sorted_pr[:5]:
            print(f"     {table}: {pr:.6f}")
    else:
        print("❌ 缓存验证失败！")
        sys.exit(1)

    # 关闭连接
    client.close()

    print("\n" + "=" * 60)
    print("预计算完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
