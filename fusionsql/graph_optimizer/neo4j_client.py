"""
Neo4j 客户端封装

提供表间关系查询功能
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from contextlib import contextmanager

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logging.warning("neo4j 包未安装，请运行: pip install neo4j")

from .config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    RELATION_WEIGHTS,
    SUBGRAPH_HOPS,
    MOSTLYIS_MIN_SIM,
    MOSTLYIS_TOP_K,
    MOSTLYIS_SPARSE_ENABLED,
    WEAK_SIGNAL_WORDS,
)

logger = logging.getLogger(__name__)


def compute_column_similarity(col1: str, col2: str) -> float:
    """
    计算两个列名的相似度

    使用词法相似度: Jaccard(tokens) + SequenceMatcher

    Args:
        col1: 列名1
        col2: 列名2

    Returns:
        相似度 [0, 1]
    """
    import re
    from difflib import SequenceMatcher

    def tokenize(name: str) -> set:
        """分词并规范化"""
        # 转小写，分割 snake_case 和 camelCase
        name = name.lower()
        # 替换非字母数字为空格
        name = re.sub(r'[^a-z0-9]', ' ', name)
        # 分词
        tokens = set(name.split())
        # 过滤弱信号词
        tokens = tokens - WEAK_SIGNAL_WORDS
        return tokens

    # 如果列名完全相同，返回 1.0
    if col1.lower() == col2.lower():
        return 1.0

    # 分词
    tokens1 = tokenize(col1)
    tokens2 = tokenize(col2)

    # Jaccard 相似度
    if tokens1 and tokens2:
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        jaccard = intersection / union if union > 0 else 0
    else:
        jaccard = 0

    # SequenceMatcher 相似度
    seq_ratio = SequenceMatcher(None, col1.lower(), col2.lower()).ratio()

    # 组合: 0.7 * jaccard + 0.3 * seq_ratio
    similarity = 0.7 * jaccard + 0.3 * seq_ratio

    return min(similarity, 1.0)


class Neo4jClient:
    """
    Neo4j 数据库客户端

    封装表关系查询，支持：
    - 获取表间关系（IS/MOSTLYIS）
    - BFS 扩展邻居表
    - 获取表度信息
    """

    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None,
    ):
        """
        初始化 Neo4j 连接

        Args:
            uri: Neo4j 连接地址
            user: 用户名
            password: 密码
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j 包未安装，请运行: pip install neo4j")

        self.uri = uri or NEO4J_URI
        self.user = user or NEO4J_USER
        self.password = password or NEO4J_PASSWORD

        self._driver = None

    @property
    def driver(self):
        """延迟初始化驱动"""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
        return self._driver

    def close(self):
        """关闭连接"""
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    @contextmanager
    def session(self):
        """获取会话上下文管理器"""
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

    def get_all_tables(self) -> List[str]:
        """
        获取所有表名

        Returns:
            表名列表
        """
        query = """
        MATCH (t:Table)
        RETURN t.name AS table_name
        """

        with self.session() as session:
            result = session.run(query)
            return [record["table_name"] for record in result]

    def get_table_relationships(
        self,
        table_names: List[str] = None,
        sparse_mostlyis: bool = None,
    ) -> List[Tuple[str, str, str, float]]:
        """
        获取表间关系

        Args:
            table_names: 限定的表名列表（None 表示获取所有）
            sparse_mostlyis: 是否对 MOSTLYIS 进行稀疏化（默认使用配置）

        Returns:
            [(source_table, target_table, relation_type, weight), ...]
        """
        if sparse_mostlyis is None:
            sparse_mostlyis = MOSTLYIS_SPARSE_ENABLED

        # 注意：外键关系 IS/MOSTLYIS 存储在 Column 节点之间
        # 需要通过 Column 来推导 Table 之间的关系
        if table_names:
            # 只获取指定表之间的关系，同时返回列名用于相似度计算
            query = """
            MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
            WHERE t1.name IN $tables AND t2.name IN $tables AND t1 <> t2
            RETURN DISTINCT t1.name AS source, t2.name AS target, type(r) AS rel_type,
                   c1.name AS col1, c2.name AS col2
            """
            params = {"tables": table_names}
        else:
            # 获取所有关系
            query = """
            MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
            WHERE t1 <> t2
            RETURN DISTINCT t1.name AS source, t2.name AS target, type(r) AS rel_type,
                   c1.name AS col1, c2.name AS col2
            """
            params = {}

        relationships = []
        mostlyis_candidates = []  # 用于稀疏化处理

        with self.session() as session:
            result = session.run(query, params)
            for record in result:
                source = record["source"]
                target = record["target"]
                rel_type = record["rel_type"]
                col1 = record["col1"]
                col2 = record["col2"]

                if rel_type == "IS":
                    # IS 边直接保留
                    weight = RELATION_WEIGHTS.get(rel_type, 1.0)
                    relationships.append((source, target, rel_type, weight))
                else:
                    # MOSTLYIS 边需要稀疏化处理
                    if sparse_mostlyis:
                        # 计算列名相似度
                        sim = compute_column_similarity(col1, col2)
                        if sim >= MOSTLYIS_MIN_SIM:
                            # 动态权重 = 基础权重 × 相似度
                            weight = RELATION_WEIGHTS.get(rel_type, 0.2) * sim
                            mostlyis_candidates.append((source, target, rel_type, weight, col1, sim))
                    else:
                        weight = RELATION_WEIGHTS.get(rel_type, 0.2)
                        relationships.append((source, target, rel_type, weight))

        # 对 MOSTLYIS 应用 top-k 过滤
        if sparse_mostlyis and mostlyis_candidates:
            # 按 (source, col1) 分组，每组只保留 top-k
            from collections import defaultdict
            grouped = defaultdict(list)
            for item in mostlyis_candidates:
                source, target, rel_type, weight, col1, sim = item
                grouped[(source, col1)].append((target, rel_type, weight, sim))

            for (source, col1), candidates in grouped.items():
                # 按相似度排序，取 top-k
                candidates.sort(key=lambda x: x[3], reverse=True)
                for target, rel_type, weight, sim in candidates[:MOSTLYIS_TOP_K]:
                    relationships.append((source, target, rel_type, weight))

        logger.debug(f"获取表关系: IS={sum(1 for r in relationships if r[2]=='IS')}, "
                    f"MOSTLYIS={sum(1 for r in relationships if r[2]=='MOSTLYIS')}")

        return relationships

    def get_connected_tables(
        self,
        seed_tables: List[str],
        hops: int = None,
    ) -> Dict[str, int]:
        """
        BFS 扩展获取邻居表

        Args:
            seed_tables: 种子表列表
            hops: 扩展跳数（默认使用配置值）

        Returns:
            {table_name: distance_from_seed, ...}
        """
        if hops is None:
            hops = SUBGRAPH_HOPS

        # 注意：外键关系在 Column 之间，需要通过 Column 扩展邻居
        # 简化查询：直接通过 Column 连接找到相邻的 Table
        query = """
        MATCH (seed:Table)-[:COLUMN]-(c1:Column)-[:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(neighbor:Table)
        WHERE seed.name IN $seeds AND seed <> neighbor
        RETURN DISTINCT neighbor.name AS table_name
        """

        # 对于多跳的情况，递归查询（hops > 1 时需要更复杂的查询）
        # 目前先支持 1-hop，后续可以扩展
        if hops > 1:
            # 多跳查询：通过多次 Column 连接
            query = f"""
            MATCH path = (seed:Table)(-[:COLUMN]-(:Column)-[:IS|MOSTLYIS]-(:Column)-[:COLUMN]-(:Table)){{{1},{hops}}}
            WHERE seed.name IN $seeds
            WITH seed, last(nodes(path)) AS neighbor
            WHERE seed <> neighbor AND neighbor:Table
            RETURN DISTINCT neighbor.name AS table_name
            """
        
        # 备用查询（简化版，只支持 1-hop）
        fallback_query = """
        MATCH (seed:Table)-[:COLUMN]-(c1:Column)-[:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(neighbor:Table)
        WHERE seed.name IN $seeds AND seed <> neighbor
        RETURN DISTINCT neighbor.name AS table_name
        """

        with self.session() as session:
            try:
                result = session.run(query, {"seeds": seed_tables, "hops": hops})
                tables = {record["table_name"]: 0 for record in result}
            except Exception:
                # APOC 不可用，使用备用查询
                result = session.run(fallback_query, {"seeds": seed_tables})
                tables = {record["table_name"]: 0 for record in result}

        return tables

    def get_table_degrees(
        self,
        table_names: List[str] = None,
    ) -> Dict[str, Dict[str, int]]:
        """
        获取表的度信息

        Args:
            table_names: 限定的表名列表（None 表示获取所有）

        Returns:
            {table_name: {"total": N, "is": N, "mostlyis": N}, ...}
        """
        # 注意：外键关系在 Column 之间，度 = 通过外键连接的其他 Table 数量
        if table_names:
            query = """
            MATCH (t:Table)
            WHERE t.name IN $tables
            OPTIONAL MATCH (t)-[:COLUMN]-(c1:Column)-[r1:IS]-(c2:Column)-[:COLUMN]-(other1:Table)
            WHERE t <> other1
            WITH t, count(DISTINCT other1) AS is_count
            OPTIONAL MATCH (t)-[:COLUMN]-(c3:Column)-[r2:MOSTLYIS]-(c4:Column)-[:COLUMN]-(other2:Table)
            WHERE t <> other2
            WITH t.name AS name, is_count, count(DISTINCT other2) AS mostlyis_count
            RETURN name, is_count, mostlyis_count
            """
            params = {"tables": table_names}
        else:
            query = """
            MATCH (t:Table)
            OPTIONAL MATCH (t)-[:COLUMN]-(c1:Column)-[r1:IS]-(c2:Column)-[:COLUMN]-(other1:Table)
            WHERE t <> other1
            WITH t, count(DISTINCT other1) AS is_count
            OPTIONAL MATCH (t)-[:COLUMN]-(c3:Column)-[r2:MOSTLYIS]-(c4:Column)-[:COLUMN]-(other2:Table)
            WHERE t <> other2
            WITH t.name AS name, is_count, count(DISTINCT other2) AS mostlyis_count
            RETURN name, is_count, mostlyis_count
            """
            params = {}

        degrees = {}
        with self.session() as session:
            result = session.run(query, params)
            for record in result:
                name = record["name"]
                is_count = record["is_count"]
                mostlyis_count = record["mostlyis_count"]
                degrees[name] = {
                    "total": is_count + mostlyis_count,
                    "is": is_count,
                    "mostlyis": mostlyis_count,
                }

        return degrees

    def get_shortest_path_length(
        self,
        table1: str,
        table2: str,
    ) -> Optional[int]:
        """
        获取两表之间的最短路径长度

        Args:
            table1: 表1名称
            table2: 表2名称

        Returns:
            路径长度（无路径返回 None）
        """
        # 注意：外键关系在 Column 之间，路径需要通过 Column 节点
        # 计算 Table 之间的最短路径（以 Table 为单位计算跳数）
        query = """
        MATCH path = shortestPath(
            (t1:Table {name: $table1})-[:COLUMN|IS|MOSTLYIS*]-(t2:Table {name: $table2})
        )
        WITH path, [n IN nodes(path) WHERE n:Table] AS table_nodes
        RETURN size(table_nodes) - 1 AS path_length
        """

        with self.session() as session:
            result = session.run(query, {"table1": table1, "table2": table2})
            record = result.single()
            if record:
                return record["path_length"]
            return None

    def verify_connection(self) -> bool:
        """验证 Neo4j 连接"""
        try:
            with self.session() as session:
                result = session.run("RETURN 1 AS test")
                record = result.single()
                return record["test"] == 1
        except Exception as e:
            logger.error(f"Neo4j 连接验证失败: {e}")
            return False

    def get_graph_stats(self) -> Dict:
        """
        获取图统计信息

        Returns:
            {"tables": N, "is_relations": N, "mostlyis_relations": N}
        """
        query = """
        MATCH (t:Table)
        WITH count(t) AS table_count
        MATCH ()-[r1:IS]-()
        WITH table_count, count(r1)/2 AS is_count
        MATCH ()-[r2:MOSTLYIS]-()
        RETURN table_count, is_count, count(r2)/2 AS mostlyis_count
        """

        with self.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {
                    "tables": record["table_count"],
                    "is_relations": record["is_count"],
                    "mostlyis_relations": record["mostlyis_count"],
                }
            return {"tables": 0, "is_relations": 0, "mostlyis_relations": 0}
