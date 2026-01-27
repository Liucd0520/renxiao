#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE 值匹配模块 - 预处理

从 MySQL 数据库提取唯一值并构建 BGE + FAISS 向量索引。
替代原有的 LSH 方案，提供更强的语义匹配能力。
"""

import os
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm

try:
    import faiss
except ImportError:
    raise ImportError("请安装 faiss: pip install faiss-cpu")

from FlagEmbedding import BGEM3FlagModel

# 复用 LSH 模块的数据提取函数
from .preprocess import _get_unique_values_mysql

# 默认 BGE 模型路径
LOCAL_MODEL_PATH = "/Users/jason/Documents/实习/理想实习/LinkAlign/embed_model_cache/BAAI/bge-m3"
MODEL_NAME = LOCAL_MODEL_PATH if os.path.exists(LOCAL_MODEL_PATH) else "BAAI/bge-m3"


def build_bge_value_index(
    output_dir: str,
    host: str = "172.31.26.206",
    port: int = 3306,
    user: str = "ai_test",
    password: str = "Netcare@13579",
    database: str = "netcaredb_ai",
    model_name: str = MODEL_NAME,
    batch_size: int = 64,
    use_sparse: bool = False,
    verbose: bool = True
) -> None:
    """
    完整的 BGE 值索引构建流程
    
    Args:
        output_dir: 输出目录
        host, port, user, password, database: 数据库连接信息
        model_name: BGE 模型名称或路径
        batch_size: embedding 批处理大小
        use_sparse: 是否使用 sparse embedding（词法匹配）
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
    
    # 2. 展平为列表并加载模型
    if verbose:
        print("\n步骤 2/3: 生成 BGE embedding...")
    
    # 展平 {table: {column: [values]}} -> [(table, column, value), ...]
    all_items = []
    for table, columns in unique_values.items():
        for column, values in columns.items():
            for value in values:
                all_items.append((table, column, str(value)))
    
    if verbose:
        print(f"共 {len(all_items)} 个值需要编码")
    
    # 加载模型
    model = BGEM3FlagModel(model_name, use_fp16=True)
    
    # 批量编码
    all_texts = [item[2] for item in all_items]  # 提取 value
    all_embeddings = []
    
    for i in tqdm(range(0, len(all_texts), batch_size), desc="BGE Encoding", disable=not verbose):
        batch = all_texts[i:i + batch_size]
        
        if use_sparse:
            # 使用 sparse embedding（词法匹配，与表检索一致）
            output = model.encode(batch, return_dense=False, return_sparse=True, return_colbert_vecs=False)
            # Sparse 需要特殊处理，这里简化为 dense
            embeddings = model.encode(batch, return_dense=True, return_sparse=False, return_colbert_vecs=False)["dense_vecs"]
        else:
            # 使用 dense embedding（语义匹配）
            output = model.encode(batch, return_dense=True, return_sparse=False, return_colbert_vecs=False)
            embeddings = output["dense_vecs"]
        
        all_embeddings.extend(embeddings)
    
    embeddings_array = np.array(all_embeddings, dtype=np.float32)
    
    # 先保存 metadata（防止后续崩溃丢失数据）
    with open(output_path / "value_metadata.pkl", "wb") as f:
        pickle.dump(all_items, f)
    
    # 保存唯一值
    with open(output_path / "unique_values.pkl", "wb") as f:
        pickle.dump(unique_values, f)
    
    # 保存原始 embeddings（checkpoint）
    np.save(output_path / "embeddings_raw.npy", embeddings_array)
    
    if verbose:
        print(f"Embedding 维度: {embeddings_array.shape}")
        print("已保存中间结果，开始构建 FAISS 索引...")
    
    # 归一化（用于内积相似度 = 余弦相似度）
    faiss.normalize_L2(embeddings_array)
    
    # 3. 构建 FAISS 索引
    if verbose:
        print("\n步骤 3/3: 构建 FAISS 索引...")
    
    dim = embeddings_array.shape[1]
    
    # 对于小规模数据（<100k），使用 Flat 索引；大规模使用 IVF
    if len(all_items) < 100000:
        index = faiss.IndexFlatIP(dim)  # 内积（归一化后 = 余弦相似度）
    else:
        # IVF + Flat，适合大规模
        nlist = min(100, len(all_items) // 100)
        quantizer = faiss.IndexFlatIP(dim)
        index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
        index.train(embeddings_array)
    
    index.add(embeddings_array)
    
    # 保存
    faiss.write_index(index, str(output_path / "value_index.faiss"))
    
    with open(output_path / "value_metadata.pkl", "wb") as f:
        pickle.dump(all_items, f)
    
    # 保存唯一值（与 LSH 兼容，用于调试）
    with open(output_path / "unique_values.pkl", "wb") as f:
        pickle.dump(unique_values, f)
    
    if verbose:
        print(f"\n✅ BGE 值索引已保存到: {output_path}")
        print(f"   - value_index.faiss ({embeddings_array.shape[0]} 向量)")
        print(f"   - value_metadata.pkl")
        print(f"   - unique_values.pkl")


def load_existing_values(unique_values_path: str) -> Dict[str, Dict[str, List[str]]]:
    """加载已保存的唯一值（用于增量更新）"""
    with open(unique_values_path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="构建 BGE 值匹配索引")
    parser.add_argument("--output", "-o", default="./bge_value_index", help="输出目录")
    parser.add_argument("--host", default="172.31.26.206", help="数据库主机")
    parser.add_argument("--port", type=int, default=3306, help="数据库端口")
    parser.add_argument("--user", default="ai_test", help="用户名")
    parser.add_argument("--password", default="Netcare@13579", help="密码")
    parser.add_argument("--database", default="netcaredb_ai", help="数据库名")
    parser.add_argument("--batch-size", type=int, default=64, help="编码批大小")
    
    args = parser.parse_args()
    
    build_bge_value_index(
        output_dir=args.output,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        batch_size=args.batch_size
    )
