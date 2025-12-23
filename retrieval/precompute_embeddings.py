#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema Embedding 预计算模块

功能：
1. 一次性计算所有 Schema 的 sparse embedding
2. 保存到文件供后续使用
3. 提供快速检索接口

使用方式：
python precompute_embeddings.py  # 预计算并保存
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
ENHANCED_COLUMN_DIR = os.path.join(PROJECT_ROOT, "spider2_dev/schemas_column_enhanced/netcaredb_ai")
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings.pkl")


def load_schemas():
    """加载所有 Schema"""
    schemas = []
    
    # 核心表列表（只增强这些表的列）
    CORE_TABLES = [
        "t_bz_config_ci_ne_root",  # 设备表
        "t_bz_config_customer",     # 客户表
        "event_history",            # 告警表
        "t_bz_config_region",       # 区域表
        "collector_v2",             # 采集机表
        "ne_type",                  # 设备类型表
        "customer_collector_v2",    # 客户-采集机关联表（新增）
    ]
    
    # 表级别（全部加载）
    for f in Path(TABLE_SCHEMA_DIR).glob("*.json"):
        with open(f, 'r') as file:
            data = json.load(file)
        table_name = data.get("table_name", f.stem)
        text = data.get("embedding_text", data.get("llm_description", f"表: {table_name}"))
        schemas.append({
            "type": "table",
            "table_name": table_name,
            "text": text
        })
    
    # 增强列级别（只加载核心表的列）
    for f in Path(ENHANCED_COLUMN_DIR).glob("*.json"):
        with open(f, 'r') as file:
            data = json.load(file)
        meta = data.get("meta_data", {})
        table_name = meta.get("table_name", "")
        
        # 只保留核心表的列
        if table_name not in CORE_TABLES:
            continue
            
        column_name = data.get("column_name", "")
        text = data.get("embedding_text", "")
        schemas.append({
            "type": "column",
            "table_name": table_name,
            "column_name": column_name,
            "text": text
        })
    
    return schemas


def precompute_embeddings():
    """预计算所有 Schema 的 embedding"""
    print("=" * 60)
    print("Schema Embedding 预计算")
    print("=" * 60)
    
    # 加载模型
    print("\n[1/3] 加载 BGE-M3 模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    
    # 加载 Schema
    print("\n[2/3] 加载 Schema...")
    schemas = load_schemas()
    print(f"  表级别: {sum(1 for s in schemas if s['type'] == 'table')}")
    print(f"  列级别: {sum(1 for s in schemas if s['type'] == 'column')}")
    print(f"  总计: {len(schemas)}")
    
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
        "version": "1.0"
    }
    
    # 保存
    print(f"\n保存到: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(embeddings_data, f)
    
    file_size = os.path.getsize(OUTPUT_FILE) / 1024 / 1024
    print(f"文件大小: {file_size:.1f} MB")
    print("\n完成！")
    
    return embeddings_data


class FastRetriever:
    """快速检索器（使用预计算的 embedding）"""
    
    def __init__(self, embeddings_file=OUTPUT_FILE, model_path=MODEL_PATH):
        # 加载预计算的 embedding
        print("加载预计算 embedding...")
        with open(embeddings_file, 'rb') as f:
            data = pickle.load(f)
        
        self.schemas = data["schemas"]
        self.lexical_weights = data["lexical_weights"]
        
        # 加载模型（只用于 encode 查询）
        print("加载模型...")
        self.model = BGEM3FlagModel(model_path, use_fp16=True)
        print(f"就绪！共 {len(self.schemas)} 个 Schema")
    
    def retrieve(self, question, top_k=10):
        """检索最相关的表"""
        # 编码问题（只需编码一次）
        query_output = self.model.encode(
            [question],
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        query_sparse = query_output["lexical_weights"][0]
        
        # 计算相似度
        scores = []
        for schema_weight in self.lexical_weights:
            score = self.model.compute_lexical_matching_score(query_sparse, schema_weight)
            scores.append(float(score))
        
        # 聚合到表（表级别 + 列级别累加）
        from collections import defaultdict
        table_scores = defaultdict(float)
        
        for i, score in enumerate(scores):
            table_name = self.schemas[i]["table_name"]
            table_scores[table_name] += score
        
        # 排序
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_tables[:top_k]


if __name__ == "__main__":
    precompute_embeddings()
