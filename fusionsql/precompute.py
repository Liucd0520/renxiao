#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预计算 Schema Embedding

使用 BGE-M3 Sparse 模式预计算所有 Schema 的 embedding
保存到文件供快速检索使用

Schema 版本：
- 表级别：schemas_table_level_enhanced（344张表的增强描述）
- 列级别：schemas（原始列级别，3353列）
"""

import os
import json
import pickle
from pathlib import Path
from datetime import datetime

from FlagEmbedding import BGEM3FlagModel

# 配置
# fusionsql 包目录
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
# 默认使用包内的 schemas 目录
TABLE_SCHEMA_DIR = os.path.join(PACKAGE_DIR, "schemas")
# BGE-M3 模型：自动从 HuggingFace 下载
MODEL_NAME = "BAAI/bge-m3"
# 输出文件
OUTPUT_FILE = os.path.join(PACKAGE_DIR, "schema_embeddings_v3.pkl")


def load_schemas(schema_dir=TABLE_SCHEMA_DIR):
    """
    加载所有 Schema

    Args:
        schema_dir: Schema JSON 文件目录（默认为 fusionsql/schemas）
    """
    schemas = []

    # 加载表级别 Schema（包含 embedding_text）
    print(f"加载 Schema 目录: {schema_dir}")
    schema_path = Path(schema_dir)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema 目录不存在: {schema_dir}")

    for f in schema_path.glob("*.json"):
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)

        table_name = data.get("table_name", data.get("meta_data", {}).get("table_name", f.stem))
        text = data.get("embedding_text", data.get("llm_description", f"表: {table_name}"))

        # 表级别
        schemas.append({
            "type": "table",
            "table_name": table_name,
            "text": text
        })

        # 列级别（从同一个 JSON 中提取）
        columns = data.get("columns", [])
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "")
            col_desc = col.get("description", "")

            text_parts = [f"表: {table_name}", f"列: {col_name}"]
            if col_desc:
                text_parts.append(f"描述: {col_desc}")
            if col_type:
                text_parts.append(f"类型: {col_type}")

            schemas.append({
                "type": "column",
                "table_name": table_name,
                "column_name": col_name,
                "text": "\n".join(text_parts)
            })

    table_count = sum(1 for s in schemas if s['type'] == 'table')
    column_count = sum(1 for s in schemas if s['type'] == 'column')
    print(f"  表级别: {table_count} 个, 列级别: {column_count} 个")

    return schemas


def precompute_embeddings(schema_dir=TABLE_SCHEMA_DIR, output_file=OUTPUT_FILE):
    """
    预计算所有 Schema 的 embedding

    Args:
        schema_dir: Schema JSON 文件目录
        output_file: 输出文件路径
    """
    print("=" * 60)
    print("FusionSQL - Schema Embedding 预计算")
    print("=" * 60)

    # 加载模型（自动从 HuggingFace 下载）
    print(f"\n[1/3] 加载 BGE-M3 模型: {MODEL_NAME}")
    model = BGEM3FlagModel(MODEL_NAME, use_fp16=True)

    # 加载 Schema
    print("\n[2/3] 加载 Schema...")
    schemas = load_schemas(schema_dir)
    print(f"总计: {len(schemas)} 个 Schema")

    # 计算 embedding
    print("\n[3/3] 计算 Sparse Embedding...")
    texts = [s["text"] for s in schemas]

    output = model.encode(
        texts,
        batch_size=32,
        max_length=512,
        return_dense=False,
        return_sparse=True,
        return_colbert_vecs=False
    )

    # 整理数据
    embeddings_data = {
        "schemas": schemas,
        "lexical_weights": output["lexical_weights"],
        "model_name": MODEL_NAME,
        "created_at": datetime.now().isoformat(),
        "version": "3.0",
        "note": "FusionSQL - 表级别 + 列级别融合检索"
    }

    # 保存
    print(f"\n保存到: {output_file}")
    with open(output_file, 'wb') as f:
        pickle.dump(embeddings_data, f)

    file_size = os.path.getsize(output_file) / 1024 / 1024
    print(f"文件大小: {file_size:.1f} MB")
    print("\n完成！")

    return embeddings_data


if __name__ == "__main__":
    precompute_embeddings()
