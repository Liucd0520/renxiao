#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 MySQL 数据库提取 Schema 并生成 LinkAlign 格式的文件
"""

import json
import os
from pathlib import Path
import pymysql
from pymysql import cursors
import argparse


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
            # 获取列信息
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()

            # 获取列注释
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
        print(f"⚠️  获取表 {table_name} 列 {column_name} 的示例数据失败: {e}")
        return []


def transform_name(table_name, col_name):
    """生成文件名（与原项目保持一致）"""
    prefix = f"{table_name}_{col_name}"
    prefix = prefix if len(prefix) < 100 else prefix[:100]

    syn_lis = ["(", ")", "%", "/", " ", "-"]
    for syn in syn_lis:
        if syn in prefix:
            prefix = prefix.replace(syn, "_")

    return prefix


def extract_schema_to_json(connection, db_name, output_dir):
    """提取数据库 schema 并保存为 JSON 文件"""
    output_path = Path(output_dir) / db_name
    output_path.mkdir(parents=True, exist_ok=True)

    tables = get_all_tables(connection)
    total_columns = 0

    print(f"\n开始提取 Schema...")
    print("=" * 60)

    for table_name in tables:
        columns, comments = get_table_columns(connection, table_name)

        for column in columns:
            col_name = column['Field']
            col_type = column['Type']
            col_comment = comments.get(col_name, "")

            # 获取示例数据
            sample_rows = get_sample_rows(connection, table_name, col_name, limit=3)

            # 构造 JSON 数据
            schema_data = {
                "meta_data": {
                    "db_id": db_name,
                    "table_name": table_name
                },
                "column_name": col_name,
                "column_types": col_type,
                "column_descriptions": col_comment if col_comment else None,
                "sample_rows": sample_rows
            }

            # 生成文件名并保存
            file_name = transform_name(table_name, col_name)
            file_path = output_path / f"{file_name}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema_data, f, ensure_ascii=False, indent=2)

            total_columns += 1

        print(f"✅ 表 {table_name}: {len(columns)} 列")

    print("=" * 60)
    print(f"✅ Schema 提取完成！共 {len(tables)} 个表，{total_columns} 个列")
    print(f"📁 保存位置: {output_path}")

    return len(tables), total_columns


def generate_db_info(db_name, table_count, column_count, output_file):
    """生成数据库信息文件"""
    db_info = [
        {
            "db_id": db_name,
            "count": column_count  # schema 数量（列数）
        }
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(db_info, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据库信息文件已生成: {output_file}")


def generate_sample_dataset(db_name, output_file):
    """生成示例测试数据集"""
    # 这里生成一个简单的示例，用户可以后续添加更多问题
    dataset = [
        {
            "instance_id": "001",
            "db_id": db_name,
            "question": "查询所有数据"
        }
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ 示例数据集已生成: {output_file}")
    print("⚠️  请根据实际需求修改测试问题")


def main():
    parser = argparse.ArgumentParser(description="从 MySQL 提取 Schema")
    parser.add_argument("--host", default="172.31.26.206", help="MySQL 主机")
    parser.add_argument("--port", type=int, default=3306, help="MySQL 端口")
    parser.add_argument("--user", default="ai_test", help="MySQL 用户名")
    parser.add_argument("--password", default="Netcare@13579", help="MySQL 密码")
    parser.add_argument("--database", default="netcaredb_ai", help="数据库名")
    parser.add_argument("--output", default="./spider2_dev/schemas", help="输出目录")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("MySQL Schema 提取工具".center(60))
    print("=" * 60)
    print(f"数据库: {args.database}")
    print(f"主机: {args.host}:{args.port}")
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
        table_count, column_count = extract_schema_to_json(
            connection,
            args.database,
            args.output
        )

        # 生成数据库信息文件
        db_info_file = "./spider2_dev/db_info.json"
        generate_db_info(args.database, table_count, column_count, db_info_file)

        # 生成示例数据集
        dataset_file = "./spider2_dev/spider2_dev_preprocessed.json"
        generate_sample_dataset(args.database, dataset_file)

        print("\n" + "=" * 60)
        print("✅ 所有文件生成完成！".center(60))
        print("=" * 60)
        print(f"\n下一步:")
        print(f"1. 查看生成的 schema 文件: {args.output}/{args.database}/")
        print(f"2. 编辑测试数据集: {dataset_file}")
        print(f"3. 运行 GenerateSchemas.py 进行测试")

    finally:
        connection.close()
        print("\n✅ 数据库连接已关闭")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
