#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 - 直接使用原始 get_schema 函数
"""

import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GenerateSchemas import get_schema
from llms.qwen.QwenModel import QwenModel
from utils import parse_schema_from_df
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
TEST_QUESTION = "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？"
EXPECTED_TABLES = ["t_bz_config_customer", "t_bz_config_ci_ne_root", "event_history"]
DB_ID = "netcaredb_ai"

# 加载 db_info
with open("./spider2_dev/db_info.json", "r", encoding="utf-8") as f:
    db_info = json.load(f)

# SQL 生成 Prompt
SQL_PROMPT = """你是专业的SQL工程师。根据Schema和问题生成SQL。

【Schema】
{schema}

【问题】
{question}

【要求】只输出SQL，用反引号包裹表名列名，缺失值用'xxx'占位。

【SQL】
"""


def run_test():
    print("=" * 70)
    print("LinkAlign 完整流程测试（使用原始 get_schema）")
    print("=" * 70)
    print(f"问题: {TEST_QUESTION}")
    print(f"期望表: {EXPECTED_TABLES}")
    print("-" * 70)
    
    # === Step 1 & 2: Schema Linking（检索+过滤） ===
    print("\n[Step 1&2] Schema Linking (检索+过滤)...")
    start = time.time()
    
    result_df = get_schema(
        db_id=DB_ID,
        question=TEST_QUESTION,
        instance_id="test_001",
        save_path_param="./spider2_dev/test_results",
        schema_path_param="./spider2_dev/schemas",
        db_info_param=db_info
    )
    
    elapsed = time.time() - start
    
    if result_df is not None and not result_df.empty:
        tables = set(result_df['Table Name'].unique())
        columns = len(result_df)
        
        print(f"  耗时: {elapsed:.1f}s")
        print(f"  结果: {columns} 列, {len(tables)} 个表")
        
        # 检查召回
        expected_set = set(EXPECTED_TABLES)
        found = expected_set & tables
        missing = expected_set - tables
        
        print(f"  期望表召回: {len(found)}/{len(expected_set)}")
        if missing:
            print(f"  ❌ 缺失: {missing}")
        else:
            print(f"  ✅ 全部找到: {found}")
        
        print(f"\n  返回的表: {sorted(tables)}")
        
        # === Step 3: SQL 生成 ===
        print("\n[Step 3] SQL 生成...")
        
        llm = QwenModel(model_name="qwen-turbo", temperature=0.3)
        schema_text = parse_schema_from_df(result_df)
        prompt = SQL_PROMPT.format(schema=schema_text[:10000], question=TEST_QUESTION)
        
        sql = llm.complete(prompt).text.strip()
        if "```" in sql:
            sql = sql.split("```")[1].replace("sql", "").strip()
        
        print(f"\n生成的 SQL:\n{sql}")
    else:
        print("❌ Schema Linking 失败")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    run_test()
