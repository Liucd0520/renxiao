#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 批量优化表描述

使用 LLM 为每个表生成高质量的业务描述，替代手动编写。
"""

import os
import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llms.qwen.QwenModel import QwenModel


# LLM 描述生成 Prompt
DESCRIPTION_PROMPT = """你是一个数据库专家。请根据以下表的元数据，生成一个简洁清晰的中文业务描述。

【表名】
{table_name}

【表注释】
{table_comment}

【列信息】
{columns_info}

【要求】
1. 用一句话概括这个表的业务用途
2. 说明这个表存储什么类型的数据
3. 如果是核心表，指出与哪些其他表有关联（基于外键列名判断，如 CUSTOMER_ID, NE_ID）
4. 长度控制在 50-100 字
5. 不要包含技术细节如主键、索引等
6. 直接输出描述，不要任何解释

输出格式示例：
"客户配置表，存储平台所有客户的基础信息，包括客户名称、联系方式、服务等级等。是设备表和事件表的关联主表。"
"""


def generate_description(llm, table_name, table_comment, columns):
    """使用 LLM 生成表描述"""
    # 构建列信息
    columns_info = []
    for col in columns[:30]:  # 只取前 30 列避免 prompt 太长
        col_str = f"{col['name']}"
        if col.get('description'):
            col_str += f"({col['description']})"
        columns_info.append(col_str)
    
    prompt = DESCRIPTION_PROMPT.format(
        table_name=table_name,
        table_comment=table_comment or "无",
        columns_info=", ".join(columns_info) + (f" ... 等共 {len(columns)} 列" if len(columns) > 30 else "")
    )
    
    try:
        response = llm.complete(prompt).text.strip()
        # 清理输出
        response = response.strip('"').strip("'").strip()
        return response
    except Exception as e:
        return f"表 {table_name}"


def generate_enhanced_embedding_text(table_name, llm_description, columns):
    """生成增强的 embedding_text"""
    parts = []
    
    # LLM 生成的描述
    if llm_description:
        parts.append(llm_description)
    
    # 表名
    parts.append(f"表名: {table_name}")
    
    # 所有列名
    column_strs = []
    for col in columns:
        col_str = col['name']
        if col.get('description'):
            col_str += f"({col['description']})"
        column_strs.append(col_str)
    
    parts.append(f"列: {', '.join(column_strs)}")
    parts.append(f"共 {len(columns)} 列")
    
    return "\n".join(parts)


def enhance_schema_with_llm(input_dir, output_dir):
    """使用 LLM 增强所有表的描述"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-plus", temperature=0.3)
    
    # 获取所有 JSON 文件
    json_files = list(input_path.glob("*.json"))
    print(f"找到 {len(json_files)} 个表需要处理")
    
    processed = 0
    errors = 0
    start_time = time.time()
    
    for i, json_file in enumerate(json_files, 1):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data['meta_data']['table_name']
        table_comment = data.get('table_comment')
        columns = data.get('columns', [])
        
        # 生成 LLM 描述
        try:
            llm_description = generate_description(llm, table_name, table_comment, columns)
            
            # 更新数据
            data['llm_description'] = llm_description
            data['embedding_text'] = generate_enhanced_embedding_text(
                table_name, llm_description, columns
            )
            
            processed += 1
        except Exception as e:
            print(f"  ❌ {table_name}: {str(e)}")
            errors += 1
            continue
        
        # 保存到输出目录
        output_file = output_path / f"{table_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 进度显示
        if i % 20 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (len(json_files) - i) / rate
            print(f"[{i}/{len(json_files)}] 已处理... (剩余约 {remaining:.0f}秒)")
    
    print(f"\n✅ 完成！")
    print(f"   - 成功: {processed}/{len(json_files)}")
    print(f"   - 失败: {errors}")
    print(f"   - 耗时: {time.time() - start_time:.1f}秒")
    print(f"📁 输出目录: {output_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM 批量优化表描述")
    parser.add_argument("--input", default="./spider2_dev/schemas_table_level_full/netcaredb_ai",
                       help="输入 Schema 目录")
    parser.add_argument("--output", default="./spider2_dev/schemas_table_level_llm/netcaredb_ai",
                       help="输出目录")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("LLM 批量优化表描述".center(60))
    print("=" * 60)
    print(f"输入目录: {args.input}")
    print(f"输出目录: {args.output}")
    print("=" * 60 + "\n")
    
    enhance_schema_with_llm(args.input, args.output)
