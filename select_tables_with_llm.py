#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 直接选表工具

直接使用 LLM 从 344 张表中选择与问题相关的表，
避免向量检索的语言不匹配问题。
"""

import os
import sys
import json
import argparse
import re
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
        
        # 使用 LLM 描述或表注释
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
    # 去除 <think>...</think>
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    
    # 提取表名
    response = response.strip()
    
    # 分割并清理
    table_names = []
    for part in response.replace('\n', ',').split(','):
        name = part.strip().strip('`').strip('"').strip("'")
        # 去掉可能的序号
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
    
    # 验证选择的表名是否存在
    valid_names = {t["name"] for t in tables}
    selected = [name for name in selected_names if name in valid_names]
    
    return selected, response


def expand_table_columns(table_name, schema_dir):
    """展开表的所有列信息"""
    schema_file = Path(schema_dir) / f"{table_name}.json"
    
    if not schema_file.exists():
        return []
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    return schema_data.get("columns", [])


def test_table_selection(questions, tables, schema_dir, llm, max_tables=10):
    """测试 LLM 表选择效果"""
    for q in questions:
        print("\n" + "=" * 70)
        print(f"问题: {q['question']}")
        if q.get('expected_tables'):
            print(f"期望表: {q['expected_tables']}")
        print("-" * 70)
        
        selected, raw_response = select_tables_with_llm(
            q['question'], tables, llm, max_tables
        )
        
        # 检查召回率
        if q.get('expected_tables'):
            expected = set(q['expected_tables'])
            retrieved = set(selected)
            hit = expected & retrieved
            recall = len(hit) / len(expected) if expected else 0
            print(f"召回率: {recall:.1%} ({len(hit)}/{len(expected)})")
            if hit:
                print(f"命中: {list(hit)}")
            missed = expected - retrieved
            if missed:
                print(f"遗漏: {list(missed)}")
        
        print(f"\nLLM 选择的表 ({len(selected)} 张):")
        for i, name in enumerate(selected, 1):
            # 获取表的描述
            table_info = next((t for t in tables if t["name"] == name), None)
            desc = table_info["description"][:50] if table_info else ""
            print(f"  {i}. {name} - {desc}...")
        
        # 展示第一张表的列
        if selected:
            first_table = selected[0]
            columns = expand_table_columns(first_table, schema_dir)
            if columns:
                col_names = [c['name'] for c in columns[:10]]
                print(f"\n第一张表 {first_table} 的列 (前10列):")
                print(f"  {', '.join(col_names)}")
                if len(columns) > 10:
                    print(f"  ... 等共 {len(columns)} 列")


def main():
    parser = argparse.ArgumentParser(description="LLM 直接选表测试")
    parser.add_argument(
        "--schema-dir",
        default="./spider2_dev/schemas_table_level_enhanced/netcaredb_ai",
        help="表级别 schema 目录"
    )
    parser.add_argument(
        "--max-tables",
        type=int,
        default=10,
        help="最多选择的表数量"
    )
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="自定义问题"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("LLM 直接选表测试".center(70))
    print("=" * 70)
    
    # 加载表摘要
    print("加载表信息...")
    tables = load_table_summaries(args.schema_dir)
    print(f"✅ 加载了 {len(tables)} 张表")
    
    # 计算 token 估算
    total_chars = sum(len(t["name"]) + len(t["description"]) for t in tables)
    print(f"表列表总字符数: {total_chars} (~{total_chars // 4} tokens)")
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    print("✅ LLM 初始化完成")
    
    # 测试问题
    if args.question:
        test_questions = [{"question": args.question}]
    else:
        test_questions = [
            {
                "question": "查询客户小明的联系方式",
                "expected_tables": ["t_bz_config_customer"]
            },
            {
                "question": "统计上个月有多少告警事件",
                "expected_tables": ["event_history", "event_backup"]
            },
            {
                "question": "查看设备的端口状态",
                "expected_tables": ["sdw_dp_port_basic", "sdw_dp_device"]
            },
            {
                "question": "获取用户的角色权限信息",
                "expected_tables": ["framework_user", "framework_role", "framework_user_role"]
            },
            {
                "question": "查询变更工单的审批状态",
                "expected_tables": ["t_bz_change_info"]
            }
        ]
    
    test_table_selection(test_questions, tables, args.schema_dir, llm, args.max_tables)
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
