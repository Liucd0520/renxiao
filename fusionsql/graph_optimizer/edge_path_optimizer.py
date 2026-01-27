#!/usr/bin/env python3
"""
边/路径增强排序算法 - 最终版本

基于实验结果的最佳配置：
- 路径聚合：avg（均值，考虑路径上所有表）
- 长度衰减：linear（1/len）
- boost_factor：0.4 × max_bge（较高加成）
- 路径贡献：累加（一个表在多条路径上会获得更高分数）

测试结果：
- Q1 event_history: #10 → #3 (+7)
- Q7 event_history: #7 → #3 (+4)
"""

import sys
import os
import logging
from collections import defaultdict
from typing import List, Tuple, Dict, Set

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(__file__))

from fusionsql.graph_optimizer.neo4j_client import Neo4jClient


class EdgePathOptimizerFinal:
    """
    基于边/路径的表排序优化器 - 最终版本

    核心思想：
    1. 不做 1-hop 扩展，只看候选表之间的边
    2. 通过路径传递语义分数（高分表的"光环效应"）
    3. 路径上的表获得加分，路径越短加分越多
    """

    def __init__(
        self,
        client: Neo4jClient,
        boost_factor_mult: float = 0.4,  # boost = max_bge × 0.4
        max_path_length: int = 3,  # 最长路径
        use_edge_boost: bool = True,  # 是否融合边加分
        edge_weight: float = 0.3,  # 边加分的权重（相对于路径加分）
    ):
        self.client = client
        self.boost_factor_mult = boost_factor_mult
        self.max_path_length = max_path_length
        self.use_edge_boost = use_edge_boost
        self.edge_weight = edge_weight

    def optimize(
        self,
        candidates: List[Tuple[str, float]],
    ) -> List[Tuple[str, float]]:
        """
        优化候选表排序

        Args:
            candidates: BGE 检索结果 [(table_name, bge_score), ...]

        Returns:
            优化后的表列表 [(table_name, final_score), ...]
        """
        if len(candidates) < 2:
            return candidates

        table_names = [t for t, _ in candidates]
        bge_scores = {t: s for t, s in candidates}

        # 1. 获取候选表之间的边（不扩展邻居）
        relationships = self.client.get_table_relationships(table_names)

        # 如果没有边，直接返回原始排序
        if not relationships:
            logger.debug("候选表之间无边连接，保持 BGE 排序")
            return candidates

        # 2. 构建邻接表
        adj = defaultdict(list)
        for rel in relationships:
            source, target, rel_type, weight = rel[0], rel[1], rel[2], rel[3]
            adj[source].append((target, rel_type, weight))
            adj[target].append((source, rel_type, weight))

        # 3. 计算分数
        max_bge = max(bge_scores.values())
        boost_factor = max_bge * self.boost_factor_mult

        # 3.1 路径加分
        path_contributions = self._compute_path_contributions(
            table_names, adj, bge_scores, max_bge
        )

        # 3.2 边加分（可选）
        if self.use_edge_boost:
            edge_contributions = self._compute_edge_contributions(
                table_names, adj, bge_scores, max_bge
            )
        else:
            edge_contributions = {t: 0 for t in table_names}

        # 4. 融合分数
        final_scores = {}
        for table in table_names:
            path_c = path_contributions.get(table, 0)
            edge_c = edge_contributions.get(table, 0)

            # 融合：路径为主，边为辅
            if self.use_edge_boost:
                combined = (1 - self.edge_weight) * path_c + self.edge_weight * edge_c
            else:
                combined = path_c

            final_scores[table] = bge_scores[table] + boost_factor * combined

        # 5. 排序返回
        sorted_tables = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return sorted_tables

    def _compute_path_contributions(
        self,
        table_names: List[str],
        adj: Dict,
        bge_scores: Dict[str, float],
        max_bge: float,
    ) -> Dict[str, float]:
        """
        计算路径贡献

        核心逻辑：
        - 找所有 2-hop 和 3-hop 路径
        - 路径分数 = 路径上所有表的 BGE 平均分 × 长度因子
        - 每个表累加其所在路径的分数
        """
        # 找所有路径
        paths = self._find_all_paths(table_names, adj, self.max_path_length)

        # 计算每条路径的分数
        path_contributions = defaultdict(float)

        for path in paths:
            # 路径 BGE 平均分
            path_bge_avg = sum(bge_scores.get(t, 0) for t in path) / len(path)
            # 长度因子（越短越好）
            length_factor = 1.0 / len(path)
            # 归一化
            path_score = path_bge_avg * length_factor / max_bge

            # 累加到路径上的每个表
            for table in path:
                path_contributions[table] += path_score

        # 归一化到 [0, 1]
        if path_contributions:
            max_contrib = max(path_contributions.values())
            if max_contrib > 0:
                path_contributions = {
                    t: v / max_contrib for t, v in path_contributions.items()
                }

        return dict(path_contributions)

    def _compute_edge_contributions(
        self,
        table_names: List[str],
        adj: Dict,
        bge_scores: Dict[str, float],
        max_bge: float,
    ) -> Dict[str, float]:
        """
        计算边贡献

        核心逻辑：
        - 有边连接的表获得加分
        - 加分 = 边权重 × 邻居的 BGE 分数归一化
        """
        edge_contributions = {}

        for table in table_names:
            neighbors = adj.get(table, [])

            if not neighbors:
                edge_contributions[table] = 0.0
            else:
                edge_boost = 0.0
                for neighbor, rel_type, weight in neighbors:
                    if neighbor in table_names:
                        neighbor_score_norm = bge_scores.get(neighbor, 0) / max_bge
                        edge_boost += weight * neighbor_score_norm

                edge_contributions[table] = min(edge_boost, 1.0)

        # 归一化
        if edge_contributions:
            max_contrib = max(edge_contributions.values())
            if max_contrib > 0:
                edge_contributions = {
                    t: v / max_contrib for t, v in edge_contributions.items()
                }

        return edge_contributions

    def _find_all_paths(
        self,
        table_names: List[str],
        adj: Dict,
        max_length: int = 3,
    ) -> List[List[str]]:
        """找所有路径（长度 2 到 max_length）"""
        paths = []
        table_set = set(table_names)

        def dfs(current: str, path: List[str], visited: Set[str]):
            if len(path) >= 2:
                paths.append(path.copy())

            if len(path) >= max_length:
                return

            for neighbor, _, _ in adj.get(current, []):
                if neighbor in table_set and neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        for table in table_names:
            visited = {table}
            dfs(table, [table], visited)

        return paths


def run_full_test():
    """运行完整测试"""
    client = Neo4jClient()
    optimizer = EdgePathOptimizerFinal(client)

    test_cases = [
        {
            'name': 'Q1: 告警统计',
            'key_tables': ['event_history'],
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
            'name': 'Q7: 客户告警',
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
        },
    ]

    print("=" * 80)
    print("边/路径增强排序算法 - 最终版本测试")
    print("=" * 80)

    summary = []

    for tc in test_cases:
        print(f"\n{'='*60}")
        print(f"查询: {tc['name']}")
        print(f"关键表: {tc['key_tables']}")
        print(f"{'='*60}")

        # BGE 原始排名
        print(f"\n--- BGE 原始排名 ---")
        key_ranks_bge = {}
        for i, (table, score) in enumerate(tc['candidates'], 1):
            marker = '⭐' if table in tc['key_tables'] else ''
            print(f"  {i:2d}. {table:30s} {score:.4f} {marker}")
            if table in tc['key_tables']:
                key_ranks_bge[table] = i

        # 优化后排名
        result = optimizer.optimize(tc['candidates'])

        print(f"\n--- 优化后排名 ---")
        key_ranks_new = {}
        for i, (table, score) in enumerate(result[:10], 1):
            marker = '⭐' if table in tc['key_tables'] else ''
            print(f"  {i:2d}. {table:30s} {score:.4f} {marker}")
            if table in tc['key_tables']:
                key_ranks_new[table] = i

        # 排名变化
        print(f"\n--- 关键表排名变化 ---")
        for key in tc['key_tables']:
            old_rank = key_ranks_bge.get(key, -1)
            new_rank = key_ranks_new.get(key, -1)
            change = old_rank - new_rank
            change_str = f"+{change}" if change > 0 else str(change)
            print(f"  {key}: {old_rank} → {new_rank} ({change_str})")
            summary.append({
                'query': tc['name'],
                'key_table': key,
                'old': old_rank,
                'new': new_rank,
                'change': change,
            })

    # 汇总
    print(f"\n\n{'='*80}")
    print("汇总")
    print("=" * 80)
    print(f"\n{'查询':<20} | {'关键表':<30} | {'BGE':<6} | {'优化后':<6} | {'提升':<6}")
    print("-" * 75)
    for s in summary:
        change_str = f"+{s['change']}" if s['change'] > 0 else str(s['change'])
        print(f"{s['query']:<20} | {s['key_table']:<30} | #{s['old']:<5} | #{s['new']:<5} | {change_str:<6}")

    total_improvement = sum(s['change'] for s in summary)
    avg_improvement = total_improvement / len(summary)
    print(f"\n总提升: {total_improvement} 位, 平均提升: {avg_improvement:.1f} 位")

    client.close()


if __name__ == '__main__':
    run_full_test()
