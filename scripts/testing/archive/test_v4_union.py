#!/usr/bin/env python3
"""
V4 Schema 并集算法测试
"""

import os, sys, json, pickle
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v4_llm.pkl")
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"

TOP_K = 10


def main():
    print("=" * 60)
    print("V4 Schema 并集算法测试")
    print("=" * 60)
    
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"问题数: {len(questions)}")
    
    with open(EMBEDDINGS_FILE, 'rb') as f:
        data = pickle.load(f)
    print(f"Schema 版本: {data.get('note', 'V4')}")
    schemas = data["schemas"]
    lexical_weights = data["lexical_weights"]
    
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    
    stats = {
        "simple": {"table": 0, "column": 0, "union": 0, "total": 0},
        "medium": {"table": 0, "column": 0, "union": 0, "total": 0},
        "hard": {"table": 0, "column": 0, "union": 0, "total": 0}
    }
    
    print("\n开始测试...\n")
    
    for i, q in enumerate(questions):
        expected = set(t.lower() for t in q.get("tables", []))
        if not expected:
            continue
        
        difficulty = q.get("difficulty", "simple")
        stats[difficulty]["total"] += 1
        
        query_output = model.encode([q["question"]], return_dense=False, return_sparse=True, return_colbert_vecs=False)
        query_sparse = query_output["lexical_weights"][0]
        
        # 表级别
        table_scores = {}
        for j, s in enumerate(schemas):
            if s['type'] == 'table':
                score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[j]))
                table_scores[s['table_name'].lower()] = score
        table_top = set(t for t, _ in sorted(table_scores.items(), key=lambda x: x[1], reverse=True)[:TOP_K])
        
        # 列级别
        column_scores = defaultdict(float)
        for j, s in enumerate(schemas):
            if s['type'] == 'column':
                score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[j]))
                column_scores[s['table_name'].lower()] += score
        column_top = set(t for t, _ in sorted(column_scores.items(), key=lambda x: x[1], reverse=True)[:TOP_K])
        
        # 并集
        union_top = table_top | column_top
        
        if expected <= table_top:
            stats[difficulty]["table"] += 1
        if expected <= column_top:
            stats[difficulty]["column"] += 1
        if expected <= union_top:
            stats[difficulty]["union"] += 1
        
        if (i + 1) % 50 == 0:
            print(f"  已测试 {i+1}/{len(questions)}")
    
    # 汇总
    print("\n" + "=" * 60)
    print("V4 Schema 测试结果 (并集算法)")
    print("=" * 60)
    
    total_table = sum(s["table"] for s in stats.values())
    total_column = sum(s["column"] for s in stats.values())
    total_union = sum(s["union"] for s in stats.values())
    total_count = sum(s["total"] for s in stats.values())
    
    print(f"\n总体 ({total_count} 个问题):")
    print(f"  表级别: {total_table}/{total_count} ({total_table/total_count*100:.1f}%)")
    print(f"  列级别: {total_column}/{total_count} ({total_column/total_count*100:.1f}%)")
    print(f"  并集:   {total_union}/{total_count} ({total_union/total_count*100:.1f}%)")
    
    print("\n按难度:")
    print(f"{'难度':<10} | {'表级别':>8} | {'列级别':>8} | {'并集':>8}")
    print("-" * 45)
    for d in ["simple", "medium", "hard"]:
        s = stats[d]
        print(f"{d:<10} | {s['table']:>8} | {s['column']:>8} | {s['union']:>8}")


if __name__ == "__main__":
    main()
