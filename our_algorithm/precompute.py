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
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

# 配置
TABLE_SCHEMA_DIR = os.path.join(PROJECT_ROOT, "spider2_dev/schemas_table_level_enhanced/netcaredb_ai")
COLUMN_SCHEMA_DIR = os.path.join(PROJECT_ROOT, "spider2_dev/schemas/netcaredb_ai")  # 原始列级别
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v2.pkl")


def load_schemas():
    """加载所有 Schema"""
    schemas = []
    
    # 表级别（全部 344 张表）
    print("加载表级别 Schema...")
    for f in Path(TABLE_SCHEMA_DIR).glob("*.json"):
        with open(f, 'r') as file:
            data = json.load(file)
        
        table_name = data.get("table_name", data.get("meta_data", {}).get("table_name", f.stem))
        text = data.get("embedding_text", data.get("llm_description", f"表: {table_name}"))
        
        schemas.append({
            "type": "table",
            "table_name": table_name,
            "text": text
        })
    
    print(f"  表级别: {len([s for s in schemas if s['type'] == 'table'])} 个")
    
    # 列级别（全部列）
    print("加载列级别 Schema...")
    for f in Path(COLUMN_SCHEMA_DIR).glob("*.json"):
        with open(f, 'r') as file:
            data = json.load(file)
        
        meta = data.get("meta_data", {})
        table_name = meta.get("table_name", "")
        column_name = data.get("column_name", "")
        
        # 构建列的 embedding_text
        text_parts = [f"表: {table_name}", f"列: {column_name}"]
        if data.get("column_descriptions"):
            text_parts.append(f"描述: {data['column_descriptions']}")
        if data.get("column_types"):
            text_parts.append(f"类型: {data['column_types']}")
        if data.get("sample_rows"):
            samples = data["sample_rows"][:3]
            text_parts.append(f"示例: {', '.join(str(s) for s in samples)}")
        
        text = "\n".join(text_parts)
        schemas.append({
            "type": "column",
            "table_name": table_name,
            "column_name": column_name,
            "text": text
        })
    
    print(f"  列级别: {len([s for s in schemas if s['type'] == 'column'])} 个")
    
    return schemas


def precompute_embeddings():
    """预计算所有 Schema 的 embedding"""
    print("=" * 60)
    print("Schema Embedding 预计算 (V2)")
    print("=" * 60)
    
    # 加载模型
    print("\n[1/3] 加载 BGE-M3 模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    
    # 加载 Schema
    print("\n[2/3] 加载 Schema...")
    schemas = load_schemas()
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
        "model_path": MODEL_PATH,
        "created_at": datetime.now().isoformat(),
        "version": "2.0",
        "note": "表级别增强 + 原始列级别（全量）"
    }
    
    # 保存
    print(f"\n保存到: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(embeddings_data, f)
    
    file_size = os.path.getsize(OUTPUT_FILE) / 1024 / 1024
    print(f"文件大小: {file_size:.1f} MB")
    print("\n完成！")
    
    return embeddings_data


if __name__ == "__main__":
    precompute_embeddings()
