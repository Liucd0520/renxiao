"""
图优化器核心类

综合 BGE 检索分数和图特征，优化候选表排序
"""

import logging
from typing import Dict, List, Tuple, Optional, Set

from .config import (
    WEIGHTS,
    TARGET_TABLES,
    MIN_TABLES,
    MAX_TABLES,
    LOCAL_PPR_TOPN,
    LOCAL_PPR_MIN_EDGES,
    LOCAL_PPR_FALLBACK,
)
from .neo4j_client import Neo4jClient
from .graph_cache import GraphCache
from .algorithms import (
    TableGraph,
    personalized_pagerank,
    find_steiner_subgraph,
    compute_connectivity_score,
    find_connected_components,
)

logger = logging.getLogger(__name__)


class GraphOptimizer:
    """
    图论优化器

    使用 Neo4j 中的表外键关系，结合 BGE 检索分数，
    筛选出真正相关且结构连通的候选表。

    策略：
    - hybrid: 综合 BGE + PPR + 连通性 + 度中心性
    - steiner_tree: 最小连接子图
    - connectivity: 最大连通分量优先
    """

    def __init__(
        self,
        neo4j_uri: str = None,
        neo4j_user: str = None,
        neo4j_password: str = None,
        cache_dir: str = None,
        lazy_init: bool = True,
    ):
        """
        初始化优化器

        Args:
            neo4j_uri: Neo4j 连接地址
            neo4j_user: 用户名
            neo4j_password: 密码
            cache_dir: 缓存目录
            lazy_init: 是否延迟初始化（默认 True）
        """
        self._client: Optional[Neo4jClient] = None
        self._cache: Optional[GraphCache] = None
        self._initialized = False

        # 保存配置用于延迟初始化
        self._neo4j_uri = neo4j_uri
        self._neo4j_user = neo4j_user
        self._neo4j_password = neo4j_password
        self._cache_dir = cache_dir

        if not lazy_init:
            self._initialize()

    def _initialize(self):
        """执行实际初始化"""
        if self._initialized:
            return

        try:
            self._client = Neo4jClient(
                uri=self._neo4j_uri,
                user=self._neo4j_user,
                password=self._neo4j_password,
            )
            self._cache = GraphCache(cache_dir=self._cache_dir)
            self._initialized = True
            logger.info("GraphOptimizer 初始化成功")
        except Exception as e:
            logger.error(f"GraphOptimizer 初始化失败: {e}")
            raise

    @property
    def client(self) -> Neo4jClient:
        """获取 Neo4j 客户端"""
        if not self._initialized:
            self._initialize()
        return self._client

    @property
    def cache(self) -> GraphCache:
        """获取缓存"""
        if not self._initialized:
            self._initialize()
        return self._cache

    def optimize(
        self,
        candidates: List[Tuple[str, float]],
        strategy: str = "hybrid",
        target_count: int = None,
        query: str = None,
    ) -> List[Tuple[str, float]]:
        """
        优化候选表列表

        Args:
            candidates: BGE 检索结果 [(table_name, bge_score), ...]
            strategy: 优化策略 ("hybrid" | "steiner_tree" | "connectivity")
            target_count: 目标返回数量（默认使用配置值）
            query: 原始查询文本（用于单表/多表判别）

        Returns:
            优化后的表列表 [(table_name, final_score), ...]
        """
        if not candidates:
            return []

        if target_count is None:
            target_count = TARGET_TABLES

        # 确保初始化
        if not self._initialized:
            self._initialize()

        # 单表/多表判别门控
        if self._is_likely_single_table(candidates, query):
            logger.info("检测到单表查询场景，跳过图优化")
            return candidates  # 直接返回 BGE 排序

        try:
            if strategy == "hybrid":
                return self._hybrid_selection(candidates, target_count)
            elif strategy == "local_hybrid":
                return self._local_hybrid_selection(candidates, target_count)
            elif strategy == "steiner_tree":
                return self._steiner_selection(candidates, target_count)
            elif strategy == "connectivity":
                return self._connectivity_selection(candidates, target_count)
            else:
                logger.warning(f"未知策略 {strategy}，使用 hybrid")
                return self._hybrid_selection(candidates, target_count)
        except Exception as e:
            logger.error(f"图优化失败: {e}，返回原始候选")
            # 降级：返回原始候选的前 target_count 个
            return candidates[:target_count]

    def _is_likely_single_table(
        self,
        candidates: List[Tuple[str, float]],
        query: str = None,
    ) -> bool:
        """
        判断是否可能是单表查询

        使用多信号融合判断:
        1. BGE top1-top2 gap: gap 大说明 top1 明显领先
        2. 子图边密度: 候选表之间边少说明不需要 JOIN
        3. 查询关键词: 是否包含多表暗示

        Args:
            candidates: BGE 检索结果
            query: 原始查询文本

        Returns:
            True 表示可能是单表查询，应跳过图优化
        """
        if len(candidates) < 2:
            return True

        # 信号 1: BGE top1-top2 gap
        top1_score = candidates[0][1]
        top2_score = candidates[1][1]
        gap_ratio = (top1_score - top2_score) / top1_score if top1_score > 0 else 0

        # 如果 top1 比 top2 高出 50% 以上，可能是单表
        if gap_ratio > 0.5:
            logger.debug(f"单表判别: gap_ratio={gap_ratio:.2f} > 0.5")
            return True

        # 信号 2: 查询关键词检测（多表暗示）
        # 注意：只使用真正表示"关联"的词，不使用实体名词
        # 因为"客户数量"是单表，但"客户的设备"是多表
        if query:
            multi_table_keywords = [
                "和", "以及", "关联", "连接", "join",
                "同时", "分别", "各个", "每个",
                # 已移除: "客户", "设备", "告警" - 这些实体词不能判断是否多表
            ]
            keyword_count = sum(1 for kw in multi_table_keywords if kw in query.lower())
            # 如果包含多个多表关键词，不太可能是单表
            if keyword_count >= 2:
                logger.debug(f"单表判别: 检测到 {keyword_count} 个多表关键词")
                return False

        # 信号 3: 子图边密度（需要查询 Neo4j）
        # 只在前面的信号不确定时使用
        try:
            table_names = [t for t, _ in candidates[:5]]  # 只看 top5
            relationships = self.client.get_table_relationships(table_names)
            edge_count = len(relationships)

            # 如果 top5 之间有 2 条以上的边，可能需要 JOIN
            if edge_count >= 2:
                logger.debug(f"单表判别: top5 之间有 {edge_count} 条边")
                return False
        except Exception as e:
            logger.debug(f"单表判别: 无法获取边信息 {e}")

        # 默认保守策略：不确定时使用图优化
        return False

    def _hybrid_selection(
        self,
        candidates: List[Tuple[str, float]],
        target_count: int,
    ) -> List[Tuple[str, float]]:
        """
        混合策略选择（Boost-Only 模式）

        核心原则：图分数只能加分，不能减分

        最终分数 = BGE原始分数 + boost_factor × 图特征加成

        图特征加成 = 0.15 × PPR + 0.10 × 连通性 + 0.05 × 度中心性
        boost_factor = BGE最高分 × 0.3（使加成有意义但不会翻盘）
        """
        table_names = [t for t, _ in candidates]
        bge_scores = {t: s for t, s in candidates}

        # 1. 构建子图（候选表 + 1-hop 邻居）
        graph = self._build_subgraph(table_names)

        if not graph.nodes:
            # 无图数据，返回原始排序（保留全部候选）
            return candidates

        # 2. 计算个性化 PageRank（用 BGE 分数加权播种）
        ppr_scores = personalized_pagerank(graph, table_names, seed_weights=bge_scores)

        # 3. 计算连通性分数
        # 改为取 BGE 前 10 高分表作为参考（而非 top5）
        top_tables = set(table_names[:min(10, len(table_names))])
        connectivity_scores = {
            t: compute_connectivity_score(graph, t, top_tables)
            for t in table_names
        }

        # 4. 获取全局度中心性（从缓存）
        degree_scores = {
            t: self.cache.get_global_degree(t)
            for t in table_names
        }

        # 5. 归一化图特征分数到 [0, 1]
        ppr_normalized = self._normalize_scores(ppr_scores)
        conn_normalized = self._normalize_scores(connectivity_scores)
        degree_normalized = self._normalize_scores(degree_scores)

        # 6. Boost-Only 计算：图分数只能加分，不能减分
        # boost_factor 基于 BGE 最高分，使加成有意义但不会翻盘
        max_bge = max(bge_scores.values()) if bge_scores else 1.0
        boost_factor = max_bge * 0.3  # 最多加 30% 的 BGE 最高分

        final_scores = {}
        for table in table_names:
            # 计算图特征加成（全部为正）
            graph_boost = (
                0.50 * ppr_normalized.get(table, 0)  # PPR 权重提高
                + 0.35 * conn_normalized.get(table, 0)  # 连通性
                + 0.15 * degree_normalized.get(table, 0)  # 度中心性
            )

            # 最终分数 = BGE原分 + boost（只加不减）
            final_scores[table] = bge_scores[table] + boost_factor * graph_boost

        # 7. 排序并返回（保留全部候选，不截断）
        sorted_tables = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # 关键修复：返回全部候选表，不做截断
        # 让调用方决定取多少
        result_count = len(sorted_tables)

        logger.info(
            f"Hybrid 优化 (Boost-Only): {len(candidates)} 表, "
            f"boost_factor={boost_factor:.4f}, "
            f"PPR 范围: [{min(ppr_scores.values()):.4f}, {max(ppr_scores.values()):.4f}]"
        )

        return sorted_tables

    def _local_hybrid_selection(
        self,
        candidates: List[Tuple[str, float]],
        target_count: int,
    ) -> List[Tuple[str, float]]:
        """
        局部子图混合策略（步骤5）

        核心思想：只看 top-N 候选表之间的关系，不做 1-hop 扩展
        - 减少噪声：不引入无关的邻居表
        - 提高信噪比：PPR 只在语义相关的小范围内传播

        回退策略：如果 top-N 之间边数不足，回退到纯 BGE 排序

        Args:
            candidates: BGE 检索结果 [(table_name, bge_score), ...]
            target_count: 目标返回数量

        Returns:
            优化后的表列表
        """
        table_names = [t for t, _ in candidates]
        bge_scores = {t: s for t, s in candidates}

        # 1. 构建局部子图（只看 top-N，不扩展邻居）
        top_n = min(LOCAL_PPR_TOPN, len(table_names))
        top_n_tables = table_names[:top_n]

        graph = self._build_local_subgraph(top_n_tables)

        # 2. 检查边数，判断是否需要回退
        edge_count = len(graph.edges)
        if edge_count < LOCAL_PPR_MIN_EDGES:
            logger.info(
                f"Local Hybrid: top-{top_n} 之间只有 {edge_count} 条边 "
                f"(< {LOCAL_PPR_MIN_EDGES})，回退到 {LOCAL_PPR_FALLBACK}"
            )
            if LOCAL_PPR_FALLBACK == "bge":
                # 回退到纯 BGE 排序
                return candidates
            else:
                # 回退到原 hybrid（带 1-hop 扩展）
                return self._hybrid_selection(candidates, target_count)

        # 3. 在局部子图上计算 PPR（用 BGE 分数加权播种）
        local_bge_scores = {t: bge_scores[t] for t in top_n_tables}
        ppr_scores = personalized_pagerank(graph, top_n_tables, seed_weights=local_bge_scores)

        # 4. 计算连通性分数（在局部子图内）
        top_tables = set(top_n_tables[:min(10, len(top_n_tables))])
        connectivity_scores = {
            t: compute_connectivity_score(graph, t, top_tables)
            for t in top_n_tables
        }

        # 5. 获取全局度中心性（从缓存）
        degree_scores = {
            t: self.cache.get_global_degree(t)
            for t in top_n_tables
        }

        # 6. 归一化
        ppr_normalized = self._normalize_scores(ppr_scores)
        conn_normalized = self._normalize_scores(connectivity_scores)
        degree_normalized = self._normalize_scores(degree_scores)

        # 7. Boost-Only 计算
        max_bge = max(bge_scores.values()) if bge_scores else 1.0
        boost_factor = max_bge * 0.3

        final_scores = {}
        for table in table_names:
            if table in top_n_tables:
                # top-N 内的表：使用图特征加成
                graph_boost = (
                    0.50 * ppr_normalized.get(table, 0)
                    + 0.35 * conn_normalized.get(table, 0)
                    + 0.15 * degree_normalized.get(table, 0)
                )
                final_scores[table] = bge_scores[table] + boost_factor * graph_boost
            else:
                # top-N 外的表：保留原始 BGE 分数
                final_scores[table] = bge_scores[table]

        # 8. 排序并返回
        sorted_tables = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        logger.info(
            f"Local Hybrid 优化: top-{top_n} 表, {edge_count} 条边, "
            f"boost_factor={boost_factor:.4f}, "
            f"PPR 范围: [{min(ppr_scores.values()):.4f}, {max(ppr_scores.values()):.4f}]"
        )

        return sorted_tables

    def _build_local_subgraph(
        self,
        table_names: List[str],
    ) -> TableGraph:
        """
        构建局部子图（不扩展邻居）

        与 _build_subgraph 的区别：
        - 不调用 get_connected_tables()
        - 只查询给定表之间的关系

        Args:
            table_names: 候选表名列表

        Returns:
            TableGraph 实例
        """
        # 直接查询给定表之间的关系，不扩展
        relationships = self.client.get_table_relationships(table_names)

        # 构建图
        graph = TableGraph.from_relationships(relationships)

        # 确保候选表都在图中（即使是孤立节点）
        for table in table_names:
            graph.add_node(table)

        return graph

    def _steiner_selection(
        self,
        candidates: List[Tuple[str, float]],
        target_count: int,
    ) -> List[Tuple[str, float]]:
        """
        Steiner 树策略

        找到连接所有高分候选表的最小连接子图
        """
        table_names = [t for t, _ in candidates]
        bge_scores = {t: s for t, s in candidates}

        # 1. 构建子图
        graph = self._build_subgraph(table_names)

        if not graph.nodes:
            return candidates[:target_count]

        # 2. 选择终端节点（BGE 前 N 高分表）
        terminal_count = min(5, len(table_names))
        terminals = table_names[:terminal_count]

        # 3. 找 Steiner 子图
        steiner_nodes = find_steiner_subgraph(
            graph,
            terminals,
            max_extra_nodes=target_count - terminal_count,
        )

        # 4. 为 Steiner 子图中的表评分
        # 终端节点保留 BGE 分数，中间节点用连通性分数
        final_scores = {}
        for table in steiner_nodes:
            if table in bge_scores:
                final_scores[table] = bge_scores[table]
            else:
                # 中间节点：用连通性评分
                conn_score = compute_connectivity_score(
                    graph, table, set(terminals)
                )
                final_scores[table] = conn_score * 0.5  # 降权

        # 5. 补充高 BGE 分数的表（如果 Steiner 子图太小）
        if len(final_scores) < target_count:
            for table, score in candidates:
                if table not in final_scores:
                    final_scores[table] = score
                if len(final_scores) >= target_count:
                    break

        sorted_tables = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        count = max(MIN_TABLES, min(target_count, len(sorted_tables)))

        logger.info(
            f"Steiner 优化: {len(candidates)} → {count} 表, "
            f"Steiner 子图: {len(steiner_nodes)} 节点"
        )

        return sorted_tables[:count]

    def _connectivity_selection(
        self,
        candidates: List[Tuple[str, float]],
        target_count: int,
    ) -> List[Tuple[str, float]]:
        """
        连通性策略

        优先保留最大连通分量中的表，移除孤立低分表
        """
        table_names = [t for t, _ in candidates]
        bge_scores = {t: s for t, s in candidates}

        # 1. 构建子图
        graph = self._build_subgraph(table_names)

        if not graph.nodes:
            return candidates[:target_count]

        # 2. 找连通分量
        components = find_connected_components(graph)

        if not components:
            return candidates[:target_count]

        # 3. 优先选择最大连通分量中的高分表
        largest_component = components[0]
        tables_in_largest = [
            t for t in table_names
            if t in largest_component
        ]

        # 4. 按 BGE 分数排序
        sorted_in_component = sorted(
            tables_in_largest,
            key=lambda t: bge_scores.get(t, 0),
            reverse=True,
        )

        # 5. 如果不够，补充其他表
        result = [(t, bge_scores[t]) for t in sorted_in_component]

        if len(result) < target_count:
            for table, score in candidates:
                if table not in set(t for t, _ in result):
                    result.append((table, score))
                if len(result) >= target_count:
                    break

        count = max(MIN_TABLES, min(target_count, len(result)))

        logger.info(
            f"Connectivity 优化: {len(candidates)} → {count} 表, "
            f"最大连通分量: {len(largest_component)} 节点"
        )

        return result[:count]

    def _build_subgraph(
        self,
        table_names: List[str],
    ) -> TableGraph:
        """
        构建候选表的子图（包含 1-hop 邻居）

        Args:
            table_names: 候选表名列表

        Returns:
            TableGraph 实例
        """
        # 获取候选表 + 邻居的关系
        expanded_tables = self.client.get_connected_tables(table_names)
        all_tables = list(expanded_tables.keys())

        # 获取关系
        relationships = self.client.get_table_relationships(all_tables)

        # 构建图
        graph = TableGraph.from_relationships(relationships)

        # 确保候选表都在图中（即使是孤立节点）
        for table in table_names:
            graph.add_node(table)

        return graph

    @staticmethod
    def _normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
        """
        Min-Max 归一化分数到 [0, 1]
        """
        if not scores:
            return {}

        values = list(scores.values())
        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return {k: 1.0 for k in scores}

        return {
            k: (v - min_val) / (max_val - min_val)
            for k, v in scores.items()
        }

    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
