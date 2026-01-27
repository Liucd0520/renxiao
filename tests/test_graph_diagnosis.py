#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图优化详细诊断报告

观察：
1. BGE 检索出的表（输入）
2. 这些表之间的外键关系（Neo4j 查询）
3. 图优化的中间过程
4. 最终结果（输出）
"""

import os
import sys
from collections import defaultdict

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


def run_detailed_diagnosis():
    """运行详细诊断"""
    print("=" * 80)
    print("图优化详细诊断报告")
    print("=" * 80)

    # ========== 1. 初始化组件 ==========
    print("\n[初始化组件]")

    from fusionsql.retriever import FastRetriever
    from fusionsql.graph_optimizer import Neo4jClient

    print("  加载 BGE-M3 检索器...")
    retriever = FastRetriever()

    print("  连接 Neo4j...")
    neo4j = Neo4jClient()

    if not neo4j.verify_connection():
        print("  ❌ Neo4j 连接失败！")
        return
    print("  ✅ Neo4j 连接成功")

    # ========== 2. 逐题诊断 ==========
    for q in TEST_QUESTIONS:
        print("\n" + "=" * 80)
        print(f"【Q{q['id']}】{q['question']}")
        print("=" * 80)

        # ----- 2.1 BGE 检索 -----
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ 第一步：BGE 检索结果（输入）                                      │")
        print("└─────────────────────────────────────────────────────────────────┘")

        bge_results = retriever.retrieve(q['question'], top_k=15)
        table_names = [t for t, _ in bge_results]

        print(f"\n  期望表: {q['expected_tables']}")
        print(f"  BGE 返回 {len(bge_results)} 张表:\n")

        for i, (table, score) in enumerate(bge_results):
            is_expected = "✓" if table.lower() in [t.lower() for t in q['expected_tables']] else " "
            print(f"    {i+1:2}. [{is_expected}] {table:45} (BGE={score:.4f})")

        # ----- 2.2 查询外键关系 -----
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ 第二步：这些表之间的外键关系（Neo4j 查询）                        │")
        print("└─────────────────────────────────────────────────────────────────┘")

        # 只查询 BGE 返回的表之间的关系
        relationships = neo4j.get_table_relationships(table_names)

        # 过滤：只保留两端都在候选表中的关系
        internal_rels = [
            (src, tgt, rel_type, weight)
            for src, tgt, rel_type, weight in relationships
            if src in table_names and tgt in table_names
        ]

        # 去重（无向边）
        seen_pairs = set()
        unique_rels = []
        for src, tgt, rel_type, weight in internal_rels:
            pair = tuple(sorted([src, tgt]))
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                unique_rels.append((src, tgt, rel_type, weight))

        if unique_rels:
            print(f"\n  在 BGE 返回的 {len(table_names)} 张表中，发现 {len(unique_rels)} 条外键关系:\n")

            # 按关系类型分组
            is_rels = [(s, t, r, w) for s, t, r, w in unique_rels if r == "IS"]
            mostlyis_rels = [(s, t, r, w) for s, t, r, w in unique_rels if r == "MOSTLYIS"]

            if is_rels:
                print("  【IS 关系（精确外键）】")
                for src, tgt, rel_type, weight in is_rels:
                    src_mark = "★" if src.lower() in [t.lower() for t in q['expected_tables']] else " "
                    tgt_mark = "★" if tgt.lower() in [t.lower() for t in q['expected_tables']] else " "
                    print(f"    {src_mark} {src:40} ──IS──> {tgt_mark} {tgt}")

            if mostlyis_rels:
                print(f"\n  【MOSTLYIS 关系（推断外键）】共 {len(mostlyis_rels)} 条")
                # 只显示前 10 条
                for src, tgt, rel_type, weight in mostlyis_rels[:10]:
                    src_mark = "★" if src.lower() in [t.lower() for t in q['expected_tables']] else " "
                    tgt_mark = "★" if tgt.lower() in [t.lower() for t in q['expected_tables']] else " "
                    print(f"    {src_mark} {src:40} ~~MOSTLY~~> {tgt_mark} {tgt}")
                if len(mostlyis_rels) > 10:
                    print(f"    ... 还有 {len(mostlyis_rels) - 10} 条")
        else:
            print("\n  ⚠️  这些表之间没有发现任何外键关系！")

        # ----- 2.3 分析期望表的连接情况 -----
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ 第三步：期望表的连接情况分析                                      │")
        print("└─────────────────────────────────────────────────────────────────┘")

        expected_lower = [t.lower() for t in q['expected_tables']]

        # 统计每个期望表的连接数
        connection_count = defaultdict(list)
        for src, tgt, rel_type, weight in unique_rels:
            if src.lower() in expected_lower:
                connection_count[src].append((tgt, rel_type))
            if tgt.lower() in expected_lower:
                connection_count[tgt].append((src, rel_type))

        print(f"\n  期望表共 {len(q['expected_tables'])} 张:")
        for exp_table in q['expected_tables']:
            # 查找在 BGE 结果中的排名
            rank = None
            for i, (t, _) in enumerate(bge_results):
                if t.lower() == exp_table.lower():
                    rank = i + 1
                    break

            connections = connection_count.get(exp_table, [])

            if rank:
                if connections:
                    conn_str = ", ".join([f"{t}({r})" for t, r in connections[:3]])
                    if len(connections) > 3:
                        conn_str += f"... (+{len(connections)-3})"
                    print(f"    ✓ {exp_table:40} 排名={rank:2}, 连接={len(connections)}个 [{conn_str}]")
                else:
                    print(f"    ✓ {exp_table:40} 排名={rank:2}, 连接=0个 (孤立表)")
            else:
                print(f"    ✗ {exp_table:40} 不在 TOP 15!")

        # ----- 2.4 判断是否需要 JOIN -----
        is_single_table = len(q['expected_tables']) == 1

        if is_single_table:
            print(f"\n  📋 这是【单表查询】，不需要 JOIN，图优化意义不大")
        else:
            # 检查期望表之间是否有直接连接
            expected_connected = False
            for src, tgt, rel_type, weight in unique_rels:
                if src.lower() in expected_lower and tgt.lower() in expected_lower:
                    expected_connected = True
                    break

            if expected_connected:
                print(f"\n  🔗 期望表之间【有直接外键关系】，可以 JOIN")
            else:
                print(f"\n  ⚠️  期望表之间【没有直接外键关系】，可能需要中间表")

        # ----- 2.5 总结 -----
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ 小结                                                             │")
        print("└─────────────────────────────────────────────────────────────────┘")

        # 检查 BGE 是否已经命中所有期望表
        bge_hit = all(
            any(t.lower() == exp.lower() for t, _ in bge_results)
            for exp in q['expected_tables']
        )

        if bge_hit:
            print(f"\n  ✅ BGE 已命中所有期望表")
            if is_single_table:
                print(f"     → 单表查询，无需图优化")
            else:
                print(f"     → 图优化可以帮助调整排序，但不应该踢掉正确的表")
        else:
            missing = [
                exp for exp in q['expected_tables']
                if not any(t.lower() == exp.lower() for t, _ in bge_results)
            ]
            print(f"\n  ❌ BGE 未命中: {missing}")
            print(f"     → 图优化无法弥补（只能在候选表内调整）")

    # ========== 3. 关闭连接 ==========
    neo4j.close()
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)


if __name__ == "__main__":
    run_detailed_diagnosis()
