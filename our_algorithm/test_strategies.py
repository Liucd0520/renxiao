#!/usr/bin/env python3
"""
测试不同融合策略
1. 并集 TOP-20：表 TOP-10 ∪ 列 TOP-10
2. 并集后重排序 TOP-10：表+列分数相加后重新排序取 TOP-10
"""

import os, sys, json, pickle
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v2.pkl")
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"

TOP_K = 10


def main():
    print("=" * 60)
    print("测试不同融合策略")
    print("=" * 60)
    
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"问题数: {len(questions)}")
    
    with open(EMBEDDINGS_FILE, 'rb') as f:
        data = pickle.load(f)
    schemas = data["schemas"]
    lexical_weights = data["lexical_weights"]
    
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    
    # 统计
    stats = {
        "table_only": {"simple": 0, "medium": 0, "hard": 0},
        "column_only": {"simple": 0, "medium": 0, "hard": 0},
        "union_top20": {"simple": 0, "medium": 0, "hard": 0},  # 并集（最多20）
        "union_rerank_top10": {"simple": 0, "medium": 0, "hard": 0},  # 并集后重排序取10
        "sum_score_top10": {"simple": 0, "medium": 0, "hard": 0},  # 分数相加取10
    }
    
    print("\n开始测试...\n")
    
    for i, q in enumerate(questions):
        expected = set(t.lower() for t in q.get("tables", []))
        if not expected:
            continue
        
        difficulty = q.get("difficulty", "simple")
        
        query_output = model.encode([q["question"]], return_dense=False, return_sparse=True, return_colbert_vecs=False)
        query_sparse = query_output["lexical_weights"][0]
        
        # 分别计算表级别和列级别分数
        table_scores = {}  # {表名: 分数}
        column_scores = {}  # {表名: 累加分}
        
        for j, s in enumerate(schemas):
            score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[j]))
            table_name = s['table_name'].lower()
            
            if s['type'] == 'table':
                table_scores[table_name] = score
            else:  # column
                column_scores[table_name] = column_scores.get(table_name, 0) + score
        
        # 各种策略
        # 1. 表级别 TOP-10
        table_top10 = set(t for t, _ in sorted(table_scores.items(), key=lambda x: x[1], reverse=True)[:TOP_K])
        
        # 2. 列级别 TOP-10
        column_top10 = set(t for t, _ in sorted(column_scores.items(), key=lambda x: x[1], reverse=True)[:TOP_K])
        
        # 3. 并集 TOP-20（最多20）
        union_top20 = table_top10 | column_top10
        
        # 4. 并集后重新排序 TOP-10
        # 只考虑并集内的表，按 表分数+列分数 排序
        union_rescored = {}
        for t in union_top20:
            union_rescored[t] = table_scores.get(t, 0) + column_scores.get(t, 0)
        union_rerank_top10 = set(t for t, _ in sorted(union_rescored.items(), key=lambda x: x[1], reverse=True)[:TOP_K])
        
        # 5. 分数相加 TOP-10（全局）
        all_scores = defaultdict(float)
        for t, s in table_scores.items():
            all_scores[t] += s
        for t, s in column_scores.items():
            all_scores[t] += s
        sum_score_top10 = set(t for t, _ in sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:TOP_K])
        
        # 统计
        if expected <= table_top10:
            stats["table_only"][difficulty] += 1
        if expected <= column_top10:
            stats["column_only"][difficulty] += 1
        if expected <= union_top20:
            stats["union_top20"][difficulty] += 1
        if expected <= union_rerank_top10:
            stats["union_rerank_top10"][difficulty] += 1
        if expected <= sum_score_top10:
            stats["sum_score_top10"][difficulty] += 1
        
        if (i + 1) % 50 == 0:
            print(f"  已测试 {i+1}/{len(questions)}")
    
    # 汇总
    print("\n" + "=" * 70)
    print("测试结果对比")
    print("=" * 70)
    
    print(f"\n{'策略':<25} | {'simple':>8} | {'medium':>8} | {'hard':>8} | {'总计':>8} | {'召回率':>8}")
    print("-" * 78)
    
    for strategy in ["table_only", "column_only", "union_top20", "union_rerank_top10", "sum_score_top10"]:
        s = stats[strategy]
        total = s["simple"] + s["medium"] + s["hard"]
        rate = total / 300 * 100
        print(f"{strategy:<25} | {s['simple']:>8} | {s['medium']:>8} | {s['hard']:>8} | {total:>8} | {rate:>7.1f}%")
    
    print("\n策略说明:")
    print("  table_only:         仅表级别 TOP-10")
    print("  column_only:        仅列级别 TOP-10")
    print("  union_top20:        表 TOP-10 ∪ 列 TOP-10（最多20张表）")
    print("  union_rerank_top10: 并集内按 表分数+列分数 重排序取 TOP-10")
    print("  sum_score_top10:    全局 表分数+列分数 取 TOP-10")


if __name__ == "__main__":
    main()
