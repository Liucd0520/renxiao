#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英文版完整测试：构建索引 + 问题翻译 + 向量检索

测试假设：英文问题 + 英文表描述 + 英文嵌入模型 → 最佳召回率
"""

import os
import sys
import json
import csv
import re
from pathlib import Path
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    Document
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llms.qwen.QwenModel import QwenModel
from embed_model.EmbedModelPathMap import embed_model_map_name_to_path


TRANSLATE_PROMPT = """将以下中文数据库查询问题翻译成英文，保持专业术语准确。只输出翻译结果，不要解释。

中文问题: {question}

英文翻译:"""


def translate_to_english(question, llm):
    """将中文问题翻译成英文"""
    prompt = TRANSLATE_PROMPT.format(question=question)
    response = llm.complete(prompt).text.strip()
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response.strip().strip('"').strip("'")


def build_english_index(schema_dir, persist_dir, embed_model_name="BAAI/bge-large-en-v1.5"):
    """构建英文版向量索引"""
    print("构建英文版向量索引...")
    
    embed_model_path = embed_model_map_name_to_path.get(embed_model_name, embed_model_name)
    Settings.embed_model = HuggingFaceEmbedding(embed_model_path)
    
    documents = []
    for json_file in Path(schema_dir).glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data["meta_data"]["table_name"]
        embedding_text = data.get("embedding_text", "")
        
        if embedding_text:
            doc = Document(
                text=embedding_text,
                metadata={
                    "file_name": json_file.name,
                    "file_path": str(json_file),
                    "table_name": table_name
                }
            )
            documents.append(doc)
    
    print(f"  ✅ 加载了 {len(documents)} 个文档")
    
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=persist_dir)
    print(f"  ✅ 索引保存到 {persist_dir}")
    
    return index


def load_index(persist_dir, embed_model_name="BAAI/bge-large-en-v1.5"):
    """加载向量索引"""
    embed_model_path = embed_model_map_name_to_path.get(embed_model_name, embed_model_name)
    Settings.embed_model = HuggingFaceEmbedding(embed_model_path)
    
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    return load_index_from_storage(storage_context)


def retrieve_tables(index, question, top_k=10):
    """检索相关表"""
    from llama_index.core.retrievers import VectorIndexRetriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
    nodes = retriever.retrieve(question)
    
    return [{"table_name": node.metadata.get("table_name", "unknown"), "score": node.score} for node in nodes]


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


def main():
    # 配置
    en_schema_dir = "./spider2_dev/schemas_table_level_english/netcaredb_ai"
    en_persist_dir = "./spider2_dev/schemas_table_level_english/netcaredb_ai/table_vector_store"
    cn_schema_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    cn_persist_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai/table_vector_store"
    csv_path = "./cc_result.csv"
    top_k = 10
    
    print("\n" + "=" * 70)
    print("英文版完整测试".center(70))
    print("=" * 70)
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    
    # 构建英文版索引
    en_index = build_english_index(en_schema_dir, en_persist_dir)
    
    # 加载中文版索引（用于对比）
    print("加载中文版向量索引...")
    cn_index = load_index(cn_persist_dir)
    
    # 加载测试用例
    test_cases = load_test_cases(csv_path)
    print(f"✅ 加载了 {len(test_cases)} 个测试用例")
    
    # 测试
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"测试 {i}/{len(test_cases)}")
        print(f"问题: {case['question'][:50]}...")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 70)
        
        expected = set(t.lower() for t in case['expected_tables'])
        
        # 1. 中文问题 + 中文描述（原始）
        cn_results = retrieve_tables(cn_index, case['question'], top_k)
        cn_retrieved = set(r['table_name'].lower() for r in cn_results)
        cn_hit = expected & cn_retrieved
        cn_recall = len(cn_hit) / len(expected) if expected else 1.0
        
        # 2. 英文问题 + 英文描述（完全英文）
        en_question = translate_to_english(case['question'], llm)
        en_results = retrieve_tables(en_index, en_question, top_k)
        en_retrieved = set(r['table_name'].lower() for r in en_results)
        en_hit = expected & en_retrieved
        en_recall = len(en_hit) / len(expected) if expected else 1.0
        
        print(f"英文翻译: {en_question}")
        print(f"\n中文问题+中文描述: {cn_recall:.1%} ({len(cn_hit)}/{len(expected)})")
        print(f"  检索到: {[r['table_name'] for r in cn_results[:3]]}...")
        print(f"\n英文问题+英文描述: {en_recall:.1%} ({len(en_hit)}/{len(expected)})")
        print(f"  检索到: {[r['table_name'] for r in en_results[:3]]}...")
        
        if en_recall > cn_recall:
            print("  ✅ 英文版更好!")
        elif en_recall < cn_recall:
            print("  ❌ 英文版更差")
        else:
            print("  ➡️ 效果相同")
        
        results.append({
            "question": case['question'],
            "expected": case['expected_tables'],
            "cn_recall": cn_recall,
            "en_recall": en_recall,
            "cn_retrieved": [r['table_name'] for r in cn_results[:5]],
            "en_retrieved": [r['table_name'] for r in en_results[:5]]
        })
    
    # 汇总
    avg_cn_recall = sum(r['cn_recall'] for r in results) / len(results)
    avg_en_recall = sum(r['en_recall'] for r in results) / len(results)
    
    print("\n" + "=" * 70)
    print("测试汇总".center(70))
    print("=" * 70)
    print(f"测试用例数: {len(results)}")
    print(f"中文问题+中文描述 平均召回率: {avg_cn_recall:.1%}")
    print(f"英文问题+英文描述 平均召回率: {avg_en_recall:.1%}")
    print(f"提升: {(avg_en_recall - avg_cn_recall)*100:.1f} 个百分点")
    print("=" * 70)
    
    # 保存详细结果
    result_path = "./docs/english_test_results.json"
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果保存到: {result_path}")


if __name__ == "__main__":
    main()
