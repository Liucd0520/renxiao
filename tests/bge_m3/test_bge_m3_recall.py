#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE-M3 召回率测试

测试 BGE-M3 多语言模型在表级别检索的召回率表现。
"""

import os
import sys
import json
import csv
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    Document
)

from embed_model.BGEM3Embedding import BGEM3Embedding


def extract_tables_from_sql(sql):
    """从 SQL 中提取表名"""
    patterns = [
        r'FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?',
        r'JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?',
    ]
    tables = set()
    for pattern in patterns:
        matches = re.findall(pattern, sql, re.IGNORECASE)
        tables.update(matches)
    return list(tables)


def load_test_cases(csv_path):
    """从 CSV 加载测试用例"""
    test_cases = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get('query', '').strip()
            sql = row.get('sql', '') or row.get('正确SQL', '')
            if not question:
                continue
            expected_tables = extract_tables_from_sql(sql)
            test_cases.append({"question": question, "expected_tables": expected_tables})
    return test_cases


def load_table_summaries(schema_dir):
    """加载表摘要"""
    tables = []
    for json_file in Path(schema_dir).glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data["meta_data"]["table_name"]
        desc = data.get("llm_description", "") or ""
        embedding_text = data.get("embedding_text", "") or f"{table_name}: {desc}"
        tables.append({
            "name": table_name, 
            "description": desc,
            "embedding_text": embedding_text
        })
    return tables


def calculate_recall(expected, retrieved):
    """计算召回率"""
    expected_set = set(t.lower() for t in expected)
    retrieved_set = set(t.lower() for t in retrieved)
    hit = expected_set & retrieved_set
    return len(hit) / len(expected_set) if expected_set else 1.0


def main():
    cn_schema_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    persist_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai/table_vector_store_bge_m3"
    csv_path = "./cc_result.csv"
    top_k = 10
    
    print("\n" + "=" * 70)
    print("BGE-M3 多语言模型召回率测试".center(70))
    print("=" * 70)
    
    # 使用 BGE-M3 嵌入模型
    print("加载 BGE-M3 嵌入模型...")
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    # 加载表描述
    print("加载表描述...")
    tables = load_table_summaries(cn_schema_dir)
    print(f"✅ 加载了 {len(tables)} 张表")
    
    # 构建或加载向量索引
    if Path(persist_dir).exists():
        print("加载已有向量索引...")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
    else:
        print("构建 BGE-M3 向量索引...")
        documents = []
        for table in tables:
            doc = Document(
                text=table["embedding_text"],
                metadata={
                    "table_name": table["name"],
                    "description": table["description"]
                }
            )
            documents.append(doc)
        
        index = VectorStoreIndex.from_documents(documents, show_progress=True)
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=persist_dir)
        print(f"✅ 索引保存到 {persist_dir}")
    
    # 加载测试用例
    test_cases = load_test_cases(csv_path)
    print(f"✅ 加载了 {len(test_cases)} 个测试用例")
    
    # 测试
    from llama_index.core.retrievers import VectorIndexRetriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
    
    results = []
    total_recall = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"测试 {i}/{len(test_cases)}")
        print(f"问题: {case['question'][:50]}...")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 70)
        
        # 检索
        nodes = retriever.retrieve(case['question'])
        retrieved = [node.metadata.get("table_name", "") for node in nodes]
        
        recall = calculate_recall(case['expected_tables'], retrieved)
        total_recall += recall
        
        print(f"检索到: {retrieved[:5]}...")
        print(f"召回率: {recall:.1%}")
        
        # 检查命中情况
        expected_set = set(t.lower() for t in case['expected_tables'])
        for rt in retrieved[:5]:
            if rt.lower() in expected_set:
                print(f"  ✅ 命中: {rt}")
        
        results.append({
            "question": case['question'],
            "expected": case['expected_tables'],
            "retrieved": retrieved[:10],
            "recall": recall
        })
    
    avg_recall = total_recall / len(test_cases)
    
    print("\n" + "=" * 70)
    print("测试汇总".center(70))
    print("=" * 70)
    print(f"测试用例数: {len(test_cases)}")
    print(f"BGE-M3 平均召回率: {avg_recall:.1%}")
    print("=" * 70)
    
    # 保存结果
    result_path = "./docs/bge_m3_test_results.json"
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump({
            "model": "BAAI/bge-m3",
            "avg_recall": avg_recall,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果保存到: {result_path}")


if __name__ == "__main__":
    main()
