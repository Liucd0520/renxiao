#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
只为核心表生成增强 Schema - 快速验证
"""

import json
import os
import sys
import re
import time
from pathlib import Path
import pymysql
from pymysql import cursors

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llms.qwen.QwenModel import QwenModel

# 核心表列表
CORE_TABLES = [
    "t_bz_config_ci_ne_root",  # 设备主表
    "t_bz_config_customer",     # 客户表
    "event_history",            # 事件历史表
]

# LLM 实例
llm = None

DESCRIPTION_PROMPT = """根据以下数据库列信息，生成一个简洁的中文描述（10-20字）。

表名: {table_name}
列名: {column_name}
类型: {column_type}
示例: {sample_values}

直接输出描述，不要思考过程。

描述:"""


def clean_response(response):
    """清理 LLM 响应"""
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    response = response.replace('"', '').replace("'", '').strip()
    lines = response.split('\n')
    response = lines[0].strip() if lines else response
    return response[:50] if len(response) > 50 else response


def generate_description(table_name, column_name, column_type, sample_rows):
    """用 LLM 生成描述"""
    global llm
    if llm is None:
        llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    
    sample_str = ", ".join(sample_rows[:5]) if sample_rows else "无"
    prompt = DESCRIPTION_PROMPT.format(
        table_name=table_name,
        column_name=column_name,
        column_type=column_type,
        sample_values=sample_str
    )
    
    try:
        response = llm.complete(prompt).text.strip()
        return clean_response(response)
    except Exception as e:
        print(f"  ⚠️ LLM error: {e}")
        return None


def main():
    print("\n" + "=" * 60)
    print("核心表 Schema 增强工具")
    print("=" * 60)
    
    # 连接数据库
    conn = pymysql.connect(
        host="172.31.26.206",
        port=3306,
        user="ai_test",
        password="Netcare@13579",
        database="netcaredb_ai",
        charset='utf8mb4',
        cursorclass=cursors.DictCursor
    )
    print("✅ 数据库连接成功")
    
    # 输出目录 - 直接覆盖原始 schema
    output_dir = Path("./spider2_dev/schemas/netcaredb_ai")
    
    total_generated = 0
    total_existing = 0
    
    try:
        cursor = conn.cursor()
        
        for table_name in CORE_TABLES:
            print(f"\n处理表: {table_name}")
            print("-" * 40)
            
            # 获取列信息
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            # 获取现有注释
            cursor.execute(f"""
                SELECT COLUMN_NAME, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
            """)
            comments = {row['COLUMN_NAME']: row['COLUMN_COMMENT'] for row in cursor.fetchall()}
            
            table_generated = 0
            
            for col in columns:
                col_name = col['Field']
                col_type = col['Type']
                col_comment = comments.get(col_name, "")
                
                # 读取现有 schema 文件
                file_name = f"{table_name}_{col_name}"
                file_name = file_name[:100] if len(file_name) > 100 else file_name
                for syn in ["(", ")", "%", "/", " ", "-"]:
                    file_name = file_name.replace(syn, "_")
                file_path = output_dir / f"{file_name}.json"
                
                # 获取样本数据
                try:
                    cursor.execute(f"SELECT DISTINCT `{col_name}` FROM `{table_name}` LIMIT 5")
                    sample_rows = [str(r[col_name]) for r in cursor.fetchall() if r[col_name] is not None]
                except:
                    sample_rows = []
                
                # 如果没有描述，用 LLM 生成
                if not col_comment:
                    col_comment = generate_description(table_name, col_name, col_type, sample_rows)
                    if col_comment:
                        table_generated += 1
                        total_generated += 1
                        print(f"  ✨ {col_name}: {col_comment}")
                else:
                    total_existing += 1
                
                # 保存更新的 schema
                schema_data = {
                    "meta_data": {
                        "db_id": "netcaredb_ai",
                        "table_name": table_name
                    },
                    "column_name": col_name,
                    "column_types": col_type,
                    "column_descriptions": col_comment if col_comment else None,
                    "sample_rows": sample_rows[:3]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(schema_data, f, ensure_ascii=False, indent=2)
            
            print(f"  📊 {table_name}: {len(columns)} 列, LLM生成: {table_generated}")
    
    finally:
        conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！")
    print(f"   - 已有描述: {total_existing}")
    print(f"   - LLM生成: {total_generated}")
    print("=" * 60)


if __name__ == "__main__":
    main()
