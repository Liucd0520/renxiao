#!/usr/bin/env python3
"""
用真实 BGE 数据重新测试步骤 1-5 + 边/路径算法

目的：用真实数据验证所有算法的效果，修正之前硬编码数据导致的错误结论
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fusionsql.retriever import FastRetriever
from fusionsql.graph_optimizer.optimizer import GraphOptimizer
from fusionsql.graph_optimizer.edge_path_optimizer import EdgePathOptimizerFinal
from fusionsql.graph_optimizer.neo4j_client import Neo4jClient


# 测试查询和关键表
TEST_CASES = [
    {
        'id': 'Q1',
        'query': '设备ciscoA上个月的告警统计',
        'key_tables': ['event_history', 't_bz_config_ci_ne_root'],
        'type': 'multi',
    },
    {
        'id': 'Q2',
        'query': '设备routerB的状态和客户信息',
        'key_tables': ['event_history', 't_bz_config_customer', 't_bz_config_ci_ne_root'],
        'type': 'multi',
    },
    {
        'id': 'Q3',
        'query': '平台上有多少客户',
        'key_tables': ['t_bz_config_customer'],
        'type': 'single',
    },
    {
        'id': 'Q4',
        'query': '平台上有多少设备',
        'key_tables': ['t_bz_config_ci_ne_root'],
        'type': 'single',
    },
    {
        'id': 'Q5',
        'query': '上个月新上线的设备有哪些',
        'key_tables': ['t_bz_config_ci_ne_root'],
        'type': 'single',
    },
    {
        'id': 'Q6',
        'query': '最近下线的设备列表',
        'key_tables': ['t_bz_config_ci_ne_root'],
        'type': 'single',
    },
    {
        'id': 'Q7',
        'query': '客户A的设备告警情况',
        'key_tables': ['event_history', 't_bz_config_customer', 't_bz_config_ci_ne_root'],
        'type': 'multi',
    },
]


def get_rank(table: str, candidates: list) -> int:
    """获取表在候选列表中的排名（1-based）"""
    for i, (t, _) in enumerate(candidates, 1):
        if t == table:
            return i
    return -1  # 不在候选中


def test_with_real_data():
    """用真实 BGE 数据测试所有算法"""

    print("=" * 80)
    print("用真实 BGE 数据测试步骤 1-5 + 边/路径算法")
    print("=" * 80)

    # 初始化
    retriever = FastRetriever()
    optimizer = GraphOptimizer()
    neo4j_client = Neo4jClient()
    edge_path_optimizer = EdgePathOptimizerFinal(neo4j_client)

    # 结果收集
    results = {
        'bge': [],           # BGE 原始
        'hybrid': [],        # 步骤 1-4 (hybrid = BGE加权PPR + 2-hop连通性 + MOSTLYIS稀疏化)
        'local_hybrid': [],  # 步骤 5 (局部子图PPR)
        'edge_path': [],     # 边/路径算法
    }

    for tc in TEST_CASES:
        print(f"\n{'='*60}")
        print(f"{tc['id']}: {tc['query']}")
        print(f"类型: {'单表' if tc['type'] == 'single' else '多表'}")
        print(f"关键表: {tc['key_tables']}")
        print("=" * 60)

        # 1. 获取真实 BGE 检索结果
        bge_results = retriever.retrieve(tc['query'], top_k=15)
        candidates = [(r['table_name'], r['score']) for r in bge_results]

        print(f"\n真实 BGE 检索结果: {len(candidates)} 张表")

        # 记录 BGE 原始排名
        bge_ranks = {}
        for key_table in tc['key_tables']:
            rank = get_rank(key_table, candidates)
            bge_ranks[key_table] = rank
            if rank == -1:
                print(f"  ⚠️ {key_table} 不在候选表中!")
            else:
                print(f"  BGE: {key_table} = #{rank}")

        # 2. 测试 hybrid 策略 (步骤 1-4)
        # 注意：需要绕过门控来测试多表场景
        hybrid_result = optimizer._hybrid_selection(candidates, len(candidates))

        print(f"\n--- Hybrid (步骤1-4) ---")
        for key_table in tc['key_tables']:
            old_rank = bge_ranks[key_table]
            new_rank = get_rank(key_table, hybrid_result)
            change = old_rank - new_rank if old_rank > 0 and new_rank > 0 else 0
            results['hybrid'].append({
                'query': tc['id'],
                'table': key_table,
                'bge_rank': old_rank,
                'new_rank': new_rank,
                'change': change,
            })
            change_str = f"+{change}" if change > 0 else str(change)
            print(f"  {key_table}: #{old_rank} → #{new_rank} ({change_str})")

        # 3. 测试 local_hybrid 策略 (步骤 5)
        local_result = optimizer._local_hybrid_selection(candidates, len(candidates))

        print(f"\n--- Local Hybrid (步骤5) ---")
        for key_table in tc['key_tables']:
            old_rank = bge_ranks[key_table]
            new_rank = get_rank(key_table, local_result)
            change = old_rank - new_rank if old_rank > 0 and new_rank > 0 else 0
            results['local_hybrid'].append({
                'query': tc['id'],
                'table': key_table,
                'bge_rank': old_rank,
                'new_rank': new_rank,
                'change': change,
            })
            change_str = f"+{change}" if change > 0 else str(change)
            print(f"  {key_table}: #{old_rank} → #{new_rank} ({change_str})")

        # 4. 测试边/路径算法
        edge_path_result = edge_path_optimizer.optimize(candidates)

        print(f"\n--- 边/路径算法 ---")
        for key_table in tc['key_tables']:
            old_rank = bge_ranks[key_table]
            new_rank = get_rank(key_table, edge_path_result)
            change = old_rank - new_rank if old_rank > 0 and new_rank > 0 else 0
            results['edge_path'].append({
                'query': tc['id'],
                'table': key_table,
                'bge_rank': old_rank,
                'new_rank': new_rank,
                'change': change,
            })
            change_str = f"+{change}" if change > 0 else str(change)
            print(f"  {key_table}: #{old_rank} → #{new_rank} ({change_str})")

    # 汇总表格
    print("\n\n" + "=" * 80)
    print("完整对比表格（真实 BGE 数据）")
    print("=" * 80)

    print(f"\n{'查询':<6} | {'关键表':<25} | {'BGE':<5} | {'Hybrid':<12} | {'Local':<12} | {'边/路径':<12}")
    print("-" * 85)

    for i, (h, l, e) in enumerate(zip(results['hybrid'], results['local_hybrid'], results['edge_path'])):
        query = h['query']
        table = h['table'][:25]
        bge = f"#{h['bge_rank']}" if h['bge_rank'] > 0 else "N/A"

        h_change = f"(+{h['change']})" if h['change'] > 0 else f"({h['change']})" if h['change'] < 0 else "(0)"
        l_change = f"(+{l['change']})" if l['change'] > 0 else f"({l['change']})" if l['change'] < 0 else "(0)"
        e_change = f"(+{e['change']})" if e['change'] > 0 else f"({e['change']})" if e['change'] < 0 else "(0)"

        hybrid_str = f"#{h['new_rank']} {h_change}" if h['new_rank'] > 0 else "N/A"
        local_str = f"#{l['new_rank']} {l_change}" if l['new_rank'] > 0 else "N/A"
        edge_str = f"#{e['new_rank']} {e_change}" if e['new_rank'] > 0 else "N/A"

        # 标记最佳效果
        if e['change'] > 0 and e['change'] > h['change'] and e['change'] > l['change']:
            edge_str += " ⭐"

        print(f"{query:<6} | {table:<25} | {bge:<5} | {hybrid_str:<12} | {local_str:<12} | {edge_str:<12}")

    # 统计汇总
    print("\n" + "=" * 80)
    print("算法效果统计")
    print("=" * 80)

    for algo_name, algo_results in results.items():
        if algo_name == 'bge':
            continue
        total_change = sum(r['change'] for r in algo_results)
        positive_count = sum(1 for r in algo_results if r['change'] > 0)
        negative_count = sum(1 for r in algo_results if r['change'] < 0)
        avg_change = total_change / len(algo_results) if algo_results else 0

        print(f"\n{algo_name}:")
        print(f"  总提升: {total_change} 位")
        print(f"  平均提升: {avg_change:.2f} 位")
        print(f"  有提升的: {positive_count}/{len(algo_results)}")
        print(f"  有下降的: {negative_count}/{len(algo_results)}")

    # 关闭连接
    neo4j_client.close()

    return results


def test_single_table_safety():
    """测试单表场景安全性"""

    print("\n\n" + "=" * 80)
    print("单表场景安全性测试")
    print("=" * 80)

    retriever = FastRetriever()
    neo4j_client = Neo4jClient()
    edge_path_optimizer = EdgePathOptimizerFinal(neo4j_client)

    single_table_cases = [tc for tc in TEST_CASES if tc['type'] == 'single']

    all_safe = True
    for tc in single_table_cases:
        print(f"\n{tc['id']}: {tc['query']}")

        bge_results = retriever.retrieve(tc['query'], top_k=15)
        candidates = [(r['table_name'], r['score']) for r in bge_results]

        # 边/路径优化
        optimized = edge_path_optimizer.optimize(candidates)

        key_table = tc['key_tables'][0]
        bge_rank = get_rank(key_table, candidates)
        new_rank = get_rank(key_table, optimized)

        if new_rank > bge_rank:
            print(f"  ❌ {key_table}: #{bge_rank} → #{new_rank} (下降!)")
            all_safe = False
        else:
            change = bge_rank - new_rank
            change_str = f"+{change}" if change > 0 else "0"
            print(f"  ✅ {key_table}: #{bge_rank} → #{new_rank} ({change_str})")

    neo4j_client.close()

    print(f"\n单表安全性: {'✅ 全部安全' if all_safe else '❌ 存在问题'}")
    return all_safe


if __name__ == '__main__':
    # 运行完整测试
    results = test_with_real_data()

    # 测试单表安全性
    test_single_table_safety()
