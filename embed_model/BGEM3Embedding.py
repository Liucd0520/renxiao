"""
BGE-M3 嵌入模型适配器

将 FlagEmbedding 的 BGEM3FlagModel 适配为 llama_index 可用的嵌入模型。
BGE-M3 支持多语言（100+语言）、长文本（8192 tokens）、多功能检索（dense, sparse, colbert）。

混合搜索模式：Dense + Sparse 向量融合
"""

from typing import Any, List, Optional, Dict
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.bridge.pydantic import Field, PrivateAttr
import numpy as np


class BGEM3Embedding(BaseEmbedding):
    """BGE-M3 多语言嵌入模型适配器
    
    支持模式:
    - dense: 只使用稠密向量（默认）
    - hybrid: 混合模式，Dense + Sparse 融合
    """
    
    # 默认使用本地下载的模型
    model_name: str = Field(default="./embed_model_cache/BAAI/bge-m3", description="模型名称或路径")
    use_fp16: bool = Field(default=True, description="是否使用 FP16 加速")
    max_length: int = Field(default=8192, description="最大输入长度")
    batch_size: int = Field(default=12, description="批处理大小")
    
    # 混合搜索配置
    use_hybrid: bool = Field(default=False, description="是否使用混合搜索")
    dense_weight: float = Field(default=0.7, description="Dense 向量权重（hybrid 模式）")
    sparse_weight: float = Field(default=0.3, description="Sparse 向量权重（hybrid 模式）")
    
    _model: Any = PrivateAttr()
    _initialized: bool = PrivateAttr(default=False)
    _sparse_embeddings_cache: Dict[str, Dict] = PrivateAttr(default_factory=dict)
    
    def __init__(
        self,
        model_name: str = "./embed_model_cache/BAAI/bge-m3",
        use_fp16: bool = True,
        max_length: int = 8192,
        batch_size: int = 12,
        use_hybrid: bool = False,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            use_fp16=use_fp16,
            max_length=max_length,
            batch_size=batch_size,
            use_hybrid=use_hybrid,
            dense_weight=dense_weight,
            sparse_weight=sparse_weight,
            **kwargs
        )
        self._model = None
        self._initialized = False
        self._sparse_embeddings_cache = {}
    
    def _lazy_init(self):
        """延迟初始化模型（第一次使用时加载）"""
        if self._initialized:
            return
        
        try:
            from FlagEmbedding import BGEM3FlagModel
            mode_str = "混合模式" if self.use_hybrid else "Dense模式"
            print(f"加载 BGE-M3 模型 ({mode_str}): {self.model_name}...")
            self._model = BGEM3FlagModel(
                self.model_name,
                use_fp16=self.use_fp16
            )
            self._initialized = True
            print(f"✅ BGE-M3 模型加载完成 ({mode_str})")
        except ImportError:
            raise ImportError(
                "请安装 FlagEmbedding: pip install FlagEmbedding"
            )
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """获取查询的嵌入向量"""
        self._lazy_init()
        
        if self.use_hybrid:
            # 混合模式：返回 Dense 向量，但同时计算 Sparse 供后续使用
            output = self._model.encode(
                [query],
                batch_size=1,
                max_length=self.max_length,
                return_dense=True,
                return_sparse=True
            )
            # 缓存 sparse embedding 供检索时使用
            self._sparse_embeddings_cache[query] = output['lexical_weights'][0]
        else:
            output = self._model.encode(
                [query],
                batch_size=1,
                max_length=self.max_length
            )
        
        # 返回 dense embedding
        embedding = output['dense_vecs'][0]
        
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        
        return embedding
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """获取文本的嵌入向量"""
        return self._get_query_embedding(text)
    
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量获取文本的嵌入向量"""
        self._lazy_init()
        
        if self.use_hybrid:
            output = self._model.encode(
                texts,
                batch_size=self.batch_size,
                max_length=self.max_length,
                return_dense=True,
                return_sparse=True
            )
            # 缓存 sparse embeddings
            for i, text in enumerate(texts):
                self._sparse_embeddings_cache[text] = output['lexical_weights'][i]
        else:
            output = self._model.encode(
                texts,
                batch_size=self.batch_size,
                max_length=self.max_length
            )
        
        embeddings = output['dense_vecs']
        
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        
        return embeddings
    
    def get_sparse_embedding(self, text: str) -> Dict[int, float]:
        """获取稀疏向量嵌入（用于混合搜索）"""
        if text in self._sparse_embeddings_cache:
            return self._sparse_embeddings_cache[text]
        
        self._lazy_init()
        output = self._model.encode(
            [text],
            batch_size=1,
            max_length=self.max_length,
            return_dense=False,
            return_sparse=True
        )
        sparse_emb = output['lexical_weights'][0]
        self._sparse_embeddings_cache[text] = sparse_emb
        return sparse_emb
    
    def compute_hybrid_score(
        self, 
        query: str, 
        doc: str,
        dense_score: float = None
    ) -> float:
        """计算混合分数（Dense + Sparse）"""
        self._lazy_init()
        
        # 如果没有提供 dense 分数，则计算
        if dense_score is None:
            q_dense = np.array(self._get_query_embedding(query))
            d_dense = np.array(self._get_query_embedding(doc))
            dense_score = float(np.dot(q_dense, d_dense) / (np.linalg.norm(q_dense) * np.linalg.norm(d_dense)))
        
        # 计算 sparse 分数
        q_sparse = self.get_sparse_embedding(query)
        d_sparse = self.get_sparse_embedding(doc)
        
        # Sparse 分数计算：共享 token 的权重乘积之和
        sparse_score = 0.0
        for token_id, q_weight in q_sparse.items():
            if token_id in d_sparse:
                sparse_score += q_weight * d_sparse[token_id]
        
        # 混合分数
        hybrid_score = self.dense_weight * dense_score + self.sparse_weight * sparse_score
        
        return hybrid_score
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """异步获取查询嵌入"""
        return self._get_query_embedding(query)
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        """异步获取文本嵌入"""
        return self._get_text_embedding(text)


# 测试代码
if __name__ == "__main__":
    print("测试 BGE-M3 嵌入模型...")
    
    # 测试 Dense 模式
    print("\n=== Dense 模式 ===")
    embed_model = BGEM3Embedding(use_hybrid=False)
    
    test_texts = [
        "设备ciscoA上个月发生了几次告警",
        "存储客户配置信息的表",
    ]
    
    embeddings = embed_model._get_text_embeddings(test_texts)
    for i, text in enumerate(test_texts):
        print(f"  {text[:30]}... -> 维度: {len(embeddings[i])}")
    
    # 测试 Hybrid 模式
    print("\n=== Hybrid 模式 ===")
    embed_model_hybrid = BGEM3Embedding(use_hybrid=True, dense_weight=0.7, sparse_weight=0.3)
    
    query = "设备ciscoA告警"
    doc1 = "网元配置表，包含设备名称HOST_NAME"
    doc2 = "事件告警历史表"
    
    # 获取 sparse embeddings
    q_sparse = embed_model_hybrid.get_sparse_embedding(query)
    print(f"  Query sparse tokens: {len(q_sparse)} 个")
    
    # 计算混合分数
    score1 = embed_model_hybrid.compute_hybrid_score(query, doc1)
    score2 = embed_model_hybrid.compute_hybrid_score(query, doc2)
    print(f"  '{query}' vs '{doc1[:20]}...': {score1:.4f}")
    print(f"  '{query}' vs '{doc2}': {score2:.4f}")
    
    print("\n✅ 测试完成!")

