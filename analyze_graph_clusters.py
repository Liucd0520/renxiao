#!/usr/bin/env python3
"""
图簇分析脚本
分析候选表通过外键形成的连通分量（簇）
"""

import sys
import os
import logging
from collections import defaultdict, deque

# 设置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

# 设置路径
sys.path.insert(0, os.path.dirname(__file__))

from fusionsql.graph_optimizer.optimizer import GraphOptimizer
from fusionsql.graph_optimizer.algorithms import find_connected_components

def analyze_clusters(optimizer, candidates, query_name):
    """
    分析候选表的连通簇

    Returns:
        dict: {
            'total_tables': int,
            'total_edges': int,
            'num_clusters': int,
            'clusters': List[Set[str]],  # 每个簇包含的表
            'cluster_sizes': List[int],
            'isolated_tables': Set[str],  # 孤立表（无外键连接）
        }
    """
    table_names = [t for t, _ in candidates]

    # 构建子图
    graph = optimizer._build_subgraph(table_names)

    # 找连通分量
    components = find_connected_components(graph)

    # 统计信息
    result = {
        'query': query_name,
        'total_tables': len(table_names),
        'total_edges': len(graph.edges),
        'num_clusters': len(components),
        'clusters': components,
        'cluster_sizes': [len(c) for c in components],
    }

    # 找孤立表（只在 1 个节点的簇中）
    isolated = set()
    for comp in components:
        if len(comp) == 1:
            isolated.update(comp)
    result['isolated_tables'] = isolated

    return result

def print_cluster_analysis(result):
    """打印簇分析结果"""
    print(f"\n{'='*80}")
    print(f"查询: {result['query']}")
    print(f"{'='*80}")

    print(f"\n总体统计:")
    print(f"  - 候选表数量: {result['total_tables']}")
    print(f"  - 外键边数量: {result['total_edges']}")
    print(f"  - 连通簇数量: {result['num_clusters']}")
    print(f"  - 孤立表数量: {len(result['isolated_tables'])}")

    print(f"\n簇大小分布:")
    for i, size in enumerate(result['cluster_sizes'], 1):
        print(f"  簇 {i}: {size} 个表")

    print(f"\n详细簇结构:")
    for i, cluster in enumerate(result['clusters'], 1):
        print(f"\n  簇 {i} ({len(cluster)} 个表):")
        for table in sorted(cluster):
            print(f"    - {table}")

    if result['isolated_tables']:
        print(f"\n  孤立表 ({len(result['isolated_tables'])} 个):")
        for table in sorted(result['isolated_tables']):
            print(f"    - {table}")

def main():
    # 初始化优化器
    optimizer = GraphOptimizer()

    # 测试用例
    test_cases = [
        {
            'name': 'Q1: 告警统计',
            'query': '告警统计',
            'key_table': 'event_history',
            'candidates': [
                ('t_bz_config_ci_ne_root', 5.07),
                ('t_bz_event_month', 2.77),
                ('t_bz_config_customer', 2.53),
                ('v_event_first_today', 2.37),
                ('v_event_first_history', 2.35),
                ('t_bz_event_day', 2.16),
                ('t_bz_event_total', 1.88),
                ('t_bz_run_event_current', 1.72),
                ('t_bz_run_ci_ne_cpe', 1.60),
                ('event_history', 1.55),
            ]
        },
        {
            'name': 'Q2: 设备状态',
            'query': '设备状态',
            'key_table': 'event_history',
            'candidates': [
                ('t_bz_config_ci_ne_root', 7.47),
                ('v_event_first_today', 2.99),
                ('t_bz_event_month', 2.92),
                ('t_bz_config_customer', 2.82),
                ('t_bz_event_day', 2.20),
                ('v_event_first_history', 2.01),
                ('t_bz_run_event_current', 1.75),
                ('t_bz_event_total', 1.64),
                ('event_history', 1.27),
                ('t_bz_run_ci_ne_cpe', 1.24),
            ]
        },
        {
            'name': 'Q3: 客户数量',
            'query': '客户数量',
            'key_table': 't_bz_config_customer',
            'candidates': [
                ('t_bz_config_customer', 11.46),
                ('t_bz_order_customer', 3.82),
                ('t_bz_order_detail', 2.62),
                ('t_bz_config_customer_vip', 2.19),
                ('t_bz_run_ci_ne_cpe', 1.41),
                ('t_bz_config_ci_ne_root', 1.33),
                ('v_customer_detail', 1.21),
                ('t_bz_event_month', 1.10),
                ('event_history', 0.95),
                ('t_bz_event_day', 0.88),
            ]
        },
        {
            'name': 'Q4: 设备数量',
            'query': '设备数量',
            'key_table': 't_bz_config_ci_ne_root',
            'candidates': [
                ('t_bz_config_ci_ne_root', 12.34),
                ('t_bz_run_ci_ne_cpe', 4.21),
                ('t_bz_config_ne_vendor', 2.88),
                ('v_device_status', 2.15),
                ('t_bz_event_month', 1.67),
                ('event_history', 1.42),
                ('t_bz_config_customer', 1.29),
                ('t_bz_event_day', 1.11),
                ('t_bz_run_event_current', 0.98),
                ('t_bz_event_total', 0.85),
            ]
        },
        {
            'name': 'Q5: 新上线设备',
            'query': '新上线设备',
            'key_table': 't_bz_config_ci_ne_root',
            'candidates': [
                ('t_bz_config_ci_ne_root', 8.92),
                ('t_bz_run_ci_ne_cpe', 3.44),
                ('event_history', 2.76),
                ('t_bz_event_month', 2.33),
                ('v_device_status', 1.98),
                ('t_bz_event_day', 1.67),
                ('t_bz_run_event_current', 1.45),
                ('t_bz_config_customer', 1.22),
                ('t_bz_config_ne_vendor', 1.01),
                ('t_bz_event_total', 0.89),
            ]
        },
        {
            'name': 'Q6: 下线设备',
            'query': '下线设备',
            'key_table': 't_bz_config_ci_ne_root',
            'candidates': [
                ('t_bz_config_ci_ne_root', 9.11),
                ('t_bz_run_ci_ne_cpe', 3.67),
                ('event_history', 2.89),
                ('t_bz_event_month', 2.45),
                ('v_device_status', 2.01),
                ('t_bz_event_day', 1.78),
                ('t_bz_run_event_current', 1.52),
                ('t_bz_config_customer', 1.31),
                ('t_bz_config_ne_vendor', 1.08),
                ('t_bz_event_total', 0.94),
            ]
        },
        {
            'name': 'Q7: 客户告警',
            'query': '客户告警',
            'key_tables': ['event_history', 't_bz_config_customer'],
            'candidates': [
                ('t_bz_config_ci_ne_root', 6.41),
                ('t_bz_config_customer', 4.94),
                ('t_bz_event_month', 2.95),
                ('v_event_first_today', 2.26),
                ('t_bz_event_day', 2.20),
                ('v_event_first_history', 2.02),
                ('event_history', 1.88),
                ('t_bz_run_event_current', 1.82),
                ('t_bz_event_total', 1.74),
                ('t_bz_run_ci_ne_cpe', 1.57),
            ]
        }
    ]

    all_results = []

    for test_case in test_cases:
        result = analyze_clusters(optimizer, test_case['candidates'], test_case['name'])
        all_results.append(result)
        print_cluster_analysis(result)

    # 统计摘要
    print(f"\n{'='*80}")
    print("全局统计摘要")
    print(f"{'='*80}")

    print(f"\n| 查询 | 候选表数 | 边数 | 簇数 | 最大簇 | 孤立表 |")
    print(f"|------|----------|------|------|--------|--------|")
    for r in all_results:
        max_cluster = max(r['cluster_sizes']) if r['cluster_sizes'] else 0
        print(f"| {r['query']:20s} | {r['total_tables']:8d} | "
              f"{r['total_edges']:4d} | {r['num_clusters']:4d} | "
              f"{max_cluster:6d} | {len(r['isolated_tables']):6d} |")

    # 平均统计
    avg_tables = sum(r['total_tables'] for r in all_results) / len(all_results)
    avg_edges = sum(r['total_edges'] for r in all_results) / len(all_results)
    avg_clusters = sum(r['num_clusters'] for r in all_results) / len(all_results)
    avg_isolated = sum(len(r['isolated_tables']) for r in all_results) / len(all_results)

    print(f"\n平均值:")
    print(f"  - 平均候选表数: {avg_tables:.1f}")
    print(f"  - 平均边数: {avg_edges:.1f}")
    print(f"  - 平均簇数: {avg_clusters:.1f}")
    print(f"  - 平均孤立表数: {avg_isolated:.1f}")

    # 簇大小分布
    all_sizes = []
    for r in all_results:
        all_sizes.extend(r['cluster_sizes'])

    print(f"\n簇大小分布 (所有查询):")
    from collections import Counter
    size_counter = Counter(all_sizes)
    for size in sorted(size_counter.keys()):
        count = size_counter[size]
        print(f"  - 大小为 {size} 的簇: {count} 个")

    optimizer.close()

if __name__ == '__main__':
    main()
