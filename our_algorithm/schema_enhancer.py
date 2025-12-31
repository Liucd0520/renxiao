#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema 枚举值增强工具（通用版）

自动检测所有表中的枚举类型字段，将 TOP10 值写入 Schema 描述。
适用于任何数据库，不依赖于特定表。

使用方法:
    # 增强指定数据库的所有表
    python schema_enhancer.py --host 172.31.26.206 --database netcaredb_ai --schema-dir ./schemas
    
    # 增强单个表
    python schema_enhancer.py --host 172.31.26.206 --database netcaredb_ai --table event_history
"""

import json
import os
import sys
import argparse
import pymysql
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# 确保项目根目录在 path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


# 枚举类型的判断规则
ENUM_COLUMN_PATTERNS = [
    '_NAME',     # xxx_NAME 通常是枚举
    '_TYPE',     # xxx_TYPE 通常是枚举
    '_STATUS',   # xxx_STATUS 通常是枚举
    '_LEVEL',    # xxx_LEVEL 通常是枚举
    '_MODE',     # xxx_MODE 通常是枚举
    '_STATE',    # xxx_STATE 通常是枚举
    'SEVERITY',  # 严重等级
    'PRIORITY',  # 优先级
]

# 排除的列（这些列虽然符合模式但不是枚举）
EXCLUDE_COLUMN_PATTERNS = [
    '_ID',       # ID 类字段
    '_TIME',     # 时间类字段
    '_DATE',     # 日期类字段
    'HOST_NAME', # 主机名不是枚举
    'TABLE_NAME',
    'COLUMN_NAME',
    'USER_NAME',
    'FILE_NAME',
]


def get_db_connection(host: str, port: int, user: str, password: str, database: str):
    """创建数据库连接"""
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )


def is_enum_column(column_name: str) -> bool:
    """
    判断一个列是否可能是枚举类型
    
    根据列名模式自动判断
    """
    column_upper = column_name.upper()
    
    # 排除明确不是枚举的列
    for pattern in EXCLUDE_COLUMN_PATTERNS:
        if pattern in column_upper:
            return False
    
    # 检查是否匹配枚举模式
    for pattern in ENUM_COLUMN_PATTERNS:
        if pattern in column_upper:
            return True
    
    return False


def detect_enum_columns(table_name: str, columns: List[Dict]) -> List[str]:
    """
    自动检测表中的枚举类型列
    
    Args:
        table_name: 表名
        columns: 列信息列表
    
    Returns:
        枚举列名列表
    """
    enum_cols = []
    for col in columns:
        col_name = col.get('name', '')
        col_type = col.get('type', '').lower()
        
        # 只处理字符串类型的列
        if not any(t in col_type for t in ['varchar', 'char', 'text', 'enum']):
            continue
        
        # 判断是否是枚举列
        if is_enum_column(col_name):
            enum_cols.append(col_name)
    
    return enum_cols


def get_column_top10(conn, table_name: str, column_name: str) -> List[str]:
    """
    查询列的 TOP10 值
    
    Args:
        conn: 数据库连接
        table_name: 表名
        column_name: 列名
    
    Returns:
        TOP10 值列表
    """
    try:
        cursor = conn.cursor()
        sql = f"""
            SELECT `{column_name}`, COUNT(*) as cnt 
            FROM `{table_name}` 
            WHERE `{column_name}` IS NOT NULL AND `{column_name}` != ''
            GROUP BY `{column_name}` 
            ORDER BY cnt DESC 
            LIMIT 10
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        
        return [str(row[0]) for row in results if row[0]]
    except Exception as e:
        print(f"  ⚠️ 查询 {table_name}.{column_name} 失败: {e}")
        return []


def enhance_schema_file(
    schema_path: str,
    conn,
    auto_detect: bool = True,
    specified_columns: List[str] = None
) -> Tuple[bool, int]:
    """
    增强单个 Schema 文件
    
    Args:
        schema_path: Schema JSON 文件路径
        conn: 数据库连接
        auto_detect: 是否自动检测枚举列
        specified_columns: 指定的枚举列（如果不自动检测）
    
    Returns:
        (是否修改, 修改的列数)
    """
    # 读取 Schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    table_name = schema['meta_data']['table_name']
    columns = schema.get('columns', [])
    
    # 确定要增强的列
    if auto_detect:
        enum_columns = detect_enum_columns(table_name, columns)
    else:
        enum_columns = specified_columns or []
    
    if not enum_columns:
        return False, 0
    
    modified_count = 0
    
    # 遍历列，添加枚举值
    for col in columns:
        if col['name'] not in enum_columns:
            continue
        
        # 查询 TOP10 值
        top10 = get_column_top10(conn, table_name, col['name'])
        
        if not top10:
            continue
        
        # 更新描述
        old_desc = col.get('description') or col['name']
        # 检查是否已经有"常见值"
        if "常见值:" not in old_desc:
            new_desc = f"{old_desc}。常见值: {', '.join(top10)}"
            col['description'] = new_desc
            modified_count += 1
    
    # 保存
    if modified_count > 0:
        with open(schema_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
    
    return modified_count > 0, modified_count


def enhance_all_schemas(
    schema_dir: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    auto_detect: bool = True
) -> Tuple[int, int]:
    """
    增强目录下所有 Schema 文件
    
    Args:
        schema_dir: Schema 目录
        host, port, user, password, database: 数据库连接信息
        auto_detect: 是否自动检测枚举列
    
    Returns:
        (修改的表数, 修改的列数)
    """
    schema_path = Path(schema_dir)
    if not schema_path.exists():
        print(f"Schema 目录不存在: {schema_dir}")
        return 0, 0
    
    # 连接数据库
    print(f"连接数据库 {host}:{port}/{database}...")
    conn = get_db_connection(host, port, user, password, database)
    
    total_tables = 0
    total_columns = 0
    
    try:
        schema_files = list(schema_path.glob("*.json"))
        print(f"找到 {len(schema_files)} 个 Schema 文件")
        print()
        
        for schema_file in schema_files:
            table_name = schema_file.stem
            modified, col_count = enhance_schema_file(
                str(schema_file), conn, auto_detect=auto_detect
            )
            
            if modified:
                print(f"✅ {table_name}: 增强了 {col_count} 个枚举列")
                total_tables += 1
                total_columns += col_count
        
        print()
        print(f"完成！共增强 {total_tables} 个表，{total_columns} 个列")
        
    finally:
        conn.close()
    
    return total_tables, total_columns


def main():
    parser = argparse.ArgumentParser(
        description="Schema 枚举值增强工具（通用版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 增强指定目录下所有表
  python schema_enhancer.py --host 172.31.26.206 --database netcaredb_ai \\
      --schema-dir ./spider2_dev/schemas_table_level_enhanced/netcaredb_ai
  
  # 增强单个表
  python schema_enhancer.py --host 172.31.26.206 --database netcaredb_ai \\
      --schema-dir ./schemas --table event_history
        """
    )
    
    # 数据库连接参数
    parser.add_argument("--host", type=str, required=True, help="数据库主机")
    parser.add_argument("--port", type=int, default=3306, help="数据库端口")
    parser.add_argument("--user", type=str, default="ai_test", help="数据库用户")
    parser.add_argument("--password", type=str, default="Netcare@13579", help="数据库密码")
    parser.add_argument("--database", type=str, required=True, help="数据库名")
    
    # Schema 参数
    parser.add_argument("--schema-dir", type=str, required=True, help="Schema 目录")
    parser.add_argument("--table", type=str, help="指定表名（不指定则处理所有表）")
    parser.add_argument("--no-auto-detect", action="store_true", help="禁用自动检测枚举列")
    
    args = parser.parse_args()
    
    if args.table:
        # 处理单个表
        schema_path = os.path.join(args.schema_dir, f"{args.table}.json")
        if not os.path.exists(schema_path):
            print(f"Schema 文件不存在: {schema_path}")
            return 1
        
        conn = get_db_connection(
            args.host, args.port, args.user, args.password, args.database
        )
        try:
            modified, col_count = enhance_schema_file(
                schema_path, conn, auto_detect=not args.no_auto_detect
            )
            if modified:
                print(f"✅ {args.table}: 增强了 {col_count} 个枚举列")
            else:
                print(f"⚠️ {args.table}: 无需增强")
        finally:
            conn.close()
    else:
        # 处理所有表
        enhance_all_schemas(
            args.schema_dir,
            args.host, args.port, args.user, args.password, args.database,
            auto_detect=not args.no_auto_detect
        )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
