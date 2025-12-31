#!/usr/bin/env python3
"""
简单明确的 300 问题测试 - 重新验证
使用 V2 Schema
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
    print("重新验证检索效果 - 使用 V2 Schema")
    print("=" * 60)
    
    # 加载
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"问题数: {len(questions)}")
    
    with open(EMBEDDINGS_FILE, 'rb') as f:
        data = pickle.load(f)
    print(f"Schema 版本: {data.get('note', 'V2')}")
    schemas = data["schemas"]
    lexical_weights = data["lexical_weights"]
    
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    
    # 按难度统计
    stats = {
        "simple": {"table": 0, "column": 0, "fusion": 0, "total": 0},
        "medium": {"table": 0, "column": 0, "fusion": 0, "total": 0},
        "hard": {"table": 0, "column": 0, "fusion": 0, "total": 0}
    }
    
    print("\n开始测试...\n")
    
    for i, q in enumerate(questions):
        expected = set(t.lower() for t in q.get("tables", []))
        if not expected:
            continue
        
        difficulty = q.get("difficulty", "simple")
        stats[difficulty]["total"] += 1
        
        # 计算分数
        query_output = model.encode([q["question"]], return_dense=False, return_sparse=True, return_colbert_vecs=False)
        query_sparse = query_output["lexical_weights"][0]
        
        # 表级别
        table_scores = []
        for j, s in enumerate(schemas):
            if s['type'] == 'table':
                score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[j]))
                table_scores.append((s['table_name'].lower(), score))
        table_scores.sort(key=lambda x: x[1], reverse=True)
        table_top = set(t for t, _ in table_scores[:TOP_K])
        
        # 列级别
        column_agg = defaultdict(float)
        for j, s in enumerate(schemas):
            if s['type'] == 'column':
                score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[j]))
                column_agg[s['table_name'].lower()] += score
        column_scores = sorted(column_agg.items(), key=lambda x: x[1], reverse=True)
        column_top = set(t for t, _ in column_scores[:TOP_K])
        
        # 融合
        fusion_top = table_top | column_top
        
        # 完全召回判断
        table_ok = expected <= table_top
        column_ok = expected <= column_top
        fusion_ok = expected <= fusion_top
        
        if table_ok:
            stats[difficulty]["table"] += 1
        if column_ok:
            stats[difficulty]["column"] += 1
        if fusion_ok:
            stats[difficulty]["fusion"] += 1
        
        # 打印前 10 个详细信息
        if i < 10:
            print(f"问题 {i+1} [{difficulty}]: {q['question'][:40]}...")
            print(f"  期望: {expected}")
            print(f"  表级别 TOP3: {[t for t, _ in table_scores[:3]]}")
            print(f"  列级别 TOP3: {[t for t, _ in column_scores[:3]]}")
            print(f"  表级别召回: {'✅' if table_ok else '❌'}, 列级别召回: {'✅' if column_ok else '❌'}, 融合召回: {'✅' if fusion_ok else '❌'}")
            print()
        
        if (i + 1) % 50 == 0:
            print(f"  已测试 {i+1}/{len(questions)}")
    
    # 汇总
    print("\n" + "=" * 60)
    print(f"测试结果 (TOP-{TOP_K})")
    print("=" * 60)
    
    total_table = sum(s["table"] for s in stats.values())
    total_column = sum(s["column"] for s in stats.values())
    total_fusion = sum(s["fusion"] for s in stats.values())
    total_count = sum(s["total"] for s in stats.values())
    
    print(f"\n总体 ({total_count} 个问题):")
    print(f"  表级别: {total_table}/{total_count} ({total_table/total_count*100:.1f}%)")
    print(f"  列级别: {total_column}/{total_count} ({total_column/total_count*100:.1f}%)")
    print(f"  融合:   {total_fusion}/{total_count} ({total_fusion/total_count*100:.1f}%)")
    
    print("\n按难度:")
    print(f"{'难度':<10} | {'表级别':>10} | {'列级别':>10} | {'融合':>10} | {'总数':>6}")
    print("-" * 55)
    for d in ["simple", "medium", "hard"]:
        s = stats[d]
        print(f"{d:<10} | {s['table']:>10} | {s['column']:>10} | {s['fusion']:>10} | {s['total']:>6}")
    
    # 验证：表+列的并集 >= max(表, 列)，且 <= 表+列
    print("\n验证融合逻辑:")
    for d in ["simple", "medium", "hard"]:
        s = stats[d]
        max_single = max(s['table'], s['column'])
        sum_both = s['table'] + s['column']
        fusion = s['fusion']
        valid = max_single <= fusion <= sum_both
        print(f"  {d}: 表={s['table']}, 列={s['column']}, 融合={fusion}, 验证: {'✅' if valid else '❌'} (应在 [{max_single}, {sum_both}] 之间)")


if __name__ == "__main__":
    main()
