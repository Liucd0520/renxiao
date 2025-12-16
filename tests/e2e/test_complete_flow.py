#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整 Text-to-SQL 流程测试（使用正确的过滤函数）
"""

import os
import sys
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.SchemaLinkingTool import SchemaLinkingTool
from utils import parse_schemas_from_nodes, parse_schema_from_df
from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
from GenerateSchemas import response_filtering, filter_llm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
TEST_CASES = [
    {
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected_tables": ["t_bz_config_customer", "t_bz_config_ci_ne_root", "event_history"],
        "ground_truth_sql": """SELECT t_bz_config_customer.CUSTOMER_NAME, t_bz_config_ci_ne_root.HOST_NAME, 
event_history.EVENT_NAME, event_history.EVENT_TIME
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.NE_ID = t_bz_config_ci_ne_root.NE_ID
JOIN t_bz_config_customer ON event_history.CUSTOMER_ID = t_bz_config_customer.ID
WHERE event_history.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
AND event_history.EVENT_STATUS_NAME = 'alarm'"""
    }
]

DB_ID = "netcaredb_ai"
SCHEMA_PATH = "./spider2_dev/schemas"

# SQL 生成 Prompt
SQL_PROMPT = """你是专业的 SQL 工程师。根据数据库 Schema 和问题生成 SQL。

【数据库 Schema】
{schema}

【用户问题】
{question}

【要求】
1. 只输出 SQL 语句，不要解释
2. 使用 JOIN 关联多个表
3. 表名和列名用反引号包裹
4. 缺失的条件值用 'xxx' 占位

【SQL】
"""


def get_tables_from_df(df):
    if df.empty or 'Table Name' not in df.columns:
        return set()
    return set(df['Table Name'].unique())


def run_complete_test():
    print("=" * 70)
    print("完整 Text-to-SQL 流程测试（带过滤）")
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
    
    for case in TEST_CASES:
        print(f"\n问题: {case['question']}")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 70)
        
        retriever = RagPipeLines.get_retriever(index=vector_index)
        retriever.similarity_top_k = 100
        
        expected_set = set(case['expected_tables'])
        
        # === Step 1: 检索 ===
        print("\n[Step 1] 向量检索 + Multi-Agent 增强...")
        start = time.time()
        
        nodes = SchemaLinkingTool.retrieve_complete_by_multi_agent_debate(
            llm=llm,
            question=case['question'],
            retriever_lis=[retriever],
            open_locate=False,
            output_format="node",
            logger=logger,
            retrieve_turn_n=3
        )
        
        df = parse_schemas_from_nodes(nodes)
        tables_after_retrieval = get_tables_from_df(df)
        
        print(f"  检索耗时: {time.time()-start:.1f}s")
        print(f"  检索到 {len(df)} 列, {len(tables_after_retrieval)} 个表")
        
        found_retrieval = expected_set & tables_after_retrieval
        print(f"  期望表召回: {len(found_retrieval)}/{len(expected_set)} ({', '.join(found_retrieval)})")
        
        # === Step 2: 过滤 ===
        print("\n[Step 2] LLM 过滤无关表...")
        start = time.time()
        
        # 计算保留的模式
        turn_n_lis = df["turn_n"].unique().tolist()
        df_lis = []
        for n in turn_n_lis:
            temp_df = df[df["turn_n"] == n]
            df_reserver_rate = 0.55 * pow(0.3, n)  # reserve_rate = 0.3
            if df_reserver_rate <= 0.1:
                continue
            temp_df = temp_df.sample(min(int(len(temp_df) * df_reserver_rate), len(temp_df)), random_state=42)
            df_lis.append(temp_df)
        reserve_df = pd.concat(df_lis, axis=0, ignore_index=True) if df_lis else None
        
        # 多轮过滤
        filtered_df = df.copy()
        for round_n in range(6):  # post_retrieval_turn = 6
            if len(filtered_df) > 20:  # post_retrieval_size = 20
                tables_before = get_tables_from_df(filtered_df)
                filtered_df = response_filtering(
                    data=filtered_df, 
                    question=case['question'], 
                    chunk_size=50,  # filter_chunk_size = 50
                    reserve_df=reserve_df
                )
                tables_after = get_tables_from_df(filtered_df)
                removed = tables_before - tables_after
                if removed:
                    print(f"  轮次 {round_n+1}: 移除了 {len(removed)} 个表")
        
        tables_after_filter = get_tables_from_df(filtered_df)
        
        print(f"  过滤耗时: {time.time()-start:.1f}s")
        print(f"  过滤后剩余 {len(filtered_df)} 列, {len(tables_after_filter)} 个表")
        
        # 检查是否误删期望表
        found_after_filter = expected_set & tables_after_filter
        lost_expected = expected_set - tables_after_filter
        
        if lost_expected:
            print(f"  ⚠️ 误删了期望表: {lost_expected}")
        else:
            print(f"  ✅ 所有期望表都保留: {found_after_filter}")
        
        # === Step 3: SQL 生成 ===
        print("\n[Step 3] SQL 生成...")
        
        final_schema = parse_schema_from_df(filtered_df)
        prompt = SQL_PROMPT.format(schema=final_schema[:12000], question=case['question'])
        
        sql_response = llm.complete(prompt).text
        
        # 清理 SQL
        sql = sql_response.strip()
        if "```" in sql:
            parts = sql.split("```")
            sql = parts[1] if len(parts) > 1 else sql
            sql = sql.replace("sql", "").strip()
        
        print(f"\n生成的 SQL:\n{sql}")
        print(f"\n参考 SQL:\n{case['ground_truth_sql']}")
        
        # === 汇总 ===
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        print(f"检索阶段: {len(tables_after_retrieval)} 个表 → 过滤后: {len(tables_after_filter)} 个表")
        print(f"期望表: 检索 {len(found_retrieval)}/3, 过滤后 {len(found_after_filter)}/3")
        if lost_expected:
            print(f"❌ 误删的期望表: {lost_expected}")
        else:
            print(f"✅ 所有期望表都保留了")
        print("=" * 70)


if __name__ == "__main__":
    run_complete_test()
