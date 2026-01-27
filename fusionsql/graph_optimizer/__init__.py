"""
FusionSQL 图论优化模块

使用 Neo4j 中的表外键关系优化 BGE 检索结果。

使用方法:
    from fusionsql.graph_optimizer import GraphOptimizer

    optimizer = GraphOptimizer()
    optimized = optimizer.optimize(candidates, strategy="hybrid")
"""

from .optimizer import GraphOptimizer
from .neo4j_client import Neo4jClient
from .graph_cache import GraphCache
from .algorithms import (
    TableGraph,
    personalized_pagerank,
    find_steiner_subgraph,
    compute_connectivity_score,
    find_connected_components,
)
from .config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    WEIGHTS,
    TARGET_TABLES,
    MIN_TABLES,
    MAX_TABLES,
)

__all__ = [
    # 核心类
    "GraphOptimizer",
    "Neo4jClient",
    "GraphCache",
    "TableGraph",
    # 算法函数
    "personalized_pagerank",
    "find_steiner_subgraph",
    "compute_connectivity_score",
    "find_connected_components",
    # 配置
    "NEO4J_URI",
    "NEO4J_USER",
    "NEO4J_PASSWORD",
    "WEIGHTS",
    "TARGET_TABLES",
    "MIN_TABLES",
    "MAX_TABLES",
]
