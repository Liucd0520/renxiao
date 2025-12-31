#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表筛选器 - 方案 B

使用 LLM 从检索到的 10-20 张表中筛选出 3-5 张最相关的表
"""

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

from llms.qwen.QwenModel import QwenModel


# 表筛选 Prompt
TABLE_FILTER_PROMPT = """你是一个数据库专家。根据用户问题，从候选表中选择最相关的表来回答问题。

## 用户问题
{question}

## 候选表（共 {table_count} 张）
{table_list}

## 要求
1. 只选择回答问题**必需**的表，通常是 1-5 张
2. 输出格式：用逗号分隔的表名列表
3. 不要解释，只输出表名

## 选择的表：
"""


class TableFilter:
    """表筛选器"""
    
    def __init__(self, schema_dir, model_name="Qwen2.5-Coder-32B-Instruct", temperature=0.1):
        """
        初始化
        
        Args:
            schema_dir: 表级别 schema 目录
            model_name: LLM 模型名称
            temperature: LLM 温度
        """
        self.schema_dir = Path(schema_dir)
        self.llm = QwenModel(model_name=model_name, temperature=temperature)
        
        # 预加载所有 schema（保存表名、描述和列信息）
        self.table_info = {}
        for schema_file in self.schema_dir.glob("*.json"):
            with open(schema_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            table_name = data["meta_data"]["table_name"]
            desc = data.get("llm_description", "")
            columns = data.get("columns", [])
            self.table_info[table_name.lower()] = {
                "name": table_name,
                "description": desc,
                "columns": columns
            }
        
        print(f"表筛选器加载了 {len(self.table_info)} 张表的信息")
    
    def filter_tables(self, question, candidate_tables, max_tables=5):
        """
        从候选表中筛选最相关的表
        
        Args:
            question: 用户问题
            candidate_tables: 候选表名列表
            max_tables: 最多返回的表数量
            
        Returns:
            筛选后的表名列表
        """
        # 构建表列表文本（包含列信息）
        table_lines = []
        for i, name in enumerate(candidate_tables, 1):
            name_lower = name.lower()
            if name_lower in self.table_info:
                info = self.table_info[name_lower]
                desc = info.get("description", "")
                columns = info.get("columns", [])
                # 构建列信息字符串
                col_names = [c["name"] for c in columns[:15]]  # 最多显示15个列
                col_str = ", ".join(col_names)
                if len(columns) > 15:
                    col_str += f"... (共{len(columns)}列)"
                table_lines.append(f"{i}. {name}\n   描述: {desc}\n   列: {col_str}")
            else:
                table_lines.append(f"{i}. {name}")
        
        table_list = "\n".join(table_lines)
        
        prompt = TABLE_FILTER_PROMPT.format(
            question=question,
            table_count=len(candidate_tables),
            table_list=table_list
        )
        
        response = self.llm.complete(prompt).text.strip()
        
        # 解析响应
        selected = self._parse_response(response, candidate_tables)
        
        # 限制数量
        return selected[:max_tables]
    
    def _parse_response(self, response, candidate_tables):
        """解析 LLM 响应，提取表名"""
        import re
        
        # 去除 <think>...</think>
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
        
        # 清理响应
        response = response.strip()
        
        # 分割表名（逗号、换行、空格）
        names = re.split(r'[,\n\s]+', response)
        
        # 验证表名
        candidate_set = set(t.lower() for t in candidate_tables)
        selected = []
        for name in names:
            name = name.strip().strip('.,;')
            if name.lower() in candidate_set:
                # 找到原始大小写
                for orig in candidate_tables:
                    if orig.lower() == name.lower():
                        if orig not in selected:
                            selected.append(orig)
                        break
        
        return selected


# 测试
if __name__ == "__main__":
    print("测试表筛选器...")
    
    filter = TableFilter(
        schema_dir="./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    )
    
    question = "查询客户南京研发中心名下所有设备的名称和IP地址"
    candidates = [
        "t_bz_config_customer",
        "t_bz_config_ci_ne_root",
        "t_gn_business_application_change",
        "event_history",
        "t_gn_botnet"
    ]
    
    print(f"\n问题: {question}")
    print(f"候选表: {candidates}")
    
    selected = filter.filter_tables(question, candidates)
    print(f"\n筛选结果: {selected}")
