#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成英文版表描述

将表描述翻译成英文，用于配合英文向量模型。
"""

import os
import sys
import json
import re
import time
from pathlib import Path
import pymysql
from pymysql import cursors

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel

# 英文描述生成 Prompt
TABLE_DESCRIPTION_PROMPT_EN = """Generate a concise English description (30-50 words) for this database table.

## Table Information
Table Name: {table_name}
Table Comment: {table_comment}
Main Columns:
{columns_info}

## Requirements
1. Start with the core business concept (e.g., "Device", "Customer", "Alert", "Event")
2. Describe what data this table stores
3. No quotes or extra formatting, just the description text

## English Description:"""


def clean_llm_response(response):
    """清理 LLM 响应"""
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    response = response.replace('"', '').replace("'", '').strip()
    lines = response.split('\n')
    response = lines[0].strip() if lines else response
    if len(response) > 200:
        response = response[:200]
    return response if response else None


def get_mysql_connection(host, port, user, password, database):
    try:
        connection = pymysql.connect(
            host=host, port=port, user=user, password=password,
            database=database, charset='utf8mb4',
            cursorclass=cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None


def get_all_tables(connection):
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        return [list(row.values())[0] for row in cursor.fetchall()]


def get_table_info(connection, table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
        """)
        result = cursor.fetchone()
        table_comment = result['TABLE_COMMENT'] if result else ""

        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()

        cursor.execute(f"""
            SELECT COLUMN_NAME, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
        """)
        comments = {row['COLUMN_NAME']: row['COLUMN_COMMENT'] for row in cursor.fetchall()}

    return table_comment, columns, comments


def generate_english_description(table_name, table_comment, columns, comments, llm):
    """生成英文描述"""
    columns_info_parts = []
    for col in columns[:10]:
        col_name = col['Field']
        col_comment = comments.get(col_name, '')
        col_str = f"- {col_name}"
        if col_comment:
            col_str += f": {col_comment}"
        columns_info_parts.append(col_str)
    
    if len(columns) > 10:
        columns_info_parts.append(f"... and {len(columns) - 10} more columns")
    
    prompt = TABLE_DESCRIPTION_PROMPT_EN.format(
        table_name=table_name,
        table_comment=table_comment or "None",
        columns_info="\n".join(columns_info_parts)
    )
    
    try:
        response = llm.complete(prompt).text.strip()
        return clean_llm_response(response)
    except Exception as e:
        print(f"  ⚠️ 生成失败: {e}")
        return None


def main():
    print("\n" + "=" * 60)
    print("英文版表描述生成".center(60))
    print("=" * 60)
    
    # 连接数据库
    connection = get_mysql_connection(
        '172.31.26.206', 3306, 'ai_test', 'Netcare@13579', 'netcaredb_ai'
    )
    if not connection:
        return
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    print("✅ 使用 qwen-turbo 模型")
    
    schema_dir = Path("./spider2_dev/schemas_table_level_english")
    schema_dir.mkdir(parents=True, exist_ok=True)
    db_schema_dir = schema_dir / "netcaredb_ai"
    db_schema_dir.mkdir(parents=True, exist_ok=True)
    
    tables = get_all_tables(connection)
    print(f"找到 {len(tables)} 张表")
    
    start_time = time.time()
    
    try:
        for idx, table_name in enumerate(tables):
            # 获取表信息
            table_comment, columns, comments = get_table_info(connection, table_name)
            
            # 生成英文描述
            en_desc = generate_english_description(table_name, table_comment, columns, comments, llm)
            
            # 构建列信息
            columns_data = []
            for col in columns:
                col_name = col['Field']
                col_type = col['Type']
                col_desc = comments.get(col_name, "")
                columns_data.append({
                    "name": col_name,
                    "type": col_type,
                    "description": col_desc if col_desc else None
                })
            
            # 构建英文版 embedding_text
            embedding_text = en_desc or f"Table {table_name}"
            embedding_text += f"\nTable: {table_name}"
            embedding_text += f"\nColumns: {', '.join([c['name'] for c in columns_data[:15]])}"
            
            # 保存
            schema_data = {
                "meta_data": {
                    "db_id": "netcaredb_ai",
                    "table_name": table_name
                },
                "table_comment": table_comment if table_comment else None,
                "llm_description_en": en_desc,
                "columns": columns_data,
                "column_count": len(columns_data),
                "embedding_text": embedding_text
            }
            
            file_path = db_schema_dir / f"{table_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema_data, f, ensure_ascii=False, indent=2)
            
            if (idx + 1) % 20 == 0:
                print(f"[{idx + 1}/{len(tables)}] 已处理...")
    
    finally:
        connection.close()
    
    elapsed = time.time() - start_time
    
    # 生成 db_info 文件
    db_info = [{"db_id": "netcaredb_ai", "count": len(tables), "level": "table", "language": "english"}]
    with open(schema_dir / "db_info_table_level.json", 'w', encoding='utf-8') as f:
        json.dump(db_info, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！耗时: {elapsed:.1f}秒")
    print(f"📁 保存位置: {db_schema_dir}")
    print("=" * 60)
    print("\n下一步:")
    print(f"1. 构建向量索引: python build_table_vector_index.py --schema-dir {db_schema_dir}")
    print("2. 运行测试: python test_query_translation.py")


if __name__ == "__main__":
    main()
