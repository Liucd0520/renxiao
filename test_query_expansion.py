# -*- coding: utf-8 -*-
"""
改进方案测试: 通过查询增强提高中英文混合检索效果

核心思路：在向量检索前，使用 LLM 将中文查询扩展为包含英文关键词的增强查询
"""

import json
import os
import sys
import time
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.SchemaLinkingTool import SchemaLinkingTool
from utils import parse_schema_from_df, parse_schemas_from_nodes
from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 查询扩展 Prompt - 将中文转换为包含英文的扩展查询
QUERY_EXPANSION_PROMPT = """你是一个数据库查询专家。给定一个中文自然语言查询，请将其扩展为包含多种同义表达的增强查询。

要求：
1. 提取核心实体和概念
2. 为每个中文概念添加对应的英文翻译（用于匹配英文表名/列名）
3. 添加常见的数据库命名变体（如 customer, cust, 客户）
4. 保持查询意图完整

示例输入：
"某客户设备近一周内发生过哪些类型的告警？"

示例输出：
"客户 customer 设备 device equipment ne ci 告警 alarm event alert 类型 type category 时间 time datetime occur_time event_time 近一周 last week recent"

现在请处理以下查询：
{question}

输出增强查询（只输出扩展后的关键词，不需要解释）：
"""

# 配置
TEST_QUESTION = "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？"
DB_ID = "netcaredb_ai"
SCHEMA_PATH = "./spider2_dev/schemas"
OUTPUT_DIR = "./spider2_dev/test_results"


def expand_query(llm, question: str) -> str:
    """使用 LLM 扩展中文查询"""
    prompt = QUERY_EXPANSION_PROMPT.format(question=question)
    response = llm.complete(prompt).text
    
    # 清理响应
    expanded = response.strip()
    # 移除可能的 <think> 标签
    if '<think>' in expanded:
        expanded = expanded.split('</think>')[-1].strip()
    
    return expanded


def test_with_query_expansion():
    """测试改进方案"""
    print("=" * 80)
    print("方案测试: 查询扩展增强检索")
    print("=" * 80)
    print(f"原始问题: {TEST_QUESTION}\n")
    
    # 初始化 LLM
    llm = QwenModel(model_name="qwen-turbo", temperature=0.3)
    
    # 扩展查询
    print("1. 扩展查询...")
    expanded_query = expand_query(llm, TEST_QUESTION)
    print(f"扩展后: {expanded_query}\n")
    
    # 加载向量索引
    print("2. 加载向量索引...")
    vector_dir = os.path.join(SCHEMA_PATH, DB_ID)
    vector_index = RagPipeLines.build_index_from_source(
        data_source=vector_dir,
        persist_dir=os.path.join(vector_dir, "vector_store"),
        is_vector_store_exist=True,
        index_method="VectorStoreIndex"
    )
    retriever = RagPipeLines.get_retriever(index=vector_index)
    
    # 测试不同配置
    test_configs = [
        {"name": "原始查询", "query": TEST_QUESTION, "top_k": 10},
        {"name": "扩展查询", "query": expanded_query, "top_k": 10},
        {"name": "组合查询", "query": TEST_QUESTION + " " + expanded_query, "top_k": 10},
        {"name": "扩展查询+小top_k", "query": expanded_query, "top_k": 5},
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n3. 测试: {config['name']}...")
        retriever.similarity_top_k = config["top_k"]
        
        start_time = time.time()
        nodes = SchemaLinkingTool.parallel_retrieve([retriever], [config["query"]])
        elapsed = time.time() - start_time
        
        # 提取结果
        df = parse_schemas_from_nodes(nodes)
        if not df.empty:
            tables = set(df['Table Name'].unique())
        else:
            tables = set()
        
        result = {
            "config": config["name"],
            "tables": sorted(tables),
            "table_count": len(tables),
            "time": elapsed
        }
        results.append(result)
        
        print(f"   返回 {len(tables)} 个表, 耗时 {elapsed:.2f}s")
        print(f"   表: {', '.join(sorted(tables)[:10])}{'...' if len(tables) > 10 else ''}")
    
    # 输出对比报告
    print("\n" + "=" * 80)
    print("对比结果:")
    print("=" * 80)
    print(f"{'配置':<20} | {'表数量':<8} | {'耗时(s)':<8} | 前5个表")
    print("-" * 80)
    for r in results:
        top5 = ', '.join(r['tables'][:5])
        print(f"{r['config']:<20} | {r['table_count']:<8} | {r['time']:<8.2f} | {top5}")
    
    # 检查关键表是否被检索到
    key_tables = ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer", "t_bz_sdn_alarm", "event_backup"]
    
    print("\n" + "=" * 80)
    print("关键表召回检查:")
    print("=" * 80)
    print(f"{'配置':<20} | " + " | ".join([f"{t[:15]:<15}" for t in key_tables]))
    print("-" * 80)
    for r in results:
        checks = ["✓" if t in r["tables"] else "✗" for t in key_tables]
        print(f"{r['config']:<20} | " + " | ".join([f"{c:<15}" for c in checks]))
    
    # 保存结果
    report_path = os.path.join(OUTPUT_DIR, "query_expansion_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 查询扩展方案测试报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 原始问题\n{TEST_QUESTION}\n\n")
        f.write(f"## 扩展查询\n{expanded_query}\n\n")
        f.write("## 结果对比\n\n")
        for r in results:
            f.write(f"### {r['config']}\n")
            f.write(f"- 返回表数: {r['table_count']}\n")
            f.write(f"- 表列表: {', '.join(r['tables'])}\n\n")
    
    print(f"\n报告已保存到: {report_path}")
    return results


if __name__ == "__main__":
    results = test_with_query_expansion()
