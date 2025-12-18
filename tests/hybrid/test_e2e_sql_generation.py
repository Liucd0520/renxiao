#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端 SQL 生成对比测试

对比：
1. 完整格式 Schema → LLM → SQL
2. 压缩格式 Schema → LLM → SQL

验证压缩格式是否影响 SQL 生成质量
"""

import os
import sys
import json
from pathlib import Path
from openai import OpenAI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from config import QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL

TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"

# 测试用例（使用 cc_result.csv 中正确的 Case）
TEST_CASES = [
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "tables": ["t_bz_config_customer"],
        "expected_sql_keywords": ["COUNT", "t_bz_config_customer", "CUSTOMER_ID"]
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "tables": ["t_bz_config_ci_ne_root"],
        "expected_sql_keywords": ["COUNT", "t_bz_config_ci_ne_root", "CI_ID"]
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "tables": ["t_bz_config_ci_ne_root"],
        "expected_sql_keywords": ["COUNT", "t_bz_config_ci_ne_root", "ONLINE_TIME"]
    },
]

SQL_PROMPT_TEMPLATE = """你是一个 SQL 专家。根据用户的问题和提供的数据库 Schema，生成正确的 SQL 查询。

## 用户问题
{question}

## 数据库 Schema
{schema}

## 要求
1. 只输出 SQL 语句，不要其他解释
2. 使用 MySQL 语法
3. 合理使用 WHERE、GROUP BY、ORDER BY 等子句

## SQL
"""


def load_table_data(table_name):
    """加载表的完整数据"""
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
                "description": col_data.get("column_descriptions", ""),
                "samples": col_data.get("sample_rows", [])[:3]
            })
    
    return table_data, columns


def format_full(tables):
    """完整格式"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        lines = [f"表名: {table_name}"]
        if table_data.get("llm_description"):
            lines.append(f"描述: {table_data['llm_description']}")
        lines.append("列信息:")
        for col in columns:
            col_line = f"  - {col['name']} ({col['type']})"
            if col['description']:
                col_line += f": {col['description']}"
            if col['samples']:
                col_line += f" [样本: {', '.join(str(s) for s in col['samples'])}]"
            lines.append(col_line)
        result.append("\n".join(lines))
    return "\n\n".join(result)


def format_compact(tables):
    """精简格式"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        lines = [f"表: {table_name}"]
        if table_data.get("llm_description"):
            desc = table_data['llm_description'][:100]
            lines.append(f"说明: {desc}...")
        col_strs = [f"{c['name']}({c['type'][:15]})" for c in columns]
        lines.append(f"列: {', '.join(col_strs)}")
        result.append("\n".join(lines))
    return "\n\n".join(result)


def format_minimal(tables):
    """最精简格式"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        desc = table_data.get("llm_description", "")[:60] + "..." if table_data.get("llm_description") else ""
        col_names = [c['name'] for c in columns]
        result.append(f"{table_name}: {desc}\n  列: {', '.join(col_names)}")
    return "\n\n".join(result)


def call_llm(prompt):
    """调用 LLM 生成 SQL"""
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    
    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.1,  # 低温度，确保稳定性
            timeout=60.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"


def check_sql_quality(sql, expected_keywords):
    """检查 SQL 是否包含关键要素"""
    sql_upper = sql.upper()
    matches = sum(1 for kw in expected_keywords if kw.upper() in sql_upper)
    return matches, len(expected_keywords)


def run_e2e_test():
    print("=" * 80)
    print("端到端 SQL 生成对比测试")
    print("=" * 80)
    print(f"模型: {QWEN_MODEL}")
    print(f"API: {QWEN_BASE_URL}")
    print("=" * 80)
    
    formats = [
        ("完整格式", format_full),
        ("精简格式", format_compact),
        ("最精简格式", format_minimal),
    ]
    
    results = {name: [] for name, _ in formats}
    
    for case in TEST_CASES:
        print(f"\n{'=' * 60}")
        print(f"测试 {case['id']}: {case['question']}")
        print(f"期望关键词: {case['expected_sql_keywords']}")
        print("-" * 60)
        
        for format_name, format_func in formats:
            schema = format_func(case['tables'])
            prompt = SQL_PROMPT_TEMPLATE.format(
                question=case['question'],
                schema=schema
            )
            
            print(f"\n[{format_name}]")
            print(f"Schema 长度: {len(schema)} 字符")
            
            sql = call_llm(prompt)
            print(f"生成 SQL:\n{sql[:200]}..." if len(sql) > 200 else f"生成 SQL:\n{sql}")
            
            matches, total = check_sql_quality(sql, case['expected_sql_keywords'])
            score = matches / total if total > 0 else 0
            results[format_name].append(score)
            print(f"关键词匹配: {matches}/{total} ({score:.0%})")
    
    # 汇总
    print("\n" + "=" * 80)
    print("汇总")
    print("=" * 80)
    
    print(f"\n{'格式':<15} | {'平均匹配率':>12}")
    print("-" * 35)
    
    for format_name, _ in formats:
        avg = sum(results[format_name]) / len(results[format_name]) if results[format_name] else 0
        print(f"{format_name:<15} | {avg:>12.0%}")


if __name__ == "__main__":
    run_e2e_test()
