#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema 压缩测试

方案：
1. 保留候选表的所有列（不过滤，确保不丢列）
2. 精简展示格式，减少 token

对比不同格式的 token 数量：
- 格式1：完整格式（表名+列名+类型+描述+样本）
- 格式2：精简格式（表名+列名+类型）
- 格式3：最精简格式（表名+列名列表）
"""

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"

TEST_TABLES = ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]


def load_table_data(table_name):
    """加载表的完整数据"""
    # 加载表级别信息
    table_file = Path(TABLE_SCHEMA_DIR) / f"{table_name}.json"
    if table_file.exists():
        with open(table_file, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
    else:
        table_data = {"table_name": table_name}
    
    # 加载列级别信息
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


def format_full(table_data, columns):
    """格式1：完整格式"""
    lines = []
    table_name = table_data.get("table_name", table_data.get("meta_data", {}).get("table_name", ""))
    lines.append(f"表名: {table_name}")
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
    return "\n".join(lines)


def format_compact(table_data, columns):
    """格式2：精简格式（列名+类型）"""
    lines = []
    table_name = table_data.get("table_name", table_data.get("meta_data", {}).get("table_name", ""))
    lines.append(f"表: {table_name}")
    if table_data.get("llm_description"):
        lines.append(f"描述: {table_data['llm_description'][:100]}...")
    col_strs = [f"{c['name']}({c['type'][:20]})" for c in columns]
    lines.append(f"列: {', '.join(col_strs)}")
    return "\n".join(lines)


def format_minimal(table_data, columns):
    """格式3：最精简格式（只有列名列表）"""
    table_name = table_data.get("table_name", table_data.get("meta_data", {}).get("table_name", ""))
    desc = table_data.get("llm_description", "")[:60] + "..." if table_data.get("llm_description") else ""
    col_names = [c['name'] for c in columns]
    return f"{table_name}: {desc}\n  列: {', '.join(col_names)}"


def format_sql_style(table_data, columns):
    """格式4：SQL DDL 风格"""
    table_name = table_data.get("table_name", table_data.get("meta_data", {}).get("table_name", ""))
    lines = [f"CREATE TABLE {table_name} ("]
    for i, col in enumerate(columns):
        comma = "," if i < len(columns) - 1 else ""
        desc = f" -- {col['description'][:30]}" if col['description'] else ""
        lines.append(f"  {col['name']} {col['type']}{comma}{desc}")
    lines.append(");")
    if table_data.get("llm_description"):
        lines.append(f"-- 说明: {table_data['llm_description'][:80]}")
    return "\n".join(lines)


def count_tokens_approx(text):
    """粗略估计 token 数（中文约 1.5 字符/token，英文约 4 字符/token）"""
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.5 + other_chars / 4)


def run_compression_test():
    print("=" * 80)
    print("Schema 压缩测试")
    print("=" * 80)
    
    formats = [
        ("完整格式", format_full),
        ("精简格式", format_compact),
        ("最精简格式", format_minimal),
        ("SQL DDL 风格", format_sql_style),
    ]
    
    total_tokens = {name: 0 for name, _ in formats}
    
    for table_name in TEST_TABLES:
        print(f"\n{'=' * 60}")
        print(f"表: {table_name}")
        print("-" * 60)
        
        table_data, columns = load_table_data(table_name)
        print(f"列数: {len(columns)}")
        
        for format_name, format_func in formats:
            text = format_func(table_data, columns)
            tokens = count_tokens_approx(text)
            total_tokens[format_name] += tokens
            chars = len(text)
            
            print(f"\n[{format_name}] {chars} 字符, ~{tokens} tokens")
            print("-" * 40)
            # 只展示前 500 字符
            if len(text) > 500:
                print(text[:500] + "\n...")
            else:
                print(text)
    
    # 汇总
    print("\n" + "=" * 80)
    print("汇总（3张表）")
    print("=" * 80)
    
    print(f"\n{'格式':<15} | {'总 Tokens':>12} | {'压缩比':>10}")
    print("-" * 45)
    
    base = total_tokens["完整格式"]
    for format_name, _ in formats:
        tokens = total_tokens[format_name]
        ratio = tokens / base if base > 0 else 0
        print(f"{format_name:<15} | {tokens:>12} | {ratio:>10.0%}")


if __name__ == "__main__":
    run_compression_test()
