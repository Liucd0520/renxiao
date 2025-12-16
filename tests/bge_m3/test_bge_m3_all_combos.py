#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE-M3 完整组合测试

测试四种组合的召回率：
1. 中文问题 + 中文表描述
2. 中文问题 + 英文表描述
3. 英文问题 + 中文表描述
4. 英文问题 + 英文表描述
"""

import os
import sys
import json
import csv
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings, Document
from embed_model.BGEM3Embedding import BGEM3Embedding
from llms.qwen.QwenModel import QwenModel


TRANSLATE_PROMPT = """将以下中文数据库查询问题翻译成英文，保持专业术语准确。只输出翻译结果，不要解释。

中文问题: {question}

英文翻译:"""


def translate_to_english(question, llm):
    """翻译问题到英文"""
    prompt = TRANSLATE_PROMPT.format(question=question)
    response = llm.complete(prompt).text.strip()
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response.strip().strip('"').strip("'")


def extract_tables_from_sql(sql):
    patterns = [r'FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?', r'JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?']
    tables = set()
    for pattern in patterns:
        tables.update(re.findall(pattern, sql, re.IGNORECASE))
    return list(tables)


def load_test_cases(csv_path):
    test_cases = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get('query', '').strip()
            sql = row.get('sql', '') or row.get('正确SQL', '')
            if question:
                test_cases.append({"question": question, "expected_tables": extract_tables_from_sql(sql)})
    return test_cases


def load_table_summaries(schema_dir, desc_field="llm_description"):
    tables = []
    for json_file in Path(schema_dir).glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data["meta_data"]["table_name"]
        desc = data.get(desc_field, "") or data.get("llm_description", "") or ""
        # 使用完整的 embedding_text，如果有的话
        embedding_text = data.get("embedding_text", "") or f"{table_name}: {desc}"
        tables.append({"name": table_name, "description": desc, "embedding_text": embedding_text})
    return tables


def calculate_recall(expected, retrieved):
    expected_set = set(t.lower() for t in expected)
    retrieved_set = set(t.lower() for t in retrieved)
    hit = expected_set & retrieved_set
    return len(hit) / len(expected_set) if expected_set else 1.0


def build_index(tables, persist_dir, embed_model):
    """构建或加载向量索引"""
    Settings.embed_model = embed_model
    
    if Path(persist_dir).exists():
        print(f"  加载已有索引: {persist_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        return load_index_from_storage(storage_context)
    
    print(f"  构建新索引...")
    documents = []
    for table in tables:
        # 使用完整的 embedding_text
        text = table.get("embedding_text", f"{table['name']}: {table['description']}")
        doc = Document(text=text, metadata={"table_name": table["name"]})
        documents.append(doc)
    
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=persist_dir)
    return index


def test_retrieval(index, questions, test_cases, top_k=10):
    """测试检索召回率"""
    from llama_index.core.retrievers import VectorIndexRetriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
    
    total_recall = 0
    for i, (question, case) in enumerate(zip(questions, test_cases)):
        nodes = retriever.retrieve(question)
        retrieved = [node.metadata.get("table_name", "") for node in nodes]
        recall = calculate_recall(case['expected_tables'], retrieved)
        total_recall += recall
    
    return total_recall / len(test_cases)


def main():
    cn_schema_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    en_schema_dir = "./spider2_dev/schemas_table_level_english/netcaredb_ai"
    csv_path = "./cc_result.csv"
    
    print("\n" + "=" * 70)
    print("BGE-M3 完整组合测试".center(70))
    print("=" * 70)
    
    # 初始化
    print("初始化...")
    embed_model = BGEM3Embedding()
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    
    # 加载表描述
    print("加载表描述...")
    tables_cn = load_table_summaries(cn_schema_dir, "llm_description")
    tables_en = load_table_summaries(en_schema_dir, "llm_description_en")
    print(f"  中文描述: {len(tables_cn)} 张表")
    print(f"  英文描述: {len(tables_en)} 张表")
    
    # 加载测试用例
    test_cases = load_test_cases(csv_path)
    print(f"  测试用例: {len(test_cases)} 个")
    
    # 翻译问题
    print("翻译问题到英文...")
    questions_cn = [case['question'] for case in test_cases]
    questions_en = []
    for i, q in enumerate(questions_cn):
        en_q = translate_to_english(q, llm)
        questions_en.append(en_q)
        print(f"  [{i+1}/{len(questions_cn)}] {q[:30]}... → {en_q[:30]}...")
    
    # 构建索引
    print("\n构建向量索引...")
    index_cn = build_index(tables_cn, cn_schema_dir + "/bge_m3_index", embed_model)
    index_en = build_index(tables_en, en_schema_dir + "/bge_m3_index", embed_model)
    
    # 测试四种组合
    print("\n" + "=" * 70)
    print("开始测试四种组合")
    print("=" * 70)
    
    results = {}
    
    # 1. 中文问题 + 中文描述
    print("\n[1/4] 中文问题 + 中文表描述")
    results['cn_cn'] = test_retrieval(index_cn, questions_cn, test_cases)
    print(f"  平均召回率: {results['cn_cn']:.1%}")
    
    # 2. 中文问题 + 英文描述
    print("\n[2/4] 中文问题 + 英文表描述")
    results['cn_en'] = test_retrieval(index_en, questions_cn, test_cases)
    print(f"  平均召回率: {results['cn_en']:.1%}")
    
    # 3. 英文问题 + 中文描述
    print("\n[3/4] 英文问题 + 中文表描述")
    results['en_cn'] = test_retrieval(index_cn, questions_en, test_cases)
    print(f"  平均召回率: {results['en_cn']:.1%}")
    
    # 4. 英文问题 + 英文描述
    print("\n[4/4] 英文问题 + 英文表描述")
    results['en_en'] = test_retrieval(index_en, questions_en, test_cases)
    print(f"  平均召回率: {results['en_en']:.1%}")
    
    # 汇总
    print("\n" + "=" * 70)
    print("测试汇总".center(70))
    print("=" * 70)
    print(f"\n{'组合':<25} | {'召回率':>10}")
    print("-" * 40)
    print(f"{'中文问题 + 中文表描述':<25} | {results['cn_cn']:>10.1%}")
    print(f"{'中文问题 + 英文表描述':<25} | {results['cn_en']:>10.1%}")
    print(f"{'英文问题 + 中文表描述':<25} | {results['en_cn']:>10.1%}")
    print(f"{'英文问题 + 英文表描述':<25} | {results['en_en']:>10.1%}")
    print("=" * 70)
    
    # 找出最佳组合
    best = max(results, key=results.get)
    best_names = {'cn_cn': '中文问题+中文描述', 'cn_en': '中文问题+英文描述', 
                  'en_cn': '英文问题+中文描述', 'en_en': '英文问题+英文描述'}
    print(f"\n🏆 最佳组合: {best_names[best]} ({results[best]:.1%})")
    
    # 保存结果
    result_path = "./docs/bge_m3_combo_test_results.json"
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果保存到: {result_path}")


if __name__ == "__main__":
    main()
