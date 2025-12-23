#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Qwen 32B 优化列级别 Schema 描述

目标：
- 为核心表的列生成更丰富的描述
- 添加同义词、常见用法等
- 生成 embedding_text 用于检索

Qwen 32B 配置：
- API: http://172.31.24.112:33080/v1
- Model: Qwen2.5-Coder-32B-Instruct
"""

import os
import sys
import json
import time
from pathlib import Path
from openai import OpenAI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# Qwen 32B 配置
QWEN_API_KEY = "yfzx202510"
QWEN_BASE_URL = "http://172.31.24.112:33080/v1"
QWEN_MODEL = "Qwen2.5-Coder-32B-Instruct"

# Schema 目录
COLUMN_SCHEMA_DIR = os.path.join(PROJECT_ROOT, "spider2_dev/schemas/netcaredb_ai")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "spider2_dev/schemas_column_enhanced/netcaredb_ai")

# 核心表（优先优化这些表的列）
CORE_TABLES = [
    "t_bz_config_ci_ne_root",  # 设备表
    "t_bz_config_customer",     # 客户表
    "event_history",            # 告警表
    "t_bz_config_region",       # 区域表
    "collector_v2",             # 采集机表
    "ne_type",                  # 设备类型表
]

# 每个表最多处理多少列
MAX_COLUMNS_PER_TABLE = 50


def call_qwen(prompt, max_tokens=500):
    """调用 Qwen 32B API"""
    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL
    )
    
    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": "你是数据库专家，帮助生成列描述。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3,
            timeout=30.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def enhance_column_description(table_name, column_name, column_type, original_desc, sample_rows):
    """为单个列生成增强描述"""
    
    samples_str = ", ".join(str(s) for s in sample_rows[:5]) if sample_rows else "无"
    
    prompt = f"""请为以下数据库列生成丰富的中文描述，用于向量检索。

表名: {table_name}
列名: {column_name}
类型: {column_type}
原始描述: {original_desc or '无'}
示例值: {samples_str}

要求：
1. 生成简洁但信息丰富的描述（50-100字）
2. 包含该列的业务含义、常见用法
3. 包含同义词（如"设备"也叫"网元"、"NE"）
4. 如果是关键标识列，说明其作用

直接输出描述文本，不要其他内容："""
    
    response = call_qwen(prompt)
    return response if response else original_desc


def generate_embedding_text(table_name, column_name, column_type, enhanced_desc, sample_rows):
    """生成用于向量检索的 embedding_text"""
    parts = [
        f"表: {table_name}",
        f"列: {column_name}",
        f"类型: {column_type}",
    ]
    
    if enhanced_desc:
        parts.append(f"描述: {enhanced_desc}")
    
    if sample_rows:
        samples = sample_rows[:5]
        parts.append(f"示例值: {', '.join(str(s) for s in samples)}")
    
    return "\n".join(parts)


def process_core_tables():
    """处理核心表的列"""
    print("=" * 70)
    print("使用 Qwen 32B 优化列级别 Schema")
    print("=" * 70)
    print(f"核心表: {CORE_TABLES}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 70)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 收集需要处理的列
    columns_to_process = []
    schema_dir = Path(COLUMN_SCHEMA_DIR)
    
    for json_file in schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("meta_data", {}).get("table_name", "")
        if table_name in CORE_TABLES:
            columns_to_process.append((json_file, data))
    
    print(f"\n找到 {len(columns_to_process)} 个核心表的列待处理")
    
    # 按表分组统计
    table_counts = {}
    for _, data in columns_to_process:
        table = data.get("meta_data", {}).get("table_name", "")
        table_counts[table] = table_counts.get(table, 0) + 1
    
    for table, count in sorted(table_counts.items()):
        print(f"  {table}: {count} 列")
    
    # 处理每个列
    processed = 0
    table_processed_counts = {t: 0 for t in CORE_TABLES}
    
    for json_file, data in columns_to_process:
        table_name = data.get("meta_data", {}).get("table_name", "")
        
        # 每个表最多处理 MAX_COLUMNS_PER_TABLE 列
        if table_processed_counts[table_name] >= MAX_COLUMNS_PER_TABLE:
            continue
        
        column_name = data.get("column_name", "")
        column_type = data.get("column_types", "")
        original_desc = data.get("column_descriptions", "")
        sample_rows = data.get("sample_rows", [])
        
        print(f"\n[{processed + 1}] {table_name}.{column_name}")
        print(f"  原始描述: {original_desc}")
        
        # 调用 LLM 生成增强描述
        enhanced_desc = enhance_column_description(
            table_name, column_name, column_type, original_desc, sample_rows
        )
        print(f"  增强描述: {enhanced_desc[:60]}..." if enhanced_desc and len(enhanced_desc) > 60 else f"  增强描述: {enhanced_desc}")
        
        # 生成 embedding_text
        embedding_text = generate_embedding_text(
            table_name, column_name, column_type, enhanced_desc, sample_rows
        )
        
        # 保存增强后的 schema
        enhanced_data = data.copy()
        enhanced_data["llm_description"] = enhanced_desc
        enhanced_data["embedding_text"] = embedding_text
        
        output_file = Path(OUTPUT_DIR) / json_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        processed += 1
        table_processed_counts[table_name] += 1
        
        # 避免 API 限流
        time.sleep(0.3)
    
    print(f"\n" + "=" * 70)
    print(f"完成！共处理 {processed} 个列")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    process_core_tables()
