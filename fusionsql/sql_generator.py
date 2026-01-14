#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 生成器

使用 LLM 根据问题和 Schema 生成 SQL
"""

import os
import json
import re
from pathlib import Path

from .llm import QwenLLM, AsyncQwenLLM


# SQL 生成 Prompt
SQL_GENERATION_PROMPT = """你是一个 MySQL 数据库专家。根据用户问题和相关表的 Schema，生成正确的 SQL 查询。

## 用户问题
{question}

## 相关表 Schema
{schema_text}
{matched_hint}
## 要求
1. 只输出一个完整的 SQL 语句
2. 不要解释，不要输出其他内容
3. 使用 MySQL 语法
4. 如果需要日期时间，使用 NOW() 函数
5. 如果上面有"匹配到的实体值"，优先使用这些精确值作为 WHERE 条件

## SQL:
"""


class SQLGenerator:
    """SQL 生成器"""
    
    def __init__(self, schema_dir, model_name="Qwen2.5-Coder-32B-Instruct", temperature=0.1, base_url=None, api_key=None):
        """
        初始化
        
        Args:
            schema_dir: 表级别 schema 目录
            model_name: LLM 模型名称（默认使用本地部署的 Qwen）
            temperature: LLM 温度
            base_url: LLM API 地址（可选）
            api_key: LLM API 密钥（可选）
        """
        self.schema_dir = Path(schema_dir)

        # 初始化 LLM
        self.llm = QwenLLM(
            model_name=model_name,
            temperature=temperature,
            base_url=base_url,
            api_key=api_key,
        )
        
        # 预加载所有 schema
        self.schemas = {}
        for schema_file in self.schema_dir.glob("*.json"):
            with open(schema_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            table_name = data["meta_data"]["table_name"]
            self.schemas[table_name.lower()] = data
        
        print(f"加载了 {len(self.schemas)} 张表的 Schema")
    
    def get_schema_text(self, table_names):
        """获取指定表的 Schema 文本"""
        parts = []
        for name in table_names:
            name_lower = name.lower()
            if name_lower not in self.schemas:
                continue
            
            data = self.schemas[name_lower]
            table_name = data["meta_data"]["table_name"]
            columns = data.get("columns", [])
            llm_desc = data.get("llm_description", "")
            
            # 构建表 schema 文本
            lines = [f"### 表: {table_name}"]
            if llm_desc:
                lines.append(f"说明: {llm_desc}")
            
            lines.append("列:")
            for col in columns:
                col_str = f"  - {col['name']} ({col['type']})"
                if col.get('description'):
                    col_str += f": {col['description']}"
                lines.append(col_str)
            
            parts.append("\n".join(lines))
        
        return "\n\n".join(parts)
    
    def generate_sql(self, question, table_names, matched_hint: str = ""):
        """
        生成 SQL
        
        Args:
            question: 用户问题
            table_names: 相关表名列表
            matched_hint: LSH 匹配的实体值提示（可选）
            
        Returns:
            生成的 SQL 语句
        """
        schema_text = self.get_schema_text(table_names)
        
        # 格式化 matched_hint
        hint_text = ""
        if matched_hint:
            hint_text = "\n" + matched_hint + "\n"
        
        prompt = SQL_GENERATION_PROMPT.format(
            question=question,
            schema_text=schema_text,
            matched_hint=hint_text
        )
        
        response = self.llm.complete(prompt)
        # 兼容新旧 LLM 封装
        if hasattr(response, 'text'):
            response = response.text
        response = response.strip()
        
        # 清理响应
        sql = self._clean_sql(response)
        
        return sql
    
    def _clean_sql(self, response):
        """清理 LLM 响应，提取 SQL"""
        import re
        
        # 去除 <think>...</think>
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
        
        # 去除 markdown 代码块
        response = re.sub(r'```sql\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # 去除开头的 SQL: 或 sql:
        response = re.sub(r'^(SQL|sql):\s*', '', response.strip())
        
        return response.strip()

class AsyncSQLGenerator:
    """
    异步 SQL 生成器
    
    使用 AsyncQwenLLM 进行异步 SQL 生成，适用于高并发场景。
    """
    
    def __init__(self, schema_dir, model_name="Qwen2.5-Coder-32B-Instruct", temperature=0.1, base_url=None, api_key=None):
        """初始化（同 SQLGenerator）"""
        self.schema_dir = Path(schema_dir)
        
        # 初始化异步 LLM
        self.llm = AsyncQwenLLM(
            model_name=model_name,
            temperature=temperature,
            base_url=base_url,
            api_key=api_key,
        )
        
        # 预加载所有 schema
        self.schemas = {}
        for schema_file in self.schema_dir.glob("*.json"):
            with open(schema_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            table_name = data["meta_data"]["table_name"]
            self.schemas[table_name.lower()] = data
        
        print(f"加载了 {len(self.schemas)} 张表的 Schema（异步模式）")
    
    def get_schema_text(self, table_names):
        """获取指定表的 Schema 文本"""
        parts = []
        for name in table_names:
            name_lower = name.lower()
            if name_lower not in self.schemas:
                continue
            
            data = self.schemas[name_lower]
            table_name = data["meta_data"]["table_name"]
            columns = data.get("columns", [])
            llm_desc = data.get("llm_description", "")
            
            lines = [f"### 表: {table_name}"]
            if llm_desc:
                lines.append(f"说明: {llm_desc}")
            
            lines.append("列:")
            for col in columns:
                col_str = f"  - {col['name']} ({col['type']})"
                if col.get('description'):
                    col_str += f": {col['description']}"
                lines.append(col_str)
            
            parts.append("\n".join(lines))
        
        return "\n\n".join(parts)
    
    async def generate_sql(self, question, table_names, matched_hint: str = ""):
        """
        异步生成 SQL
        
        Args:
            question: 用户问题
            table_names: 相关表名列表
            matched_hint: LSH 匹配的实体值提示（可选）
            
        Returns:
            生成的 SQL 语句
        """
        schema_text = self.get_schema_text(table_names)
        
        hint_text = ""
        if matched_hint:
            hint_text = "\n" + matched_hint + "\n"
        
        prompt = SQL_GENERATION_PROMPT.format(
            question=question,
            schema_text=schema_text,
            matched_hint=hint_text
        )
        
        response = await self.llm.acomplete(prompt)
        if hasattr(response, 'text'):
            response = response.text
        response = response.strip()
        
        sql = self._clean_sql(response)
        return sql
    
    def _clean_sql(self, response):
        """清理 LLM 响应，提取 SQL"""
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
        response = re.sub(r'```sql\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        response = re.sub(r'^(SQL|sql):\s*', '', response.strip())
        return response.strip()


# 测试
if __name__ == "__main__":
    print("测试 SQL 生成器...")
    
    generator = SQLGenerator(
        schema_dir="./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    )
    
    question = "查询客户测试客户名下有多少设备"
    tables = ["t_bz_config_customer", "t_bz_config_ci_ne_root"]
    
    print(f"\n问题: {question}")
    print(f"表: {tables}")
    
    sql = generator.generate_sql(question, tables)
    print(f"\n生成的 SQL:\n{sql}")
