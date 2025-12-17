#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表+列融合检索测试

策略：
- 表级别检索：Top 10 表
- 列级别检索：Top 200 列 → 累加分聚合 → Top 10 表
- 融合：并集（最大化召回率）

配置理由：
- 1 表 ≈ 60-70 列
- Top 10 表 → 约 600-700 列的覆盖
- 列级别 Top 200 → 累加分后约 30-50 表 → 取 Top 10
"""

import os
import sys
from collections import defaultdict

# 添加项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from embed_model.BGEM3Embedding import BGEM3Embedding

# 配置
TABLE_VECTOR_STORE = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai/table_vector_store_bge_m3"
COLUMN_VECTOR_STORE = "./spider2_dev/schemas/netcaredb_ai/vector_store_bge_m3_enhanced"

TABLE_TOP_K = 10      # 表级别检索 Top 10
COLUMN_TOP_K = 200    # 列级别检索 Top 200
FINAL_TOP_K = 10      # 最终返回 Top 10 表


# 测试用例
TEST_CASES = [
    {
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected": ["event_history", "t_bz_config_ci_ne_root"]
    },
    {
        "question": "现在平台上有多少台设备",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "现在平台上有多少家客户",
        "expected": ["t_bz_config_customer"]
    },
    {
        "question": "上个月上线的新设备有多少",
        "expected": ["t_bz_config_ci_ne_root"]
    },
]


def aggregate_sum_score(nodes):
    """累加分聚合：列分数之和"""
    table_scores = defaultdict(float)
    table_columns = defaultdict(list)
    
    for node in nodes:
        table_name = node.metadata.get("table_name", "")
        column_name = node.metadata.get("column_name", "")
        score = node.score
        
        table_scores[table_name] += score
        table_columns[table_name].append((column_name, score))
    
    sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_tables, table_columns


def run_fusion_test():
    print("=" * 80)
    print("表+列融合检索测试")
    print("=" * 80)
    print(f"表级别: Top {TABLE_TOP_K}")
    print(f"列级别: Top {COLUMN_TOP_K} → 累加分 → Top {TABLE_TOP_K}")
    print(f"融合策略: 并集")
    print("=" * 80)
    
    # 1. 初始化
    print("\n[初始化] 加载模型和索引...")
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    # 加载表级别索引
    table_storage = StorageContext.from_defaults(persist_dir=TABLE_VECTOR_STORE)
    table_index = load_index_from_storage(table_storage)
    table_retriever = VectorIndexRetriever(index=table_index, similarity_top_k=TABLE_TOP_K)
    
    # 加载列级别索引
    column_storage = StorageContext.from_defaults(persist_dir=COLUMN_VECTOR_STORE)
    column_index = load_index_from_storage(column_storage)
    column_retriever = VectorIndexRetriever(index=column_index, similarity_top_k=COLUMN_TOP_K)
    
    print("✅ 初始化完成")
    
    # 结果收集
    results = {
        "table_only": [],
        "column_only": [],
        "fusion": []
    }
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 80}")
        print(f"测试 {i}: {case['question'][:40]}...")
        print(f"期望表: {case['expected']}")
        print("-" * 80)
        
        expected_set = set(t.lower() for t in case['expected'])
        
        # A. 表级别检索
        table_nodes = table_retriever.retrieve(case['question'])
        table_results = [(node.metadata.get("table_name", ""), node.score) for node in table_nodes]
        table_set = set(t.lower() for t, _ in table_results[:TABLE_TOP_K])
        
        table_recall = len(expected_set & table_set) / len(expected_set)
        results["table_only"].append(table_recall)
        
        print(f"\n[表级别 Top {TABLE_TOP_K}]")
        for j, (table, score) in enumerate(table_results[:5], 1):
            is_exp = "✅" if table.lower() in expected_set else ""
            print(f"  {j}. {table} ({score:.4f}) {is_exp}")
        print(f"  召回率: {table_recall:.0%}")
        
        # B. 列级别检索 + 累加分聚合
        column_nodes = column_retriever.retrieve(case['question'])
        sorted_tables, _ = aggregate_sum_score(column_nodes)
        column_set = set(t.lower() for t, _ in sorted_tables[:TABLE_TOP_K])
        
        column_recall = len(expected_set & column_set) / len(expected_set)
        results["column_only"].append(column_recall)
        
        print(f"\n[列级别 Top {COLUMN_TOP_K} → 累加分 → Top {TABLE_TOP_K}]")
        for j, (table, score) in enumerate(sorted_tables[:5], 1):
            is_exp = "✅" if table.lower() in expected_set else ""
            print(f"  {j}. {table} ({score:.4f}) {is_exp}")
        print(f"  召回率: {column_recall:.0%}")
        
        # C. 融合：并集
        fusion_set = table_set | column_set
        fusion_recall = len(expected_set & fusion_set) / len(expected_set)
        results["fusion"].append(fusion_recall)
        
        print(f"\n[融合 - 并集] ({len(fusion_set)} 个表)")
        print(f"  包含期望表: {expected_set & fusion_set}")
        print(f"  缺失: {expected_set - fusion_set}")
        print(f"  召回率: {fusion_recall:.0%}")
    
    # 汇总
    print("\n" + "=" * 80)
    print("汇总（Top 10 平均召回率）")
    print("=" * 80)
    
    for method, recalls in results.items():
        avg_recall = sum(recalls) / len(recalls)
        full_recall = sum(1 for r in recalls if r == 1.0)
        print(f"{method:<15}: {avg_recall:.0%} ({full_recall}/{len(recalls)} 完全召回)")
    
    # 逐测试对比
    print("\n" + "-" * 80)
    print(f"{'测试':<5} | {'表级别':^10} | {'列级别':^10} | {'融合':^10}")
    print("-" * 50)
    for i, case in enumerate(TEST_CASES):
        table_r = results["table_only"][i]
        col_r = results["column_only"][i]
        fus_r = results["fusion"][i]
        print(f"{i+1:<5} | {table_r:^10.0%} | {col_r:^10.0%} | {fus_r:^10.0%}")
    
    print("=" * 80)


if __name__ == "__main__":
    run_fusion_test()
