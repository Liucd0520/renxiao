#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试脚本：对比三种方案的召回率

1. 纯 LLM 选表 + 英文表描述
2. BGE-M3 多语言向量检索（中文问题 + 中文描述）
3. BGE-M3 + 问题翻译成英文
"""

import os
import sys
import json
import csv
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel


# ============ 工具函数 ============

TRANSLATE_PROMPT = """将以下中文数据库查询问题翻译成英文，保持专业术语准确。只输出翻译结果，不要解释。

中文问题: {question}

英文翻译:"""

TABLE_SELECTION_PROMPT = """You are a database expert. Based on the user's question, select the most relevant tables from the list below (maximum {max_tables} tables).

## User Question
{question}

## Available Tables
{table_list}

## Requirements
1. Analyze what data the question needs
2. Select the most relevant tables (usually 3-8 is enough)
3. Only output table names separated by commas, no explanation

## Selected Tables:"""


def translate_to_english(question, llm):
    """翻译问题到英文"""
    prompt = TRANSLATE_PROMPT.format(question=question)
    response = llm.complete(prompt).text.strip()
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response.strip().strip('"').strip("'")


def clean_llm_response(response):
    """清理 LLM 响应"""
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = response.strip()
    
    table_names = []
    for part in response.replace('\n', ',').split(','):
        name = part.strip().strip('`').strip('"').strip("'")
        name = re.sub(r'^\d+\.\s*', '', name)
        if name and not name.startswith('#'):
            table_names.append(name)
    
    return table_names


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


def load_table_summaries(schema_dir, desc_field="llm_description"):
    """加载表摘要"""
    tables = []
    for json_file in Path(schema_dir).glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data["meta_data"]["table_name"]
        desc = data.get(desc_field, "") or data.get("llm_description", "") or ""
        tables.append({"name": table_name, "description": desc})
    return tables


def calculate_recall(expected, retrieved):
    """计算召回率"""
    expected_set = set(t.lower() for t in expected)
    retrieved_set = set(t.lower() for t in retrieved)
    hit = expected_set & retrieved_set
    return len(hit) / len(expected_set) if expected_set else 1.0


# ============ 测试方法 1: 纯 LLM 选表 + 英文描述 ============

def test_llm_english(test_cases, tables_en, llm, max_tables=10):
    """测试纯 LLM 选表（英文描述）"""
    print("\n" + "=" * 60)
    print("方法 1: 纯 LLM 选表 + 英文表描述")
    print("=" * 60)
    
    # 格式化表列表
    table_list = "\n".join([f"{i+1}. {t['name']}: {t['description'][:80]}..." 
                           for i, t in enumerate(tables_en)])
    
    total_recall = 0
    for i, case in enumerate(test_cases, 1):
        # 翻译问题到英文
        en_question = translate_to_english(case['question'], llm)
        
        prompt = TABLE_SELECTION_PROMPT.format(
            question=en_question,
            table_list=table_list,
            max_tables=max_tables
        )
        
        response = llm.complete(prompt).text
        selected = clean_llm_response(response)
        
        # 只保留有效表名
        valid_names = {t["name"] for t in tables_en}
        selected = [name for name in selected if name in valid_names]
        
        recall = calculate_recall(case['expected_tables'], selected)
        total_recall += recall
        
        print(f"[{i}/{len(test_cases)}] 召回率: {recall:.1%} | 期望: {case['expected_tables']}")
    
    avg_recall = total_recall / len(test_cases)
    print(f"\n平均召回率: {avg_recall:.1%}")
    return avg_recall


# ============ 测试方法 2&3: BGE-M3 向量检索 ============

def test_bge_m3(test_cases, tables_cn, llm, top_k=10, translate_query=False):
    """测试 BGE-M3 多语言向量检索"""
    method_name = "BGE-M3 + 问题翻译" if translate_query else "BGE-M3 中文直接检索"
    print("\n" + "=" * 60)
    print(f"方法: {method_name}")
    print("=" * 60)
    
    try:
        from FlagEmbedding import BGEM3FlagModel
    except ImportError:
        print("❌ FlagEmbedding 未安装")
        return 0
    
    # 加载模型
    print("加载 BGE-M3 模型...")
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
    print("✅ 模型加载完成")
    
    # 准备表描述的嵌入
    print("生成表描述嵌入...")
    table_texts = [f"{t['name']}: {t['description']}" for t in tables_cn]
    table_embeddings = model.encode(table_texts)['dense_vecs']
    print(f"✅ 生成了 {len(table_embeddings)} 个表嵌入")
    
    # 测试
    total_recall = 0
    for i, case in enumerate(test_cases, 1):
        # 准备查询
        if translate_query:
            query = translate_to_english(case['question'], llm)
        else:
            query = case['question']
        
        # 生成查询嵌入
        query_embedding = model.encode([query])['dense_vecs'][0]
        
        # 计算相似度
        import numpy as np
        similarities = query_embedding @ table_embeddings.T
        
        # 获取 top_k 结果
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        selected = [tables_cn[idx]['name'] for idx in top_indices]
        
        recall = calculate_recall(case['expected_tables'], selected)
        total_recall += recall
        
        print(f"[{i}/{len(test_cases)}] 召回率: {recall:.1%} | 期望: {case['expected_tables']}")
        print(f"  检索到: {selected[:5]}...")
    
    avg_recall = total_recall / len(test_cases)
    print(f"\n平均召回率: {avg_recall:.1%}")
    return avg_recall


# ============ 主函数 ============

def main():
    cn_schema_dir = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    en_schema_dir = "./spider2_dev/schemas_table_level_english/netcaredb_ai"
    csv_path = "./cc_result.csv"
    
    print("\n" + "=" * 70)
    print("综合测试：对比三种召回方案".center(70))
    print("=" * 70)
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    
    # 加载测试用例
    test_cases = load_test_cases(csv_path)
    print(f"✅ 加载了 {len(test_cases)} 个测试用例")
    
    # 加载表描述
    print("加载表描述...")
    tables_cn = load_table_summaries(cn_schema_dir, "llm_description")
    tables_en = load_table_summaries(en_schema_dir, "llm_description_en")
    print(f"✅ 中文: {len(tables_cn)} 张表, 英文: {len(tables_en)} 张表")
    
    results = {}
    
    # 测试 1: 纯 LLM 选表 + 英文描述
    results['llm_english'] = test_llm_english(test_cases, tables_en, llm)
    
    # 测试 2: BGE-M3 中文直接检索
    results['bge_m3_chinese'] = test_bge_m3(test_cases, tables_cn, llm, translate_query=False)
    
    # 测试 3: BGE-M3 + 问题翻译
    results['bge_m3_translated'] = test_bge_m3(test_cases, tables_cn, llm, translate_query=True)
    
    # 汇总
    print("\n" + "=" * 70)
    print("测试汇总".center(70))
    print("=" * 70)
    print(f"{'方法':<35} | {'平均召回率':>10}")
    print("-" * 50)
    print(f"{'纯 LLM 选表 + 英文描述':<35} | {results['llm_english']:>10.1%}")
    print(f"{'BGE-M3 中文问题 + 中文描述':<35} | {results['bge_m3_chinese']:>10.1%}")
    print(f"{'BGE-M3 英文问题 + 中文描述':<35} | {results['bge_m3_translated']:>10.1%}")
    print("=" * 70)
    
    # 保存结果
    result_path = "./docs/comprehensive_test_results.json"
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果保存到: {result_path}")


if __name__ == "__main__":
    main()
