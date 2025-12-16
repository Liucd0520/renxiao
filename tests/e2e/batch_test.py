#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试 LinkAlign - 追踪每一步的表过滤情况
对每个问题运行完整测试，记录每一步的情况，生成 SQL 并与正确答案对比
"""

import os
import sys
import time
import json
import pandas as pd
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.SchemaLinkingTool import SchemaLinkingTool
from utils import parse_schemas_from_nodes, parse_schema_from_df
from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
from GenerateSchemas import response_filtering
import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

DB_ID = "netcaredb_ai"
SCHEMA_PATH = "./spider2_dev/schemas"
OUTPUT_DIR = "./batch_test_results"

# SQL 生成 Prompt - 改进版
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


def extract_tables_from_sql(sql_text):
    """从 SQL 中提取表名"""
    if pd.isna(sql_text) or not sql_text:
        return set()
    
    # 匹配 FROM 和 JOIN 后的表名
    pattern = r'(?:FROM|JOIN)\s+[`]?(\w+)[`]?'
    matches = re.findall(pattern, sql_text, re.IGNORECASE)
    return set(matches)


def run_single_test(question, expected_tables, llm, vector_index, test_id):
    """运行单个问题的完整测试，追踪每一步"""
    result = {
        "test_id": test_id,
        "question": question,
        "expected_tables": list(expected_tables),
        "steps": [],
        "final_tables": [],
        "generated_sql": "",
        "table_recall": 0,
        "missing_tables": [],
        "lost_at_step": None
    }
    
    retriever = RagPipeLines.get_retriever(index=vector_index)
    retriever.similarity_top_k = 100
    
    # === Step 1: 检索 ===
    step1_start = time.time()
    
    nodes = SchemaLinkingTool.retrieve_complete_by_multi_agent_debate(
        llm=llm,
        question=question,
        retriever_lis=[retriever],
        open_locate=False,
        output_format="node",
        logger=logger,
        retrieve_turn_n=3
    )
    
    df = parse_schemas_from_nodes(nodes)
    tables_step1 = get_tables_from_df(df)
    found_step1 = expected_tables & tables_step1
    missing_step1 = expected_tables - tables_step1
    
    step1 = {
        "step": "1. 向量检索+增强",
        "time": f"{time.time() - step1_start:.1f}s",
        "columns": len(df),
        "tables": len(tables_step1),
        "expected_found": list(found_step1),
        "expected_missing": list(missing_step1)
    }
    result["steps"].append(step1)
    
    if missing_step1:
        result["lost_at_step"] = "检索阶段"
    
    # === Step 2: 计算 reserve_df ===
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
    
    reserve_df = pd.concat(df_lis, axis=0, ignore_index=True) if df_lis else None
    reserve_tables = get_tables_from_df(reserve_df) if reserve_df is not None else set()
    
    step2 = {
        "step": "2. 计算 reserve_df",
        "columns": len(reserve_df) if reserve_df is not None else 0,
        "tables": len(reserve_tables),
        "expected_in_reserve": list(expected_tables & reserve_tables),
        "expected_not_in_reserve": list(expected_tables - reserve_tables)
    }
    result["steps"].append(step2)
    
    # === Step 3: LLM 过滤 ===
    filter_chunk_size = 250
    post_retrieval_size = 100
    post_retrieval_turn = 4
    
    filtered_df = df.copy()
    current_expected = found_step1.copy()
    
    step3_start = time.time()
    
    for turn in range(post_retrieval_turn):
        if len(filtered_df) > post_retrieval_size:
            tables_before = get_tables_from_df(filtered_df)
            expected_before = expected_tables & tables_before
            
            filtered_df = response_filtering(
                data=filtered_df, 
                question=question, 
                chunk_size=filter_chunk_size, 
                reserve_df=reserve_df
            )
            
            tables_after = get_tables_from_df(filtered_df)
            expected_after = expected_tables & tables_after
            
            removed = tables_before - tables_after
            lost_expected = expected_before - expected_after
            
            filter_step = {
                "step": f"3.{turn+1} LLM过滤轮次{turn+1}",
                "columns_before": len(df) if turn == 0 else "same",
                "tables_before": len(tables_before),
                "tables_after": len(tables_after),
                "removed_count": len(removed),
                "expected_before": list(expected_before),
                "expected_after": list(expected_after),
                "lost_expected": list(lost_expected)
            }
            result["steps"].append(filter_step)
            
            if lost_expected and result["lost_at_step"] is None:
                result["lost_at_step"] = f"LLM过滤轮次{turn+1}"
            
            current_expected = expected_after
        else:
            filter_step = {
                "step": f"3.{turn+1} LLM过滤轮次{turn+1}",
                "skipped": True,
                "reason": f"列数 {len(filtered_df)} <= {post_retrieval_size}"
            }
            result["steps"].append(filter_step)
    
    step3_summary = {
        "step": "3. LLM过滤总结",
        "time": f"{time.time() - step3_start:.1f}s",
        "final_columns": len(filtered_df),
        "final_tables": len(get_tables_from_df(filtered_df))
    }
    result["steps"].append(step3_summary)
    
    # === Step 4: SQL 生成 ===
    final_tables = get_tables_from_df(filtered_df)
    final_expected = expected_tables & final_tables
    
    schema_text = parse_schema_from_df(filtered_df)
    prompt = SQL_PROMPT.format(schema=schema_text[:15000], question=question)
    
    try:
        sql_response = llm.complete(prompt).text.strip()
        if "```" in sql_response:
            sql_response = sql_response.split("```")[1].replace("sql", "").strip()
    except Exception as e:
        sql_response = f"Error: {str(e)}"
    
    result["final_tables"] = list(final_tables)
    result["generated_sql"] = sql_response
    result["table_recall"] = len(final_expected) / len(expected_tables) if expected_tables else 1.0
    result["missing_tables"] = list(expected_tables - final_tables)
    
    step4 = {
        "step": "4. SQL生成",
        "table_recall": f"{len(final_expected)}/{len(expected_tables)}",
        "missing": list(expected_tables - final_tables)
    }
    result["steps"].append(step4)
    
    return result


def load_test_cases():
    """加载测试用例"""
    df = pd.read_csv("cc_result.csv")
    
    test_cases = []
    for idx, row in df.iterrows():
        question = row['query']
        old_sql = row['sql']
        is_correct = row['是否正确']
        correct_sql = row['正确SQL'] if pd.notna(row['正确SQL']) else old_sql
        
        # 从正确 SQL 中提取期望表
        expected_tables = extract_tables_from_sql(correct_sql)
        
        test_cases.append({
            "id": idx + 1,
            "question": question,
            "old_sql": old_sql,
            "is_correct": is_correct,
            "correct_sql": correct_sql,
            "expected_tables": expected_tables
        })
    
    return test_cases


def run_batch_test():
    """运行批量测试"""
    print("=" * 80)
    print("LinkAlign 批量测试")
    print("=" * 80)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
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
    
    # 加载测试用例
    test_cases = load_test_cases()
    print(f"\n共 {len(test_cases)} 个测试用例\n")
    
    all_results = []
    
    for case in test_cases:
        print(f"\n{'='*80}")
        print(f"[测试 {case['id']}] {case['question'][:50]}...")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 80)
        
        start_time = time.time()
        
        result = run_single_test(
            question=case['question'],
            expected_tables=case['expected_tables'],
            llm=llm,
            vector_index=vector_index,
            test_id=case['id']
        )
        
        result["old_sql"] = case['old_sql']
        result["correct_sql"] = case['correct_sql']
        result["old_is_correct"] = case['is_correct']
        result["total_time"] = f"{time.time() - start_time:.1f}s"
        
        all_results.append(result)
        
        # 打印简要结果
        print(f"\n结果: 表召回 {result['table_recall']:.0%}")
        if result['missing_tables']:
            print(f"缺失表: {result['missing_tables']}")
            print(f"丢失位置: {result['lost_at_step']}")
        print(f"耗时: {result['total_time']}")
    
    # 保存详细结果
    with open(os.path.join(OUTPUT_DIR, "detailed_results.json"), "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # 生成对比报告
    generate_comparison_report(all_results)
    
    print(f"\n\n{'='*80}")
    print("测试完成！结果保存在:")
    print(f"  - {OUTPUT_DIR}/detailed_results.json")
    print(f"  - {OUTPUT_DIR}/comparison_report.md")
    print("=" * 80)


def generate_comparison_report(results):
    """生成 Markdown 格式的对比报告"""
    report = []
    report.append("# LinkAlign 批量测试报告\n")
    report.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"测试用例数: {len(results)}\n")
    
    # 总结统计
    full_recall = sum(1 for r in results if r['table_recall'] == 1.0)
    avg_recall = sum(r['table_recall'] for r in results) / len(results) if results else 0
    
    report.append(f"\n## 总体统计\n")
    report.append(f"- 完全召回: {full_recall}/{len(results)} ({full_recall/len(results)*100:.0f}%)\n")
    report.append(f"- 平均召回率: {avg_recall:.0%}\n")
    
    report.append("\n---\n")
    
    # 每个测试用例的详细结果
    for r in results:
        report.append(f"\n## 测试 {r['test_id']}: {r['question'][:40]}...\n")
        report.append(f"\n**期望表**: `{', '.join(r['expected_tables'])}`\n")
        report.append(f"\n**表召回**: {r['table_recall']:.0%}")
        
        if r['missing_tables']:
            report.append(f" ❌ 缺失: `{', '.join(r['missing_tables'])}`\n")
            report.append(f"\n**丢失位置**: {r['lost_at_step']}\n")
        else:
            report.append(" ✅\n")
        
        # 步骤追踪
        report.append("\n### 处理步骤\n")
        report.append("| 步骤 | 表数 | 期望表 | 备注 |\n")
        report.append("|------|------|--------|------|\n")
        
        for step in r['steps']:
            step_name = step.get('step', '')
            tables = step.get('tables', step.get('tables_after', '-'))
            expected = step.get('expected_found', step.get('expected_after', '-'))
            if isinstance(expected, list):
                expected = ', '.join(expected) if expected else '-'
            
            note = ""
            if step.get('skipped'):
                note = f"跳过: {step.get('reason', '')}"
            elif step.get('lost_expected'):
                note = f"❌ 丢失: {', '.join(step['lost_expected'])}"
            elif step.get('expected_missing'):
                note = f"❌ 缺失: {', '.join(step['expected_missing'])}"
            
            report.append(f"| {step_name} | {tables} | {expected} | {note} |\n")
        
        # SQL 对比
        report.append("\n### SQL 对比\n")
        
        report.append("\n**LinkAlign 生成的 SQL**:\n")
        report.append(f"```sql\n{r['generated_sql']}\n```\n")
        
        report.append("\n**正确 SQL**:\n")
        report.append(f"```sql\n{r['correct_sql']}\n```\n")
        
        report.append("\n---\n")
    
    # 保存报告
    report_path = os.path.join(OUTPUT_DIR, "comparison_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("".join(report))


if __name__ == "__main__":
    run_batch_test()
