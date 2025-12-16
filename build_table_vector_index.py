#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表级别向量索引构建工具

为表级别 Schema 构建向量索引，用于表级别检索。
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Document,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter

from embed_model.EmbedModelPathMap import embed_model_map_name_to_path


def load_table_schemas(schema_dir):
    """加载表级别 schema 文件"""
    schema_files = list(Path(schema_dir).glob("*.json"))
    print(f"找到 {len(schema_files)} 个表级别 schema 文件")
    
    documents = []
    for schema_file in schema_files:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        # 使用 embedding_text 作为文档内容
        embedding_text = schema_data.get("embedding_text", "")
        if not embedding_text:
            # 如果没有 embedding_text，用表名作为兜底
            embedding_text = f"表名: {schema_data['meta_data']['table_name']}"
        
        # 创建 Document，保存元数据
        doc = Document(
            text=embedding_text,
            metadata={
                "db_id": schema_data["meta_data"]["db_id"],
                "table_name": schema_data["meta_data"]["table_name"],
                "column_count": schema_data.get("column_count", 0),
                "file_name": schema_file.stem,  # 表名
                "file_path": str(schema_file)
            }
        )
        documents.append(doc)
    
    return documents


def build_table_vector_index(schema_dir, persist_dir, embed_model_name="BAAI/bge-large-en-v1.5"):
    """构建表级别向量索引"""
    
    # 设置嵌入模型
    embed_model_path = embed_model_map_name_to_path.get(embed_model_name, embed_model_name)
    Settings.embed_model = HuggingFaceEmbedding(embed_model_path)
    
    # 加载表级别 schema
    documents = load_table_schemas(schema_dir)
    
    if not documents:
        print("❌ 没有找到任何 schema 文件")
        return None
    
    print(f"\n开始构建向量索引...")
    print(f"文档数量: {len(documents)}")
    
    # 使用大 chunk_size，因为每个文档就是一张表
    parser = SentenceSplitter(chunk_size=10000, chunk_overlap=0)
    
    # 构建索引
    index = VectorStoreIndex.from_documents(
        documents, 
        transformations=[parser], 
        show_progress=True
    )
    
    # 保存索引
    os.makedirs(persist_dir, exist_ok=True)
    index.storage_context.persist(persist_dir=persist_dir)
    
    print(f"\n✅ 向量索引构建完成！")
    print(f"📁 保存位置: {persist_dir}")
    
    return index


def main():
    parser = argparse.ArgumentParser(description="构建表级别向量索引")
    parser.add_argument(
        "--schema-dir", 
        default="./spider2_dev/schemas_table_level/netcaredb_ai",
        help="表级别 schema 目录"
    )
    parser.add_argument(
        "--persist-dir",
        default=None,
        help="向量索引保存目录（默认为 schema-dir/table_vector_store）"
    )
    parser.add_argument(
        "--embed-model",
        default="BAAI/bge-large-en-v1.5",
        help="嵌入模型名称"
    )
    
    args = parser.parse_args()
    
    schema_dir = args.schema_dir
    persist_dir = args.persist_dir or os.path.join(schema_dir, "table_vector_store")
    
    print("\n" + "=" * 60)
    print("表级别向量索引构建工具".center(60))
    print("=" * 60)
    print(f"Schema 目录: {schema_dir}")
    print(f"索引保存位置: {persist_dir}")
    print(f"嵌入模型: {args.embed_model}")
    print("=" * 60 + "\n")
    
    build_table_vector_index(schema_dir, persist_dir, args.embed_model)
    
    print("\n" + "=" * 60)
    print("下一步:".center(60))
    print("=" * 60)
    print("运行测试脚本验证表级别检索效果:")
    print(f"  python test_table_level_retrieval.py")


if __name__ == "__main__":
    main()
