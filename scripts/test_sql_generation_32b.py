#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Qwen2.5-Coder-32B-Instruct 进行完整 100 个问题的 SQL 生成测试

对比两种模式:
1. 不开 thinking (直接输出 SQL)
2. 开 thinking (让模型思考后再输出)

判断标准: 使用的表和关键字段是否正确
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from openai import OpenAI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# 生产环境模型配置
QWEN_MODEL = "Qwen2.5-Coder-32B-Instruct"
QWEN_BASE_URL = "http://172.31.24.112:33080/v1"
QWEN_API_KEY = "yfzx202510"

# 配置路径
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
QUESTIONS_FILE = "./test_questions_100.json"
OUTPUT_FILE = "./docs/milestone_20241219/sql_generation_100_test_report.md"

# 两种 Prompt
PROMPT_NO_THINK = """你是一个 MySQL 专家。根据用户问题和数据库 Schema，直接生成正确的 SQL 查询。

## 用户问题
{question}

## 数据库 Schema
{schema}

## 要求
- 直接输出 SQL，不要解释，不要思考过程
- 使用 MySQL 语法

SQL:"""

PROMPT_WITH_THINK = """你是一个资深的 MySQL 专家。请根据用户问题和数据库 Schema，生成正确的 SQL 查询。

## 用户问题
{question}

## 数据库 Schema
{schema}

## 任务
请先深度思考：
1. 这个问题需要查询哪些表？
2. 需要哪些字段？JOIN 条件是什么？
3. WHERE 条件和 GROUP BY 怎么写？

思考完成后，输出最终的 SQL 查询。

## 回答
"""


def load_table_data(table_name):
    """加载单个表的详细数据"""
    table_file = Path(TABLE_SCHEMA_DIR) / f"{table_name}.json"
    if table_file.exists():
        with open(table_file, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
    else:
        table_data = {"table_name": table_name}
    
    columns = []
    for col_file in Path(COLUMN_SCHEMA_DIR).glob("*.json"):
        with open(col_file, 'r', encoding='utf-8') as f:
            col_data = json.load(f)
        meta = col_data.get("meta_data", {})
        if meta.get("table_name", "").lower() == table_name.lower():
            columns.append({
                "name": col_data.get("column_name", ""),
                "type": col_data.get("column_types", ""),
            })
    return table_data, columns


def load_test_questions():
    """加载测试问题"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_schema_compact(tables):
    """精简格式化 Schema"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        
        lines = [f"表: {table_name}"]
        if table_data.get("llm_description"):
            lines.append(f"说明: {table_data['llm_description'][:100]}...")
        col_strs = [f"{c['name']}({c['type'][:20]})" for c in columns[:25]]
        lines.append(f"列: {', '.join(col_strs)}")
        result.append("\n".join(lines))
    
    return "\n\n".join(result)


def call_llm(prompt, max_tokens=2048):
    """调用 LLM"""
    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL
    )
    
    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.1,
            timeout=120.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {e}"


def extract_sql(text):
    """提取 SQL"""
    if not text:
        return ""
    
    # 移除 think 标签内容
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    
    # 尝试提取代码块
    if "```sql" in text:
        match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    elif "```" in text:
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # 查找 SELECT 语句
    if "SELECT" in text.upper():
        idx = text.upper().find("SELECT")
        # 找到分号或双换行
        end_idx = len(text)
        for end_char in [";", "\n\n"]:
            pos = text.find(end_char, idx)
            if pos != -1 and pos < end_idx:
                end_idx = pos + 1
        return text[idx:end_idx].strip()
    
    return text.strip()[:500]


def judge_sql(generated_sql, expected_sql, expected_tables):
    """
    判断生成的 SQL 是否正确
    
    判断标准:
    1. 使用的表是否正确（主表必须包含）
    2. 关键字段是否正确（SELECT/WHERE 中的核心字段）
    3. SQL 结构是否合理（有 SELECT/FROM）
    """
    gen_upper = generated_sql.upper()
    exp_upper = expected_sql.upper()
    
    errors = []
    
    # 1. 检查是否有有效的 SQL
    if "SELECT" not in gen_upper or "FROM" not in gen_upper:
        return False, ["无效的 SQL 结构"]
    
    # 2. 检查主表是否包含
    for table in expected_tables:
        if table.upper() not in gen_upper:
            errors.append(f"缺少表: {table}")
    
    # 3. 检查期望 SQL 中的核心操作
    key_ops = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'GROUP BY', 'ORDER BY', 'JOIN', 'WHERE']
    for op in key_ops:
        if op in exp_upper and op not in gen_upper:
            errors.append(f"缺少操作: {op}")
    
    # 4. 提取期望 SQL 中的关键字段 (简化版)
    # 找 SELECT 后面的字段
    exp_select_match = re.search(r'SELECT\s+(.*?)\s+FROM', exp_upper, re.DOTALL)
    gen_select_match = re.search(r'SELECT\s+(.*?)\s+FROM', gen_upper, re.DOTALL)
    
    if exp_select_match and gen_select_match:
        exp_fields = set(re.findall(r'`?([A-Z_]+)`?', exp_select_match.group(1)))
        gen_fields = set(re.findall(r'`?([A-Z_]+)`?', gen_select_match.group(1)))
        
        # 至少有一个核心字段匹配
        common = exp_fields & gen_fields
        if len(common) == 0 and len(exp_fields) > 0:
            errors.append("SELECT 字段不匹配")
    
    # 判断: 没有错误或只有轻微错误
    if len(errors) == 0:
        return True, []
    elif len(errors) <= 1 and "缺少操作" in str(errors):
        return True, errors  # 轻微错误也算正确
    else:
        return False, errors


def run_full_test():
    print("=" * 70)
    print("SQL 生成完整测试 - Qwen2.5-Coder-32B-Instruct")
    print("=" * 70)
    print(f"模型: {QWEN_MODEL}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载数据
    questions = load_test_questions()
    test_count = len(questions)
    
    print(f"测试问题: {test_count} 个")
    print("对比模式: 不开 thinking vs 开 thinking")
    print("=" * 70)
    
    results_no_think = []
    results_with_think = []
    
    for i, q in enumerate(questions):
        question = q['question']
        expected_sql = q.get('sql', '')
        expected_tables = q.get('tables', [])
        
        print(f"[{i+1}/{test_count}] {question[:35]}...")
        
        # 格式化 Schema
        schema = format_schema_compact(expected_tables)
        
        # 模式 1: 不开 thinking
        prompt1 = PROMPT_NO_THINK.format(question=question, schema=schema)
        response1 = call_llm(prompt1)
        sql1 = extract_sql(response1)
        correct1, errors1 = judge_sql(sql1, expected_sql, expected_tables)
        
        results_no_think.append({
            "id": i + 1,
            "question": question,
            "correct": correct1,
            "errors": errors1,
            "sql": sql1
        })
        
        # 模式 2: 开 thinking
        prompt2 = PROMPT_WITH_THINK.format(question=question, schema=schema)
        response2 = call_llm(prompt2)
        sql2 = extract_sql(response2)
        correct2, errors2 = judge_sql(sql2, expected_sql, expected_tables)
        
        results_with_think.append({
            "id": i + 1,
            "question": question,
            "correct": correct2,
            "errors": errors2,
            "sql": sql2
        })
        
        status1 = "✅" if correct1 else "❌"
        status2 = "✅" if correct2 else "❌"
        print(f"  不开thinking: {status1} | 开thinking: {status2}")
    
    print(f"\n完成！")
    
    # 统计
    correct_no_think = sum(1 for r in results_no_think if r['correct'])
    correct_with_think = sum(1 for r in results_with_think if r['correct'])
    
    # 保存报告
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# SQL 生成完整测试报告 (100题)\n\n")
        f.write(f"**模型**: {QWEN_MODEL}\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**测试问题**: {test_count} 个\n\n")
        f.write("---\n\n")
        
        # 汇总对比
        f.write("## 汇总对比\n\n")
        f.write("| 模式 | 正确数 | 正确率 |\n")
        f.write("|-----|-------|-------|\n")
        f.write(f"| 不开 Thinking | {correct_no_think}/{test_count} | **{correct_no_think/test_count*100:.1f}%** |\n")
        f.write(f"| 开 Thinking | {correct_with_think}/{test_count} | **{correct_with_think/test_count*100:.1f}%** |\n")
        f.write("\n")
        
        diff = correct_with_think - correct_no_think
        if diff > 0:
            f.write(f"**结论**: 开 Thinking 提升了 {diff} 题的准确率\n\n")
        elif diff < 0:
            f.write(f"**结论**: 不开 Thinking 反而更好（多 {-diff} 题正确）\n\n")
        else:
            f.write("**结论**: 两种模式效果相当\n\n")
        
        f.write("---\n\n")
        
        # 错误案例对比
        f.write("## 错误案例对比\n\n")
        
        # 找出两种模式结果不同的案例
        diff_cases = []
        for r1, r2 in zip(results_no_think, results_with_think):
            if r1['correct'] != r2['correct']:
                diff_cases.append((r1, r2))
        
        if diff_cases:
            f.write(f"共有 **{len(diff_cases)}** 个问题两种模式结果不同:\n\n")
            f.write("| ID | 问题 | 不开Thinking | 开Thinking |\n")
            f.write("|----|------|-------------|------------|\n")
            for r1, r2 in diff_cases[:20]:
                s1 = "✅" if r1['correct'] else "❌"
                s2 = "✅" if r2['correct'] else "❌"
                f.write(f"| {r1['id']} | {r1['question'][:30]}... | {s1} | {s2} |\n")
            f.write("\n")
        else:
            f.write("两种模式结果完全一致。\n\n")
        
        f.write("---\n\n")
        
        # 详细错误列表
        f.write("## 不开 Thinking 模式的错误案例\n\n")
        wrong_no_think = [r for r in results_no_think if not r['correct']]
        for r in wrong_no_think[:15]:
            f.write(f"### 问题 {r['id']}: {r['question'][:40]}...\n")
            f.write(f"**错误**: {', '.join(r['errors'])}\n\n")
        
        f.write("\n---\n\n")
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"\n报告已保存: {OUTPUT_FILE}")
    print("\n" + "=" * 50)
    print("汇总")
    print("=" * 50)
    print(f"不开 Thinking: {correct_no_think}/{test_count} ({correct_no_think/test_count*100:.1f}%)")
    print(f"开 Thinking: {correct_with_think}/{test_count} ({correct_with_think/test_count*100:.1f}%)")


if __name__ == "__main__":
    run_full_test()
