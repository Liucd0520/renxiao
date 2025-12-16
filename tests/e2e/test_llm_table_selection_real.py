#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实测试数据测试 LLM 直接选表效果
"""

import os
import sys
import json
import re
import csv
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel


# 表选择 Prompt
TABLE_SELECTION_PROMPT = """你是一个数据库专家。根据用户的问题，从以下表列表中选择最相关的表（最多选 {max_tables} 张）。

## 用户问题
{question}

## 可用的表
{table_list}

## 要求
1. 分析用户问题需要哪些数据
2. 选择最相关的表（通常 3-8 张就够了）
3. 只输出表名，用逗号分隔，不要解释

## 选择的表:"""


def load_table_summaries(schema_dir):
    """加载所有表的摘要信息"""
    tables = []
    schema_files = list(Path(schema_dir).glob("*.json"))
    
    for schema_file in schema_files:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        table_name = schema_data["meta_data"]["table_name"]
        llm_desc = schema_data.get("llm_description", "")
        table_comment = schema_data.get("table_comment", "")
        column_count = schema_data.get("column_count", 0)
        
        desc = llm_desc or table_comment or ""
        
        tables.append({
            "name": table_name,
            "description": desc,
            "column_count": column_count
        })
    
    return tables


def format_table_list(tables, include_desc=True):
    """格式化表列表用于 LLM 输入"""
    lines = []
    for i, t in enumerate(tables, 1):
        if include_desc and t["description"]:
            lines.append(f"{i}. {t['name']}: {t['description']}")
        else:
            lines.append(f"{i}. {t['name']} ({t['column_count']}列)")
    return "\n".join(lines)


def clean_llm_response(response):
    """清理 LLM 响应，提取表名列表"""
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    response = response.strip()
    
    table_names = []
    for part in response.replace('\n', ',').split(','):
        name = part.strip().strip('`').strip('"').strip("'")
        name = re.sub(r'^\d+\.\s*', '', name)
        if name and not name.startswith('#'):
            table_names.append(name)
    
    return table_names


def select_tables_with_llm(question, tables, llm, max_tables=10):
    """使用 LLM 选择相关表"""
    table_list = format_table_list(tables, include_desc=True)
    
    prompt = TABLE_SELECTION_PROMPT.format(
        question=question,
        table_list=table_list,
        max_tables=max_tables
    )
    
    response = llm.complete(prompt).text
    selected_names = clean_llm_response(response)
    
    valid_names = {t["name"] for t in tables}
    selected = [name for name in selected_names if name in valid_names]
    
    return selected


def extract_tables_from_sql(sql):
    """从 SQL 中提取表名"""
    sql_upper = sql.upper()
    
    # 匹配 FROM 和 JOIN 后的表名
    patterns = [
        r'FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?',
        r'JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?',
    ]
    
    tables = set()
    for pattern in patterns:
        matches = re.findall(pattern, sql, re.IGNORECASE)
        tables.update(matches)
    
    return list(tables)


def load_test_cases(csv_path):
    """从 CSV 加载测试用例"""
    test_cases = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get('query', '').strip()
            sql = row.get('sql', '') or row.get('正确SQL', '')
            
            if not question:
                continue
            
            # 从 SQL 中提取表名作为期望表
            expected_tables = extract_tables_from_sql(sql)
            
            test_cases.append({
                "question": question,
                "expected_tables": expected_tables,
                "sql": sql
            })
    
    return test_cases


def main():
    schema_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    csv_path = "./cc_result.csv"
    max_tables = 10
    
    print("\n" + "=" * 70)
    print("LLM 直接选表测试（使用真实测试数据）".center(70))
    print("=" * 70)
    
    # 加载表摘要
    print("加载表信息...")
    tables = load_table_summaries(schema_dir)
    print(f"✅ 加载了 {len(tables)} 张表")
    
    # 加载测试用例
    print("加载测试用例...")
    test_cases = load_test_cases(csv_path)
    print(f"✅ 加载了 {len(test_cases)} 个测试用例")
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    print("✅ LLM 初始化完成")
    
    # 测试每个问题
    total_recall = 0
    total_cases = 0
    
    for i, case in enumerate(test_cases, 1):
        print("\n" + "=" * 70)
        print(f"测试 {i}/{len(test_cases)}")
        print(f"问题: {case['question'][:60]}...")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 70)
        
        selected = select_tables_with_llm(case['question'], tables, llm, max_tables)
        
        # 计算召回率
        expected = set(t.lower() for t in case['expected_tables'])
        retrieved = set(t.lower() for t in selected)
        hit = expected & retrieved
        recall = len(hit) / len(expected) if expected else 1.0
        
        total_recall += recall
        total_cases += 1
        
        print(f"召回率: {recall:.1%} ({len(hit)}/{len(expected)})")
        if hit:
            print(f"命中: {list(hit)}")
        missed = expected - retrieved
        if missed:
            print(f"遗漏: {list(missed)}")
        
        print(f"\nLLM 选择的表 ({len(selected)} 张):")
        for j, name in enumerate(selected[:5], 1):
            table_info = next((t for t in tables if t["name"] == name), None)
            desc = table_info["description"][:40] if table_info and table_info["description"] else ""
            print(f"  {j}. {name} - {desc}...")
        if len(selected) > 5:
            print(f"  ... 等共 {len(selected)} 张表")
    
    # 汇总
    avg_recall = total_recall / total_cases if total_cases else 0
    
    print("\n" + "=" * 70)
    print("测试汇总".center(70))
    print("=" * 70)
    print(f"测试用例数: {total_cases}")
    print(f"平均召回率: {avg_recall:.1%}")
    print("=" * 70)


if __name__ == "__main__":
    main()
