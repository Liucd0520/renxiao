#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Qwen 32B 优化**全部**列级别 Schema 描述

跳过已处理的列，继续处理剩余的列
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


def call_qwen(prompt, max_tokens=300):
    """调用 Qwen 32B API"""
    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL
    )
    
    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": "你是数据库专家，生成简洁的列描述。"},
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
    samples_str = ", ".join(str(s) for s in sample_rows[:3]) if sample_rows else "无"
    
    prompt = f"""为以下数据库列生成简洁描述（30-60字），包含业务含义和同义词。

表: {table_name}
列: {column_name}
类型: {column_type}
原始描述: {original_desc or '无'}
示例: {samples_str}

直接输出描述："""
    
    response = call_qwen(prompt)
    return response if response else original_desc


def generate_embedding_text(table_name, column_name, column_type, enhanced_desc, sample_rows):
    """生成用于向量检索的 embedding_text"""
    parts = [f"表: {table_name}", f"列: {column_name}", f"类型: {column_type}"]
    if enhanced_desc:
        parts.append(f"描述: {enhanced_desc}")
    if sample_rows:
        parts.append(f"示例: {', '.join(str(s) for s in sample_rows[:3])}")
    return "\n".join(parts)


def process_all_columns():
    """处理所有列（跳过已处理的）"""
    print("=" * 70)
    print("使用 Qwen 32B 优化全部列级别 Schema")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 获取已处理的文件
    schema_dir = Path(COLUMN_SCHEMA_DIR)
    output_dir = Path(OUTPUT_DIR)
    
    all_files = list(schema_dir.glob("*.json"))
    already_done = set(f.name for f in output_dir.glob("*.json"))
    
    to_process = [f for f in all_files if f.name not in already_done]
    
    print(f"总列数: {len(all_files)}")
    print(f"已完成: {len(already_done)}")
    print(f"待处理: {len(to_process)}")
    print(f"预计时间: ~{len(to_process) * 0.4 / 60:.0f} 分钟")
    print("=" * 70)
    
    processed = 0
    failed = 0
    start_time = time.time()
    
    for json_file in to_process:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            table_name = data.get("meta_data", {}).get("table_name", "")
            column_name = data.get("column_name", "")
            column_type = data.get("column_types", "")
            original_desc = data.get("column_descriptions", "")
            sample_rows = data.get("sample_rows", [])
            
            if (processed + 1) % 100 == 0 or processed == 0:
                elapsed = time.time() - start_time
                remaining = (len(to_process) - processed) * elapsed / max(processed, 1)
                print(f"\n[{processed + 1}/{len(to_process)}] 进度: {processed/len(to_process)*100:.1f}% | 剩余: ~{remaining/60:.0f}分钟")
            
            if (processed + 1) % 20 == 0:
                print(f"  {table_name}.{column_name}")
            
            # 调用 LLM
            enhanced_desc = enhance_column_description(
                table_name, column_name, column_type, original_desc, sample_rows
            )
            
            # 生成 embedding_text
            embedding_text = generate_embedding_text(
                table_name, column_name, column_type, enhanced_desc, sample_rows
            )
            
            # 保存
            enhanced_data = data.copy()
            enhanced_data["llm_description"] = enhanced_desc
            enhanced_data["embedding_text"] = embedding_text
            
            output_file = output_dir / json_file.name
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
            
            processed += 1
            
            # 避免限流
            time.sleep(0.2)
            
        except Exception as e:
            print(f"处理 {json_file.name} 失败: {e}")
            failed += 1
    
    total_time = time.time() - start_time
    print(f"\n" + "=" * 70)
    print(f"完成！")
    print(f"成功: {processed}")
    print(f"失败: {failed}")
    print(f"总耗时: {total_time/60:.1f} 分钟")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    process_all_columns()
