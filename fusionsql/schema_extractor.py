#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版表级别 Schema 提取工具

使用 LLM 为每张表生成中文语义描述，优化向量检索效果。
解决中文问题与英文表名/列名语义差距大的问题。
"""

import json
import os
import sys
import time
import argparse
import re
from pathlib import Path
import pymysql
from pymysql import cursors

from .llm import QwenLLM

# 全局 LLM 实例
llm = None

# 表描述生成 Prompt
TABLE_DESCRIPTION_PROMPT = """根据以下数据库表信息，生成一个简洁的中文功能描述（20-50字）。

表名: {table_name}
表注释: {table_comment}
主要列:
{columns_info}

要求：
1. 用中文描述这张表存储什么数据、有什么用途
2. 包含关键业务词汇（如：客户、订单、告警、设备、用户、权限等）
3. 直接输出描述，不要任何标签或额外内容

描述:"""


def clean_llm_response(response):
    """清理 LLM 响应"""
    # 去除 <think>...</think> 标签
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    response = response.replace('"', '').replace("'", '').strip()
    lines = response.split('\n')
    response = lines[0].strip() if lines else response
    if len(response) > 100:
        response = response[:100]
    return response if response else None


def get_mysql_connection(host, port, user, password, database):
    """创建 MySQL 连接"""
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=cursors.DictCursor
        )
        print(f"✅ 成功连接到 MySQL 数据库: {database}")
        return connection
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        return None


def get_all_tables(connection):
    """获取数据库中的所有表"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
        print(f"✅ 找到 {len(tables)} 个表")
        return tables
    except Exception as e:
        print(f"❌ 获取表列表失败: {e}")
        return []


def get_table_comment(connection, table_name):
    """获取表的注释"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT TABLE_COMMENT
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = '{table_name}'
            """)
            result = cursor.fetchone()
            return result['TABLE_COMMENT'] if result else ""
    except Exception as e:
        return ""


def get_table_columns(connection, table_name):
    """获取表的所有列信息"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()

            cursor.execute(f"""
                SELECT COLUMN_NAME, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = '{table_name}'
            """)
            comments = {row['COLUMN_NAME']: row['COLUMN_COMMENT'] for row in cursor.fetchall()}

        return columns, comments
    except Exception as e:
        print(f"❌ 获取表 {table_name} 的列信息失败: {e}")
        return [], {}


def generate_table_description_with_llm(table_name, table_comment, columns):
    """使用 LLM 生成表的中文描述"""
    global llm
    
    if llm is None:
        llm = QwenLLM(preset="qwen3_moe", temperature=0.1)
    
    # 准备列信息（最多显示10列）
    columns_info_parts = []
    for col in columns[:10]:
        col_str = f"- {col['name']}"
        if col.get('description'):
            col_str += f": {col['description']}"
        columns_info_parts.append(col_str)
    
    if len(columns) > 10:
        columns_info_parts.append(f"... 等共 {len(columns)} 列")
    
    columns_info = "\n".join(columns_info_parts)
    
    prompt = TABLE_DESCRIPTION_PROMPT.format(
        table_name=table_name,
        table_comment=table_comment or "无",
        columns_info=columns_info
    )
    
    try:
        response = llm.complete(prompt).text.strip()
        response = clean_llm_response(response)
        return response
    except Exception as e:
        print(f"    ⚠️ LLM 生成描述失败: {e}")
        return None


def generate_enhanced_embedding_text(table_name, table_comment, columns, llm_description, max_columns=15):
    """
    生成增强版嵌入文本
    
    策略：
    1. LLM 生成的中文功能描述（最重要）
    2. 表名（英文）
    3. 有中文描述的列（语义信息丰富）
    4. 英文列名（作为补充）
    """
    parts = []
    
    # 1. LLM 生成的中文描述（最重要，放在最前面）
    if llm_description:
        parts.append(llm_description)
    
    # 2. 表名
    parts.append(f"表名: {table_name}")
    
    # 3. 表注释
    if table_comment:
        parts.append(f"表注释: {table_comment}")
    
    # 4. 列信息：分离有描述和无描述的列
    columns_with_desc = [c for c in columns if c.get('description')]
    columns_without_desc = [c for c in columns if not c.get('description')]
    
    # 有描述的列（中文语义）
    if columns_with_desc:
        desc_strs = []
        for col in columns_with_desc[:max_columns]:
            desc_strs.append(f"{col['name']}({col['description']})")
        parts.append(f"列信息: {', '.join(desc_strs)}")
    
    # 无描述的列（只列出名字）
    remaining = max_columns - len(columns_with_desc)
    if remaining > 0 and columns_without_desc:
        name_strs = [col['name'] for col in columns_without_desc[:remaining]]
        parts.append(f"其他列: {', '.join(name_strs)}")
    
    return "\n".join(parts)


def extract_table_level_schema_enhanced(connection, db_name, output_dir, max_columns=15, use_llm=True):
    """
    提取增强版表级别 Schema
    """
    output_path = Path(output_dir) / db_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    tables = get_all_tables(connection)
    
    print(f"\n开始提取增强版表级别 Schema (LLM: {'开启' if use_llm else '关闭'})...")
    print("=" * 60)
    
    llm_count = 0
    
    for table_idx, table_name in enumerate(tables):
        # 获取表注释
        table_comment = get_table_comment(connection, table_name)
        
        # 获取列信息
        columns_raw, comments = get_table_columns(connection, table_name)
        
        # 构建列列表
        columns = []
        for col in columns_raw:
            col_name = col['Field']
            col_type = col['Type']
            col_desc = comments.get(col_name, "")
            
            columns.append({
                "name": col_name,
                "type": col_type,
                "description": col_desc if col_desc else None
            })
        
        # 使用 LLM 生成表描述
        llm_description = None
        if use_llm:
            llm_description = generate_table_description_with_llm(
                table_name, table_comment, columns
            )
            if llm_description:
                llm_count += 1
        
        # 生成增强版嵌入文本
        embedding_text = generate_enhanced_embedding_text(
            table_name, table_comment, columns, llm_description, max_columns
        )
        
        # 构建 schema 数据
        schema_data = {
            "meta_data": {
                "db_id": db_name,
                "table_name": table_name
            },
            "table_comment": table_comment if table_comment else None,
            "llm_description": llm_description,
            "columns": columns,
            "column_count": len(columns),
            "embedding_text": embedding_text
        }
        
        # 保存文件
        file_path = output_path / f"{table_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        
        if (table_idx + 1) % 20 == 0:
            print(f"[{table_idx + 1}/{len(tables)}] 已处理... (LLM描述: {llm_count})")
    
    print("=" * 60)
    print(f"✅ 增强版表级别 Schema 提取完成！")
    print(f"   - 总表数: {len(tables)}")
    print(f"   - LLM 生成描述: {llm_count}")
    print(f"📁 保存位置: {output_path}")
    
    # 生成数据库信息文件
    db_info = [{
        "db_id": db_name,
        "count": len(tables),
        "level": "table",
        "enhanced": True
    }]
    
    db_info_file = Path(output_dir) / "db_info_table_level.json"
    with open(db_info_file, 'w', encoding='utf-8') as f:
        json.dump(db_info, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据库信息文件已生成: {db_info_file}")
    
    return len(tables)


def main():
    parser = argparse.ArgumentParser(description="提取增强版表级别 Schema")
    parser.add_argument("--host", default="172.31.26.206", help="MySQL 主机")
    parser.add_argument("--port", type=int, default=3306, help="MySQL 端口")
    parser.add_argument("--user", default="ai_test", help="MySQL 用户名")
    parser.add_argument("--password", default="Netcare@13579", help="MySQL 密码")
    parser.add_argument("--database", default="netcaredb_ai", help="数据库名")
    parser.add_argument("--output", default="./spider2_dev/schemas_table_level_enhanced", help="输出目录")
    parser.add_argument("--max-columns", type=int, default=15, help="embedding_text 中最多展示的列数")
    parser.add_argument("--no-llm", action="store_true", help="禁用 LLM 生成描述")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("增强版表级别 Schema 提取工具".center(60))
    print("=" * 60)
    print(f"数据库: {args.database}")
    print(f"主机: {args.host}:{args.port}")
    print(f"LLM增强: {'禁用' if args.no_llm else '启用'}")
    print("=" * 60 + "\n")
    
    # 连接数据库
    connection = get_mysql_connection(
        args.host,
        args.port,
        args.user,
        args.password,
        args.database
    )
    
    if connection is None:
        return 1
    
    try:
        start_time = time.time()
        table_count = extract_table_level_schema_enhanced(
            connection,
            args.database,
            args.output,
            args.max_columns,
            use_llm=not args.no_llm
        )
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print(f"✅ 完成！耗时: {elapsed:.1f}秒".center(60))
        print("=" * 60)
        print(f"\n下一步:")
        print(f"1. 查看生成的 schema 文件: {args.output}/{args.database}/")
        print(f"2. 运行 build_table_vector_index.py --schema-dir {args.output}/{args.database}")
        
    finally:
        connection.close()
        print("\n✅ 数据库连接已关闭")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
