#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列级别检索测试（Max Score 聚合）

测试核心问题：如果一个表只有少数列相关，能否通过 Max Score 聚合保留该表？
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

# 添加项目根目录 (tests/table_level/ -> 项目根目录)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)  # 切换工作目录

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from embed_model.BGEM3Embedding import BGEM3Embedding

# 配置
SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
VECTOR_STORE_DIR = "./spider2_dev/schemas/netcaredb_ai/vector_store_bge_m3_enhanced"  # 使用增强版索引
TOP_K_COLUMNS = 100  # 检索 Top 100 列（提高召回率）
TOP_K_TABLES = 10    # 聚合后返回 Top 10 表

# 测试用例
TEST_CASES = [
    {
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root"]
    },
    {
        "question": "现在平台上有多少台设备",
        "expected_tables": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "现在平台上有多少家客户",
        "expected_tables": ["t_bz_config_customer"]
    },
    {
        "question": "上个月上线的新设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"]
    },
]


def get_table_from_filename(filename):
    """从文件名提取表名（已废弃，使用 metadata 更准确）"""
    # 格式: table_name_column_name.json
    name = filename.replace('.json', '')
    parts = name.rsplit('_', 1)
    if len(parts) >= 2:
        return parts[0]
    return name


def max_score_aggregate(retrieved_columns):
    """
    Max Score 聚合：按表名聚合，取每个表的最高分
    
    返回: [(table_name, max_score, best_column, all_columns), ...]
    """
    table_data = defaultdict(lambda: {"max_score": 0, "best_column": "", "columns": []})
    
    for node in retrieved_columns:
        # 直接从 metadata 读取表名（最可靠的方式！）
        table_name = node.metadata.get("table_name", "")
        column_name = node.metadata.get("column_name", "")
        
        # 如果 metadata 没有表名，尝试从文件名解析（fallback）
        if not table_name:
            filename = node.metadata.get("file_name", "")
            table_name = get_table_from_filename(filename)
            column_name = filename.replace('.json', '').replace(table_name + '_', '')
        
        score = node.score
        
        table_data[table_name]["columns"].append((column_name, score))
        
        if score > table_data[table_name]["max_score"]:
            table_data[table_name]["max_score"] = score
            table_data[table_name]["best_column"] = column_name
    
    # 转换为列表并按分数排序
    results = []
    for table_name, data in table_data.items():
        results.append((
            table_name, 
            data["max_score"], 
            data["best_column"],
            data["columns"]
        ))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def run_column_level_test():
    print("=" * 70)
    print("列级别检索测试（Max Score 聚合）")
    print("=" * 70)
    print(f"Schema 目录: {SCHEMA_DIR}")
    print(f"检索列数: Top {TOP_K_COLUMNS}")
    print(f"返回表数: Top {TOP_K_TABLES}")
    print("=" * 70)
    
    # 1. 加载 BGE-M3 向量索引
    print("\n加载 BGE-M3 列级别向量索引...")
    
    # 设置 BGE-M3 嵌入模型
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    # 加载持久化的索引
    storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_DIR)
    vector_index = load_index_from_storage(storage_context)
    
    retriever = VectorIndexRetriever(
        index=vector_index,
        similarity_top_k=TOP_K_COLUMNS
    )
    print("✅ BGE-M3 向量索引加载完成")
    
    # 2. 运行测试
    results = []
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 70}")
        print(f"测试 {i}/{len(TEST_CASES)}")
        print(f"问题: {case['question']}")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 70)
        
        # 检索
        nodes = retriever.retrieve(case['question'])
        print(f"检索到 {len(nodes)} 个列")
        
        # Max Score 聚合
        aggregated = max_score_aggregate(nodes)
        top_tables = aggregated[:TOP_K_TABLES]
        
        print(f"\nMax Score 聚合结果 (Top {TOP_K_TABLES} 表):")
        for j, (table, score, best_col, cols) in enumerate(top_tables, 1):
            is_expected = "✅" if table.lower() in [t.lower() for t in case['expected_tables']] else ""
            print(f"  {j}. {table} (score={score:.4f}, best_col={best_col}, {len(cols)}列) {is_expected}")
        
        # 计算召回率
        expected_set = set(t.lower() for t in case['expected_tables'])
        retrieved_set = set(t.lower() for t, _, _, _ in top_tables)
        found = expected_set & retrieved_set
        recall = len(found) / len(expected_set) if expected_set else 1.0
        
        print(f"\n召回率: {recall:.0%}")
        if recall < 1.0:
            missing = expected_set - retrieved_set
            print(f"❌ 缺失: {missing}")
        
        results.append({
            "question": case['question'],
            "expected": case['expected_tables'],
            "retrieved": [t for t, _, _, _ in top_tables],
            "recall": recall
        })
    
    # 3. 汇总
    print("\n" + "=" * 70)
    print("测试汇总")
    print("=" * 70)
    
    full_recall = sum(1 for r in results if r['recall'] == 1.0)
    avg_recall = sum(r['recall'] for r in results) / len(results)
    
    print(f"完全召回: {full_recall}/{len(results)} ({full_recall/len(results)*100:.0f}%)")
    print(f"平均召回率: {avg_recall:.0%}")
    
    for i, r in enumerate(results, 1):
        status = "✅" if r['recall'] == 1.0 else "❌"
        print(f"\n测试 {i}: {status} (召回 {r['recall']:.0%})")
        print(f"  期望: {r['expected']}")
        print(f"  检索: {r['retrieved'][:5]}...")


if __name__ == "__main__":
    run_column_level_test()
