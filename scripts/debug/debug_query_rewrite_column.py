#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LinkAlign 查询重写对列级别检索的帮助

使用 LinkAlign 的 CROSS_LINGUAL_EXPANSION_TEMPLATE 进行查询扩展，
然后测试扩展后的查询在列级别检索中的效果。
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

# 配置
VECTOR_STORE_DIR = "./spider2_dev/schemas/netcaredb_ai/vector_store_bge_m3_enhanced"
TOP_K = 100

# 测试问题
TEST_QUESTION = "现在平台上有多少台设备"
EXPECTED_TABLE = "t_bz_config_ci_ne_root"


def run_query_rewrite_test():
    print("=" * 80)
    print("查询重写 + 列级别检索测试")
    print("=" * 80)
    print(f"\n原始问题: {TEST_QUESTION}")
    print(f"期望表: {EXPECTED_TABLE}")
    print("=" * 80)
    
    # 1. 初始化
    print("\n[Step 1] 初始化模型...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    print("✅ 模型初始化完成")
    
    # 2. 查询重写
    print("\n[Step 2] 使用 LinkAlign 的跨语言查询扩展...")
    prompt = CROSS_LINGUAL_EXPANSION_TEMPLATE.format(question=TEST_QUESTION)
    
    print("\n--- 发送给 LLM 的 Prompt ---")
    print(prompt)
    print("-" * 40)
    
    expanded_query = llm.complete(prompt).text.strip()
    
    # 清理可能的 <think> 标签
    if '<think>' in expanded_query:
        expanded_query = expanded_query.split('</think>')[-1].strip()
    
    print(f"\n扩展后的查询:")
    print(expanded_query)
    
    # 组合查询
    combined_query = TEST_QUESTION + " " + expanded_query
    print(f"\n组合查询:")
    print(combined_query[:200] + "..." if len(combined_query) > 200 else combined_query)
    
    # 3. 加载索引
    print("\n[Step 3] 加载向量索引...")
    storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_DIR)
    vector_index = load_index_from_storage(storage_context)
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=TOP_K)
    print("✅ 索引加载完成")
    
    # 4. 检索对比
    print("\n[Step 4] 检索对比...")
    
    # 原始查询
    print("\n--- A. 原始中文查询 ---")
    nodes_original = retriever.retrieve(TEST_QUESTION)
    target_original = find_target_rank(nodes_original, EXPECTED_TABLE)
    
    # 扩展后查询
    print("\n--- B. 扩展后查询 ---")
    nodes_expanded = retriever.retrieve(combined_query)
    target_expanded = find_target_rank(nodes_expanded, EXPECTED_TABLE)
    
    # 5. 结果对比
    print("\n" + "=" * 80)
    print("结果对比")
    print("=" * 80)
    
    print(f"\n查询类型       | 目标表最高排名 | 目标表列数")
    print("-" * 50)
    print(f"原始中文       | #{target_original['best_rank']:3d}         | {target_original['col_count']}")
    print(f"扩展后查询     | #{target_expanded['best_rank']:3d}         | {target_expanded['col_count']}")
    
    # 6. 分析
    print("\n" + "=" * 80)
    print("分析")
    print("=" * 80)
    
    if target_expanded['best_rank'] < target_original['best_rank']:
        improvement = target_original['best_rank'] - target_expanded['best_rank']
        print(f"\n✅ 查询重写有帮助！排名从 #{target_original['best_rank']} 提升到 #{target_expanded['best_rank']} (提升 {improvement} 位)")
    elif target_expanded['best_rank'] == target_original['best_rank']:
        print(f"\n➡️ 查询重写没有变化，排名仍为 #{target_original['best_rank']}")
    else:
        decline = target_expanded['best_rank'] - target_original['best_rank']
        print(f"\n❌ 查询重写反而变差！排名从 #{target_original['best_rank']} 下降到 #{target_expanded['best_rank']} (下降 {decline} 位)")
    
    # 是否进入 Top 10
    if target_expanded['best_rank'] <= 10:
        print(f"✅ 目标表进入 Top 10！")
    else:
        print(f"❌ 目标表仍未进入 Top 10（需要排名 <= 10）")
    
    # 展示扩展后查询的 Top 10 表
    print("\n扩展后查询的 Top 10 表:")
    top_tables = get_top_tables(nodes_expanded, 10)
    for i, (table, score, col_count) in enumerate(top_tables, 1):
        is_target = "✅ TARGET" if table.lower() == EXPECTED_TABLE.lower() else ""
        print(f"  {i}. {table} (score={score:.4f}, {col_count}列) {is_target}")


def find_target_rank(nodes, target_table):
    """找到目标表在检索结果中的排名"""
    table_data = defaultdict(lambda: {"best_rank": float('inf'), "col_count": 0})
    
    for i, node in enumerate(nodes, 1):
        table_name = node.metadata.get("table_name", "")
        if table_name.lower() == target_table.lower():
            table_data[target_table]["col_count"] += 1
            if i < table_data[target_table]["best_rank"]:
                table_data[target_table]["best_rank"] = i
    
    result = table_data[target_table]
    if result["best_rank"] == float('inf'):
        result["best_rank"] = -1  # 未找到
    
    return result


def get_top_tables(nodes, n):
    """获取按 Max Score 聚合后的 Top N 表"""
    table_scores = {}
    table_counts = defaultdict(int)
    
    for node in nodes:
        table_name = node.metadata.get("table_name", "")
        score = node.score
        table_counts[table_name] += 1
        
        if table_name not in table_scores or score > table_scores[table_name]:
            table_scores[table_name] = score
    
    sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
    
    return [(table, score, table_counts[table]) for table, score in sorted_tables[:n]]


if __name__ == "__main__":
    run_query_rewrite_test()
