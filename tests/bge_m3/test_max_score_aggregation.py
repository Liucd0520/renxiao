#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进的列级别检索：表级别最大相似度聚合

原理：
- 检索时仍然按列匹配
- 但按表聚合时，取每个表中所有列的最大 score（而非平均）
- 这样只要有一列匹配好，整个表就能被召回
"""

import os
import sys
import csv
import re
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
from tools.SchemaLinkingTool import SchemaLinkingTool
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

DB_ID = "netcaredb_ai"
SCHEMA_PATH = "./spider2_dev/schemas"


def extract_tables_from_sql(sql):
    patterns = [r'FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?', r'JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?']
    tables = set()
    for p in patterns:
        tables.update(re.findall(p, sql, re.IGNORECASE))
    return list(tables)


def load_test_cases():
    test_cases = []
    with open("./cc_result.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            question = row.get('query', '').strip()
            sql = row.get('sql', '') or row.get('正确SQL', '')
            if question:
                test_cases.append({
                    "question": question, 
                    "expected_tables": extract_tables_from_sql(sql)
                })
    return test_cases


def aggregate_by_max_score(nodes, top_n=15):
    """
    按表级别聚合，取每个表的最大 score
    
    原始方法：直接返回 top_k 列，表的出现取决于列的排名
    改进方法：聚合所有列，按表最大 score 排序，返回 top_n 表
    """
    table_scores = defaultdict(lambda: {"max_score": 0, "columns": []})
    
    for node in nodes:
        # 从文件名提取表名（格式：tablename_columnname.json）
        file_name = node.node.metadata.get("file_name", "")
        # 假设格式是 table_column.json，取最后一个 _ 之前的部分
        parts = file_name.replace(".json", "").rsplit("_", 1)
        if len(parts) >= 1:
            table_name = parts[0]
        else:
            table_name = file_name.replace(".json", "")
        
        score = node.score
        
        # 更新表的最大 score
        if score > table_scores[table_name]["max_score"]:
            table_scores[table_name]["max_score"] = score
        
        table_scores[table_name]["columns"].append({
            "column": file_name,
            "score": score
        })
    
    # 按最大 score 排序
    sorted_tables = sorted(
        table_scores.items(), 
        key=lambda x: x[1]["max_score"], 
        reverse=True
    )[:top_n]
    
    return sorted_tables


def test_max_score_aggregation():
    print("\n" + "=" * 70)
    print("测试改进方案：表级别最大相似度聚合")
    print("=" * 70)
    
    # 初始化
    llm = QwenModel(model_name="qwen-turbo", temperature=0.3)
    
    # 加载向量索引
    vector_dir = os.path.join(SCHEMA_PATH, DB_ID)
    vector_index = RagPipeLines.build_index_from_source(
        data_source=vector_dir,
        persist_dir=os.path.join(vector_dir, "vector_store"),
        is_vector_store_exist=True,
        index_method="VectorStoreIndex"
    )
    
    retriever = RagPipeLines.get_retriever(index=vector_index)
    retriever.similarity_top_k = 300  # 扩大初始检索范围
    
    # 加载测试用例
    test_cases = load_test_cases()
    print(f"测试用例数: {len(test_cases)}\n")
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"测试 {i}/{len(test_cases)}")
        print(f"问题: {case['question'][:50]}...")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 70)
        
        # 检索
        nodes = retriever.retrieve(case['question'])
        
        # 原始方法：直接从 top_k 列中提取表
        original_tables = set()
        for node in nodes[:100]:  # 原始 top 100
            file_name = node.node.metadata.get("file_name", "")
            parts = file_name.replace(".json", "").rsplit("_", 1)
            if len(parts) >= 1:
                original_tables.add(parts[0])
        
        # 改进方法：按表最大 score 聚合
        aggregated = aggregate_by_max_score(nodes, top_n=15)
        improved_tables = [t[0] for t in aggregated]
        
        # 计算召回率
        expected_set = set(t.lower() for t in case['expected_tables'])
        
        original_found = len(expected_set & set(t.lower() for t in original_tables))
        improved_found = len(expected_set & set(t.lower() for t in improved_tables))
        
        original_recall = original_found / len(expected_set) if expected_set else 1.0
        improved_recall = improved_found / len(expected_set) if expected_set else 1.0
        
        print(f"\n原始方法 (top 100 列 → {len(original_tables)} 表):")
        print(f"  召回率: {original_recall:.1%}")
        print(f"  找到: {expected_set & set(t.lower() for t in original_tables)}")
        print(f"  缺失: {expected_set - set(t.lower() for t in original_tables)}")
        
        print(f"\n改进方法 (300 列聚合 → top 15 表):")
        print(f"  召回率: {improved_recall:.1%}")
        print(f"  Top 5 表及 score:")
        for t, info in aggregated[:5]:
            is_expected = "✅" if t.lower() in expected_set else ""
            print(f"    {t}: {info['max_score']:.4f} {is_expected}")
        
        results.append({
            "question": case['question'],
            "expected": case['expected_tables'],
            "original_recall": original_recall,
            "improved_recall": improved_recall
        })
    
    # 汇总
    avg_original = sum(r['original_recall'] for r in results) / len(results)
    avg_improved = sum(r['improved_recall'] for r in results) / len(results)
    
    print("\n" + "=" * 70)
    print("测试汇总")
    print("=" * 70)
    print(f"\n{'方法':<30} | {'平均召回率':>10}")
    print("-" * 45)
    print(f"{'原始方法（列级别 top 100）':<30} | {avg_original:>10.1%}")
    print(f"{'改进方法（表最大 score 聚合）':<30} | {avg_improved:>10.1%}")
    print("=" * 70)
    
    if avg_improved > avg_original:
        print(f"\n🎉 改进方法提升了 {(avg_improved - avg_original) * 100:.1f} 个百分点！")
    elif avg_improved < avg_original:
        print(f"\n⚠️ 改进方法下降了 {(avg_original - avg_improved) * 100:.1f} 个百分点")
    else:
        print(f"\n➡️ 两种方法效果相同")


if __name__ == "__main__":
    test_max_score_aggregation()
