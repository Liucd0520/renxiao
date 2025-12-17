#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表+列融合检索优化测试

测试多种配置组合以达到 90%+ 召回率
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
    """累加分聚合"""
    table_scores = defaultdict(float)
    for node in nodes:
        table_name = node.metadata.get("table_name", "")
        table_scores[table_name] += node.score
    return sorted(table_scores.items(), key=lambda x: x[1], reverse=True)


def test_config(table_retriever, column_retriever, table_k, column_k, final_k):
    """测试一种配置"""
    results = {"table_only": [], "column_only": [], "fusion": []}
    
    for case in TEST_CASES:
        expected_set = set(t.lower() for t in case['expected'])
        
        # 表级别
        table_retriever._similarity_top_k = table_k
        table_nodes = table_retriever.retrieve(case['question'])
        table_set = set(node.metadata.get("table_name", "").lower() for node in table_nodes[:final_k])
        table_recall = len(expected_set & table_set) / len(expected_set)
        results["table_only"].append(table_recall)
        
        # 列级别
        column_retriever._similarity_top_k = column_k
        column_nodes = column_retriever.retrieve(case['question'])
        sorted_tables = aggregate_sum_score(column_nodes)
        column_set = set(t.lower() for t, _ in sorted_tables[:final_k])
        column_recall = len(expected_set & column_set) / len(expected_set)
        results["column_only"].append(column_recall)
        
        # 融合
        fusion_set = table_set | column_set
        fusion_recall = len(expected_set & fusion_set) / len(expected_set)
        results["fusion"].append(fusion_recall)
    
    return results


def run_optimization_tests():
    print("=" * 80)
    print("融合检索参数优化测试")
    print("=" * 80)
    
    # 初始化
    print("\n初始化...")
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    table_storage = StorageContext.from_defaults(persist_dir=TABLE_VECTOR_STORE)
    table_index = load_index_from_storage(table_storage)
    table_retriever = VectorIndexRetriever(index=table_index, similarity_top_k=10)
    
    column_storage = StorageContext.from_defaults(persist_dir=COLUMN_VECTOR_STORE)
    column_index = load_index_from_storage(column_storage)
    column_retriever = VectorIndexRetriever(index=column_index, similarity_top_k=200)
    
    print("✅ 初始化完成")
    
    # 测试不同配置
    configs = [
        # (table_k, column_k, final_k, description)
        (10, 200, 10, "基线: T10 + C200 → 10"),
        (15, 200, 10, "表增加: T15 + C200 → 10"),
        (15, 300, 15, "全增加: T15 + C300 → 15"),
        (20, 300, 15, "再增加: T20 + C300 → 15"),
        (20, 400, 20, "最大化: T20 + C400 → 20"),
    ]
    
    print("\n" + "=" * 80)
    print("不同配置的召回率对比")
    print("=" * 80)
    print(f"\n{'配置':<25} | {'表级别':^8} | {'列级别':^8} | {'融合':^8}")
    print("-" * 60)
    
    best_config = None
    best_fusion = 0
    
    for table_k, column_k, final_k, desc in configs:
        results = test_config(table_retriever, column_retriever, table_k, column_k, final_k)
        
        table_avg = sum(results["table_only"]) / len(results["table_only"])
        column_avg = sum(results["column_only"]) / len(results["column_only"])
        fusion_avg = sum(results["fusion"]) / len(results["fusion"])
        
        print(f"{desc:<25} | {table_avg:^8.0%} | {column_avg:^8.0%} | {fusion_avg:^8.0%}")
        
        if fusion_avg > best_fusion:
            best_fusion = fusion_avg
            best_config = (table_k, column_k, final_k, desc, results)
    
    # 最佳配置详情
    print("\n" + "=" * 80)
    print(f"最佳配置: {best_config[3]} → 融合召回率 {best_fusion:.0%}")
    print("=" * 80)
    
    # 分析失败 case
    print("\n失败 Case 分析:")
    results = best_config[4]
    for i, case in enumerate(TEST_CASES):
        if results["fusion"][i] < 1.0:
            print(f"\n  Case {i+1}: {case['question'][:40]}...")
            print(f"    期望: {case['expected']}")
            print(f"    表级别: {results['table_only'][i]:.0%}")
            print(f"    列级别: {results['column_only'][i]:.0%}")
            print(f"    融合: {results['fusion'][i]:.0%}")
            
            # 详细分析这个 case
            expected_set = set(t.lower() for t in case['expected'])
            
            table_retriever._similarity_top_k = best_config[0]
            table_nodes = table_retriever.retrieve(case['question'])
            
            # 检查期望表在 Top N 之外的什么位置
            for target in expected_set:
                found = False
                for rank, node in enumerate(table_nodes, 1):
                    if node.metadata.get("table_name", "").lower() == target:
                        print(f"    → {target} 在表级别排名 #{rank}")
                        found = True
                        break
                if not found:
                    print(f"    → {target} 不在表级别 Top {best_config[0]} 中")


if __name__ == "__main__":
    run_optimization_tests()
