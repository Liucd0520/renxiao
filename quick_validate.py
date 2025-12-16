#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证 - 只运行测试用例 5
验证 schema 增强和 prompt 改进是否有效
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.SchemaLinkingTool import SchemaLinkingTool
from utils import parse_schemas_from_nodes, parse_schema_from_df
from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
from GenerateSchemas import response_filtering
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 测试用例 5
TEST_QUESTION = "上个月上线的新设备有多少"
EXPECTED_TABLES = {"t_bz_config_ci_ne_root"}
CORRECT_SQL = """SELECT COUNT(`CI_ID`) AS `new_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `ONLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
AND YEAR(`ONLINE_TIME`) = 2025
LIMIT 10;"""

# 改进后的 SQL Prompt
SQL_PROMPT = """根据以下 Schema 信息回答用户的问题，生成 SQL 查询。

【Schema】
{schema}

【用户问题】
{question}

【规则】
1. 直接输出 SQL，不要任何思考过程或解释
2. 必须使用 Schema 中实际存在的表名和列名
3. 根据问题复杂度决定是否使用 JOIN（简单查询不需要强制 JOIN）
4. 时间条件使用动态函数如 DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
5. 表名和列名用反引号包裹
6. 不确定的参数值用 'xxx' 占位

【SQL】
```sql
"""


def get_tables_from_df(df):
    if df.empty or 'Table Name' not in df.columns:
        return set()
    return set(df['Table Name'].unique())


def main():
    print("\n" + "=" * 70)
    print("🔬 验证测试：Schema 增强 + Prompt 改进")
    print("=" * 70)
    print(f"\n问题: {TEST_QUESTION}")
    print(f"期望表: {EXPECTED_TABLES}")
    print("-" * 70)
    
    # 初始化
    llm = QwenModel(model_name="qwen-turbo", temperature=0.3)
    
    # 重新构建向量索引（强制重建）
    print("\n📦 重新构建向量索引...")
    schema_dir = "./spider2_dev/schemas/netcaredb_ai"
    vector_store_dir = os.path.join(schema_dir, "vector_store")
    
    # 删除旧的向量存储以强制重建
    if os.path.exists(vector_store_dir):
        import shutil
        shutil.rmtree(vector_store_dir)
        print("   已删除旧索引")
    
    start = time.time()
    vector_index = RagPipeLines.build_index_from_source(
        data_source=schema_dir,
        persist_dir=vector_store_dir,
        is_vector_store_exist=False,
        index_method="VectorStoreIndex"
    )
    print(f"   ✅ 向量索引构建完成 ({time.time()-start:.1f}s)")
    
    # 检索
    print("\n🔍 Step 1: 向量检索...")
    retriever = RagPipeLines.get_retriever(index=vector_index)
    retriever.similarity_top_k = 100
    
    start = time.time()
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
    tables_step1 = get_tables_from_df(df)
    found_step1 = EXPECTED_TABLES & tables_step1
    print(f"   检索到 {len(tables_step1)} 张表 ({time.time()-start:.1f}s)")
    print(f"   期望表: {'✅ 找到' if found_step1 == EXPECTED_TABLES else '❌ 缺失'} {found_step1}")
    
    # Reserve 计算
    print("\n📊 Step 2: 计算 reserve_df...")
    reserve_rate = 0.4
    turn_n_lis = df["turn_n"].unique().tolist()
    df_lis = []
    for n in turn_n_lis:
        temp_df = df[df["turn_n"] == n]
        df_reserver_rate = 0.55 * pow(reserve_rate, n)
        if df_reserver_rate <= 0.1:
            continue
        sample_size = min(int(len(temp_df) * df_reserver_rate), len(temp_df))
        if sample_size > 0:
            temp_df = temp_df.sample(sample_size, random_state=42)
            df_lis.append(temp_df)
    
    import pandas as pd
    reserve_df = pd.concat(df_lis, axis=0, ignore_index=True) if df_lis else None
    reserve_tables = get_tables_from_df(reserve_df) if reserve_df is not None else set()
    print(f"   Reserve 表数: {len(reserve_tables)}")
    
    in_reserve = EXPECTED_TABLES & reserve_tables
    print(f"   期望表在 reserve: {'✅ 是' if in_reserve else '⚠️ 否'}")
    
    # LLM 过滤
    print("\n🔄 Step 3: LLM 过滤...")
    filtered_df = df.copy()
    post_retrieval_turn = 4
    post_retrieval_size = 100
    filter_chunk_size = 250
    
    start = time.time()
    for turn in range(post_retrieval_turn):
        if len(filtered_df) > post_retrieval_size:
            tables_before = get_tables_from_df(filtered_df)
            expected_before = EXPECTED_TABLES & tables_before
            
            filtered_df = response_filtering(
                data=filtered_df,
                question=TEST_QUESTION,
                chunk_size=filter_chunk_size,
                reserve_df=reserve_df
            )
            
            tables_after = get_tables_from_df(filtered_df)
            expected_after = EXPECTED_TABLES & tables_after
            lost = expected_before - expected_after
            
            status = "❌ 丢失!" if lost else "✅"
            print(f"   轮次{turn+1}: {len(tables_before)} → {len(tables_after)} 表 {status}")
            
            if lost:
                print(f"         丢失表: {lost}")
        else:
            print(f"   轮次{turn+1}: 跳过 (列数 {len(filtered_df)} <= {post_retrieval_size})")
    
    print(f"   过滤耗时: {time.time()-start:.1f}s")
    
    # 最终表召回
    final_tables = get_tables_from_df(filtered_df)
    final_expected = EXPECTED_TABLES & final_tables
    recall = len(final_expected) / len(EXPECTED_TABLES) if EXPECTED_TABLES else 1.0
    
    print(f"\n📈 表召回率: {recall:.0%}")
    if final_expected != EXPECTED_TABLES:
        print(f"   ❌ 缺失: {EXPECTED_TABLES - final_expected}")
    else:
        print(f"   ✅ 所有期望表都保留了!")
    
    # SQL 生成
    print("\n📝 Step 4: SQL 生成...")
    schema_text = parse_schema_from_df(filtered_df)
    prompt = SQL_PROMPT.format(schema=schema_text[:15000], question=TEST_QUESTION)
    
    try:
        sql_response = llm.complete(prompt).text.strip()
        # 提取 SQL
        if "```" in sql_response:
            parts = sql_response.split("```")
            for p in parts:
                if "SELECT" in p.upper():
                    sql_response = p.replace("sql", "").strip()
                    break
    except Exception as e:
        sql_response = f"Error: {e}"
    
    print("\n" + "=" * 70)
    print("📋 结果对比")
    print("=" * 70)
    
    print("\n【LinkAlign 生成的 SQL】:")
    print(sql_response[:500])
    
    print("\n【正确 SQL】:")
    print(CORRECT_SQL)
    
    print("\n" + "=" * 70)
    print("📊 验证总结")
    print("=" * 70)
    print(f"表召回率: {recall:.0%}")
    
    # 检查生成的 SQL 是否使用了正确的表
    uses_correct_table = "t_bz_config_ci_ne_root" in sql_response
    uses_online_time = "ONLINE_TIME" in sql_response.upper()
    
    print(f"使用正确表 t_bz_config_ci_ne_root: {'✅' if uses_correct_table else '❌'}")
    print(f"使用 ONLINE_TIME 列: {'✅' if uses_online_time else '❌'}")
    
    if recall == 1.0 and uses_correct_table and uses_online_time:
        print("\n🎉 验证成功！Schema 增强和 Prompt 改进有效！")
    else:
        print("\n⚠️ 还需要进一步优化")


if __name__ == "__main__":
    main()
