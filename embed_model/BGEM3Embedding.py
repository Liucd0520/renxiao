"""
BGE-M3 嵌入模型适配器

将 FlagEmbedding 的 BGEM3FlagModel 适配为 llama_index 可用的嵌入模型。
BGE-M3 支持多语言（100+语言）、长文本（8192 tokens）、多功能检索（dense, sparse, colbert）。
"""

from typing import Any, List, Optional
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.bridge.pydantic import Field, PrivateAttr
import numpy as np


class BGEM3Embedding(BaseEmbedding):
    """BGE-M3 多语言嵌入模型适配器"""
    
    # 默认使用本地下载的模型
    model_name: str = Field(default="./embed_model_cache/BAAI/bge-m3", description="模型名称或路径")
    use_fp16: bool = Field(default=True, description="是否使用 FP16 加速")
    max_length: int = Field(default=8192, description="最大输入长度")
    batch_size: int = Field(default=12, description="批处理大小")
    
    _model: Any = PrivateAttr()
    _initialized: bool = PrivateAttr(default=False)
    
    def __init__(
        self,
        model_name: str = "./embed_model_cache/BAAI/bge-m3",
        use_fp16: bool = True,
        max_length: int = 8192,
        batch_size: int = 12,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            use_fp16=use_fp16,
            max_length=max_length,
            batch_size=batch_size,
            **kwargs
        )
        self._model = None
        self._initialized = False
    
    def _lazy_init(self):
        """延迟初始化模型（第一次使用时加载）"""
        if self._initialized:
            return
        
        try:
            from FlagEmbedding import BGEM3FlagModel
            print(f"加载 BGE-M3 模型: {self.model_name}...")
            self._model = BGEM3FlagModel(
                self.model_name,
                use_fp16=self.use_fp16
            )
            self._initialized = True
            print("✅ BGE-M3 模型加载完成")
        except ImportError:
            raise ImportError(
                "请安装 FlagEmbedding: pip install FlagEmbedding"
            )
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """获取查询的嵌入向量"""
        self._lazy_init()
        
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
        
        output = self._model.encode(
            texts,
            batch_size=self.batch_size,
            max_length=self.max_length
        )
        
        embeddings = output['dense_vecs']
        
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        
        return embeddings
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """异步获取查询嵌入"""
        return self._get_query_embedding(query)
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        """异步获取文本嵌入"""
        return self._get_text_embedding(text)


# 测试代码
if __name__ == "__main__":
    print("测试 BGE-M3 嵌入模型...")
    
    embed_model = BGEM3Embedding()
    
    # 测试中文
    test_texts_cn = [
        "设备ciscoA上个月发生了几次告警",
        "存储客户配置信息的表",
        "记录事件历史的数据表"
    ]
    
    # 测试英文
    test_texts_en = [
        "How many devices are on the platform",
        "Customer configuration table",
        "Event history records"
    ]
    
    print("\n测试中文嵌入:")
    embeddings_cn = embed_model._get_text_embeddings(test_texts_cn)
    for i, text in enumerate(test_texts_cn):
        print(f"  {text[:30]}... -> 维度: {len(embeddings_cn[i])}")
    
    print("\n测试英文嵌入:")
    embeddings_en = embed_model._get_text_embeddings(test_texts_en)
    for i, text in enumerate(test_texts_en):
        print(f"  {text[:30]}... -> 维度: {len(embeddings_en[i])}")
    
    # 测试跨语言相似度
    print("\n测试跨语言相似度:")
    cn_embed = np.array(embed_model._get_text_embedding("客户信息表"))
    en_embed = np.array(embed_model._get_text_embedding("Customer information table"))
    similarity = np.dot(cn_embed, en_embed) / (np.linalg.norm(cn_embed) * np.linalg.norm(en_embed))
    print(f"  '客户信息表' vs 'Customer information table': {similarity:.4f}")
    
    print("\n✅ 测试完成!")
