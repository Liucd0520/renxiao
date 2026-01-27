#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图优化模块单元测试

测试算法正确性和优化器功能
"""

import pytest
import sys
import os

# 添加项目根目录到 path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fusionsql.graph_optimizer.algorithms import (
    TableGraph,
    personalized_pagerank,
    compute_pagerank,
    find_steiner_subgraph,
    compute_connectivity_score,
    find_connected_components,
)


class TestTableGraph:
    """测试 TableGraph 数据结构"""

    def test_add_node(self):
        graph = TableGraph()
        graph.add_node("table_a")
        assert "table_a" in graph.nodes

    def test_add_edge(self):
        graph = TableGraph()
        graph.add_edge("table_a", "table_b", "IS", 1.0)

        assert "table_a" in graph.nodes
        assert "table_b" in graph.nodes
        assert len(graph.edges["table_a"]) == 1
        assert len(graph.edges["table_b"]) == 1  # 无向边

    def test_get_neighbors(self):
        graph = TableGraph()
        graph.add_edge("table_a", "table_b", "IS", 1.0)
        graph.add_edge("table_a", "table_c", "MOSTLYIS", 0.2)

        neighbors = graph.get_neighbors("table_a")
        assert len(neighbors) == 2

    def test_get_degree(self):
        graph = TableGraph()
        graph.add_edge("table_a", "table_b", "IS", 1.0)
        graph.add_edge("table_a", "table_c", "MOSTLYIS", 0.2)

        assert graph.get_degree("table_a") == 2
        assert graph.get_degree("table_b") == 1

    def test_from_relationships(self):
        relationships = [
            ("t1", "t2", "IS", 1.0),
            ("t2", "t3", "MOSTLYIS", 0.2),
        ]
        graph = TableGraph.from_relationships(relationships)

        assert len(graph.nodes) == 3
        assert graph.get_degree("t2") == 2


class TestPageRank:
    """测试 PageRank 算法"""

    def test_simple_pagerank(self):
        """简单图的 PageRank"""
        nodes = ["a", "b", "c"]
        adjacency = {
            "a": [("b", 1.0)],
            "b": [("a", 1.0), ("c", 1.0)],
            "c": [("b", 1.0)],
        }

        pr = compute_pagerank(nodes, adjacency)

        assert len(pr) == 3
        # b 应该有最高的 PageRank（连接最多）
        assert pr["b"] >= pr["a"]
        assert pr["b"] >= pr["c"]

    def test_personalized_pagerank(self):
        """个性化 PageRank"""
        graph = TableGraph()
        graph.add_edge("a", "b", "IS", 1.0)
        graph.add_edge("b", "c", "IS", 1.0)
        graph.add_edge("c", "d", "IS", 1.0)

        # 以 a 为种子
        ppr = personalized_pagerank(graph, ["a"])

        # a 应该有较高的分数（种子节点）
        assert ppr["a"] > ppr["d"]

    def test_ppr_with_multiple_seeds(self):
        """多种子节点的 PPR"""
        graph = TableGraph()
        graph.add_edge("a", "b", "IS", 1.0)
        graph.add_edge("c", "d", "IS", 1.0)

        ppr = personalized_pagerank(graph, ["a", "c"])

        # 种子节点应该有较高分数
        assert ppr["a"] > 0
        assert ppr["c"] > 0


class TestSteinerSubgraph:
    """测试 Steiner 子图算法"""

    def test_connected_terminals(self):
        """直接连接的终端节点"""
        graph = TableGraph()
        graph.add_edge("a", "b", "IS", 1.0)
        graph.add_edge("b", "c", "IS", 1.0)

        steiner = find_steiner_subgraph(graph, ["a", "c"])

        assert "a" in steiner
        assert "c" in steiner
        assert "b" in steiner  # 连接 a 和 c 的中间节点

    def test_single_terminal(self):
        """单个终端节点"""
        graph = TableGraph()
        graph.add_edge("a", "b", "IS", 1.0)

        steiner = find_steiner_subgraph(graph, ["a"])
        assert steiner == {"a"}

    def test_disconnected_terminals(self):
        """不连通的终端节点"""
        graph = TableGraph()
        graph.add_edge("a", "b", "IS", 1.0)
        graph.add_edge("c", "d", "IS", 1.0)
        # a-b 和 c-d 不连通

        steiner = find_steiner_subgraph(graph, ["a", "c"])

        # 应该至少包含一个终端
        assert "a" in steiner or "c" in steiner


class TestConnectivity:
    """测试连通性相关函数"""

    def test_connectivity_score(self):
        """连通性得分"""
        graph = TableGraph()
        graph.add_edge("a", "b", "IS", 1.0)
        graph.add_edge("a", "c", "IS", 1.0)
        graph.add_edge("a", "d", "IS", 1.0)

        # a 连接到所有参考表
        score = compute_connectivity_score(graph, "a", {"b", "c", "d"})
        assert score == 1.0

        # b 只连接到 a，不直接连接 c, d
        score = compute_connectivity_score(graph, "b", {"a", "c", "d"})
        assert score == 1/3  # 只连接 a

    def test_isolated_node_connectivity(self):
        """孤立节点的连通性"""
        graph = TableGraph()
        graph.add_node("a")
        graph.add_edge("b", "c", "IS", 1.0)

        score = compute_connectivity_score(graph, "a", {"b", "c"})
        assert score == 0.0

    def test_find_connected_components(self):
        """连通分量"""
        graph = TableGraph()
        # 分量 1: a-b-c
        graph.add_edge("a", "b", "IS", 1.0)
        graph.add_edge("b", "c", "IS", 1.0)
        # 分量 2: d-e
        graph.add_edge("d", "e", "IS", 1.0)
        # 孤立节点
        graph.add_node("f")

        components = find_connected_components(graph)

        assert len(components) == 3
        # 最大分量应该在前面
        assert len(components[0]) == 3  # a, b, c


class TestGraphOptimizerMock:
    """测试 GraphOptimizer（使用 mock）"""

    def test_normalize_scores(self):
        """分数归一化"""
        from fusionsql.graph_optimizer.optimizer import GraphOptimizer

        scores = {"a": 10, "b": 20, "c": 30}
        normalized = GraphOptimizer._normalize_scores(scores)

        assert normalized["a"] == 0.0
        assert normalized["c"] == 1.0
        assert 0 < normalized["b"] < 1

    def test_normalize_empty(self):
        """空分数归一化"""
        from fusionsql.graph_optimizer.optimizer import GraphOptimizer

        assert GraphOptimizer._normalize_scores({}) == {}

    def test_normalize_same_values(self):
        """相同分数归一化"""
        from fusionsql.graph_optimizer.optimizer import GraphOptimizer

        scores = {"a": 5, "b": 5, "c": 5}
        normalized = GraphOptimizer._normalize_scores(scores)

        # 所有值相同时，归一化为 1.0
        assert all(v == 1.0 for v in normalized.values())


class TestIntegration:
    """集成测试（需要 Neo4j 连接）"""

    @pytest.fixture
    def optimizer(self):
        """创建优化器（跳过如果 Neo4j 不可用）"""
        try:
            from fusionsql.graph_optimizer import GraphOptimizer
            opt = GraphOptimizer(lazy_init=True)
            # 尝试连接
            if not opt.client.verify_connection():
                pytest.skip("Neo4j 连接不可用")
            return opt
        except Exception as e:
            pytest.skip(f"GraphOptimizer 初始化失败: {e}")

    def test_optimize_hybrid(self, optimizer):
        """测试 hybrid 策略"""
        candidates = [
            ("ne_device", 0.9),
            ("ne_device_extend", 0.85),
            ("ne_alert", 0.8),
            ("ne_customer", 0.75),
            ("ne_vendor", 0.7),
        ]

        result = optimizer.optimize(candidates, strategy="hybrid")

        assert len(result) >= 5
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)

    def test_optimize_empty_candidates(self, optimizer):
        """空候选列表"""
        result = optimizer.optimize([], strategy="hybrid")
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
