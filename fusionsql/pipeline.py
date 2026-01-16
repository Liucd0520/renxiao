#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text-to-SQL Pipeline - 统一入口

问题 → 检索相关表 → LSH值匹配 → 生成SQL

使用方法:
    from fusionsql import TextToSQL

    pipeline = TextToSQL()
    sql = pipeline.run("查询客户测试客户名下有多少设备")
    print(sql)
"""

import os
import sys
import logging

# 确保项目根目录在 path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from .retriever import FastRetriever
from .sql_generator import SQLGenerator

# LSH 值匹配（可选）
try:
    from .value_search import ValueSearcher
    LSH_AVAILABLE = True
except ImportError:
    LSH_AVAILABLE = False
    logging.warning("LSH 值匹配模块未安装，跳过值匹配功能")


class TextToSQL:
    """
    Text-to-SQL 完整链路
    
    流程:
    1. FastRetriever.retrieve() - 检索相关表
    2. ValueSearcher.find_entity_values() - LSH 值匹配（可选）
    3. SQLGenerator.generate_sql() - 生成SQL
    """
    
    def __init__(
        self,
        schema_dir: str = None,
        embeddings_file: str = None,
        lsh_index_dir: str = None,
        enable_lsh: bool = True,  # 新增：是否启用 LSH
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
            lsh_index_dir: LSH 索引目录（可选）
            enable_lsh: 是否启用 LSH 值匹配（默认 True）
            model_name: LLM 模型名称（覆盖 preset）
            model_base_url: LLM API 地址（覆盖 preset）
            model_api_key: LLM API 密钥（覆盖 preset）
            temperature: LLM 温度
            top_k: 检索 TOP-K 数量
            model_preset: 预设模型 "qwen3_moe"(默认) 或 "qwen32b"
        """
        # 默认路径
        our_dir = os.path.dirname(os.path.abspath(__file__))
        
        if schema_dir is None:
            schema_dir = os.path.join(our_dir, "schemas")
        
        if embeddings_file is None:
            embeddings_file = os.path.join(our_dir, "schema_embeddings_v3.pkl")
        
        if lsh_index_dir is None:
            lsh_index_dir = os.path.join(our_dir, "lsh_index")
        
        # 如果没有指定模型参数，使用预设
        if model_name is None and model_base_url is None:
            from .llm import QwenLLM
            presets = QwenLLM.MODEL_PRESETS.get(model_preset, QwenLLM.MODEL_PRESETS["qwen3_moe"])
            model_name = presets["model_name"]
            model_base_url = presets["base_url"]
            model_api_key = presets["api_key"]
        
        self.top_k = top_k
        self.enable_lsh = enable_lsh and LSH_AVAILABLE
        
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
        
        # 初始化 LSH 值匹配器（可选）
        self.value_searcher = None
        if self.enable_lsh:
            if os.path.exists(lsh_index_dir):
                print("初始化 LSH 值匹配器...")
                try:
                    self.value_searcher = ValueSearcher(lsh_index_dir)
                    print(f"LSH 索引加载完成")
                except Exception as e:
                    print(f"LSH 初始化失败: {e}")
                    self.value_searcher = None
            else:
                print(f"LSH 索引目录不存在: {lsh_index_dir}，跳过值匹配")
        
        print("Pipeline 初始化完成！")
    
    def _extract_keywords(self, question: str) -> list:
        """
        使用 LLM 从问题中提取关键词（CHESS 论文方法）
        
        Args:
            question: 用户问题
            
        Returns:
            关键词列表
        """
        prompt = '''从问题中提取实体关键词，这些关键词可能对应数据库中的具体值。
只提取：设备名、客户名、厂商名、状态值等具体实体。
如果问题中没有具体实体，返回"无"。

示例1:
问题: 设备ciscoA，上个月发生了几次告警
提取: ciscoA

示例2:
问题: 查询客户华为公司的所有设备
提取: 华为公司

示例3:
问题: 设备状态down超过3个月
提取: down

示例4:
问题: 现在平台上有多少家客户
提取: 无

当前问题: {}
提取:'''.format(question)
        
        try:
            response = self.generator.llm.complete(prompt)
            # 解析响应
            keywords_text = response.strip()
            
            # 处理"无"或空返回
            if not keywords_text or keywords_text in ['无', 'None', '无关键词', '无实体']:
                return []
            
            # 清理和分割
            import re
            # 移除可能的前缀
            keywords_text = re.sub(r'^(提取|关键词)[：:]\s*', '', keywords_text)
            
            keywords = re.split(r'[,，、\s]+', keywords_text)
            keywords = [k.strip() for k in keywords if k.strip() and len(k.strip()) >= 2]
            
            # 过滤掉一些明显错误的关键词
            invalid_keywords = {'关键词', '提取', '无', 'None', '问题', '示例'}
            keywords = [k for k in keywords if k not in invalid_keywords]
            
            if keywords:
                print(f"[LLM] 提取关键词: {keywords}")
            return keywords
            
        except Exception as e:
            logging.warning(f"LLM 关键词提取失败: {e}")
            return []
    
    def _find_matched_values(self, question: str) -> dict:
        """
        使用 LLM + LSH 进行 Entity Linking（CHESS 论文方法）
        
        流程：
        1. LLM 提取问题中的关键词
        2. 对每个关键词用 LSH 搜索数据库值
        3. 返回匹配结果
        
        Returns:
            {table: {column: [values]}} 格式的匹配结果
        """
        if self.value_searcher is None:
            return {}
        
        try:
            # Step 1: LLM 提取关键词
            keywords = self._extract_keywords(question)
            if not keywords:
                return {}
            
            # Step 2: 对每个关键词用 LSH 搜索
            all_results = {}
            for keyword in keywords:
                results = self.value_searcher.search_grouped(
                    keyword, 
                    top_n=3, 
                    min_similarity=0.6
                )
                
                # 合并结果
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
            
        except Exception as e:
            logging.warning(f"LSH Entity Linking 失败: {e}")
            return {}
    
    def _format_matched_values(self, matched_values: dict) -> str:
        """
        格式化 LSH Entity Linking 结果为 prompt 文本
        
        重要：只提供值的匹配信息，不要提及表名！
        否则 LLM 可能被误导使用 LSH 匹配到的表而非 BGE 检索到的表。
        """
        if not matched_values:
            return ""
        
        # 收集所有 keyword -> matched_value 的映射（不含表名）
        value_hints = []
        seen_values = set()
        
        for table, columns in matched_values.items():
            for column, values in columns.items():
                for v in values[:2]:  # 每列最多2个值
                    if v not in seen_values:
                        seen_values.add(v)
                        value_hints.append(v)
        
        if not value_hints:
            return ""
        
        # 只告诉 LLM 这些值在数据库中存在，不提及具体表
        lines = [
            "## 值匹配提示（仅供参考，请以检索到的表为准）",
            f"问题中提到的值在数据库中可能对应: {', '.join(repr(v) for v in value_hints[:5])}"
        ]
        
        return "\n".join(lines)
    
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
        
        # Step 1 & 2 并行执行（BGE 检索 和 LLM+LSH Entity Linking 互不依赖）
        from concurrent.futures import ThreadPoolExecutor
        
        def do_retrieval():
            return self.retriever.retrieve(question, top_k=top_k)
        
        def do_entity_linking():
            matched = self._find_matched_values(question)
            return self._format_matched_values(matched)
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_retrieval = executor.submit(do_retrieval)
            future_linking = executor.submit(do_entity_linking)
            
            retrieved = future_retrieval.result()
            matched_hint = future_linking.result()
        
        table_names = [t[0] for t in retrieved]
        
        # Step 3: 生成 SQL
        sql = self.generator.generate_sql(question, table_names, matched_hint=matched_hint)
        
        return sql
    
    def run_with_details(self, question: str, top_k: int = None) -> dict:
        """
        执行 Text-to-SQL 并返回详细信息
        
        Returns:
            {
                "question": 问题,
                "retrieved_tables": 检索到的表,
                "matched_values": LSH 匹配的值,
                "sql": 生成的SQL
            }
        """
        if top_k is None:
            top_k = self.top_k
        
        # Step 1 & 2 并行执行
        from concurrent.futures import ThreadPoolExecutor
        
        def do_retrieval():
            return self.retriever.retrieve(question, top_k=top_k)
        
        def do_entity_linking():
            matched = self._find_matched_values(question)
            return matched, self._format_matched_values(matched)
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_retrieval = executor.submit(do_retrieval)
            future_linking = executor.submit(do_entity_linking)
            
            retrieved = future_retrieval.result()
            matched_values, matched_hint = future_linking.result()
        
        table_names = [t[0] for t in retrieved]
        table_scores = {t: s for t, s in retrieved}
        
        # Step 3: 生成
        sql = self.generator.generate_sql(question, table_names, matched_hint=matched_hint)
        
        return {
            "question": question,
            "retrieved_tables": table_names,
            "table_scores": table_scores,
            "matched_values": matched_values,  # 新增
            "sql": sql,
        }


class AsyncTextToSQL:
    """
    异步版 Text-to-SQL Pipeline
    
    使用 AsyncSQLGenerator，适用于高并发场景。
    检索仍然是同步的（BGE-M3 模型不易改异步），但 LLM 调用是异步的。
    """
    
    def __init__(
        self,
        schema_dir: str = None,
        embeddings_file: str = None,
        lsh_index_dir: str = None,
        enable_lsh: bool = True,
        model_name: str = None,
        model_base_url: str = None,
        model_api_key: str = None,
        temperature: float = 0,
        top_k: int = 10,
        model_preset: str = "qwen3_moe",
    ):
        """初始化（同 TextToSQL）"""
        from .sql_generator import AsyncSQLGenerator
        
        our_dir = os.path.dirname(os.path.abspath(__file__))
        
        if schema_dir is None:
            schema_dir = os.path.join(our_dir, "schemas")
        
        if embeddings_file is None:
            embeddings_file = os.path.join(our_dir, "schema_embeddings_v3.pkl")
        
        if lsh_index_dir is None:
            lsh_index_dir = os.path.join(our_dir, "lsh_index")
        
        # 如果没有指定模型参数，使用预设
        if model_name is None and model_base_url is None:
            from .llm import MODEL_PRESETS
            presets = MODEL_PRESETS.get(model_preset, MODEL_PRESETS["qwen3_moe"])
            model_name = presets["model_name"]
            model_base_url = presets["base_url"]
            model_api_key = presets["api_key"]
        
        self.top_k = top_k
        self.enable_lsh = enable_lsh and LSH_AVAILABLE
        
        # 初始化组件
        print("初始化检索器...")
        self.retriever = FastRetriever(embeddings_file=embeddings_file)
        
        print("初始化异步SQL生成器...")
        self.generator = AsyncSQLGenerator(
            schema_dir=schema_dir,
            model_name=model_name,
            base_url=model_base_url,
            api_key=model_api_key,
            temperature=temperature,
        )
        
        # 初始化 LSH 值匹配器（可选）
        self.value_searcher = None
        if self.enable_lsh:
            if os.path.exists(lsh_index_dir):
                print("初始化 LSH 值匹配器...")
                try:
                    self.value_searcher = ValueSearcher(lsh_index_dir)
                    print(f"LSH 索引加载完成")
                except Exception as e:
                    print(f"LSH 初始化失败: {e}")
                    self.value_searcher = None
            else:
                print(f"LSH 索引目录不存在: {lsh_index_dir}，跳过值匹配")
        
        print("异步 Pipeline 初始化完成！")
    
    def _find_matched_values(self, question: str) -> dict:
        """
        使用 LSH 进行 Entity Linking
        
        目的：帮助 LLM 理解问题中的实体在数据库中的对应值
        """
        if self.value_searcher is None:
            return {}
        
        try:
            return self.value_searcher.find_entity_values(
                question,
                top_n_per_word=3,
                min_word_length=2,
                min_similarity=0.6  # 提高阈值，过滤低质量匹配
            )
        except Exception as e:
            logging.warning(f"LSH 搜索失败: {e}")
            return {}
    
    def _format_matched_values(self, matched_values: dict) -> str:
        """
        格式化 LSH Entity Linking 结果为 prompt 文本
        """
        if not matched_values:
            return ""
        
        lines = ["## Entity Linking（问题中的实体可能对应的数据库值）"]
        for table, columns in matched_values.items():
            for column, values in columns.items():
                values_str = ", ".join(f"'{v}'" for v in values[:3])
                lines.append(f"- {table}.{column} 可能的值: {values_str}")
        
        return "\n".join(lines)
    
    async def run(self, question: str, top_k: int = None) -> str:
        """
        异步执行 Text-to-SQL
        
        Args:
            question: 自然语言问题
            top_k: 检索 TOP-K
        
        Returns:
            生成的 SQL 语句
        """
        if top_k is None:
            top_k = self.top_k
        
        # Step 1: 检索相关表（BGE-M3 表级别 + 列级别融合）
        retrieved = self.retriever.retrieve(question, top_k=top_k)
        table_names = [t[0] for t in retrieved]
        
        # Step 2: LSH Entity Linking
        matched_values = self._find_matched_values(question)
        matched_hint = self._format_matched_values(matched_values)
        
        # Step 3: 异步生成 SQL
        sql = await self.generator.generate_sql(question, table_names, matched_hint=matched_hint)
        
        return sql
    
    async def run_with_details(self, question: str, top_k: int = None) -> dict:
        """
        异步执行 Text-to-SQL 并返回详细信息
        """
        if top_k is None:
            top_k = self.top_k
        
        # Step 1: 检索（BGE-M3 表级别 + 列级别融合）
        retrieved = self.retriever.retrieve(question, top_k=top_k)
        table_names = [t[0] for t in retrieved]
        table_scores = {t: s for t, s in retrieved}
        
        # Step 2: LSH Entity Linking
        matched_values = self._find_matched_values(question)
        matched_hint = self._format_matched_values(matched_values)
        
        # Step 3: 异步生成
        sql = await self.generator.generate_sql(question, table_names, matched_hint=matched_hint)
        
        return {
            "question": question,
            "retrieved_tables": table_names,
            "table_scores": table_scores,
            "matched_values": matched_values,
            "sql": sql,
        }


# 测试入口
if __name__ == "__main__":
    print("=" * 60)
    print("Text-to-SQL Pipeline 测试（含 LSH 值匹配）")
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
        if result.get('matched_values'):
            print(f"LSH 匹配: {result['matched_values']}")
        print(f"SQL: {result['sql'][:100]}...")

