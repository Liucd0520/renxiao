#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSH 集成测试脚本

测试 LSH 三路融合检索是否正常工作，并对比有无 LSH 的表召回率差异。
"""

import sys
import os

# 确保能导入 fusionsql
sys.path.insert(0, "/Users/jason/Documents/实习/理想实习/FusionSQL")

from fusionsql.retriever import FastRetriever
from fusionsql.value_search.search import ValueSearcher

# 7 题标准测试集
TEST_CASES = [
    {
        "id": 1,
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root"]
    },
    {
        "id": 2,
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]
    },
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "expected_tables": ["t_bz_config_customer"]
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "expected_tables": ["t_bz_config_ci_ne_root"]
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"]
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"]
    },
    {
        "id": 7,
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]
    },
]


def calculate_recall(retrieved_tables: list, expected_tables: list) -> float:
    """计算表召回率"""
    retrieved_set = set(retrieved_tables)
    expected_set = set(expected_tables)
    
    if not expected_set:
        return 1.0
    
    hit_count = len(retrieved_set & expected_set)
    return hit_count / len(expected_set)


def test_retrieval_comparison():
    """对比有无 LSH 的检索效果"""
    
    print("=" * 60)
    print("LSH 三路融合检索测试")
    print("=" * 60)
    
    # 初始化组件
    print("\n初始化检索器...")
    retriever = FastRetriever()
    
    print("\n初始化 LSH 搜索器...")
    lsh_index_dir = "/Users/jason/Documents/实习/理想实习/FusionSQL/fusionsql/lsh_index"
    if os.path.exists(lsh_index_dir):
        lsh_searcher = ValueSearcher(lsh_index_dir)
        print(f"LSH 索引加载成功")
    else:
        print(f"LSH 索引不存在: {lsh_index_dir}")
        return
    
    print("\n" + "=" * 60)
    
    results = []
    
    for tc in TEST_CASES:
        print(f"\n## 测试 {tc['id']}: {tc['question'][:30]}...")
        print(f"   期望表: {tc['expected_tables']}")
        
        # 无 LSH 检索
        retrieved_no_lsh = retriever.retrieve(tc['question'], top_k=10)
        tables_no_lsh = [t for t, _ in retrieved_no_lsh]
        recall_no_lsh = calculate_recall(tables_no_lsh, tc['expected_tables'])
        
        # 有 LSH 检索
        retrieved_with_lsh = retriever.retrieve_with_lsh(
            tc['question'], 
            top_k=10, 
            lsh_searcher=lsh_searcher,
            lsh_min_similarity=0.5,  # 高阈值过滤
            lsh_max_tables=5         # 限制 LSH 贡献的表数
        )
        tables_with_lsh = [t for t, _ in retrieved_with_lsh]
        recall_with_lsh = calculate_recall(tables_with_lsh, tc['expected_tables'])
        
        # 检查哪些期望表被召回
        expected_set = set(tc['expected_tables'])
        hit_no_lsh = expected_set & set(tables_no_lsh)
        hit_with_lsh = expected_set & set(tables_with_lsh)
        
        print(f"   无 LSH: 召回 {len(hit_no_lsh)}/{len(expected_set)} ({recall_no_lsh*100:.0f}%)")
        print(f"           检索到 {len(tables_no_lsh)} 张表")
        print(f"   有 LSH: 召回 {len(hit_with_lsh)}/{len(expected_set)} ({recall_with_lsh*100:.0f}%)")
        print(f"           检索到 {len(tables_with_lsh)} 张表")
        
        # 显示 LSH 新增的表
        new_tables = set(tables_with_lsh) - set(tables_no_lsh)
        if new_tables:
            print(f"   LSH 新增: {list(new_tables)}")
        
        results.append({
            "id": tc['id'],
            "recall_no_lsh": recall_no_lsh,
            "recall_with_lsh": recall_with_lsh,
            "tables_no_lsh": len(tables_no_lsh),
            "tables_with_lsh": len(tables_with_lsh),
            "improvement": recall_with_lsh - recall_no_lsh
        })
    
    # 汇总统计
    print("\n" + "=" * 60)
    print("汇总统计")
    print("=" * 60)
    
    avg_recall_no_lsh = sum(r['recall_no_lsh'] for r in results) / len(results)
    avg_recall_with_lsh = sum(r['recall_with_lsh'] for r in results) / len(results)
    avg_tables_no_lsh = sum(r['tables_no_lsh'] for r in results) / len(results)
    avg_tables_with_lsh = sum(r['tables_with_lsh'] for r in results) / len(results)
    
    improved_count = sum(1 for r in results if r['improvement'] > 0)
    same_count = sum(1 for r in results if r['improvement'] == 0)
    worse_count = sum(1 for r in results if r['improvement'] < 0)
    
    print(f"\n平均召回率:")
    print(f"  无 LSH: {avg_recall_no_lsh*100:.1f}%")
    print(f"  有 LSH: {avg_recall_with_lsh*100:.1f}%")
    print(f"  提升: {(avg_recall_with_lsh - avg_recall_no_lsh)*100:.1f}%")
    
    print(f"\n平均检索表数:")
    print(f"  无 LSH: {avg_tables_no_lsh:.1f} 张")
    print(f"  有 LSH: {avg_tables_with_lsh:.1f} 张")
    
    print(f"\n效果对比:")
    print(f"  提升: {improved_count} 题")
    print(f"  持平: {same_count} 题")
    print(f"  下降: {worse_count} 题")


if __name__ == "__main__":
    test_retrieval_comparison()
