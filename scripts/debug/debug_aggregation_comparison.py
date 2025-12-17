#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列级别检索综合对比测试

对比多种列到表的聚合策略：
1. Max Score（取最高分）
2. 平均分（所有列的平均分）
3. 投票（相关列数/总列数）
4. 加权投票（高分列权重更大）
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
VECTOR_STORE_DIR = "./spider2_dev/schemas/netcaredb_ai/vector_store_bge_m3_enhanced"
TOP_K = 200  # 检索更多列以便对比


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


def aggregate_max_score(table_columns):
    """Max Score: 取每个表的最高分列"""
    table_scores = {}
    for table, cols in table_columns.items():
        max_score = max(score for _, score in cols)
        table_scores[table] = max_score
    return sorted(table_scores.items(), key=lambda x: x[1], reverse=True)


def aggregate_avg_score(table_columns):
    """平均分: 所有检索到的列的平均分"""
    table_scores = {}
    for table, cols in table_columns.items():
        avg_score = sum(score for _, score in cols) / len(cols)
        table_scores[table] = avg_score
    return sorted(table_scores.items(), key=lambda x: x[1], reverse=True)


def aggregate_vote(table_columns, total_columns_per_table):
    """投票: 检索到的列数 / 表总列数（LinkAlign 方式）"""
    table_scores = {}
    for table, cols in table_columns.items():
        total = total_columns_per_table.get(table, len(cols))
        vote_ratio = len(cols) / total if total > 0 else 0
        table_scores[table] = vote_ratio
    return sorted(table_scores.items(), key=lambda x: x[1], reverse=True)


def aggregate_weighted_vote(table_columns):
    """加权投票: 高分列权重更大"""
    table_scores = {}
    for table, cols in table_columns.items():
        # 分数 > 0.5 的列权重为 1，否则权重为 0.5
        weighted_sum = sum(1 if score > 0.5 else 0.5 for _, score in cols)
        table_scores[table] = weighted_sum
    return sorted(table_scores.items(), key=lambda x: x[1], reverse=True)


def aggregate_sum_score(table_columns):
    """累加分: 所有检索到的列分数之和"""
    table_scores = {}
    for table, cols in table_columns.items():
        sum_score = sum(score for _, score in cols)
        table_scores[table] = sum_score
    return sorted(table_scores.items(), key=lambda x: x[1], reverse=True)


def run_comprehensive_test():
    print("=" * 80)
    print("列级别检索聚合策略综合对比")
    print("=" * 80)
    
    # 初始化
    print("\n初始化...")
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_DIR)
    vector_index = load_index_from_storage(storage_context)
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=TOP_K)
    print("✅ 初始化完成")
    
    # 结果收集
    results = {
        "max_score": [],
        "avg_score": [],
        "sum_score": [],
        "weighted_vote": []
    }
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 80}")
        print(f"测试 {i}: {case['question'][:30]}...")
        print(f"期望表: {case['expected']}")
        print("-" * 80)
        
        # 检索
        nodes = retriever.retrieve(case['question'])
        
        # 按表聚合列
        table_columns = defaultdict(list)
        for node in nodes:
            table_name = node.metadata.get("table_name", "")
            column_name = node.metadata.get("column_name", "")
            table_columns[table_name].append((column_name, node.score))
        
        print(f"检索到 {len(nodes)} 列，来自 {len(table_columns)} 个表")
        
        # 各种聚合策略
        strategies = {
            "max_score": aggregate_max_score(table_columns),
            "avg_score": aggregate_avg_score(table_columns),
            "sum_score": aggregate_sum_score(table_columns),
            "weighted_vote": aggregate_weighted_vote(table_columns)
        }
        
        expected_set = set(t.lower() for t in case['expected'])
        
        print(f"\n{'策略':<15} | {'Top1':^20} | {'Top5 召回':^10} | {'Top10 召回':^10}")
        print("-" * 65)
        
        for strategy_name, sorted_tables in strategies.items():
            top10_tables = set(t.lower() for t, _ in sorted_tables[:10])
            top5_tables = set(t.lower() for t, _ in sorted_tables[:5])
            
            recall_5 = len(expected_set & top5_tables) / len(expected_set)
            recall_10 = len(expected_set & top10_tables) / len(expected_set)
            
            top1 = sorted_tables[0][0] if sorted_tables else "N/A"
            top1_short = top1[:20] + "..." if len(top1) > 20 else top1
            
            results[strategy_name].append(recall_10)
            
            print(f"{strategy_name:<15} | {top1_short:^20} | {recall_5:.0%}       | {recall_10:.0%}")
    
    # 汇总
    print("\n" + "=" * 80)
    print("汇总（Top 10 平均召回率）")
    print("=" * 80)
    
    for strategy_name, recall_list in results.items():
        avg_recall = sum(recall_list) / len(recall_list)
        print(f"{strategy_name:<15}: {avg_recall:.0%}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_comprehensive_test()
