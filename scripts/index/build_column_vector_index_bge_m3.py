#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 BGE-M3 构建列级别向量索引

原始 LinkAlign 使用 bge-large-en-v1.5（英文模型），无法支持中文查询。
本脚本使用 BGE-M3（多语言模型）重建列级别索引。
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
from embed_model.BGEM3Embedding import BGEM3Embedding

# 配置
SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
OUTPUT_DIR = "./spider2_dev/schemas/netcaredb_ai/vector_store_bge_m3"


def build_column_level_index():
    print("=" * 70)
    print("使用 BGE-M3 构建列级别向量索引")
    print("=" * 70)
    print(f"Schema 目录: {SCHEMA_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 70)
    
    # 1. 初始化 BGE-M3 嵌入模型
    print("\n初始化 BGE-M3 模型...")
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    # 2. 加载所有列 JSON 文件
    print("\n加载列级别 Schema 文件...")
    schema_path = Path(SCHEMA_DIR)
    json_files = list(schema_path.glob("*.json"))
    print(f"找到 {len(json_files)} 个列级别 Schema 文件")
    
    # 3. 构建文档
    documents = []
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("meta_data", {}).get("table_name", "")
        column_name = data.get("column_name", "")
        column_desc = data.get("column_descriptions", "")
        column_type = data.get("column_types", "")
        sample_rows = data.get("sample_rows", [])
        
        # 构建嵌入文本：中文友好
        text_parts = [
            f"表名: {table_name}",
            f"列名: {column_name}",
        ]
        if column_desc:
            text_parts.append(f"描述: {column_desc}")
        if column_type:
            text_parts.append(f"类型: {column_type}")
        if sample_rows:
            # 只取前 3 个样本值
            samples = [str(s)[:50] for s in sample_rows[:3]]
            text_parts.append(f"样本值: {', '.join(samples)}")
        
        text = "\n".join(text_parts)
        
        doc = Document(
            text=text,
            metadata={
                "file_name": json_file.name,
                "table_name": table_name,
                "column_name": column_name,
            }
        )
        documents.append(doc)
    
    print(f"构建了 {len(documents)} 个文档")
    
    # 4. 构建向量索引
    print("\n构建向量索引（这需要几分钟）...")
    start_time = time.time()
    
    index = VectorStoreIndex.from_documents(
        documents,
        show_progress=True
    )
    
    # 5. 保存索引
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    index.storage_context.persist(persist_dir=OUTPUT_DIR)
    
    elapsed = time.time() - start_time
    print(f"\n✅ 向量索引构建完成！")
    print(f"   耗时: {elapsed:.1f} 秒")
    print(f"   保存位置: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    build_column_level_index()
