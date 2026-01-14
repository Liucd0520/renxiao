#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSH 值匹配模块 - 搜索

加载预计算的 LSH 索引并进行相似度查询。
"""

import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

try:
    from datasketch import MinHash, MinHashLSH
except ImportError:
    raise ImportError("请安装 datasketch: pip install datasketch")

from .preprocess import _create_minhash


class ValueSearcher:
    """
    基于 LSH 的值搜索器
    
    使用预计算的 MinHash LSH 索引进行相似度查询。
    """
    
    def __init__(
        self,
        index_dir: str,
        signature_size: int = 100,
        n_gram: int = 3
    ):
        """
        初始化搜索器
        
        Args:
            index_dir: 索引目录路径（包含 lsh.pkl 和 minhashes.pkl）
            signature_size: MinHash 签名大小（需与预处理时一致）
            n_gram: n-gram 大小（需与预处理时一致）
        """
        self.index_dir = Path(index_dir)
        self.signature_size = signature_size
        self.n_gram = n_gram
        
        self.lsh: Optional[MinHashLSH] = None
        self.minhashes: Optional[Dict[str, Tuple[MinHash, str, str, str]]] = None
        
        self._load_index()
    
    def _load_index(self) -> None:
        """加载预计算索引"""
        lsh_path = self.index_dir / "lsh.pkl"
        minhashes_path = self.index_dir / "minhashes.pkl"
        
        if not lsh_path.exists() or not minhashes_path.exists():
            raise FileNotFoundError(
                f"索引文件不存在，请先运行预处理: {self.index_dir}"
            )
        
        logging.info(f"加载 LSH 索引: {self.index_dir}")
        
        with open(lsh_path, "rb") as f:
            self.lsh = pickle.load(f)
        
        with open(minhashes_path, "rb") as f:
            self.minhashes = pickle.load(f)
        
        logging.info(f"索引加载完成，包含 {len(self.minhashes)} 个条目")
    
    def _jaccard_similarity(self, m1: MinHash, m2: MinHash) -> float:
        """计算两个 MinHash 的 Jaccard 相似度"""
        return m1.jaccard(m2)
    
    def search(
        self,
        keyword: str,
        top_n: int = 10,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        搜索与关键词相似的值
        
        Args:
            keyword: 搜索关键词
            top_n: 返回结果数量
            min_similarity: 最小相似度阈值
        
        Returns:
            匹配结果列表，每项包含 {table, column, value, similarity}
        """
        if self.lsh is None or self.minhashes is None:
            raise RuntimeError("索引未加载")
        
        # 创建查询的 MinHash
        query_minhash = _create_minhash(self.signature_size, keyword, self.n_gram)
        
        # LSH 查询
        results = self.lsh.query(query_minhash)
        
        # 计算精确相似度并排序
        similarities = []
        for result in results:
            if result in self.minhashes:
                minhash, table, column, value = self.minhashes[result]
                sim = self._jaccard_similarity(query_minhash, minhash)
                if sim >= min_similarity:
                    similarities.append({
                        "table": table,
                        "column": column,
                        "value": value,
                        "similarity": sim
                    })
        
        # 按相似度排序
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similarities[:top_n]
    
    def search_grouped(
        self,
        keyword: str,
        top_n: int = 10,
        min_similarity: float = 0.0
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        搜索并按表/列分组返回
        
        Args:
            keyword: 搜索关键词
            top_n: 返回结果数量
            min_similarity: 最小相似度阈值
        
        Returns:
            {table: {column: [values]}} 格式的字典
        """
        results = self.search(keyword, top_n, min_similarity)
        
        grouped: Dict[str, Dict[str, List[str]]] = {}
        for r in results:
            table = r["table"]
            column = r["column"]
            value = r["value"]
            
            if table not in grouped:
                grouped[table] = {}
            if column not in grouped[table]:
                grouped[table][column] = []
            
            grouped[table][column].append(value)
        
        return grouped
    
    def find_entity_values(
        self,
        question: str,
        top_n_per_word: int = 3,
        min_word_length: int = 2,
        min_similarity: float = 0.3
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        从问题中提取实体并匹配数据库值
        
        简单实现：对问题中的每个词进行搜索
        
        Args:
            question: 用户问题
            top_n_per_word: 每个词返回的结果数
            min_word_length: 最小词长度
            min_similarity: 最小相似度
        
        Returns:
            {table: {column: [values]}} 格式的匹配结果
        """
        # 改进的分词：分离中文和英文/数字
        import re
        
        # 先用正则分离中文和英文/数字
        # 例如 "设备ciscoA上个月" -> ["设备", "ciscoA", "上个月"]
        tokens = re.findall(r'[a-zA-Z0-9]+|[\u4e00-\u9fff]+', question)
        
        # 尝试使用 jieba 对中文进行分词
        words = []
        try:
            import jieba
            for token in tokens:
                if re.match(r'^[\u4e00-\u9fff]+$', token):
                    # 中文用 jieba 分词
                    words.extend(jieba.lcut(token))
                else:
                    # 英文/数字保持原样
                    words.append(token)
        except ImportError:
            # 没有 jieba 就用原始 token
            words = tokens
        
        words = [w for w in words if len(w) >= min_word_length]
        
        all_results: Dict[str, Dict[str, List[str]]] = {}
        
        for word in words:
            results = self.search_grouped(word, top_n_per_word, min_similarity)
            
            for table, columns in results.items():
                if table not in all_results:
                    all_results[table] = {}
                for column, values in columns.items():
                    if column not in all_results[table]:
                        all_results[table][column] = []
                    for v in values:
                        if v not in all_results[table][column]:
                            all_results[table][column].append(v)
        
        return all_results


def load_searcher(index_dir: str) -> ValueSearcher:
    """
    便捷函数：加载搜索器
    
    Args:
        index_dir: 索引目录
    
    Returns:
        ValueSearcher 实例
    """
    return ValueSearcher(index_dir)
