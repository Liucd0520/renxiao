#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心检索器 - FastRetriever

使用预计算的 BGE-M3 Sparse Embedding 进行快速检索
"""

import os
import sys
import pickle
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

# 配置
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v2.pkl")


class FastRetriever:
    """
    快速检索器（使用预计算的 embedding）
    
    检索策略：
    - 表级别 + 列级别(核心表) 的 Sparse Embedding
    - 累加分聚合到表
    """
    
    def __init__(self, embeddings_file=EMBEDDINGS_FILE, model_path=MODEL_PATH):
        # 加载预计算的 embedding
        print("加载预计算 embedding...")
        with open(embeddings_file, 'rb') as f:
            data = pickle.load(f)
        
        self.schemas = data["schemas"]
        self.lexical_weights = data["lexical_weights"]
        
        # 加载模型（只用于 encode 查询）
        print("加载模型...")
        self.model = BGEM3FlagModel(model_path, use_fp16=True)
        
        # 统计
        table_count = sum(1 for s in self.schemas if s['type'] == 'table')
        column_count = sum(1 for s in self.schemas if s['type'] == 'column')
        print(f"就绪！表级别: {table_count}, 列级别: {column_count}, 共 {len(self.schemas)} 个 Schema")
    
    def retrieve(self, question, top_k=10):
        """
        融合检索：表 TOP-K ∪ 列 TOP-K（并集）
        
        返回: [(table_name, score), ...]，最多 2*top_k 张表
        """
        # 编码问题
        query_output = self.model.encode(
            [question],
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        query_sparse = query_output["lexical_weights"][0]
        
        # 表级别分数
        table_scores = {}
        for i, schema in enumerate(self.schemas):
            if schema['type'] == 'table':
                score = self.model.compute_lexical_matching_score(query_sparse, self.lexical_weights[i])
                table_scores[schema['table_name']] = float(score)
        
        # 列级别分数（累加分聚合到表）
        column_scores = defaultdict(float)
        for i, schema in enumerate(self.schemas):
            if schema['type'] == 'column':
                score = self.model.compute_lexical_matching_score(query_sparse, self.lexical_weights[i])
                column_scores[schema['table_name']] += float(score)
        
        # 表级别 TOP-K
        table_top = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        table_top_set = set(t for t, _ in table_top)
        
        # 列级别 TOP-K
        column_top = sorted(column_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        column_top_set = set(t for t, _ in column_top)
        
        # 并集
        union_set = table_top_set | column_top_set
        
        # 返回并集内的表，按 表分数+列分数 排序
        result = []
        for t in union_set:
            combined_score = table_scores.get(t, 0) + column_scores.get(t, 0)
            result.append((t, combined_score))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result
    
    def retrieve_table_only(self, question, top_k=10):
        """仅表级别检索"""
        query_output = self.model.encode(
            [question],
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        query_sparse = query_output["lexical_weights"][0]
        
        results = []
        for i, schema in enumerate(self.schemas):
            if schema['type'] == 'table':
                score = self.model.compute_lexical_matching_score(query_sparse, self.lexical_weights[i])
                results.append((schema['table_name'], float(score)))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def retrieve_column_only(self, question, top_k=10):
        """仅列级别检索（累加分聚合到表）"""
        query_output = self.model.encode(
            [question],
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        query_sparse = query_output["lexical_weights"][0]
        
        table_scores = defaultdict(float)
        for i, schema in enumerate(self.schemas):
            if schema['type'] == 'column':
                score = self.model.compute_lexical_matching_score(query_sparse, self.lexical_weights[i])
                table_scores[schema['table_name']] += float(score)
        
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_tables[:top_k]


# 测试
if __name__ == "__main__":
    print("测试 FastRetriever...")
    
    retriever = FastRetriever()
    
    test_question = "查询客户测试客户名下有多少设备"
    
    print(f"\n问题: {test_question}")
    
    print("\n融合检索结果:")
    for table, score in retriever.retrieve(test_question, top_k=5):
        print(f"  {table}: {score:.4f}")
    
    print("\n表级别检索结果:")
    for table, score in retriever.retrieve_table_only(test_question, top_k=5):
        print(f"  {table}: {score:.4f}")
    
    print("\n列级别检索结果:")
    for table, score in retriever.retrieve_column_only(test_question, top_k=5):
        print(f"  {table}: {score:.4f}")
