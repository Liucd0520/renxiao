#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：追踪 LLM 过滤阶段的表变化
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.SchemaLinkingTool import SchemaLinkingTool
from utils import parse_schemas_from_nodes
from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
from GenerateSchemas import response_filtering
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
TEST_QUESTION = "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？"
EXPECTED_TABLES = ["t_bz_config_customer", "t_bz_config_ci_ne_root", "event_history"]
DB_ID = "netcaredb_ai"
SCHEMA_PATH = "./spider2_dev/schemas"


def get_tables_from_df(df):
    if df.empty or 'Table Name' not in df.columns:
        return set()
    return set(df['Table Name'].unique())


def run_filter_debug():
    print("=" * 70)
    print("LLM 过滤阶段调试")
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
    retriever.similarity_top_k = 100
    
    # === Step 1: 检索 ===
    print("\n[Step 1] Multi-Agent 增强检索...")
    
    nodes = SchemaLinkingTool.retrieve_complete_by_multi_agent_debate(
        llm=llm,
        question=TEST_QUESTION,
        retriever_lis=[retriever],
        open_locate=False,
        output_format="node",
        logger=logger,
        retrieve_turn_n=3
    )
    
    df = parse_schemas_from_nodes(nodes)
    tables_before = get_tables_from_df(df)
    expected_set = set(EXPECTED_TABLES)
    
    print(f"  检索到 {len(df)} 列, {len(tables_before)} 个表")
    print(f"  期望表召回: {expected_set & tables_before}")
    print(f"  缺失: {expected_set - tables_before}")
    
    # 检查 t_bz_config_customer 是否在检索结果中
    customer_rows = df[df['Table Name'] == 't_bz_config_customer']
    print(f"\n  t_bz_config_customer 的列数: {len(customer_rows)}")
    if not customer_rows.empty:
        col_name = 'Column' if 'Column' in customer_rows.columns else 'Column Name'
        if col_name in customer_rows.columns:
            print(f"  t_bz_config_customer 的列: {customer_rows[col_name].tolist()[:10]}...")
    
    # === Step 2: 计算 reserve_df ===
    print("\n[Step 2] 计算 reserve_df...")
    
    reserve_rate = 0.4  # 原始参数
    turn_n_lis = df["turn_n"].unique().tolist()
    df_lis = []
    for n in turn_n_lis:
        temp_df = df[df["turn_n"] == n]
        df_reserver_rate = 0.55 * pow(reserve_rate, n)
        if df_reserver_rate <= 0.1:
            continue
        temp_df = temp_df.sample(min(int(len(temp_df) * df_reserver_rate), len(temp_df)), random_state=42)
        df_lis.append(temp_df)
    
    if df_lis:
        reserve_df = pd.concat(df_lis, axis=0, ignore_index=True)
    else:
        reserve_df = None
    
    reserve_tables = get_tables_from_df(reserve_df) if reserve_df is not None else set()
    print(f"  reserve_df: {len(reserve_df) if reserve_df is not None else 0} 列, {len(reserve_tables)} 个表")
    print(f"  期望表在 reserve_df 中: {expected_set & reserve_tables}")
    
    # === Step 3: LLM 过滤 ===
    print("\n[Step 3] LLM 过滤...")
    
    filter_chunk_size = 250  # 原始参数
    post_retrieval_size = 100  # 原始参数
    post_retrieval_turn = 4  # 原始参数
    
    filtered_df = df.copy()
    
    for turn in range(post_retrieval_turn):
        if len(filtered_df) > post_retrieval_size:
            tables_before_turn = get_tables_from_df(filtered_df)
            expected_before = expected_set & tables_before_turn
            
            print(f"\n  === 过滤轮次 {turn + 1} ===")
            print(f"  过滤前: {len(filtered_df)} 列, {len(tables_before_turn)} 表")
            print(f"  期望表: {expected_before}")
            
            filtered_df = response_filtering(
                data=filtered_df, 
                question=TEST_QUESTION, 
                chunk_size=filter_chunk_size, 
                reserve_df=reserve_df
            )
            
            tables_after_turn = get_tables_from_df(filtered_df)
            expected_after = expected_set & tables_after_turn
            
            removed = tables_before_turn - tables_after_turn
            lost_expected = expected_before - expected_after
            
            print(f"  过滤后: {len(filtered_df)} 列, {len(tables_after_turn)} 表")
            print(f"  期望表: {expected_after}")
            
            if removed:
                print(f"  ➖ 移除了 {len(removed)} 个表")
            if lost_expected:
                print(f"  ❌ 丢失了期望表: {lost_expected}")
                # 停止并分析
                print("\n  !!! 发现问题：期望表被过滤掉了 !!!")
                break
        else:
            print(f"\n  轮次 {turn + 1}: 跳过 (列数 {len(filtered_df)} <= {post_retrieval_size})")
    
    # === 总结 ===
    print("\n" + "=" * 70)
    print("调试总结")
    print("=" * 70)
    
    final_tables = get_tables_from_df(filtered_df)
    print(f"最终结果: {len(filtered_df)} 列, {len(final_tables)} 表")
    print(f"期望表召回: {expected_set & final_tables}")
    print(f"缺失的期望表: {expected_set - final_tables}")
    
    print("=" * 70)


if __name__ == "__main__":
    run_filter_debug()
