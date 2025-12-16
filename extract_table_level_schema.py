#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表级别 Schema 提取工具

将每张表的所有列信息聚合成一个文档，用于表级别向量检索。
针对 Denormalized 数据库优化。
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
import pymysql
from pymysql import cursors

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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


def get_sample_values(connection, table_name, column_name, limit=3):
    """获取列的示例值"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT DISTINCT `{column_name}` FROM `{table_name}` LIMIT {limit}")
            rows = cursor.fetchall()
            return [str(list(row.values())[0]) for row in rows if list(row.values())[0] is not None]
    except Exception:
        return []


def generate_embedding_text(table_name, table_comment, columns):
    """
    生成用于向量检索的嵌入文本
    
    策略：
    1. 表名 + 表注释（如有）
    2. 所有列名（有描述的优先展示描述）
    
    注意：BGE-M3 支持 8192 tokens，足够容纳所有列信息
    """
    parts = []
    
    # 表名
    parts.append(f"表名: {table_name}")
    
    # 表注释（如有）
    if table_comment:
        parts.append(f"描述: {table_comment}")
    
    # 列信息：优先展示有描述的列
    columns_with_desc = [c for c in columns if c.get('description')]
    columns_without_desc = [c for c in columns if not c.get('description')]
    
    # 合并，有描述的优先
    sorted_columns = columns_with_desc + columns_without_desc
    
    column_strs = []
    for col in sorted_columns:
        col_str = col['name']
        if col.get('description'):
            col_str += f"({col['description']})"
        column_strs.append(col_str)
    
    if column_strs:
        parts.append(f"列: {', '.join(column_strs)}")
    
    parts.append(f"共 {len(columns)} 列")
    
    return "\n".join(parts)


def extract_table_level_schema(connection, db_name, output_dir, max_columns=20):
    """
    提取表级别 Schema
    
    每张表生成一个 JSON 文件，包含：
    - 表的元数据
    - 所有列的详细信息
    - 用于向量检索的 embedding_text
    """
    output_path = Path(output_dir) / db_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    tables = get_all_tables(connection)
    
    print(f"\n开始提取表级别 Schema...")
    print("=" * 60)
    
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
        
        # 生成嵌入文本（包含所有列）
        embedding_text = generate_embedding_text(
            table_name, table_comment, columns
        )
        
        # 构建 schema 数据
        schema_data = {
            "meta_data": {
                "db_id": db_name,
                "table_name": table_name
            },
            "table_comment": table_comment if table_comment else None,
            "columns": columns,
            "column_count": len(columns),
            "embedding_text": embedding_text
        }
        
        # 保存文件
        file_path = output_path / f"{table_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        
        if (table_idx + 1) % 50 == 0:
            print(f"[{table_idx + 1}/{len(tables)}] 已处理...")
    
    print("=" * 60)
    print(f"✅ 表级别 Schema 提取完成！")
    print(f"   - 总表数: {len(tables)}")
    print(f"📁 保存位置: {output_path}")
    
    # 生成数据库信息文件
    db_info = [{
        "db_id": db_name,
        "count": len(tables),  # 表级别索引，count 表示表数量
        "level": "table"
    }]
    
    db_info_file = Path(output_dir) / "db_info_table_level.json"
    with open(db_info_file, 'w', encoding='utf-8') as f:
        json.dump(db_info, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据库信息文件已生成: {db_info_file}")
    
    return len(tables)


def main():
    parser = argparse.ArgumentParser(description="提取表级别 Schema")
    parser.add_argument("--host", default="172.31.26.206", help="MySQL 主机")
    parser.add_argument("--port", type=int, default=3306, help="MySQL 端口")
    parser.add_argument("--user", default="ai_test", help="MySQL 用户名")
    parser.add_argument("--password", default="Netcare@13579", help="MySQL 密码")
    parser.add_argument("--database", default="netcaredb_ai", help="数据库名")
    parser.add_argument("--output", default="./spider2_dev/schemas_table_level", help="输出目录")
    parser.add_argument("--max-columns", type=int, default=20, help="embedding_text 中最多展示的列数")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("表级别 Schema 提取工具".center(60))
    print("=" * 60)
    print(f"数据库: {args.database}")
    print(f"主机: {args.host}:{args.port}")
    print(f"最大列数: {args.max_columns}")
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
        table_count = extract_table_level_schema(
            connection,
            args.database,
            args.output,
            args.max_columns
        )
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print(f"✅ 完成！耗时: {elapsed:.1f}秒".center(60))
        print("=" * 60)
        print(f"\n下一步:")
        print(f"1. 查看生成的 schema 文件: {args.output}/{args.database}/")
        print(f"2. 运行 build_table_vector_index.py 构建向量索引")
        
    finally:
        connection.close()
        print("\n✅ 数据库连接已关闭")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
