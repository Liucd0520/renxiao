#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图优化 A/B 对比测试

对比：
1. Baseline: 纯 BGE 检索
2. With Graph: BGE + 图优化

观察图优化的输入输出变化
"""

import os
import sys
import json
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 7道测试题
TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root"],
    },
    {
        "id": 2,
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
    },
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "expected_tables": ["t_bz_config_customer"],
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "expected_tables": ["t_bz_config_ci_ne_root"],
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
    },
    {
        "id": 7,
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
    },
]


def check_table_coverage(retrieved_tables, expected_tables):
    """检查检索到的表是否覆盖了期望的表"""
    retrieved_set = set(t.lower() for t in retrieved_tables)
    expected_set = set(t.lower() for t in expected_tables)
    covered = expected_set & retrieved_set
    missing = expected_set - retrieved_set
    return len(missing) == 0, list(covered), list(missing)


def run_comparison():
    """运行对比测试"""
    print("=" * 70)
    print("图优化 A/B 对比测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ========== 初始化两个 Pipeline ==========
    from fusionsql.pipeline import TextToSQL
    from fusionsql.retriever import FastRetriever

    print("\n[1/3] 初始化 Baseline Pipeline（无图优化）...")
    pipeline_baseline = TextToSQL(enable_graph_optimizer=False)

    print("\n[2/3] 初始化 Graph Pipeline（有图优化）...")
    try:
        pipeline_graph = TextToSQL(enable_graph_optimizer=True)
        graph_available = pipeline_graph.graph_optimizer is not None
    except Exception as e:
        print(f"图优化初始化失败: {e}")
        graph_available = False
        pipeline_graph = None

    if not graph_available:
        print("\n⚠️  图优化不可用，只运行 Baseline 测试")
        print("    请确保 Neo4j 可连接: neo4j://172.31.24.111:7689")

    # ========== 运行测试 ==========
    print("\n[3/3] 开始测试...")
    print("-" * 70)

    results = []
    baseline_correct = 0
    graph_correct = 0

    for q in TEST_QUESTIONS:
        print(f"\n{'='*70}")
        print(f"[Q{q['id']}] {q['question']}")
        print(f"期望表: {q['expected_tables']}")
        print("-" * 70)

        # ----- Baseline -----
        print("\n📊 Baseline (纯 BGE):")
        result_base = pipeline_baseline.run_with_details(q['question'])
        base_tables = result_base['retrieved_tables'][:10]
        base_scores = result_base['table_scores']

        # 显示 TOP 10
        print("  检索结果 (TOP 10):")
        for i, t in enumerate(base_tables):
            score = base_scores.get(t, 0)
            marker = "✓" if t.lower() in [x.lower() for x in q['expected_tables']] else " "
            print(f"    {i+1:2}. [{marker}] {t:40} ({score:.4f})")

        base_ok, base_covered, base_missing = check_table_coverage(base_tables, q['expected_tables'])
        if base_ok:
            baseline_correct += 1
            print(f"  ✅ 全部命中")
        else:
            print(f"  ❌ 缺失: {base_missing}")

        # ----- Graph -----
        if graph_available:
            print("\n🔗 With Graph (BGE + 图优化):")
            result_graph = pipeline_graph.run_with_details(q['question'])
            graph_tables = result_graph['retrieved_tables'][:10]
            graph_scores = result_graph['table_scores']

            # 显示 TOP 10
            print("  优化结果 (TOP 10):")
            for i, t in enumerate(graph_tables):
                score = graph_scores.get(t, 0)
                marker = "✓" if t.lower() in [x.lower() for x in q['expected_tables']] else " "
                # 标记排名变化
                if t in base_tables:
                    old_rank = base_tables.index(t) + 1
                    if i + 1 < old_rank:
                        change = f"↑{old_rank - i - 1}"
                    elif i + 1 > old_rank:
                        change = f"↓{i + 1 - old_rank}"
                    else:
                        change = "="
                else:
                    change = "NEW"
                print(f"    {i+1:2}. [{marker}] {t:40} ({score:.4f}) {change}")

            graph_ok, graph_covered, graph_missing = check_table_coverage(graph_tables, q['expected_tables'])
            if graph_ok:
                graph_correct += 1
                print(f"  ✅ 全部命中")
            else:
                print(f"  ❌ 缺失: {graph_missing}")

            # ----- 对比分析 -----
            print("\n📈 变化分析:")
            # 排名变化
            for exp_t in q['expected_tables']:
                exp_lower = exp_t.lower()
                base_rank = next((i+1 for i, t in enumerate(base_tables) if t.lower() == exp_lower), None)
                graph_rank = next((i+1 for i, t in enumerate(graph_tables) if t.lower() == exp_lower), None)

                if base_rank and graph_rank:
                    if graph_rank < base_rank:
                        print(f"  ⬆️  {exp_t}: 排名 {base_rank} → {graph_rank} (提升 {base_rank - graph_rank} 位)")
                    elif graph_rank > base_rank:
                        print(f"  ⬇️  {exp_t}: 排名 {base_rank} → {graph_rank} (下降 {graph_rank - base_rank} 位)")
                    else:
                        print(f"  ➡️  {exp_t}: 排名不变 ({base_rank})")
                elif base_rank and not graph_rank:
                    print(f"  ❌ {exp_t}: 原排名 {base_rank}，优化后跌出 TOP 10")
                elif not base_rank and graph_rank:
                    print(f"  ✨ {exp_t}: 原不在 TOP 10，优化后排名 {graph_rank}")
                else:
                    print(f"  ⚠️  {exp_t}: 两者都不在 TOP 10")

        results.append({
            "id": q['id'],
            "question": q['question'],
            "expected_tables": q['expected_tables'],
            "baseline_tables": base_tables,
            "baseline_ok": base_ok,
            "graph_tables": graph_tables if graph_available else None,
            "graph_ok": graph_ok if graph_available else None,
        })

    # ========== 汇总 ==========
    print("\n" + "=" * 70)
    print("测试汇总")
    print("=" * 70)
    print(f"\nBaseline (纯 BGE):     {baseline_correct}/7 ({baseline_correct/7*100:.1f}%)")
    if graph_available:
        print(f"With Graph (BGE+图优化): {graph_correct}/7 ({graph_correct/7*100:.1f}%)")
        diff = graph_correct - baseline_correct
        if diff > 0:
            print(f"\n🎉 图优化提升了 {diff} 题的表覆盖率!")
        elif diff < 0:
            print(f"\n⚠️  图优化降低了 {-diff} 题的表覆盖率")
        else:
            print(f"\n➡️  表覆盖率持平")

    # 保存结果
    output = {
        "test_time": datetime.now().isoformat(),
        "baseline_correct": baseline_correct,
        "graph_correct": graph_correct if graph_available else None,
        "results": results,
    }
    output_file = os.path.join(os.path.dirname(__file__), "graph_compare_result.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {output_file}")


if __name__ == "__main__":
    run_comparison()
