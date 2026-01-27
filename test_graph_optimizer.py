#!/usr/bin/env python3
"""
图优化器测试脚本
测试步骤5: 局部子图 PPR vs 步骤1-4: Hybrid
"""

import sys
import os
import logging

# 设置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

# 设置路径
sys.path.insert(0, os.path.dirname(__file__))

# 直接导入 graph_optimizer 模块，避免通过 fusionsql 包
from fusionsql.graph_optimizer.optimizer import GraphOptimizer

def main():
    # 初始化优化器
    optimizer = GraphOptimizer()

    # 测试用例
    test_cases = [
        {
            'name': 'Q1: 告警统计 (设备告警统计)',
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
            'name': 'Q2: 设备状态 (设备状态与客户关联)',
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
            'name': 'Q7: 客户告警 (客户设备告警关联)',
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

    results_summary = []

    for test_case in test_cases:
        print('=' * 80)
        print(test_case['name'])
        print('=' * 80)

        candidates = test_case['candidates']
        query = test_case['query']
        key_tables = test_case.get('key_tables', [test_case.get('key_table')])

        # 测试 Hybrid 策略（步骤1-4）
        print('\n--- Hybrid 策略 (步骤1-4) ---')
        result_hybrid = optimizer.optimize(candidates, strategy='hybrid', query=query)
        for i, (t, s) in enumerate(result_hybrid[:10], 1):
            marker = '*** 关键表' if t in key_tables else ''
            print(f'{i:2d}. {t:30s} {s:.4f} {marker}')

        # 测试 Local Hybrid 策略（步骤5）
        print('\n--- Local Hybrid 策略 (步骤5: 局部子图 PPR) ---')
        result_local = optimizer.optimize(candidates, strategy='local_hybrid', query=query)
        for i, (t, s) in enumerate(result_local[:10], 1):
            marker = '*** 关键表' if t in key_tables else ''
            print(f'{i:2d}. {t:30s} {s:.4f} {marker}')

        # 排名对比
        print('\n--- 关键表排名对比 ---')
        for key_table in key_tables:
            hybrid_rank = next((i for i, (t, _) in enumerate(result_hybrid, 1) if t == key_table), -1)
            local_rank = next((i for i, (t, _) in enumerate(result_local, 1) if t == key_table), -1)
            change = local_rank - hybrid_rank
            change_str = f'{change:+d}' if change != 0 else '0'

            print(f'{key_table:30s} Hybrid={hybrid_rank:2d} → Local={local_rank:2d} ({change_str})')

            results_summary.append({
                'query': test_case['name'],
                'table': key_table,
                'hybrid': hybrid_rank,
                'local': local_rank,
                'change': change
            })

        print()

    # 总结
    print('=' * 80)
    print('总结')
    print('=' * 80)
    print()
    print('| 查询 | 关键表 | Hybrid | Local Hybrid | 变化 |')
    print('|------|--------|--------|--------------|------|')
    for r in results_summary:
        change_str = f'{r["change"]:+d}' if r['change'] != 0 else '0'
        print(f'| {r["query"]:30s} | {r["table"]:25s} | {r["hybrid"]:2d} | {r["local"]:2d} | {change_str:5s} |')

    # 计算平均提升
    improvements = [r['change'] for r in results_summary if r['change'] < 0]  # 负数表示排名提升
    if improvements:
        avg_improvement = -sum(improvements) / len(improvements)
        print(f'\n平均排名提升: {avg_improvement:.2f} 位')

    optimizer.close()

if __name__ == '__main__':
    main()
