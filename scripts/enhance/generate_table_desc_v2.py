#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版表描述生成 - V2

使用更强的 Prompt 让 LLM 生成更精准的表描述，确保关键业务词被包含。
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

# 改进版 Prompt - 强调关键业务词
TABLE_DESCRIPTION_PROMPT_V2 = """你是一个数据库文档专家。请为下面的表生成一个精准的中文功能描述。

## 表信息
表名: {table_name}
表注释: {table_comment}
主要列:
{columns_info}

## 生成要求（非常重要！）
1. 描述长度：30-60个字
2. **必须明确说明这张表存储什么核心数据**
3. **必须在描述开头使用最关键的业务词**，例如：
   - 如果是存储告警/事件的表 → 开头用"告警"、"事件"
   - 如果是存储设备的表 → 开头用"设备"
   - 如果是存储客户的表 → 开头用"客户"
   - 如果是存储用户/权限的表 → 开头用"用户"、"权限"
4. 避免无意义的表名复读，直接说业务含义
5. 不要输出任何标签或额外内容，只输出描述文字

## 表功能描述:"""


def clean_llm_response(response):
    """清理 LLM 响应"""
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    response = response.replace('"', '').replace("'", '').strip()
    lines = response.split('\n')
    response = lines[0].strip() if lines else response
    if len(response) > 120:
        response = response[:120]
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


def generate_description_v2(table_name, table_comment, columns, comments, llm):
    """使用改进版 Prompt 生成描述"""
    columns_info_parts = []
    for col in columns[:15]:  # 增加到15列
        col_name = col['Field']
        col_comment = comments.get(col_name, '')
        col_str = f"- {col_name}"
        if col_comment:
            col_str += f": {col_comment}"
        columns_info_parts.append(col_str)
    
    if len(columns) > 15:
        columns_info_parts.append(f"... 等共 {len(columns)} 列")
    
    prompt = TABLE_DESCRIPTION_PROMPT_V2.format(
        table_name=table_name,
        table_comment=table_comment or "无",
        columns_info="\n".join(columns_info_parts)
    )
    
    try:
        response = llm.complete(prompt).text.strip()
        return clean_llm_response(response)
    except Exception as e:
        print(f"  ⚠️ 生成失败: {e}")
        return None


def main():
    # 只更新核心表的描述（测试用例中涉及的表）
    core_tables = [
        'event_history',
        't_bz_config_ci_ne_root', 
        't_bz_config_customer',
    ]
    
    print("\n" + "=" * 60)
    print("改进版表描述生成 V2".center(60))
    print("=" * 60)
    
    # 连接数据库
    connection = get_mysql_connection(
        '172.31.26.206', 3306, 'ai_test', 'Netcare@13579', 'netcaredb_ai'
    )
    if not connection:
        return
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-plus", temperature=0.1)  # 用更强的模型
    print("✅ 使用 qwen-plus 模型")
    
    schema_dir = Path("./spider2_dev/schemas_table_level_enhanced/netcaredb_ai")
    
    try:
        for table_name in core_tables:
            print(f"\n处理: {table_name}")
            
            # 获取表信息
            table_comment, columns, comments = get_table_info(connection, table_name)
            
            # 生成新描述
            new_desc = generate_description_v2(table_name, table_comment, columns, comments, llm)
            
            if new_desc:
                print(f"  新描述: {new_desc}")
                
                # 更新 JSON 文件
                json_path = schema_dir / f"{table_name}.json"
                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    old_desc = data.get('llm_description', '')
                    print(f"  旧描述: {old_desc}")
                    
                    data['llm_description'] = new_desc
                    data['llm_description_v2'] = True
                    
                    # 更新 embedding_text
                    data['embedding_text'] = new_desc + "\n" + data.get('embedding_text', '').split('\n', 1)[-1]
                    
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"  ✅ 已更新")
                else:
                    print(f"  ⚠️ 文件不存在: {json_path}")
    
    finally:
        connection.close()
    
    print("\n" + "=" * 60)
    print("完成！请重新构建向量索引后测试")
    print("=" * 60)


if __name__ == "__main__":
    main()
