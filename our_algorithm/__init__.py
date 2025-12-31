"""
our_algorithm - Text-to-SQL 全链路算法包

核心组件:
    - TextToSQL: 统一 Pipeline 入口（问题 → SQL）
    - FastRetriever: 基于 BGE-M3 的 Schema 检索器
    - SQLGenerator: 基于 LLM 的 SQL 生成器

工具组件:
    - QwenLLM: Qwen LLM 封装（默认 MoE，可切换 32B）
    - schema_enhancer: Schema 枚举值增强工具
    - schema_extractor: Schema 提取工具

使用方法:
    from our_algorithm import TextToSQL
    
    pipeline = TextToSQL()
    sql = pipeline.run("查询客户测试客户名下有多少设备")
"""

from .retriever import FastRetriever
from .sql_generator import SQLGenerator
from .pipeline import TextToSQL
from .llm import QwenLLM, get_default_llm, get_qwen32b_llm

__all__ = [
    # 核心组件
    "TextToSQL",
    "FastRetriever",
    "SQLGenerator",
    # LLM
    "QwenLLM",
    "get_default_llm",
    "get_qwen32b_llm",
]

__version__ = "1.0.0"
