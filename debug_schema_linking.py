#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：追踪 Schema Linking 每一步的表变化
记录向量检索和 LLM 过滤各自去掉了哪些表
"""

import os
import sys
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.SchemaLinkingTool import SchemaLinkingTool
from utils import parse_schemas_from_nodes, set_node_turn_n
from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
TEST_QUESTION = "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？"
EXPECTED_TABLES = ["t_bz_config_customer", "t_bz_config_ci_ne_root", "event_history"]
DB_ID = "netcaredb_ai"
SCHEMA_PATH = "./spider2_dev/schemas"


def get_tables_from_nodes(nodes):
    """从 nodes 提取表名"""
    tables = set()
    for node in nodes:
        if hasattr(node, 'node') and hasattr(node.node, 'metadata'):
            meta = node.node.metadata
            # 从文件名提取表名
            if 'file_name' in meta:
                table = meta['file_name'].rsplit('_', 1)[0]  # 去掉列名部分
                # 更精确地提取表名
                parts = meta['file_name'].split('_')
                if len(parts) >= 2:
                    # 尝试找到表名（假设格式是 tablename_columnname.json）
                    for i in range(len(parts)-1, 0, -1):
                        potential_table = '_'.join(parts[:i])
                        tables.add(potential_table)
                        break
    return tables


def get_tables_from_df(df):
    """从 DataFrame 提取表名"""
    if df.empty or 'Table Name' not in df.columns:
        return set()
    return set(df['Table Name'].unique())


def run_debug_test():
    print("=" * 70)
    print("Schema Linking 调试测试")
    print("=" * 70)
    print(f"问题: {TEST_QUESTION}")
    print(f"期望表: {EXPECTED_TABLES}")
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
    retriever.similarity_top_k = 100  # 设置高 top_k
    
    print(f"\n[Step 1] 向量检索 (top_k=100)...")
    
    # === Step 1: 首次向量检索 ===
    from tools.SchemaLinkingTool import SchemaLinkingTool
    
    # 跨语言扩展
    expanded = SchemaLinkingTool.expand_query_cross_lingual(llm=llm, query=TEST_QUESTION)
    print(f"  扩展后的查询: {expanded[:100]}...")
    
    combined_query = TEST_QUESTION + " " + expanded
    
    # 检索
    initial_nodes = SchemaLinkingTool.parallel_retrieve([retriever], [combined_query])
    initial_nodes = [set_node_turn_n(node, 0) for node in initial_nodes]
    
    initial_df = parse_schemas_from_nodes(initial_nodes)
    initial_tables = get_tables_from_df(initial_df)
    
    print(f"  检索到 {len(initial_nodes)} 个列, {len(initial_tables)} 个表")
    
    # 检查期望表
    expected_set = set(EXPECTED_TABLES)
    found_in_initial = expected_set & initial_tables
    missing_in_initial = expected_set - initial_tables
    
    print(f"  ✅ 初始检索找到的期望表: {found_in_initial}")
    if missing_in_initial:
        print(f"  ❌ 初始检索缺失的期望表: {missing_in_initial}")
        print(f"     → 问题出在向量检索阶段！这些表的 embedding 与问题不匹配")
    
    print(f"\n  检索到的全部表: {sorted(initial_tables)}")
    
    # === Step 2: Multi-Agent 增强检索 ===
    print(f"\n[Step 2] Multi-Agent 问题增强检索 (turn_n=3)...")
    
    all_nodes = SchemaLinkingTool.retrieve_complete_by_multi_agent_debate(
        llm=llm,
        question=TEST_QUESTION,
        retriever_lis=[retriever],
        open_locate=False,
        output_format="node",
        logger=logger,
        retrieve_turn_n=3
    )
    
    enhanced_df = parse_schemas_from_nodes(all_nodes)
    enhanced_tables = get_tables_from_df(enhanced_df)
    
    print(f"  增强后检索到 {len(all_nodes)} 个列, {len(enhanced_tables)} 个表")
    
    found_after_enhance = expected_set & enhanced_tables
    missing_after_enhance = expected_set - enhanced_tables
    new_found = found_after_enhance - found_in_initial
    
    if new_found:
        print(f"  ✅ 增强后新找到的期望表: {new_found}")
    if missing_after_enhance:
        print(f"  ❌ 增强后仍缺失的期望表: {missing_after_enhance}")
    
    # 新增的表
    added_tables = enhanced_tables - initial_tables
    if added_tables:
        print(f"  ➕ 增强后新增的表: {added_tables}")
    
    print(f"\n  增强后的全部表: {sorted(enhanced_tables)}")
    
    # === 汇总 ===
    print("\n" + "=" * 70)
    print("调试总结")
    print("=" * 70)
    
    print(f"\n期望表: {EXPECTED_TABLES}")
    print(f"\n向量检索阶段结果:")
    print(f"  - 找到的期望表: {found_in_initial}")
    print(f"  - 缺失的期望表: {missing_in_initial}")
    
    print(f"\n增强检索阶段结果:")
    print(f"  - 找到的期望表: {found_after_enhance}")
    print(f"  - 缺失的期望表: {missing_after_enhance}")
    
    if missing_after_enhance:
        print(f"\n❌ 最终缺失表的原因分析:")
        for table in missing_after_enhance:
            if table in missing_in_initial:
                print(f"   - {table}: 向量检索阶段就没找到（Schema 描述与问题不匹配）")
            else:
                print(f"   - {table}: 向量检索找到了，但被 LLM 过滤掉了")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_debug_test()
