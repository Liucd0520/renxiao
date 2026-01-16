#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心检索器 - FastRetriever

使用预计算的 BGE-M3 Sparse Embedding 进行快速检索
"""

import os
import pickle
from collections import defaultdict

from FlagEmbedding import BGEM3FlagModel

# 配置
# BGE-M3 模型：优先使用本地缓存
LOCAL_MODEL_PATH = "/Users/jason/Documents/实习/理想实习/LinkAlign/embed_model_cache/BAAI/bge-m3"
MODEL_NAME = LOCAL_MODEL_PATH if os.path.exists(LOCAL_MODEL_PATH) else "BAAI/bge-m3"
# 默认 embedding 文件：fusionsql 包内的 schema_embeddings_v3.pkl
EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "schema_embeddings_v3.pkl")


class FastRetriever:
    """
    快速检索器（使用预计算的 embedding）
    
    检索策略：
    - 表级别 + 列级别(核心表) 的 Sparse Embedding
    - 累加分聚合到表
    """
    
    def __init__(self, embeddings_file=EMBEDDINGS_FILE, model_name=MODEL_NAME):
        # 加载预计算的 embedding
        print("加载预计算 embedding...")
        with open(embeddings_file, 'rb') as f:
            data = pickle.load(f)
        
        self.schemas = data["schemas"]
        self.lexical_weights = data["lexical_weights"]
        
        # 加载模型（只用于 encode 查询，首次运行自动从 HuggingFace 下载）
        print(f"加载 BGE-M3 模型: {model_name}")
        self.model = BGEM3FlagModel(model_name, use_fp16=True)
        
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
    
    def retrieve_with_lsh(self, question, top_k=10, lsh_searcher=None, 
                          lsh_min_similarity=0.5, lsh_max_tables=5):
        """
        三路融合检索：表 TOP-K ∪ 列 TOP-K ∪ LSH 值匹配表
        
        LSH 值匹配的作用：
        - 从问题中提取实体（如 "ciscoA"）
        - 在数据库所有值中寻找相似匹配（如 vendor.VENDOR_NAME='cisco'）
        - 将匹配到的值所在的表加入检索结果
        
        防止 LSH 返回过多表的策略：
        1. min_similarity=0.5：只保留相似度 ≥50% 的匹配（过滤低质量匹配）
        2. max_tables=5：最多只从 LSH 添加 5 张表（限制噪音）
        3. 只统计不同表的数量，不重复计数
        
        Args:
            question: 用户问题
            top_k: BGE-M3 检索返回的表数
            lsh_searcher: ValueSearcher 实例（可选）
            lsh_min_similarity: LSH 最小相似度阈值（默认 0.5，较高）
            lsh_max_tables: LSH 最多贡献的表数（默认 5）
        
        Returns:
            [(table_name, score), ...]，最多 2*top_k + lsh_max_tables 张表
        """
        # 1. 表级别检索（BGE-M3）
        table_top = self.retrieve_table_only(question, top_k)
        table_top_set = set(t for t, _ in table_top)
        table_scores = {t: s for t, s in table_top}
        
        # 2. 列级别检索（BGE-M3）
        column_top = self.retrieve_column_only(question, top_k)
        column_top_set = set(t for t, _ in column_top)
        column_scores = {t: s for t, s in column_top}
        
        # 3. LSH 值匹配检索（新增第三路）
        lsh_tables = set()
        lsh_details = {}  # 记录 LSH 匹配详情，用于调试
        
        if lsh_searcher:
            try:
                # find_entity_values 返回 {table: {column: [values]}}
                matched = lsh_searcher.find_entity_values(
                    question,
                    top_n_per_word=3,           # 每个词最多匹配 3 个值
                    min_word_length=2,          # 忽略太短的词
                    min_similarity=lsh_min_similarity  # 关键：高阈值过滤
                )
                
                # 统计每个表被匹配到的次数和详情
                table_match_count = defaultdict(int)
                for table, columns in matched.items():
                    for column, values in columns.items():
                        table_match_count[table] += len(values)
                        if table not in lsh_details:
                            lsh_details[table] = []
                        lsh_details[table].append(f"{column}={values[:2]}")  # 只记录前2个值
                
                # 按匹配次数排序，只取 top N 张表
                sorted_tables = sorted(table_match_count.items(), 
                                       key=lambda x: x[1], reverse=True)
                lsh_tables = set(t for t, _ in sorted_tables[:lsh_max_tables])
                
                if lsh_tables:
                    print(f"[LSH] 匹配到 {len(lsh_tables)} 张表: {list(lsh_tables)[:5]}")
                    for t in list(lsh_tables)[:3]:  # 只打印前3张表的详情
                        print(f"  - {t}: {lsh_details.get(t, [])[:2]}")
                        
            except Exception as e:
                print(f"[LSH] 搜索失败: {e}")
        
        # 4. 三路并集融合
        union_set = table_top_set | column_top_set | lsh_tables
        
        # 5. 计算综合分数
        # BGE-M3 的表有分数，LSH 匹配的表给一个固定较低分数（作为补充，不抢占排名）
        LSH_BASE_SCORE = 0.1  # LSH 匹配的表基础分
        
        result = []
        for t in union_set:
            combined_score = table_scores.get(t, 0) + column_scores.get(t, 0)
            if t in lsh_tables and combined_score == 0:
                # 纯 LSH 匹配的表，给基础分
                combined_score = LSH_BASE_SCORE
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
