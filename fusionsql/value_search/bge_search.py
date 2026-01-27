#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE 值匹配模块 - 搜索

加载预构建的 BGE + FAISS 向量索引并进行语义相似度查询。
替代原有的 LSH 方案，接口保持兼容。
"""

import os
import pickle
import re
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import faiss
except ImportError:
    raise ImportError("请安装 faiss: pip install faiss-cpu")

from FlagEmbedding import BGEM3FlagModel

# 默认 BGE 模型路径
LOCAL_MODEL_PATH = "/Users/jason/Documents/实习/理想实习/LinkAlign/embed_model_cache/BAAI/bge-m3"
MODEL_NAME = LOCAL_MODEL_PATH if os.path.exists(LOCAL_MODEL_PATH) else "BAAI/bge-m3"


class BGEValueSearcher:
    """
    基于 BGE + FAISS 的值搜索器
    
    替代 LSH ValueSearcher，接口兼容。
    
    优势：
    - 语义匹配能力更强
    - 中文支持更好
    - 可共享已加载的 BGE 模型
    """
    
    def __init__(
        self,
        index_dir: str,
        model: Optional[BGEM3FlagModel] = None,
        model_name: str = MODEL_NAME
    ):
        """
        初始化搜索器
        
        Args:
            index_dir: 索引目录（包含 value_index.faiss 和 value_metadata.pkl）
            model: 可选，共享已加载的 BGE-M3 模型以节省内存
            model_name: 若 model 为 None，使用此模型
        """
        self.index_dir = Path(index_dir)
        
        self.index: Optional[faiss.Index] = None
        self.metadata: Optional[List[Tuple[str, str, str]]] = None  # [(table, column, value), ...]
        
        # 共享模型或加载新模型
        if model is not None:
            self.model = model
            self._model_shared = True
        else:
            logging.info(f"加载 BGE-M3 模型: {model_name}")
            self.model = BGEM3FlagModel(model_name, use_fp16=True)
            self._model_shared = False
        
        self._load_index()
    
    def _load_index(self) -> None:
        """加载预构建索引"""
        index_path = self.index_dir / "value_index.faiss"
        metadata_path = self.index_dir / "value_metadata.pkl"
        
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"索引文件不存在，请先运行 bge_preprocess.py: {self.index_dir}"
            )
        
        logging.info(f"加载 BGE 值索引: {self.index_dir}")
        
        self.index = faiss.read_index(str(index_path))
        
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
        
        logging.info(f"索引加载完成，包含 {len(self.metadata)} 个条目")
    
    def search(
        self,
        keyword: str,
        top_n: int = 10,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        搜索与关键词语义相似的值
        
        Args:
            keyword: 搜索关键词
            top_n: 返回结果数量
            min_similarity: 最小相似度阈值 (0-1，余弦相似度)
        
        Returns:
            匹配结果列表，每项包含 {table, column, value, similarity}
        """
        if self.index is None or self.metadata is None:
            raise RuntimeError("索引未加载")
        
        # 编码查询
        query_output = self.model.encode(
            [keyword],
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False
        )
        query_vec = np.array(query_output["dense_vecs"], dtype=np.float32)
        
        # 归一化
        faiss.normalize_L2(query_vec)
        
        # FAISS 检索
        distances, indices = self.index.search(query_vec, top_n)
        
        # 整理结果
        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx >= 0 and score >= min_similarity:  # idx=-1 表示不足 top_n
                table, column, value = self.metadata[idx]
                results.append({
                    "table": table,
                    "column": column,
                    "value": value,
                    "similarity": float(score)
                })
        
        return results
    
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
            
            if value not in grouped[table][column]:
                grouped[table][column].append(value)
        
        return grouped
    
    def find_entity_values(
        self,
        question: str,
        top_n_per_word: int = 3,
        min_word_length: int = 2,
        min_similarity: float = 0.5,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        从问题中提取实体并匹配数据库值 (Entity Linking)
        
        接口与 LSH ValueSearcher.find_entity_values 完全兼容
        
        Args:
            question: 用户问题
            top_n_per_word: 每个词返回的结果数
            min_word_length: 最小词长度
            min_similarity: 最小相似度（BGE 推荐 0.5-0.7）
            keywords: 可选，外部传入的关键词列表（如 LLM 提取的）
        
        Returns:
            {table: {column: [values]}} 格式的匹配结果
        """
        # 提取关键词（或使用外部传入的）
        if keywords is None:
            # 提取英文/数字和中文词
            # 英文/数字
            english_tokens = re.findall(r'[a-zA-Z0-9]+', question)
            # 中文词（简单按连续中文字符分割，每 2-4 字为一词）
            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', question)
            chinese_tokens = []
            for chars in chinese_chars:
                # 简单的 2-gram 分词
                if len(chars) >= 2:
                    for i in range(len(chars) - 1):
                        chinese_tokens.append(chars[i:i+2])
            
            words = [w for w in english_tokens if len(w) >= min_word_length]
            words.extend(chinese_tokens)
        else:
            words = keywords
        
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


def load_bge_searcher(
    index_dir: str,
    model: Optional[BGEM3FlagModel] = None
) -> BGEValueSearcher:
    """
    便捷函数：加载 BGE 搜索器
    
    Args:
        index_dir: 索引目录
        model: 可选，共享的 BGE 模型
    
    Returns:
        BGEValueSearcher 实例
    """
    return BGEValueSearcher(index_dir, model=model)


if __name__ == "__main__":
    # 测试
    import sys
    
    index_dir = sys.argv[1] if len(sys.argv) > 1 else "./bge_value_index"
    
    print(f"测试 BGEValueSearcher: {index_dir}")
    
    searcher = BGEValueSearcher(index_dir)
    
    test_keywords = ["cisco", "down", "测试客户"]
    
    for kw in test_keywords:
        print(f"\n搜索: {kw}")
        results = searcher.search(kw, top_n=5, min_similarity=0.3)
        for r in results:
            print(f"  {r['table']}.{r['column']} = '{r['value']}' (sim={r['similarity']:.3f})")
