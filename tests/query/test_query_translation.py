#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题翻译测试：将中文问题翻译成英文后进行向量检索

验证假设：英文问题 + 英文向量模型 → 更好的召回率
"""

import os
import sys
import json
import csv
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import VectorIndexRetriever

from llms.qwen.QwenModel import QwenModel
from embed_model.EmbedModelPathMap import embed_model_map_name_to_path


# 翻译 Prompt
TRANSLATE_PROMPT = """将以下中文数据库查询问题翻译成英文，保持专业术语准确。只输出翻译结果，不要解释。

中文问题: {question}

英文翻译:"""


def translate_to_english(question, llm):
    """将中文问题翻译成英文"""
    prompt = TRANSLATE_PROMPT.format(question=question)
    response = llm.complete(prompt).text.strip()
    
    # 清理响应
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = response.strip().strip('"').strip("'")
    
    return response


def load_table_index(persist_dir, embed_model_name="BAAI/bge-large-en-v1.5"):
    """加载向量索引"""
    embed_model_path = embed_model_map_name_to_path.get(embed_model_name, embed_model_name)
    Settings.embed_model = HuggingFaceEmbedding(embed_model_path)
    
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    return index


def retrieve_tables(index, question, top_k=10):
    """检索相关表"""
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
    nodes = retriever.retrieve(question)
    
    results = []
    for node in nodes:
        results.append({
            "table_name": node.metadata.get("table_name", "unknown"),
            "score": node.score,
        })
    
    return results


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
            
            test_cases.append({
                "question": question,
                "expected_tables": expected_tables,
            })
    
    return test_cases


def main():
    persist_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai/table_vector_store"
    csv_path = "./cc_result.csv"
    top_k = 10
    
    print("\n" + "=" * 70)
    print("问题翻译 + 向量检索测试".center(70))
    print("=" * 70)
    
    # 初始化 LLM（用于翻译）
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    print("✅ LLM 初始化完成")
    
    # 加载向量索引
    print("加载向量索引...")
    index = load_table_index(persist_dir)
    print("✅ 向量索引加载完成")
    
    # 加载测试用例
    test_cases = load_test_cases(csv_path)
    print(f"✅ 加载了 {len(test_cases)} 个测试用例")
    
    # 测试
    total_recall_cn = 0
    total_recall_en = 0
    total_cases = 0
    
    for i, case in enumerate(test_cases, 1):
        print("\n" + "=" * 70)
        print(f"测试 {i}/{len(test_cases)}")
        print(f"中文问题: {case['question'][:50]}...")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 70)
        
        # 1. 中文问题直接检索
        results_cn = retrieve_tables(index, case['question'], top_k)
        retrieved_cn = set(r['table_name'].lower() for r in results_cn)
        expected = set(t.lower() for t in case['expected_tables'])
        hit_cn = expected & retrieved_cn
        recall_cn = len(hit_cn) / len(expected) if expected else 1.0
        
        # 2. 翻译成英文后检索
        english_question = translate_to_english(case['question'], llm)
        print(f"英文翻译: {english_question}")
        
        results_en = retrieve_tables(index, english_question, top_k)
        retrieved_en = set(r['table_name'].lower() for r in results_en)
        hit_en = expected & retrieved_en
        recall_en = len(hit_en) / len(expected) if expected else 1.0
        
        # 统计
        total_recall_cn += recall_cn
        total_recall_en += recall_en
        total_cases += 1
        
        # 输出对比
        print(f"\n中文检索召回率: {recall_cn:.1%} ({len(hit_cn)}/{len(expected)})")
        print(f"  检索到: {[r['table_name'] for r in results_cn[:5]]}...")
        
        print(f"\n英文检索召回率: {recall_en:.1%} ({len(hit_en)}/{len(expected)})")
        print(f"  检索到: {[r['table_name'] for r in results_en[:5]]}...")
        
        if recall_en > recall_cn:
            print("  ✅ 翻译后效果更好!")
        elif recall_en < recall_cn:
            print("  ❌ 翻译后效果变差")
        else:
            print("  ➡️ 效果相同")
    
    # 汇总
    avg_recall_cn = total_recall_cn / total_cases if total_cases else 0
    avg_recall_en = total_recall_en / total_cases if total_cases else 0
    
    print("\n" + "=" * 70)
    print("测试汇总".center(70))
    print("=" * 70)
    print(f"测试用例数: {total_cases}")
    print(f"中文问题平均召回率: {avg_recall_cn:.1%}")
    print(f"英文翻译平均召回率: {avg_recall_en:.1%}")
    print(f"提升: {(avg_recall_en - avg_recall_cn)*100:.1f} 个百分点")
    print("=" * 70)


if __name__ == "__main__":
    main()
