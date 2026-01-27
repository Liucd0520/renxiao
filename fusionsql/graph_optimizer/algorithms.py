"""
图算法模块

实现：
- 个性化 PageRank
- Steiner 树近似
- 连通性评分
- 标准 PageRank
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import heapq

from .config import (
    PPR_DAMPING,
    PPR_MAX_ITER,
    PPR_TOLERANCE,
    RELATION_WEIGHTS,
)

logger = logging.getLogger(__name__)


class TableGraph:
    """
    表关系图数据结构

    支持带权边，用于子图分析
    """

    def __init__(self):
        """初始化空图"""
        self.nodes: Set[str] = set()
        self.edges: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
        # edges[table] = [(neighbor, rel_type, weight), ...]

    def add_node(self, table: str):
        """添加节点"""
        self.nodes.add(table)

    def add_edge(
        self,
        source: str,
        target: str,
        rel_type: str,
        weight: float = None,
    ):
        """
        添加边（无向）

        Args:
            source: 源表
            target: 目标表
            rel_type: 关系类型 (IS/MOSTLYIS)
            weight: 权重（默认根据关系类型）
        """
        if weight is None:
            weight = RELATION_WEIGHTS.get(rel_type, 0.5)

        self.nodes.add(source)
        self.nodes.add(target)

        # 无向边，双向添加
        self.edges[source].append((target, rel_type, weight))
        self.edges[target].append((source, rel_type, weight))

    def get_neighbors(self, table: str) -> List[Tuple[str, float]]:
        """
        获取邻居及权重

        Returns:
            [(neighbor, weight), ...]
        """
        return [(n, w) for n, _, w in self.edges.get(table, [])]

    def get_degree(self, table: str) -> int:
        """获取节点度数"""
        return len(self.edges.get(table, []))

    def get_weighted_degree(self, table: str) -> float:
        """获取加权度数"""
        return sum(w for _, _, w in self.edges.get(table, []))

    @classmethod
    def from_relationships(
        cls,
        relationships: List[Tuple[str, str, str, float]],
    ) -> "TableGraph":
        """
        从关系列表构建图

        Args:
            relationships: [(source, target, rel_type, weight), ...]

        Returns:
            TableGraph 实例
        """
        graph = cls()
        for source, target, rel_type, weight in relationships:
            graph.add_edge(source, target, rel_type, weight)
        return graph


def personalized_pagerank(
    graph: TableGraph,
    seed_tables: List[str],
    seed_weights: Dict[str, float] = None,
    damping: float = None,
    max_iter: int = None,
    tolerance: float = None,
) -> Dict[str, float]:
    """
    个性化 PageRank（以 BGE 候选表为种子）

    与全局 PageRank 不同，PPR 从特定节点集合出发，
    更能反映与当前查询相关的表的重要性。

    Args:
        graph: 表关系图
        seed_tables: 种子表列表（BGE 检索结果）
        seed_weights: BGE 分数权重 {table: score}，用于加权播种
                     如果为 None，则均匀播种（旧行为）
        damping: 阻尼系数
        max_iter: 最大迭代次数
        tolerance: 收敛阈值

    Returns:
        {table: ppr_score, ...}
    """
    if damping is None:
        damping = PPR_DAMPING
    if max_iter is None:
        max_iter = PPR_MAX_ITER
    if tolerance is None:
        tolerance = PPR_TOLERANCE

    nodes = list(graph.nodes)
    if not nodes:
        return {}

    n = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # 初始化个性化向量
    personalization = [0.0] * n
    seed_set = set(seed_tables) & graph.nodes

    if seed_set:
        if seed_weights:
            # 按 BGE 分数加权播种（新行为）
            # 使用 softmax 归一化，避免极端权重差异
            valid_weights = {t: seed_weights.get(t, 0) for t in seed_set}
            total_weight = sum(valid_weights.values())
            if total_weight > 0:
                for seed in seed_set:
                    weight = valid_weights[seed] / total_weight
                    personalization[node_to_idx[seed]] = weight
            else:
                # 权重全为 0，回退到均匀播种
                seed_weight = 1.0 / len(seed_set)
                for seed in seed_set:
                    personalization[node_to_idx[seed]] = seed_weight
        else:
            # 均匀播种（旧行为）
            seed_weight = 1.0 / len(seed_set)
            for seed in seed_set:
                personalization[node_to_idx[seed]] = seed_weight
    else:
        # 如果没有有效种子，回退到均匀分布
        personalization = [1.0 / n] * n

    # 初始化 PageRank 向量
    pr = personalization.copy()

    # 构建转移概率矩阵（出边归一化）
    out_weights = {}
    for node in nodes:
        neighbors = graph.get_neighbors(node)
        total_weight = sum(w for _, w in neighbors)
        if total_weight > 0:
            out_weights[node] = {n: w / total_weight for n, w in neighbors}
        else:
            out_weights[node] = {}

    # Power iteration
    for iteration in range(max_iter):
        new_pr = [0.0] * n

        # 计算传递的 PageRank
        for i, node in enumerate(nodes):
            neighbors = out_weights.get(node, {})
            if neighbors:
                for neighbor, prob in neighbors.items():
                    j = node_to_idx[neighbor]
                    new_pr[j] += damping * pr[i] * prob

        # 加上个性化跳转
        for i in range(n):
            new_pr[i] += (1 - damping) * personalization[i]

        # 检查收敛
        diff = sum(abs(new_pr[i] - pr[i]) for i in range(n))
        pr = new_pr

        if diff < tolerance:
            logger.debug(f"PPR 在第 {iteration + 1} 次迭代收敛")
            break

    return {nodes[i]: pr[i] for i in range(n)}


def compute_pagerank(
    nodes: List[str],
    adjacency: Dict[str, List[Tuple[str, float]]],
    damping: float = None,
    max_iter: int = None,
    tolerance: float = None,
) -> Dict[str, float]:
    """
    计算标准 PageRank（用于全局预计算）

    Args:
        nodes: 节点列表
        adjacency: 邻接表 {node: [(neighbor, weight), ...]}
        damping: 阻尼系数
        max_iter: 最大迭代次数
        tolerance: 收敛阈值

    Returns:
        {node: pagerank_score, ...}
    """
    if damping is None:
        damping = PPR_DAMPING
    if max_iter is None:
        max_iter = PPR_MAX_ITER
    if tolerance is None:
        tolerance = PPR_TOLERANCE

    if not nodes:
        return {}

    n = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # 初始化
    pr = [1.0 / n] * n

    # 构建转移概率
    out_weights = {}
    for node in nodes:
        neighbors = adjacency.get(node, [])
        total_weight = sum(w for _, w in neighbors)
        if total_weight > 0:
            out_weights[node] = {n: w / total_weight for n, w in neighbors}
        else:
            out_weights[node] = {}

    # Power iteration
    for iteration in range(max_iter):
        new_pr = [(1 - damping) / n] * n

        for i, node in enumerate(nodes):
            neighbors = out_weights.get(node, {})
            if neighbors:
                for neighbor, prob in neighbors.items():
                    if neighbor in node_to_idx:
                        j = node_to_idx[neighbor]
                        new_pr[j] += damping * pr[i] * prob

        # 检查收敛
        diff = sum(abs(new_pr[i] - pr[i]) for i in range(n))
        pr = new_pr

        if diff < tolerance:
            break

    return {nodes[i]: pr[i] for i in range(n)}


def find_steiner_subgraph(
    graph: TableGraph,
    terminal_tables: List[str],
    max_extra_nodes: int = 5,
) -> Set[str]:
    """
    找到连接所有终端表的最小连接子图（Steiner 树近似）

    使用贪心策略：依次连接每个终端表到当前树

    Args:
        graph: 表关系图
        terminal_tables: 必须包含的表（终端节点）
        max_extra_nodes: 最多添加的中间节点数

    Returns:
        Steiner 子图中的表集合
    """
    terminals = set(terminal_tables) & graph.nodes
    if len(terminals) <= 1:
        return terminals

    # 从第一个终端开始构建树
    tree_nodes = {list(terminals)[0]}
    remaining = terminals - tree_nodes
    extra_added = 0

    while remaining and extra_added <= max_extra_nodes:
        # 找到离树最近的终端
        best_path = None
        best_terminal = None
        best_length = float("inf")

        for terminal in remaining:
            path = _shortest_path_to_set(graph, terminal, tree_nodes)
            if path and len(path) < best_length:
                best_path = path
                best_terminal = terminal
                best_length = len(path)

        if best_path is None:
            # 无法连接剩余终端
            break

        # 添加路径上的所有节点
        new_nodes = set(best_path) - tree_nodes
        extra_added += len(new_nodes) - 1  # -1 因为终端本身不算额外节点
        tree_nodes.update(best_path)
        remaining.discard(best_terminal)

    return tree_nodes


def _shortest_path_to_set(
    graph: TableGraph,
    source: str,
    target_set: Set[str],
) -> Optional[List[str]]:
    """
    找到从 source 到 target_set 中任一节点的最短路径

    使用 Dijkstra 算法（基于边权的倒数作为距离）
    """
    if source in target_set:
        return [source]

    # 距离使用边权的倒数（权重越高，距离越短）
    distances = {source: 0}
    predecessors = {source: None}
    heap = [(0, source)]
    visited = set()

    while heap:
        dist, node = heapq.heappop(heap)

        if node in visited:
            continue
        visited.add(node)

        if node in target_set and node != source:
            # 找到目标，重建路径
            path = []
            current = node
            while current is not None:
                path.append(current)
                current = predecessors[current]
            return path[::-1]

        for neighbor, weight in graph.get_neighbors(node):
            if neighbor in visited:
                continue
            # 距离 = 1 / weight（权重越高，距离越短）
            edge_dist = 1.0 / weight if weight > 0 else 10.0
            new_dist = dist + edge_dist

            if neighbor not in distances or new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))

    return None  # 无法到达


def compute_connectivity_score(
    graph: TableGraph,
    table: str,
    reference_tables: Set[str],
    max_hops: int = 2,
) -> float:
    """
    计算表在子图中的连通性得分（支持多跳路径强度衰减）

    评估一个表与其他重要表的连接程度

    Args:
        graph: 表关系图
        table: 目标表
        reference_tables: 参考表集合（如高分候选表）
        max_hops: 最大跳数（默认 2）

    Returns:
        连通性得分 [0, 1]
    """
    if table not in graph.nodes:
        return 0.0

    max_possible = len(reference_tables)
    if max_possible == 0:
        return 0.0

    # 使用 BFS 计算到每个参考表的最短跳数
    distances = _bfs_distances(graph, table, max_hops)

    # 计算路径强度衰减分数
    # 1-hop: 1.0, 2-hop: 0.5, 无连接: 0
    score = 0.0
    for ref in reference_tables:
        if ref == table:
            continue  # 跳过自己
        dist = distances.get(ref)
        if dist is not None and dist <= max_hops:
            # 衰减公式: 1 / (dist + 1)
            # dist=1 -> 0.5, dist=2 -> 0.33
            score += 1.0 / (dist + 1)

    # 归一化到 [0, 1]
    # 最大可能分数 = sum(1/(i+1) for i in range(1, max_hops+1)) * (len-1)
    # 简化: 除以参考表数量
    return score / max_possible


def _bfs_distances(
    graph: TableGraph,
    source: str,
    max_depth: int,
) -> Dict[str, int]:
    """
    BFS 计算从 source 到所有可达节点的最短跳数

    Args:
        graph: 表关系图
        source: 起始节点
        max_depth: 最大深度

    Returns:
        {node: distance, ...}
    """
    if source not in graph.nodes:
        return {}

    distances = {source: 0}
    queue = [(source, 0)]

    while queue:
        node, depth = queue.pop(0)

        if depth >= max_depth:
            continue

        for neighbor, _ in graph.get_neighbors(node):
            if neighbor not in distances:
                distances[neighbor] = depth + 1
                queue.append((neighbor, depth + 1))

    return distances



def find_connected_components(
    graph: TableGraph,
) -> List[Set[str]]:
    """
    找到图中的所有连通分量

    Returns:
        [component1, component2, ...]
        每个 component 是一个表名集合
    """
    visited = set()
    components = []

    for node in graph.nodes:
        if node in visited:
            continue

        # BFS 找连通分量
        component = set()
        queue = [node]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            component.add(current)

            for neighbor, _ in graph.get_neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)

        components.append(component)

    # 按大小降序排序
    components.sort(key=len, reverse=True)
    return components
