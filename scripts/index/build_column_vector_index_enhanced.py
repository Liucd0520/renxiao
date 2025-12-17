#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 BGE-M3 构建增强版列级别向量索引

核心改进：在列的 embedding text 中加入表级别描述，提供更丰富的语义上下文。
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
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_llm/netcaredb_ai"  # 包含表级别描述
OUTPUT_DIR = "./spider2_dev/schemas/netcaredb_ai/vector_store_bge_m3_enhanced"


def load_table_descriptions():
    """加载表级别的 LLM 生成描述"""
    table_desc = {}
    table_path = Path(TABLE_SCHEMA_DIR)
    
    if not table_path.exists():
        print(f"警告: 表级别 Schema 目录不存在: {TABLE_SCHEMA_DIR}")
        return table_desc
    
    for json_file in table_path.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data.get("table_name", json_file.stem)
        llm_desc = data.get("llm_description", "")
        table_comment = data.get("table_comment", "")
        table_desc[table_name] = llm_desc or table_comment or ""
    
    print(f"加载了 {len(table_desc)} 个表的描述")
    return table_desc


def build_enhanced_column_index():
    print("=" * 70)
    print("使用 BGE-M3 构建增强版列级别向量索引")
    print("=" * 70)
    print(f"列 Schema 目录: {SCHEMA_DIR}")
    print(f"表描述目录: {TABLE_SCHEMA_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 70)
    
    # 1. 初始化 BGE-M3 嵌入模型
    print("\n初始化 BGE-M3 模型...")
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    # 2. 加载表级别描述
    print("\n加载表级别描述...")
    table_descriptions = load_table_descriptions()
    
    # 3. 加载所有列 JSON 文件
    print("\n加载列级别 Schema 文件...")
    schema_path = Path(SCHEMA_DIR)
    json_files = list(schema_path.glob("*.json"))
    print(f"找到 {len(json_files)} 个列级别 Schema 文件")
    
    # 4. 构建增强版文档
    documents = []
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("meta_data", {}).get("table_name", "")
        column_name = data.get("column_name", "")
        column_desc = data.get("column_descriptions", "")
        column_type = data.get("column_types", "")
        sample_rows = data.get("sample_rows", [])
        
        # 获取表级别描述
        table_desc = table_descriptions.get(table_name, "")
        
        # 构建增强版嵌入文本：加入表描述上下文！
        text_parts = []
        
        # 关键改进：首先加入表描述
        if table_desc:
            text_parts.append(f"【表描述】{table_desc}")
        
        text_parts.append(f"表名: {table_name}")
        text_parts.append(f"列名: {column_name}")
        
        if column_desc:
            text_parts.append(f"列描述: {column_desc}")
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
    
    print(f"构建了 {len(documents)} 个增强版文档")
    
    # 示例：展示一个增强后的文档
    if documents:
        print("\n示例文档内容:")
        print("-" * 40)
        print(documents[0].text[:500])
        print("-" * 40)
    
    # 5. 构建向量索引
    print("\n构建向量索引（这需要几分钟）...")
    start_time = time.time()
    
    index = VectorStoreIndex.from_documents(
        documents,
        show_progress=True
    )
    
    # 6. 保存索引
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    index.storage_context.persist(persist_dir=OUTPUT_DIR)
    
    elapsed = time.time() - start_time
    print(f"\n✅ 增强版向量索引构建完成！")
    print(f"   耗时: {elapsed:.1f} 秒")
    print(f"   保存位置: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    build_enhanced_column_index()
