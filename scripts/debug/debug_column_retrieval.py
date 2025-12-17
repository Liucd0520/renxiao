#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列级别检索调试脚本

详细展示检索过程：
1. 用户问题
2. 检索到的 Top K 列及其完整 embedding text
3. 目标表的列为什么没有被检索到
"""

import os
import sys
import json
from pathlib import Path
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
TOP_K = 20  # 只展示 Top 20 方便阅读

# 测试问题
TEST_QUESTION = "现在平台上有多少台设备"
EXPECTED_TABLE = "t_bz_config_ci_ne_root"


def debug_retrieval():
    print("=" * 80)
    print("列级别检索调试报告")
    print("=" * 80)
    print(f"\n问题: {TEST_QUESTION}")
    print(f"期望表: {EXPECTED_TABLE}")
    print("\n" + "=" * 80)
    
    # 1. 加载索引
    print("\n[Step 1] 加载 BGE-M3 增强版索引...")
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_DIR)
    vector_index = load_index_from_storage(storage_context)
    
    retriever = VectorIndexRetriever(
        index=vector_index,
        similarity_top_k=TOP_K
    )
    print("✅ 索引加载完成")
    
    # 2. 检索
    print(f"\n[Step 2] 检索 Top {TOP_K} 列...")
    nodes = retriever.retrieve(TEST_QUESTION)
    print(f"检索到 {len(nodes)} 个列")
    
    # 3. 展示检索结果
    print("\n" + "=" * 80)
    print("检索结果详情")
    print("=" * 80)
    
    table_columns = defaultdict(list)
    
    for i, node in enumerate(nodes, 1):
        table_name = node.metadata.get("table_name", "unknown")
        column_name = node.metadata.get("column_name", "unknown")
        score = node.score
        text = node.text
        
        table_columns[table_name].append((column_name, score))
        
        print(f"\n--- 第 {i} 名 ---")
        print(f"表: {table_name}")
        print(f"列: {column_name}")
        print(f"分数: {score:.4f}")
        print(f"Embedding Text:")
        print("-" * 40)
        # 展示完整的 embedding text
        print(text[:800] if len(text) > 800 else text)
        if len(text) > 800:
            print("... (truncated)")
        print("-" * 40)
    
    # 4. 按表聚合
    print("\n" + "=" * 80)
    print("按表聚合（Max Score）")
    print("=" * 80)
    
    table_max_scores = {}
    for table, cols in table_columns.items():
        max_score = max(score for _, score in cols)
        best_col = [col for col, score in cols if score == max_score][0]
        table_max_scores[table] = (max_score, best_col, len(cols))
    
    sorted_tables = sorted(table_max_scores.items(), key=lambda x: x[1][0], reverse=True)
    
    print(f"\n聚合后表排名（共 {len(sorted_tables)} 个表）:")
    for i, (table, (score, best_col, col_count)) in enumerate(sorted_tables, 1):
        is_target = "✅ TARGET" if table.lower() == EXPECTED_TABLE.lower() else ""
        print(f"  {i}. {table} (score={score:.4f}, best_col={best_col}, {col_count}列) {is_target}")
    
    # 5. 检查目标表
    print("\n" + "=" * 80)
    print(f"目标表 {EXPECTED_TABLE} 分析")
    print("=" * 80)
    
    if EXPECTED_TABLE.lower() in [t.lower() for t in table_columns.keys()]:
        cols = [(c, s) for t, cols_ in table_columns.items() 
                for c, s in cols_ if t.lower() == EXPECTED_TABLE.lower()]
        print(f"\n在 Top {TOP_K} 中找到 {len(cols)} 个列:")
        for col, score in sorted(cols, key=lambda x: x[1], reverse=True):
            print(f"  - {col}: {score:.4f}")
    else:
        print(f"\n❌ 目标表不在 Top {TOP_K} 中！")
        print("\n扩大搜索范围看看...")
        
        # 扩大搜索
        retriever2 = VectorIndexRetriever(index=vector_index, similarity_top_k=200)
        nodes2 = retriever2.retrieve(TEST_QUESTION)
        
        target_cols = []
        for i, node in enumerate(nodes2, 1):
            if node.metadata.get("table_name", "").lower() == EXPECTED_TABLE.lower():
                target_cols.append((i, node.metadata.get("column_name", ""), node.score, node.text))
        
        if target_cols:
            print(f"\n在 Top 200 中找到 {len(target_cols)} 个列来自目标表:")
            for rank, col, score, text in target_cols[:5]:
                print(f"\n  排名 {rank}: {col} (score={score:.4f})")
                print(f"  Embedding Text 片段:")
                print(f"  {text[:300]}...")
        else:
            print(f"\n即使在 Top 200 中也没有找到目标表的任何列！")
    
    # 6. 对比第一名和目标表的 embedding
    print("\n" + "=" * 80)
    print("语义对比分析")
    print("=" * 80)
    
    if nodes:
        top1 = nodes[0]
        print(f"\n问题关键词: 平台, 设备, 多少台")
        print(f"\n第 1 名表: {top1.metadata.get('table_name')}")
        print(f"列: {top1.metadata.get('column_name')}")
        print(f"为什么匹配高？因为 embedding text 包含:")
        
        keywords = ["设备", "平台", "数量", "device", "num"]
        for kw in keywords:
            if kw.lower() in top1.text.lower():
                print(f"  ✅ 包含关键词: '{kw}'")
            else:
                print(f"  ❌ 不包含: '{kw}'")


if __name__ == "__main__":
    debug_retrieval()
