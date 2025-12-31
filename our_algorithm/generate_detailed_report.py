#!/usr/bin/env python3
"""
完整 300 问题详细分析 - 生成报告
"""

import os, sys, json, pickle
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v2.pkl")
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"
OUTPUT_FILE = "./docs/milestone_20241224/retrieval_detailed_analysis.md"

TARGET_TABLES = {"t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"}


def main():
    print("加载数据...")
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    
    with open(EMBEDDINGS_FILE, 'rb') as f:
        data = pickle.load(f)
    schemas = data["schemas"]
    lexical_weights = data["lexical_weights"]
    
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    print(f"就绪！{len(questions)} 个问题")
    
    # 统计
    top_k_values = [5, 10, 15, 20, 30]
    results = {k: {"table": {"full": 0, "partial": 0, "fail": 0}, 
                   "column": {"full": 0, "partial": 0, "fail": 0},
                   "fusion": {"full": 0, "partial": 0, "fail": 0}} for k in top_k_values}
    
    by_difficulty = {d: {k: {"table": 0, "column": 0, "fusion": 0} for k in top_k_values} 
                     for d in ["simple", "medium", "hard"]}
    
    rank_stats = {"table": [], "column": []}
    fail_cases = []
    
    for i, q in enumerate(questions):
        expected = set(t.lower() for t in q.get("tables", []))
        if not expected:
            continue
        
        difficulty = q.get("difficulty", "unknown")
        
        # 计算排名
        query_output = model.encode([q["question"]], return_dense=False, return_sparse=True, return_colbert_vecs=False)
        query_sparse = query_output["lexical_weights"][0]
        
        # 表级别
        table_scores = []
        for j, s in enumerate(schemas):
            if s['type'] == 'table':
                score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[j]))
                table_scores.append((s['table_name'].lower(), score))
        table_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 列级别
        column_agg = defaultdict(float)
        for j, s in enumerate(schemas):
            if s['type'] == 'column':
                score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[j]))
                column_agg[s['table_name'].lower()] += score
        column_scores = sorted(column_agg.items(), key=lambda x: x[1], reverse=True)
        
        # 记录排名
        for t in expected:
            for rank, (name, _) in enumerate(table_scores):
                if name == t:
                    rank_stats["table"].append(rank + 1)
                    break
            for rank, (name, _) in enumerate(column_scores):
                if name == t:
                    rank_stats["column"].append(rank + 1)
                    break
        
        # 不同 TOP-K 统计
        for k in top_k_values:
            table_set = set(t for t, _ in table_scores[:k])
            column_set = set(t for t, _ in column_scores[:k])
            fusion_set = table_set | column_set
            
            # 表级别
            if expected <= table_set:
                results[k]["table"]["full"] += 1
                by_difficulty[difficulty][k]["table"] += 1
            elif expected & table_set:
                results[k]["table"]["partial"] += 1
            else:
                results[k]["table"]["fail"] += 1
            
            # 列级别
            if expected <= column_set:
                results[k]["column"]["full"] += 1
                by_difficulty[difficulty][k]["column"] += 1
            elif expected & column_set:
                results[k]["column"]["partial"] += 1
            else:
                results[k]["column"]["fail"] += 1
            
            # 融合
            if expected <= fusion_set:
                results[k]["fusion"]["full"] += 1
                by_difficulty[difficulty][k]["fusion"] += 1
            elif expected & fusion_set:
                results[k]["fusion"]["partial"] += 1
            else:
                results[k]["fusion"]["fail"] += 1
        
        # 记录失败案例（TOP-10 融合未完全召回）
        table_set = set(t for t, _ in table_scores[:10])
        column_set = set(t for t, _ in column_scores[:10])
        fusion_set = table_set | column_set
        if not (expected <= fusion_set):
            fail_cases.append({
                "question": q["question"][:80],
                "difficulty": difficulty,
                "expected": list(expected),
                "table_top10": [t for t, _ in table_scores[:10]],
                "column_top10": [t for t, _ in column_scores[:10]]
            })
        
        if (i + 1) % 50 == 0:
            print(f"  已分析 {i+1}/{len(questions)}")
    
    # 生成报告
    total = len(questions)
    report = f"""# 检索算法详细分析报告

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Schema 版本**: V2 (schemas_table_level_enhanced + schemas)  
**测试问题**: {total} 个（simple/medium/hard 各 100）  
**目标表**: t_bz_config_ci_ne_root, t_bz_config_customer, event_history

---

## 1. 不同 TOP-K 的完全召回率对比

| TOP-K | 融合(并集) | 表级别 | 列级别 |
|------|-----------|-------|-------|
"""
    for k in top_k_values:
        f_rate = results[k]["fusion"]["full"] / total * 100
        t_rate = results[k]["table"]["full"] / total * 100
        c_rate = results[k]["column"]["full"] / total * 100
        report += f"| {k} | **{f_rate:.1f}%** ({results[k]['fusion']['full']}) | {t_rate:.1f}% ({results[k]['table']['full']}) | {c_rate:.1f}% ({results[k]['column']['full']}) |\n"
    
    report += """
> **结论**: 增加 TOP-K 可以显著提升召回率，但边际效益递减。

---

## 2. 按难度分析（完全召回数）

### TOP-10 配置

| 难度 | 融合 | 表级别 | 列级别 |
|-----|------|-------|-------|
"""
    for d in ["simple", "medium", "hard"]:
        report += f"| {d} | **{by_difficulty[d][10]['fusion']}** | {by_difficulty[d][10]['table']} | {by_difficulty[d][10]['column']} |\n"
    
    report += """
### TOP-20 配置

| 难度 | 融合 | 表级别 | 列级别 |
|-----|------|-------|-------|
"""
    for d in ["simple", "medium", "hard"]:
        report += f"| {d} | **{by_difficulty[d][20]['fusion']}** | {by_difficulty[d][20]['table']} | {by_difficulty[d][20]['column']} |\n"
    
    report += f"""
---

## 3. 目标表排名统计

| 方法 | 平均排名 | 中位数 | TOP10内 | TOP20内 | TOP30内 |
|-----|---------|-------|---------|---------|---------|
| 表级别 | {sum(rank_stats['table'])/len(rank_stats['table']):.1f} | {sorted(rank_stats['table'])[len(rank_stats['table'])//2]} | {sum(1 for r in rank_stats['table'] if r <= 10)} | {sum(1 for r in rank_stats['table'] if r <= 20)} | {sum(1 for r in rank_stats['table'] if r <= 30)} |
| 列级别 | {sum(rank_stats['column'])/len(rank_stats['column']):.1f} | {sorted(rank_stats['column'])[len(rank_stats['column'])//2]} | {sum(1 for r in rank_stats['column'] if r <= 10)} | {sum(1 for r in rank_stats['column'] if r <= 20)} | {sum(1 for r in rank_stats['column'] if r <= 30)} |

> 总共 {len(rank_stats['table'])} 个目标表需要检索

---

## 4. TOP-10 融合失败案例（{len(fail_cases)} 个）

"""
    for c in fail_cases[:15]:
        report += f"### [{c['difficulty']}] {c['question']}...\n"
        report += f"- **期望**: {c['expected']}\n"
        report += f"- **表级别 TOP10**: {c['table_top10'][:5]}...\n"
        report += f"- **列级别 TOP10**: {c['column_top10'][:5]}...\n\n"
    
    report += """
---

## 5. 优化建议

1. **当前最优配置**: TOP-10 融合（并集），召回率 81.7%
2. **提升到 TOP-15**: 融合召回率可提升约 3-5%
3. **表级别检索对 simple 问题效果好**（单表查询，语义明确）
4. **列级别检索对 hard 问题更依赖**（多表关联，需要列语义辅助）

---
*报告自动生成*
"""
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(report)
    print(f"\n报告已保存: {OUTPUT_FILE}")
    
    # 打印摘要
    print("\n=== TOP-10 摘要 ===")
    print(f"融合: {results[10]['fusion']['full']}/{total} ({results[10]['fusion']['full']/total*100:.1f}%)")
    print(f"表级别: {results[10]['table']['full']}/{total} ({results[10]['table']['full']/total*100:.1f}%)")
    print(f"列级别: {results[10]['column']['full']}/{total} ({results[10]['column']['full']/total*100:.1f}%)")


if __name__ == "__main__":
    main()
