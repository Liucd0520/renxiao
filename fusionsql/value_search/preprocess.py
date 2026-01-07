#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSH 值匹配模块 - 预处理

从 MySQL 数据库提取唯一值并构建 MinHash LSH 索引。
基于 CHESS 项目的实现，适配 MySQL。
"""

import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from tqdm import tqdm

try:
    from datasketch import MinHash, MinHashLSH
except ImportError:
    raise ImportError("请安装 datasketch: pip install datasketch")

import pymysql


def _create_minhash(signature_size: int, string: str, n_gram: int) -> MinHash:
    """
    为字符串创建 MinHash 指纹
    
    Args:
        signature_size: MinHash 签名大小
        string: 输入字符串
        n_gram: n-gram 大小
    
    Returns:
        MinHash 对象
    """
    m = MinHash(num_perm=signature_size)
    for d in [string[i:i + n_gram] for i in range(len(string) - n_gram + 1)]:
        m.update(d.encode('utf8'))
    return m


def _get_unique_values_mysql(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    max_values_per_column: int = 10000,
    verbose: bool = True
) -> Dict[str, Dict[str, List[str]]]:
    """
    从 MySQL 数据库提取唯一文本值
    
    Args:
        host: 数据库主机
        port: 数据库端口
        user: 用户名
        password: 密码
        database: 数据库名
        max_values_per_column: 每列最大提取值数
        verbose: 是否显示进度
    
    Returns:
        {table_name: {column_name: [values]}} 格式的字典
    """
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute(f"""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = '{database}' AND TABLE_TYPE = 'BASE TABLE'
    """)
    tables = [t[0] for t in cursor.fetchall()]
    
    if verbose:
        print(f"发现 {len(tables)} 张表")
    
    unique_values: Dict[str, Dict[str, List[str]]] = {}
    
    # 需要跳过的关键词
    skip_keywords = ['_id', 'id', 'url', 'email', 'web', 'time', 'phone', 'date', 'address', 'password', 'token']
    
    for table in tqdm(tables, desc="处理表", disable=not verbose):
        # 获取 TEXT/VARCHAR 类型的列
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{database}' 
              AND TABLE_NAME = '{table}'
              AND DATA_TYPE IN ('varchar', 'text', 'char', 'enum')
        """)
        columns = cursor.fetchall()
        
        table_values: Dict[str, List[str]] = {}
        
        for col_name, data_type, max_length in columns:
            # 跳过 ID、时间等字段
            col_lower = col_name.lower()
            if any(kw in col_lower for kw in skip_keywords) or col_name.endswith('Id'):
                continue
            
            # 跳过超长文本字段
            if max_length and max_length > 500:
                continue
            
            try:
                # 获取唯一值统计
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT `{col_name}`) as cnt,
                           SUM(LENGTH(`{col_name}`)) as total_len
                    FROM `{table}` 
                    WHERE `{col_name}` IS NOT NULL
                """)
                stats = cursor.fetchone()
                count, total_len = stats[0] or 0, stats[1] or 0
                
                # 过滤规则：值太多或太长的列跳过
                if count == 0:
                    continue
                avg_len = total_len / count if count > 0 else 0
                
                # 允许条件：
                # 1. name 相关列，总长度 < 500万
                # 2. 值数量 < 1000 且 平均长度 < 50
                # 3. 枚举类型
                if not (
                    ('name' in col_lower and total_len < 5000000) or
                    (count < 1000 and avg_len < 50) or
                    data_type == 'enum'
                ):
                    continue
                
                # 获取唯一值
                cursor.execute(f"""
                    SELECT DISTINCT `{col_name}` 
                    FROM `{table}` 
                    WHERE `{col_name}` IS NOT NULL AND `{col_name}` != ''
                    LIMIT {max_values_per_column}
                """)
                values = [str(v[0]) for v in cursor.fetchall() if v[0]]
                
                if values:
                    table_values[col_name] = values
                    logging.debug(f"{table}.{col_name}: {len(values)} 个唯一值")
                    
            except Exception as e:
                logging.warning(f"处理 {table}.{col_name} 时出错: {e}")
                continue
        
        if table_values:
            unique_values[table] = table_values
    
    cursor.close()
    conn.close()
    
    # 统计
    total_columns = sum(len(cols) for cols in unique_values.values())
    total_values = sum(len(vals) for cols in unique_values.values() for vals in cols.values())
    
    if verbose:
        print(f"提取完成: {len(unique_values)} 张表, {total_columns} 列, {total_values} 个唯一值")
    
    return unique_values


def make_lsh(
    unique_values: Dict[str, Dict[str, List[str]]],
    signature_size: int = 100,
    n_gram: int = 3,
    threshold: float = 0.1,
    verbose: bool = True
) -> Tuple[MinHashLSH, Dict[str, Tuple[MinHash, str, str, str]]]:
    """
    从唯一值创建 MinHash LSH 索引
    
    Args:
        unique_values: {table: {column: [values]}} 格式的字典
        signature_size: MinHash 签名大小
        n_gram: n-gram 大小
        threshold: LSH 阈值
        verbose: 是否显示进度
    
    Returns:
        (LSH对象, MinHash字典)
    """
    lsh = MinHashLSH(threshold=threshold, num_perm=signature_size)
    minhashes: Dict[str, Tuple[MinHash, str, str, str]] = {}
    
    total_values = sum(len(vals) for cols in unique_values.values() for vals in cols.values())
    
    if verbose:
        print(f"构建 LSH 索引，共 {total_values} 个值...")
    
    progress_bar = tqdm(total=total_values, desc="创建 LSH", disable=not verbose)
    
    for table_name, table_values in unique_values.items():
        for column_name, column_values in table_values.items():
            for idx, value in enumerate(column_values):
                try:
                    minhash = _create_minhash(signature_size, value, n_gram)
                    minhash_key = f"{table_name}_{column_name}_{idx}"
                    minhashes[minhash_key] = (minhash, table_name, column_name, value)
                    lsh.insert(minhash_key, minhash)
                except Exception as e:
                    logging.warning(f"处理值 {value[:50]}... 时出错: {e}")
                
                progress_bar.update(1)
    
    progress_bar.close()
    
    if verbose:
        print(f"LSH 索引构建完成，包含 {len(minhashes)} 个条目")
    
    return lsh, minhashes


def build_lsh_index(
    output_dir: str,
    host: str = "172.31.26.206",
    port: int = 3306,
    user: str = "ai_test",
    password: str = "Netcare@13579",
    database: str = "netcaredb_ai",
    signature_size: int = 100,
    n_gram: int = 3,
    threshold: float = 0.1,
    verbose: bool = True
) -> None:
    """
    完整的 LSH 索引构建流程
    
    Args:
        output_dir: 输出目录
        host, port, user, password, database: 数据库连接信息
        signature_size, n_gram, threshold: LSH 参数
        verbose: 是否显示进度
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. 提取唯一值
    if verbose:
        print("步骤 1/3: 从数据库提取唯一值...")
    
    unique_values = _get_unique_values_mysql(
        host=host, port=port, user=user, password=password, 
        database=database, verbose=verbose
    )
    
    # 保存唯一值（用于调试）
    with open(output_path / "unique_values.pkl", "wb") as f:
        pickle.dump(unique_values, f)
    
    # 2. 构建 LSH 索引
    if verbose:
        print("\n步骤 2/3: 构建 LSH 索引...")
    
    lsh, minhashes = make_lsh(
        unique_values,
        signature_size=signature_size,
        n_gram=n_gram,
        threshold=threshold,
        verbose=verbose
    )
    
    # 3. 保存索引
    if verbose:
        print("\n步骤 3/3: 保存索引...")
    
    with open(output_path / "lsh.pkl", "wb") as f:
        pickle.dump(lsh, f)
    
    with open(output_path / "minhashes.pkl", "wb") as f:
        pickle.dump(minhashes, f)
    
    if verbose:
        print(f"\n✅ LSH 索引已保存到: {output_path}")
        print(f"   - lsh.pkl")
        print(f"   - minhashes.pkl")
        print(f"   - unique_values.pkl")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="构建 MySQL LSH 值匹配索引")
    parser.add_argument("--output", "-o", default="./lsh_index", help="输出目录")
    parser.add_argument("--host", default="172.31.26.206", help="数据库主机")
    parser.add_argument("--port", type=int, default=3306, help="数据库端口")
    parser.add_argument("--user", default="ai_test", help="用户名")
    parser.add_argument("--password", default="Netcare@13579", help="密码")
    parser.add_argument("--database", default="netcaredb_ai", help="数据库名")
    parser.add_argument("--signature-size", type=int, default=100, help="MinHash 签名大小")
    parser.add_argument("--n-gram", type=int, default=3, help="n-gram 大小")
    parser.add_argument("--threshold", type=float, default=0.1, help="LSH 阈值")
    
    args = parser.parse_args()
    
    build_lsh_index(
        output_dir=args.output,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        signature_size=args.signature_size,
        n_gram=args.n_gram,
        threshold=args.threshold
    )
