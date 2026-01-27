"""
图缓存模块

离线预计算全局图指标（度中心性、PageRank），避免在线计算开销
"""

import os
import pickle
import logging
from typing import Dict, Optional
from datetime import datetime

from .config import CACHE_DIR, CACHE_FILE

logger = logging.getLogger(__name__)


class GraphCache:
    """
    图指标缓存

    预计算并缓存：
    - 全局度中心性
    - 全局 PageRank
    - 表统计信息
    """

    def __init__(self, cache_dir: str = None):
        """
        初始化缓存

        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_path = os.path.join(self.cache_dir, CACHE_FILE)

        self._cache: Optional[Dict] = None
        self._loaded = False

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    @property
    def cache(self) -> Dict:
        """延迟加载缓存"""
        if not self._loaded:
            self.load_cache()
        return self._cache or {}

    def load_cache(self) -> bool:
        """
        加载缓存文件

        Returns:
            是否成功加载
        """
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "rb") as f:
                    self._cache = pickle.load(f)
                self._loaded = True
                logger.info(f"图缓存加载成功: {self.cache_path}")
                return True
            except Exception as e:
                logger.warning(f"图缓存加载失败: {e}")
                self._cache = {}
                self._loaded = True
                return False
        else:
            logger.info("图缓存文件不存在，将使用空缓存")
            self._cache = {}
            self._loaded = True
            return False

    def save_cache(self, data: Dict) -> bool:
        """
        保存缓存文件

        Args:
            data: 缓存数据

        Returns:
            是否成功保存
        """
        self._ensure_cache_dir()
        try:
            # 添加元数据
            data["_metadata"] = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            with open(self.cache_path, "wb") as f:
                pickle.dump(data, f)

            self._cache = data
            self._loaded = True
            logger.info(f"图缓存保存成功: {self.cache_path}")
            return True
        except Exception as e:
            logger.error(f"图缓存保存失败: {e}")
            return False

    def get_global_degree(self, table_name: str) -> float:
        """
        获取表的全局度中心性（归一化）

        Args:
            table_name: 表名

        Returns:
            归一化度中心性 [0, 1]
        """
        degrees = self.cache.get("global_degrees", {})
        return degrees.get(table_name, 0.0)

    def get_global_pagerank(self, table_name: str) -> float:
        """
        获取表的全局 PageRank 值

        Args:
            table_name: 表名

        Returns:
            PageRank 值
        """
        pageranks = self.cache.get("global_pagerank", {})
        return pageranks.get(table_name, 0.0)

    def get_table_count(self) -> int:
        """获取缓存的表数量"""
        return len(self.cache.get("global_degrees", {}))

    def is_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self._loaded:
            self.load_cache()
        return bool(self._cache) and "global_degrees" in self._cache

    def precompute_global_metrics(self, neo4j_client) -> Dict:
        """
        预计算全局图指标

        Args:
            neo4j_client: Neo4j 客户端实例

        Returns:
            计算结果字典
        """
        from .algorithms import compute_pagerank

        logger.info("开始预计算全局图指标...")

        # 1. 获取所有表
        all_tables = neo4j_client.get_all_tables()
        logger.info(f"共 {len(all_tables)} 张表")

        # 2. 获取所有关系
        relationships = neo4j_client.get_table_relationships()
        logger.info(f"共 {len(relationships)} 条关系")

        # 3. 获取度信息
        degrees_info = neo4j_client.get_table_degrees()

        # 4. 计算归一化度中心性
        max_degree = max(
            (d["total"] for d in degrees_info.values()),
            default=1
        )
        global_degrees = {
            table: info["total"] / max_degree
            for table, info in degrees_info.items()
        }

        # 5. 计算全局 PageRank
        # 构建邻接表
        adjacency = {}
        for source, target, rel_type, weight in relationships:
            if source not in adjacency:
                adjacency[source] = []
            if target not in adjacency:
                adjacency[target] = []
            adjacency[source].append((target, weight))
            adjacency[target].append((source, weight))

        global_pagerank = compute_pagerank(
            nodes=all_tables,
            adjacency=adjacency,
        )

        # 6. 构建缓存数据
        cache_data = {
            "global_degrees": global_degrees,
            "global_pagerank": global_pagerank,
            "table_count": len(all_tables),
            "relation_count": len(relationships),
            "degrees_raw": degrees_info,
        }

        # 7. 保存缓存
        self.save_cache(cache_data)

        logger.info(
            f"预计算完成: {len(all_tables)} 表, "
            f"{len(relationships)} 关系"
        )

        return cache_data
