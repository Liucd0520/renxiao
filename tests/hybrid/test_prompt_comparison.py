#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt 模式对比测试

对比两种 Prompt 模式：
1. 禁止思考模式：直接输出 SQL，不要思考过程
2. 深度思考模式：鼓励深度思考、反复推敲

测试目的：验证深度思考是否能提高 SQL 生成质量
"""

import os
import sys
import json
import re
from pathlib import Path
from openai import OpenAI
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from config import QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL

TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
OUTPUT_FILE = "./docs/milestone_20241217_table_column_fusion/prompt_comparison_report.md"

# 两种 Prompt 模式
PROMPT_NO_THINK = """你是一个 MySQL 专家。根据用户问题和数据库 Schema，生成正确的 SQL 查询。

## 问题
{question}

## Schema
{schema}

## 要求
- 直接输出 SQL 语句，不要思考过程，不要解释
- 使用 MySQL 语法
- 注意表之间的关联关系

直接输出SQL："""

PROMPT_DEEP_THINK = """你是一个资深的 MySQL 专家。请根据用户问题和数据库 Schema，生成正确的 SQL 查询。

## 用户问题
{question}

## 数据库 Schema
{schema}

## 任务
请仔细分析用户问题和数据库 Schema：
1. 深度思考：这个问题需要查询哪些表？表之间如何关联？
2. 反复推敲：选择最准确的字段，确保条件逻辑正确
3. 验证检查：SQL 语法是否正确？能否得到用户想要的结果？

请先进行深度思考，然后输出最终的 SQL 查询。

## SQL 查询
"""

# 测试用例
TEST_CASES = [
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "tables": ["t_bz_config_customer"],
        "correct_sql": "SELECT COUNT(CUSTOMER_ID) FROM t_bz_config_customer WHERE IS_ACTIVE = 1",
        "key_fields": ["COUNT", "CUSTOMER_ID", "IS_ACTIVE"]
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "tables": ["t_bz_config_ci_ne_root"],
        "correct_sql": "SELECT COUNT(CI_ID) FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0",
        "key_fields": ["COUNT", "CI_ID", "IS_DELETED"]
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "tables": ["t_bz_config_ci_ne_root"],
        "correct_sql": "SELECT COUNT(CI_ID) FROM t_bz_config_ci_ne_root WHERE ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)",
        "key_fields": ["COUNT", "ONLINE_TIME", "DATE_SUB", "INTERVAL 1 MONTH"]
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "tables": ["t_bz_config_ci_ne_root"],
        "correct_sql": "SELECT COUNT(CI_ID) FROM t_bz_config_ci_ne_root WHERE OFFLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)",
        "key_fields": ["COUNT", "OFFLINE_TIME", "DATE_SUB", "INTERVAL 1 MONTH"]
    },
]


def load_table_data(table_name):
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


def format_compact(tables):
    """精简格式：列名+类型"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        lines = [f"表: {table_name}"]
        if table_data.get("llm_description"):
            lines.append(f"说明: {table_data['llm_description'][:100]}...")
        col_strs = [f"{c['name']}({c['type'][:20]})" for c in columns]
        lines.append(f"列: {', '.join(col_strs)}")
        result.append("\n".join(lines))
    return "\n\n".join(result)


def extract_sql(text):
    """提取 SQL，清理思考过程"""
    # 移除 <think> 标签内容
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    
    # 提取 ```sql 代码块
    if "```sql" in text:
        match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    elif "```" in text:
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # 查找 SELECT 开始的 SQL
    if "SELECT" in text.upper():
        idx = text.upper().find("SELECT")
        # 找到 SQL 结束位置（分号或换行）
        end_idx = len(text)
        for end_char in [";", "\n\n"]:
            pos = text.find(end_char, idx)
            if pos != -1 and pos < end_idx:
                end_idx = pos + 1
        return text[idx:end_idx].strip()
    
    return text.strip()


def call_llm(prompt):
    """调用 LLM"""
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.1,
            timeout=120.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"


def check_sql_quality(sql, key_fields, correct_sql):
    """检查 SQL 质量"""
    sql_upper = sql.upper()
    correct_upper = correct_sql.upper()
    
    # 检查关键字段
    field_matches = sum(1 for kw in key_fields if kw.upper() in sql_upper)
    field_score = field_matches / len(key_fields) if key_fields else 0
    
    # 检查严重错误
    errors = []
    
    # 检查是否用错字段
    if "ONLINE_TIME" in correct_upper and "ONLINE_TIME" not in sql_upper:
        if "CREATE_TIME" in sql_upper:
            errors.append("用错字段：CREATE_TIME → ONLINE_TIME")
    
    if "OFFLINE_TIME" in correct_upper and "OFFLINE_TIME" not in sql_upper:
        errors.append("缺少 OFFLINE_TIME 字段")
    
    if "IS_ACTIVE" in correct_upper and "IS_ACTIVE" not in sql_upper:
        errors.append("缺少 IS_ACTIVE 条件")
    
    if "IS_DELETED" in correct_upper and "IS_DELETED" not in sql_upper:
        errors.append("缺少 IS_DELETED 条件")
    
    return {
        "field_score": field_score,
        "errors": errors,
        "is_correct": field_score >= 0.8 and len(errors) == 0
    }


def run_batch_test():
    print("=" * 80)
    print("Prompt 模式对比批量测试")
    print("=" * 80)
    print(f"模型: {QWEN_MODEL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    prompts = [
        ("禁止思考", PROMPT_NO_THINK),
        ("深度思考", PROMPT_DEEP_THINK),
    ]
    
    results = {name: {"correct": 0, "partial": 0, "wrong": 0, "sqls": []} for name, _ in prompts}
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Prompt 模式对比测试报告\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**模型**: {QWEN_MODEL}\n\n")
        f.write("---\n\n")
        
        f.write("## 测试说明\n\n")
        f.write("### 禁止思考模式\n```\n")
        f.write("要求：直接输出 SQL 语句，不要思考过程，不要解释\n")
        f.write("```\n\n")
        f.write("### 深度思考模式\n```\n")
        f.write("任务：请仔细分析用户问题和数据库 Schema\n")
        f.write("1. 深度思考：这个问题需要查询哪些表？表之间如何关联？\n")
        f.write("2. 反复推敲：选择最准确的字段，确保条件逻辑正确\n")
        f.write("3. 验证检查：SQL 语法是否正确？能否得到用户想要的结果？\n")
        f.write("```\n\n")
        f.write("---\n\n")
        
        for case in TEST_CASES:
            print(f"\n测试 {case['id']}: {case['question']}")
            
            f.write(f"## 测试 {case['id']}: {case['question']}\n\n")
            f.write(f"**正确答案关键字段**: {case['key_fields']}\n\n")
            
            schema = format_compact(case['tables'])
            
            for prompt_name, prompt_template in prompts:
                print(f"  {prompt_name}...")
                
                prompt = prompt_template.format(question=case['question'], schema=schema)
                raw_response = call_llm(prompt)
                sql = extract_sql(raw_response)
                
                quality = check_sql_quality(sql, case['key_fields'], case['correct_sql'])
                
                # 评级
                if quality['is_correct']:
                    rating = "✅ 正确"
                    results[prompt_name]['correct'] += 1
                elif quality['field_score'] >= 0.5:
                    rating = "⚠️ 部分正确"
                    results[prompt_name]['partial'] += 1
                else:
                    rating = "❌ 错误"
                    results[prompt_name]['wrong'] += 1
                
                results[prompt_name]['sqls'].append({
                    'id': case['id'],
                    'sql': sql,
                    'quality': quality,
                    'rating': rating
                })
                
                f.write(f"### {prompt_name} {rating}\n\n")
                f.write(f"**关键字段匹配**: {quality['field_score']:.0%}\n\n")
                if quality['errors']:
                    f.write(f"**问题**: {', '.join(quality['errors'])}\n\n")
                f.write(f"```sql\n{sql}\n```\n\n")
            
            f.write("---\n\n")
        
        # 汇总
        f.write("## 汇总对比\n\n")
        f.write("| 指标 | 禁止思考 | 深度思考 |\n")
        f.write("|-----|---------|--------|\n")
        f.write(f"| ✅ 正确 | {results['禁止思考']['correct']}/{len(TEST_CASES)} | {results['深度思考']['correct']}/{len(TEST_CASES)} |\n")
        f.write(f"| ⚠️ 部分正确 | {results['禁止思考']['partial']}/{len(TEST_CASES)} | {results['深度思考']['partial']}/{len(TEST_CASES)} |\n")
        f.write(f"| ❌ 错误 | {results['禁止思考']['wrong']}/{len(TEST_CASES)} | {results['深度思考']['wrong']}/{len(TEST_CASES)} |\n")
        f.write(f"| **正确率** | **{results['禁止思考']['correct']/len(TEST_CASES):.0%}** | **{results['深度思考']['correct']/len(TEST_CASES):.0%}** |\n")
        f.write("\n")
        
        # 结论
        f.write("## 结论\n\n")
        no_think_correct = results['禁止思考']['correct']
        deep_think_correct = results['深度思考']['correct']
        
        if deep_think_correct > no_think_correct:
            f.write(f"**深度思考模式更好**：正确率从 {no_think_correct/len(TEST_CASES):.0%} 提高到 {deep_think_correct/len(TEST_CASES):.0%}\n\n")
            f.write("深度思考帮助 LLM：\n")
            f.write("1. 选择正确的字段\n")
            f.write("2. 确保条件逻辑正确\n")
            f.write("3. 减少常见错误\n")
        elif deep_think_correct < no_think_correct:
            f.write(f"**禁止思考模式更好**：正确率 {no_think_correct/len(TEST_CASES):.0%} vs {deep_think_correct/len(TEST_CASES):.0%}\n\n")
        else:
            f.write(f"**两种模式效果相当**：正确率都是 {no_think_correct/len(TEST_CASES):.0%}\n\n")
        
        f.write("\n---\n\n")
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"\n报告已保存: {OUTPUT_FILE}")
    
    # 打印汇总
    print("\n" + "=" * 50)
    print("汇总")
    print("=" * 50)
    print(f"{'模式':<15} | {'正确':>8} | {'部分正确':>8} | {'错误':>8}")
    print("-" * 50)
    for name in ['禁止思考', '深度思考']:
        r = results[name]
        print(f"{name:<15} | {r['correct']:>8} | {r['partial']:>8} | {r['wrong']:>8}")


if __name__ == "__main__":
    run_batch_test()
