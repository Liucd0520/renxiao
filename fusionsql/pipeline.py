#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text-to-SQL Pipeline - 统一入口

问题 → 检索相关表 → 生成SQL

使用方法:
    from fusionsql import TextToSQL

    pipeline = TextToSQL()
    sql = pipeline.run("查询客户测试客户名下有多少设备")
    print(sql)
"""

import os
import sys

# 确保项目根目录在 path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from .retriever import FastRetriever
from .sql_generator import SQLGenerator


class TextToSQL:
    """
    Text-to-SQL 完整链路
    
    流程:
    1. FastRetriever.retrieve() - 检索相关表
    2. SQLGenerator.generate_sql() - 生成SQL
    """
    
    def __init__(
        self,
        schema_dir: str = None,
        embeddings_file: str = None,
        model_name: str = None,
        model_base_url: str = None,
        model_api_key: str = None,
        temperature: float = 0,  # 温度=0 更稳定
        top_k: int = 10,
        model_preset: str = "qwen3_moe",  # 默认使用 MoE
    ):
        """
        初始化 Pipeline
        
        Args:
            schema_dir: Schema JSON 文件目录
            embeddings_file: 预计算 embedding 文件路径
            model_name: LLM 模型名称（覆盖 preset）
            model_base_url: LLM API 地址（覆盖 preset）
            model_api_key: LLM API 密钥（覆盖 preset）
            temperature: LLM 温度
            top_k: 检索 TOP-K 数量
            model_preset: 预设模型 "qwen3_moe"(默认) 或 "qwen32b"
        """
        # 默认路径（使用 our_algorithm 目录下的新文件）
        our_dir = os.path.dirname(os.path.abspath(__file__))
        
        if schema_dir is None:
            schema_dir = os.path.join(our_dir, "schemas")
        
        if embeddings_file is None:
            embeddings_file = os.path.join(our_dir, "schema_embeddings_v3.pkl")
        
        # 如果没有指定模型参数，使用预设
        if model_name is None and model_base_url is None:
            from .llm import QwenLLM
            presets = QwenLLM.MODEL_PRESETS.get(model_preset, QwenLLM.MODEL_PRESETS["qwen3_moe"])
            model_name = presets["model_name"]
            model_base_url = presets["base_url"]
            model_api_key = presets["api_key"]
        
        self.top_k = top_k
        
        # 初始化组件
        print("初始化检索器...")
        self.retriever = FastRetriever(embeddings_file=embeddings_file)
        
        print("初始化SQL生成器...")
        self.generator = SQLGenerator(
            schema_dir=schema_dir,
            model_name=model_name,
            base_url=model_base_url,
            api_key=model_api_key,
            temperature=temperature,
        )
        
        print("Pipeline 初始化完成！")
    
    def run(self, question: str, top_k: int = None) -> str:
        """
        执行 Text-to-SQL
        
        Args:
            question: 自然语言问题
            top_k: 检索 TOP-K（可选，默认使用初始化时的值）
        
        Returns:
            生成的 SQL 语句
        """
        if top_k is None:
            top_k = self.top_k
        
        # Step 1: 检索相关表
        retrieved = self.retriever.retrieve(question, top_k=top_k)
        table_names = [t[0] for t in retrieved]
        
        # Step 2: 生成 SQL
        sql = self.generator.generate_sql(question, table_names)
        
        return sql
    
    def run_with_details(self, question: str, top_k: int = None) -> dict:
        """
        执行 Text-to-SQL 并返回详细信息
        
        Returns:
            {
                "question": 问题,
                "retrieved_tables": 检索到的表,
                "sql": 生成的SQL
            }
        """
        if top_k is None:
            top_k = self.top_k
        
        # Step 1: 检索
        retrieved = self.retriever.retrieve(question, top_k=top_k)
        table_names = [t[0] for t in retrieved]
        table_scores = {t: s for t, s in retrieved}
        
        # Step 2: 生成
        sql = self.generator.generate_sql(question, table_names)
        
        return {
            "question": question,
            "retrieved_tables": table_names,
            "table_scores": table_scores,
            "sql": sql,
        }


# 测试入口
if __name__ == "__main__":
    print("=" * 60)
    print("Text-to-SQL Pipeline 测试")
    print("=" * 60)
    
    # 初始化
    pipeline = TextToSQL()
    
    # 测试问题
    test_questions = [
        "查询客户测试客户名下有多少设备",
        "查询今天发生的所有告警",
        "设备ciscoA上个月的告警统计",
    ]
    
    for q in test_questions:
        print(f"\n问题: {q}")
        result = pipeline.run_with_details(q)
        print(f"检索表: {result['retrieved_tables'][:5]}...")
        print(f"SQL: {result['sql'][:100]}...")
