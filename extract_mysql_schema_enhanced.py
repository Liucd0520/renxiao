#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 MySQL 数据库提取 Schema 并使用 LLM 生成缺失的列描述
增强版：自动为没有注释的列生成描述
"""

import json
import os
import sys
import time
from pathlib import Path
import pymysql
from pymysql import cursors
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel

# 全局 LLM 实例
llm = None

# 描述生成 Prompt
DESCRIPTION_PROMPT = """根据以下数据库列信息，生成一个简洁的中文描述（10-20字）。

表名: {table_name}
列名: {column_name}
类型: {column_type}
示例: {sample_values}

要求：直接输出描述文本，不要任何思考过程、标签或额外内容。

描述:"""


def clean_llm_response(response):
    """清理 LLM 响应，去除 think 标签等"""
    import re
    # 去除 <think>...</think> 标签
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    # 去除其他常见噪音
    response = response.replace('"', '').replace("'", '').strip()
    # 取第一行
    lines = response.split('\n')
    response = lines[0].strip() if lines else response
    # 限制长度
    if len(response) > 50:
        response = response[:50]
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


def get_sample_rows(connection, table_name, column_name, limit=10):
    """获取列的示例数据"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT DISTINCT `{column_name}` FROM `{table_name}` LIMIT {limit}")
            rows = cursor.fetchall()
            return [str(list(row.values())[0]) for row in rows if list(row.values())[0] is not None]
    except Exception as e:
        return []


def generate_description_with_llm(table_name, column_name, column_type, sample_rows):
    """使用 LLM 生成列描述"""
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
        # 清理响应
        response = clean_llm_response(response)
        return response
    except Exception as e:
        print(f"    ⚠️ LLM 生成描述失败: {e}")
        return None


def transform_name(table_name, col_name):
    """生成文件名"""
    prefix = f"{table_name}_{col_name}"
    prefix = prefix if len(prefix) < 100 else prefix[:100]

    syn_lis = ["(", ")", "%", "/", " ", "-"]
    for syn in syn_lis:
        if syn in prefix:
            prefix = prefix.replace(syn, "_")

    return prefix


def extract_schema_to_json(connection, db_name, output_dir, use_llm=True, limit_tables=None):
    """提取数据库 schema 并保存为 JSON 文件"""
    output_path = Path(output_dir) / db_name
    output_path.mkdir(parents=True, exist_ok=True)

    tables = get_all_tables(connection)
    
    if limit_tables:
        tables = tables[:limit_tables]
        print(f"⚠️ 限制处理前 {limit_tables} 个表")
    
    total_columns = 0
    llm_generated_count = 0
    db_has_comment_count = 0

    print(f"\n开始提取 Schema (LLM增强: {'开启' if use_llm else '关闭'})...")
    print("=" * 60)

    for table_idx, table_name in enumerate(tables):
        columns, comments = get_table_columns(connection, table_name)
        table_llm_count = 0

        for column in columns:
            col_name = column['Field']
            col_type = column['Type']
            col_comment = comments.get(col_name, "")

            # 获取示例数据
            sample_rows = get_sample_rows(connection, table_name, col_name, limit=5)

            # 如果数据库没有注释，使用 LLM 生成
            if not col_comment and use_llm:
                col_comment = generate_description_with_llm(
                    table_name, col_name, col_type, sample_rows
                )
                if col_comment:
                    llm_generated_count += 1
                    table_llm_count += 1
            elif col_comment:
                db_has_comment_count += 1

            # 构造 JSON 数据
            schema_data = {
                "meta_data": {
                    "db_id": db_name,
                    "table_name": table_name
                },
                "column_name": col_name,
                "column_types": col_type,
                "column_descriptions": col_comment if col_comment else None,
                "sample_rows": sample_rows[:3]
            }

            # 保存文件
            file_name = transform_name(table_name, col_name)
            file_path = output_path / f"{file_name}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema_data, f, ensure_ascii=False, indent=2)

            total_columns += 1

        print(f"[{table_idx+1}/{len(tables)}] ✅ {table_name}: {len(columns)} 列 (LLM生成: {table_llm_count})")

    print("=" * 60)
    print(f"✅ Schema 提取完成！")
    print(f"   - 总表数: {len(tables)}")
    print(f"   - 总列数: {total_columns}")
    print(f"   - 数据库已有注释: {db_has_comment_count}")
    print(f"   - LLM 生成描述: {llm_generated_count}")
    print(f"📁 保存位置: {output_path}")

    return len(tables), total_columns


def generate_db_info(db_name, table_count, column_count, output_file):
    """生成数据库信息文件"""
    db_info = [
        {
            "db_id": db_name,
            "count": column_count
        }
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(db_info, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据库信息文件已生成: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="从 MySQL 提取 Schema（LLM增强版）")
    parser.add_argument("--host", default="172.31.26.206", help="MySQL 主机")
    parser.add_argument("--port", type=int, default=3306, help="MySQL 端口")
    parser.add_argument("--user", default="ai_test", help="MySQL 用户名")
    parser.add_argument("--password", default="Netcare@13579", help="MySQL 密码")
    parser.add_argument("--database", default="netcaredb_ai", help="数据库名")
    parser.add_argument("--output", default="./spider2_dev/schemas_enhanced", help="输出目录")
    parser.add_argument("--no-llm", action="store_true", help="禁用 LLM 生成描述")
    parser.add_argument("--limit", type=int, default=None, help="限制处理的表数量（用于测试）")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("MySQL Schema 提取工具 (LLM增强版)".center(60))
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
        # 提取 schema
        start_time = time.time()
        table_count, column_count = extract_schema_to_json(
            connection,
            args.database,
            args.output,
            use_llm=not args.no_llm,
            limit_tables=args.limit
        )
        elapsed = time.time() - start_time

        # 生成数据库信息文件
        db_info_file = "./spider2_dev/db_info_enhanced.json"
        generate_db_info(args.database, table_count, column_count, db_info_file)

        print("\n" + "=" * 60)
        print(f"✅ 所有文件生成完成！耗时: {elapsed:.1f}秒".center(60))
        print("=" * 60)
        print(f"\n下一步:")
        print(f"1. 查看生成的 schema 文件: {args.output}/{args.database}/")
        print(f"2. 重新构建向量索引")
        print(f"3. 运行批量测试验证效果")

    finally:
        connection.close()
        print("\n✅ 数据库连接已关闭")

    return 0


if __name__ == "__main__":
    sys.exit(main())
