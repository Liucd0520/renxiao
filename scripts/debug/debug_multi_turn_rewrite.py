#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LinkAlign 完整的多轮查询重写

LinkAlign 的查询重写流程：
1. 第 0 轮: 跨语言扩展 → 初始检索
2. 第 1-N 轮: Judge 分析 → Annotator 注释 → 增强检索

本脚本模拟这个完整流程，追踪每一轮后目标表的排名变化。
"""

import os
import sys
from collections import defaultdict

# 添加项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from embed_model.BGEM3Embedding import BGEM3Embedding
from llms.qwen.QwenModel import QwenModel
from prompts.PipelinePromptStore import CROSS_LINGUAL_EXPANSION_TEMPLATE
from prompts.AgentPromptStore import JUDGE_TEMPLATE, ANNOTATOR_TEMPLATE
from utils import parse_schema_from_df, parse_schemas_from_nodes

# 配置
VECTOR_STORE_DIR = "./spider2_dev/schemas/netcaredb_ai/vector_store_bge_m3_enhanced"
TOP_K = 100
RETRIEVE_TURNS = 2  # 多少轮查询重写

# 测试问题
TEST_QUESTION = "现在平台上有多少台设备"
EXPECTED_TABLE = "t_bz_config_ci_ne_root"


def find_target_rank(nodes, target_table):
    """找到目标表的最高排名"""
    for i, node in enumerate(nodes, 1):
        if node.metadata.get("table_name", "").lower() == target_table.lower():
            return i, node.metadata.get("column_name", "")
    return -1, "N/A"


def run_multi_turn_test():
    print("=" * 80)
    print("LinkAlign 多轮查询重写测试")
    print("=" * 80)
    print(f"\n原始问题: {TEST_QUESTION}")
    print(f"期望表: {EXPECTED_TABLE}")
    print(f"重写轮数: {RETRIEVE_TURNS}")
    print("=" * 80)
    
    # 1. 初始化
    print("\n[初始化] 加载模型...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_DIR)
    vector_index = load_index_from_storage(storage_context)
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=TOP_K)
    print("✅ 初始化完成")
    
    # 2. 第 0 轮：跨语言扩展 + 初始检索
    print("\n" + "=" * 80)
    print("[轮次 0] 跨语言扩展 + 初始检索")
    print("-" * 80)
    
    expanded_query = llm.complete(CROSS_LINGUAL_EXPANSION_TEMPLATE.format(question=TEST_QUESTION)).text.strip()
    if '<think>' in expanded_query:
        expanded_query = expanded_query.split('</think>')[-1].strip()
    
    print(f"扩展后: {expanded_query[:100]}...")
    
    combined_query = TEST_QUESTION + " " + expanded_query
    nodes = retriever.retrieve(combined_query)
    
    rank, col = find_target_rank(nodes, EXPECTED_TABLE)
    print(f"检索到 {len(nodes)} 列")
    print(f"目标表排名: #{rank} (列: {col})")
    
    all_nodes = nodes.copy()
    enhanced_question = TEST_QUESTION
    
    # 3. 多轮 Judge + Annotator
    for turn in range(1, RETRIEVE_TURNS + 1):
        print("\n" + "=" * 80)
        print(f"[轮次 {turn}] Judge 分析 + Annotator 重写")
        print("-" * 80)
        
        # 从当前节点解析 schema
        schema_df = parse_schemas_from_nodes(all_nodes)
        schemas = parse_schema_from_df(schema_df)
        
        # Judge 分析
        print(f"\n[Judge] 分析 Schema 完整性...")
        analysis = llm.complete(JUDGE_TEMPLATE.format(question=TEST_QUESTION, context=schemas[:8000])).text
        print(f"分析结果片段: {analysis[:300]}...")
        
        # Annotator 重写
        print(f"\n[Annotator] 重写问题...")
        annotation = llm.complete(ANNOTATOR_TEMPLATE.format(question=TEST_QUESTION, analysis=analysis)).text.strip()
        if '<think>' in annotation:
            annotation = annotation.split('</think>')[-1].strip()
        
        enhanced_question = TEST_QUESTION + " " + annotation
        print(f"重写后问题: {enhanced_question[:200]}...")
        
        # 增强检索
        new_nodes = retriever.retrieve(enhanced_question)
        all_nodes.extend(new_nodes)
        
        rank, col = find_target_rank(new_nodes, EXPECTED_TABLE)
        print(f"\n本轮检索到 {len(new_nodes)} 列")
        print(f"目标表排名: #{rank} (列: {col})")
    
    # 4. 汇总
    print("\n" + "=" * 80)
    print("汇总: 各轮次目标表排名变化")
    print("=" * 80)
    
    # 在所有累积节点中查找目标表
    table_columns = defaultdict(list)
    for node in all_nodes:
        table_name = node.metadata.get("table_name", "")
        column_name = node.metadata.get("column_name", "")
        table_columns[table_name].append((column_name, node.score))
    
    print(f"\n累积检索了 {len(all_nodes)} 列，来自 {len(table_columns)} 个表")
    
    if EXPECTED_TABLE.lower() in [t.lower() for t in table_columns.keys()]:
        target_cols = [c for t, cols in table_columns.items() if t.lower() == EXPECTED_TABLE.lower() for c in cols]
        print(f"目标表 {EXPECTED_TABLE} 的列: {len(target_cols)} 个")
        for col, score in sorted(target_cols, key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {col}: {score:.4f}")
    else:
        print(f"❌ 目标表 {EXPECTED_TABLE} 在所有轮次中都没有被检索到！")


if __name__ == "__main__":
    run_multi_turn_test()
