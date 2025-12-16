#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表级别检索测试脚本

测试表级别向量检索的效果，对比问题与检索到的表。
"""

import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import VectorIndexRetriever

from embed_model.EmbedModelPathMap import embed_model_map_name_to_path


def load_table_index(persist_dir, embed_model_name="BAAI/bge-large-en-v1.5"):
    """加载表级别向量索引"""
    embed_model_path = embed_model_map_name_to_path.get(embed_model_name, embed_model_name)
    Settings.embed_model = HuggingFaceEmbedding(embed_model_path)
    
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    return index


def retrieve_tables(index, question, top_k=8):
    """检索相关表"""
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
    nodes = retriever.retrieve(question)
    
    results = []
    for node in nodes:
        results.append({
            "table_name": node.metadata.get("table_name", "unknown"),
            "score": node.score,
            "column_count": node.metadata.get("column_count", 0),
            "text_preview": node.text[:200] + "..." if len(node.text) > 200 else node.text
        })
    
    return results


def expand_table_to_columns(table_name, schema_dir):
    """展开表的所有列信息"""
    schema_file = Path(schema_dir) / f"{table_name}.json"
    
    if not schema_file.exists():
        return []
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    return schema_data.get("columns", [])


def test_table_retrieval(index, questions, schema_dir, top_k=8):
    """测试表级别检索"""
    for q in questions:
        print("\n" + "=" * 70)
        print(f"问题: {q['question']}")
        if q.get('expected_tables'):
            print(f"期望表: {q['expected_tables']}")
        print("-" * 70)
        
        results = retrieve_tables(index, q['question'], top_k)
        
        retrieved_tables = [r['table_name'] for r in results]
        
        # 检查召回率
        if q.get('expected_tables'):
            expected = set(q['expected_tables'])
            retrieved = set(retrieved_tables)
            hit = expected & retrieved
            recall = len(hit) / len(expected) if expected else 0
            print(f"召回率: {recall:.1%} ({len(hit)}/{len(expected)})")
            if hit:
                print(f"命中: {list(hit)}")
            missed = expected - retrieved
            if missed:
                print(f"遗漏: {list(missed)}")
        
        print(f"\n检索到的表 (top_{top_k}):")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['table_name']} (score: {r['score']:.4f}, 列数: {r['column_count']})")
        
        # 展示第一张表的列信息
        if results:
            first_table = results[0]['table_name']
            columns = expand_table_to_columns(first_table, schema_dir)
            if columns:
                col_names = [c['name'] for c in columns[:10]]
                print(f"\n第一张表 {first_table} 的列 (前10列):")
                print(f"  {', '.join(col_names)}")
                if len(columns) > 10:
                    print(f"  ... 等共 {len(columns)} 列")


def main():
    parser = argparse.ArgumentParser(description="测试表级别检索")
    parser.add_argument(
        "--persist-dir",
        default="./spider2_dev/schemas_table_level/netcaredb_ai/table_vector_store",
        help="向量索引目录"
    )
    parser.add_argument(
        "--schema-dir",
        default="./spider2_dev/schemas_table_level/netcaredb_ai",
        help="表级别 schema 目录"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=8,
        help="检索的表数量"
    )
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="自定义问题"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("表级别检索测试".center(70))
    print("=" * 70)
    
    # 加载索引
    print("加载向量索引...")
    index = load_table_index(args.persist_dir)
    print("✅ 索引加载完成")
    
    # 测试问题
    if args.question:
        test_questions = [{"question": args.question}]
    else:
        # 使用默认测试问题
        test_questions = [
            {
                "question": "查询客户小明的联系方式",
                "expected_tables": ["t_bz_config_customer"]
            },
            {
                "question": "统计上个月有多少告警事件",
                "expected_tables": ["event_history", "event_backup"]
            },
            {
                "question": "查看设备的端口状态",
                "expected_tables": ["sdw_dp_port_basic", "sdw_dp_device"]
            },
            {
                "question": "获取用户的角色权限信息",
                "expected_tables": ["framework_user", "framework_role", "framework_user_role"]
            },
            {
                "question": "查询变更工单的审批状态",
                "expected_tables": ["t_bz_change_info"]
            }
        ]
    
    test_table_retrieval(index, test_questions, args.schema_dir, args.top_k)
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
