#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 B：SQL 生成测试（LLM 二次筛选）

流程：
1. 检索 10-20 张表
2. LLM 筛选到 3-5 张最相关的表
3. 用筛选后的表生成 SQL
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from our_algorithm.retriever import FastRetriever
from our_algorithm.table_filter import TableFilter
from our_algorithm.sql_generator import SQLGenerator


# 配置
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"
OUTPUT_DIR = "./docs/milestone_20241225"
TOP_K = 10
MAX_FILTERED_TABLES = 5


def main():
    print("=" * 70)
    print("方案 B：SQL 生成测试（LLM 二次筛选）")
    print("=" * 70)
    
    # 加载测试问题
    with open(QUESTIONS_FILE, 'r') as f:
        all_questions = json.load(f)
    print(f"加载了 {len(all_questions)} 个测试问题")
    
    # 初始化组件
    print("\n初始化检索器...")
    retriever = FastRetriever()
    
    print("\n初始化表筛选器...")
    table_filter = TableFilter(
        schema_dir="./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    )
    
    print("\n初始化 SQL 生成器...")
    generator = SQLGenerator(
        schema_dir="./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    )
    
    # Step 1: 找出检索成功的问题
    print("\n[Step 1] 检索并筛选成功的问题...")
    
    success_by_difficulty = {"simple": [], "medium": [], "hard": []}
    
    for i, q in enumerate(all_questions):
        question = q["question"]
        expected_tables = set(t.lower() for t in q.get("tables", []))
        difficulty = q.get("difficulty", "simple")
        
        # 检索
        retrieved = retriever.retrieve(question, top_k=TOP_K)
        retrieved_tables = set(name.lower() for name, _ in retrieved)
        
        # 判断是否成功（期望表都在检索结果中）
        if expected_tables <= retrieved_tables:
            q["retrieved_tables"] = [name for name, _ in retrieved]
            success_by_difficulty[difficulty].append(q)
        
        if (i + 1) % 50 == 0:
            print(f"  已检查 {i+1}/{len(all_questions)}")
    
    print("\n检索成功的问题数:")
    for d in ["simple", "medium", "hard"]:
        print(f"  {d}: {len(success_by_difficulty[d])}")
    
    # Step 2: 从成功的问题中选 150 个
    print("\n[Step 2] 选择 150 个问题（各难度 50 个）...")
    
    selected = []
    for d in ["simple", "medium", "hard"]:
        selected.extend(success_by_difficulty[d][:50])
    
    print(f"选择了 {len(selected)} 个问题")
    
    # Step 3: 方案 B 流程
    results = []
    start_time = time.time()
    
    print("\n[Step 3] 开始方案 B 流程...")
    print("流程: 检索表 -> LLM 筛选 -> 生成 SQL\n")
    
    for i, q in enumerate(selected):
        question = q["question"]
        expected_sql = q.get("sql", "")
        difficulty = q.get("difficulty", "simple")
        retrieved_tables = q["retrieved_tables"]
        expected_tables = q.get("tables", [])
        
        # LLM 筛选表
        try:
            filtered_tables = table_filter.filter_tables(
                question, 
                retrieved_tables, 
                max_tables=MAX_FILTERED_TABLES
            )
        except Exception as e:
            filtered_tables = retrieved_tables[:MAX_FILTERED_TABLES]
            print(f"  筛选失败: {e}")
        
        # 检查期望表是否在筛选结果中
        expected_set = set(t.lower() for t in expected_tables)
        filtered_set = set(t.lower() for t in filtered_tables)
        tables_preserved = expected_set <= filtered_set
        
        # 生成 SQL
        try:
            generated_sql = generator.generate_sql(question, filtered_tables)
        except Exception as e:
            generated_sql = f"ERROR: {str(e)}"
        
        status = "✅" if tables_preserved else "⚠️"
        print(f"[{i+1:2d}/{len(selected)}] [{difficulty:6s}] {status} 筛选: {len(retrieved_tables)} -> {len(filtered_tables)} 表")
        
        results.append({
            "question": question,
            "difficulty": difficulty,
            "expected_tables": expected_tables,
            "retrieved_tables": retrieved_tables,
            "filtered_tables": filtered_tables,
            "tables_preserved": tables_preserved,
            "expected_sql": expected_sql,
            "generated_sql": generated_sql
        })
    
    total_time = time.time() - start_time
    
    # 统计
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
    
    preserved_count = sum(1 for r in results if r["tables_preserved"])
    print(f"\n共测试 {len(selected)} 个问题")
    print(f"期望表被保留: {preserved_count}/{len(selected)} ({preserved_count/len(selected)*100:.1f}%)")
    print(f"耗时: {total_time:.1f}秒")
    
    # 按难度统计
    print("\n按难度:")
    for d in ["simple", "medium", "hard"]:
        d_results = [r for r in results if r["difficulty"] == d]
        d_preserved = sum(1 for r in d_results if r["tables_preserved"])
        print(f"  {d}: 保留 {d_preserved}/{len(d_results)}")
    
    # 保存结果
    output_file = Path(OUTPUT_DIR) / "sql_generation_scheme_b_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果保存到: {output_file}")
    print("请人工审核 expected_sql 与 generated_sql 的语义是否一致")


if __name__ == "__main__":
    main()
