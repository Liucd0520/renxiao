#!/usr/bin/env python3
"""
详细分析检索失败案例
- 分析目标表在 TOP 几
- 测试不同 TOP-K 的效果
- 验证问题的正确性
"""

import os, sys, json, pickle
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

# 使用 V2 embedding（最佳版本）
EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v2.pkl")
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"

# 目标三张表
TARGET_TABLES = {"t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"}


def load_retriever():
    print("加载 embedding...")
    with open(EMBEDDINGS_FILE, 'rb') as f:
        data = pickle.load(f)
    
    print("加载模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    
    return data["schemas"], data["lexical_weights"], model


def get_full_ranking(question, schemas, lexical_weights, model):
    """获取完整排名（不限制 TOP-K）"""
    query_output = model.encode([question], return_dense=False, return_sparse=True, return_colbert_vecs=False)
    query_sparse = query_output["lexical_weights"][0]
    
    # 表级别
    table_scores = []
    for i, s in enumerate(schemas):
        if s['type'] == 'table':
            score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[i]))
            table_scores.append((s['table_name'], score))
    table_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 列级别（累加分）
    column_agg = defaultdict(float)
    for i, s in enumerate(schemas):
        if s['type'] == 'column':
            score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[i]))
            column_agg[s['table_name']] += score
    column_scores = sorted(column_agg.items(), key=lambda x: x[1], reverse=True)
    
    # 融合（累加）
    fusion_agg = defaultdict(float)
    for i, s in enumerate(schemas):
        score = float(model.compute_lexical_matching_score(query_sparse, lexical_weights[i]))
        fusion_agg[s['table_name']] += score
    fusion_scores = sorted(fusion_agg.items(), key=lambda x: x[1], reverse=True)
    
    return table_scores, column_scores, fusion_scores


def find_table_rank(scores, table_name):
    """找出表在排名中的位置"""
    for i, (t, _) in enumerate(scores):
        if t.lower() == table_name.lower():
            return i + 1
    return -1


def validate_questions(questions):
    """验证问题的正确性"""
    issues = []
    
    for i, q in enumerate(questions):
        tables = q.get("tables", [])
        
        # 检查 tables 是否都在目标三张表中
        for t in tables:
            if t not in TARGET_TABLES:
                issues.append(f"问题 {i+1}: 使用了非目标表 '{t}'")
        
        # 检查 SQL 是否包含 tables 中的表
        sql = q.get("sql", "").lower()
        for t in tables:
            if t.lower() not in sql:
                issues.append(f"问题 {i+1}: SQL 中未包含声明的表 '{t}'")
    
    return issues


def main():
    print("=" * 70)
    print("检索失败案例详细分析")
    print("=" * 70)
    
    # 加载问题
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"加载了 {len(questions)} 个问题")
    
    # 验证问题
    print("\n1. 验证问题正确性...")
    issues = validate_questions(questions)
    if issues:
        print(f"  发现 {len(issues)} 个问题:")
        for issue in issues[:10]:
            print(f"    - {issue}")
    else:
        print("  ✅ 所有问题都正确（只使用目标三张表）")
    
    # 加载检索器
    schemas, lexical_weights, model = load_retriever()
    
    # 分析失败案例
    print("\n2. 分析失败案例（目标表排名）...")
    
    # 统计不同 TOP-K 的效果
    top_k_results = {k: {"fusion": 0, "table": 0, "column": 0} for k in [5, 10, 15, 20, 30]}
    
    # 记录目标表的排名分布
    rank_distribution = {"table": [], "column": [], "fusion": []}
    
    fail_cases = []
    
    for i, q in enumerate(questions[:50]):  # 只分析前 50 个
        expected = set(t.lower() for t in q.get("tables", []))
        if not expected:
            continue
        
        table_scores, column_scores, fusion_scores = get_full_ranking(
            q["question"], schemas, lexical_weights, model
        )
        
        # 找出每个期望表的排名
        for t in expected:
            rank_distribution["table"].append(find_table_rank(table_scores, t))
            rank_distribution["column"].append(find_table_rank(column_scores, t))
            rank_distribution["fusion"].append(find_table_rank(fusion_scores, t))
        
        # 统计不同 TOP-K 的召回
        for k in top_k_results.keys():
            table_set = set(t.lower() for t, _ in table_scores[:k])
            column_set = set(t.lower() for t, _ in column_scores[:k])
            fusion_set = table_set | column_set  # 并集
            
            if expected <= table_set:
                top_k_results[k]["table"] += 1
            if expected <= column_set:
                top_k_results[k]["column"] += 1
            if expected <= fusion_set:
                top_k_results[k]["fusion"] += 1
        
        # 记录失败案例（TOP-10 未完全召回）
        table_set = set(t.lower() for t, _ in table_scores[:10])
        column_set = set(t.lower() for t, _ in column_scores[:10])
        
        if not (expected <= table_set) or not (expected <= column_set):
            fail_cases.append({
                "question": q["question"][:60],
                "difficulty": q.get("difficulty"),
                "expected": list(expected),
                "table_top5": [t for t, _ in table_scores[:5]],
                "column_top5": [t for t, _ in column_scores[:5]],
                "expected_table_ranks": {t: find_table_rank(table_scores, t) for t in expected},
                "expected_column_ranks": {t: find_table_rank(column_scores, t) for t in expected}
            })
        
        if (i + 1) % 10 == 0:
            print(f"  已分析 {i+1}/50")
    
    # 输出结果
    print("\n" + "=" * 70)
    print("3. 不同 TOP-K 的完全召回数（前 50 个问题）")
    print("=" * 70)
    print(f"{'TOP-K':>10} | {'融合(并集)':>12} | {'表级别':>10} | {'列级别':>10}")
    print("-" * 50)
    for k, r in top_k_results.items():
        print(f"{k:>10} | {r['fusion']:>12} | {r['table']:>10} | {r['column']:>10}")
    
    print("\n" + "=" * 70)
    print("4. 目标表的排名分布")
    print("=" * 70)
    for method, ranks in rank_distribution.items():
        valid_ranks = [r for r in ranks if r > 0]
        if valid_ranks:
            avg = sum(valid_ranks) / len(valid_ranks)
            in_top10 = sum(1 for r in valid_ranks if r <= 10)
            in_top20 = sum(1 for r in valid_ranks if r <= 20)
            print(f"{method}: 平均排名={avg:.1f}, TOP10内={in_top10}/{len(valid_ranks)}, TOP20内={in_top20}/{len(valid_ranks)}")
    
    print("\n" + "=" * 70)
    print("5. 失败案例详情（前 5 个）")
    print("=" * 70)
    for c in fail_cases[:5]:
        print(f"\n问题: {c['question']}...")
        print(f"  难度: {c['difficulty']}")
        print(f"  期望: {c['expected']}")
        print(f"  期望表排名(表级别): {c['expected_table_ranks']}")
        print(f"  期望表排名(列级别): {c['expected_column_ranks']}")
        print(f"  表级别 TOP5: {c['table_top5']}")
        print(f"  列级别 TOP5: {c['column_top5']}")


if __name__ == "__main__":
    main()
