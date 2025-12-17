#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表级别 + 列级别融合检索测试

策略：
- 表级别：Sparse 模式（74% 召回率）
- 列级别：Sparse 模式累加分
- 融合：并集
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel
import numpy as np

# 配置
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"  # 列级别 Schema
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"

TABLE_TOP_K = 10
COLUMN_TOP_K = 200  # 列级别检索更多

# 测试用例（完整 7 个）
TEST_CASES = [
    {
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected": ["event_history", "t_bz_config_ci_ne_root"]
    },
    {
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected": ["t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"]
    },
    {
        "question": "现在平台上有多少家客户",
        "expected": ["t_bz_config_customer"]
    },
    {
        "question": "现在平台上有多少台设备",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "上个月上线的新设备有多少",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "上个月下线的设备有多少",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]
    },
]


def load_table_schemas():
    """加载表级别 Schema"""
    schemas = []
    schema_dir = Path(TABLE_SCHEMA_DIR)
    
    for json_file in schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("table_name", data.get("meta_data", {}).get("table_name", json_file.stem))
        text = data.get("embedding_text", data.get("llm_description", f"表名: {table_name}"))
        
        schemas.append({"table_name": table_name, "text": text})
    
    return schemas


def load_column_schemas():
    """加载列级别 Schema"""
    schemas = []
    schema_dir = Path(COLUMN_SCHEMA_DIR)
    
    for json_file in schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 列级别 Schema 结构
        meta = data.get("meta_data", {})
        table_name = meta.get("table_name", "")
        column_name = data.get("column_name", "")
        
        # 构建列的 embedding_text
        text_parts = [f"表: {table_name}", f"列: {column_name}"]
        if data.get("column_descriptions"):
            text_parts.append(f"描述: {data['column_descriptions']}")
        if data.get("column_types"):
            text_parts.append(f"类型: {data['column_types']}")
        if data.get("sample_rows"):
            samples = data["sample_rows"][:5]
            text_parts.append(f"示例: {', '.join(str(s) for s in samples)}")
        
        text = "\n".join(text_parts)
        schemas.append({"table_name": table_name, "column_name": column_name, "text": text})
    
    return schemas


def sparse_retrieve(model, query, schemas, top_k):
    """使用 Sparse 模式检索"""
    sentence_pairs = [[query, s["text"]] for s in schemas]
    
    scores = model.compute_score(
        sentence_pairs,
        max_passage_length=512,
        weights_for_different_modes=[0.0, 1.0, 0.0]  # 只用 Sparse
    )
    
    sparse_scores = scores['sparse']
    indexed_scores = list(enumerate(sparse_scores))
    indexed_scores.sort(key=lambda x: x[1], reverse=True)
    
    return indexed_scores[:top_k]


def aggregate_column_to_table(column_results, column_schemas):
    """列级别累加分聚合到表"""
    table_scores = defaultdict(float)
    
    for idx, score in column_results:
        table_name = column_schemas[idx]["table_name"]
        table_scores[table_name] += score
    
    sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_tables


def run_fusion_test():
    print("=" * 80)
    print("表 + 列融合检索测试")
    print("=" * 80)
    print(f"表级别: Sparse Top {TABLE_TOP_K}")
    print(f"列级别: Sparse Top {COLUMN_TOP_K} → 累加分 → Top {TABLE_TOP_K}")
    print("融合策略: 并集")
    print("=" * 80)
    
    # 1. 初始化
    print("\n[初始化] 加载 BGE-M3 模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    print("✅ 模型加载完成")
    
    # 2. 加载 Schema
    print("\n[加载] 读取 Schema...")
    table_schemas = load_table_schemas()
    column_schemas = load_column_schemas()
    print(f"✅ 表级别: {len(table_schemas)} 个")
    print(f"✅ 列级别: {len(column_schemas)} 个")
    
    # 3. 测试
    results = {"table_only": [], "column_only": [], "fusion": []}
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}: {case['question'][:40]}...")
        print(f"期望表: {case['expected']}")
        print("-" * 60)
        
        expected_set = set(t.lower() for t in case['expected'])
        
        # 表级别 Sparse 检索
        table_results = sparse_retrieve(model, case['question'], table_schemas, TABLE_TOP_K)
        table_set = set(table_schemas[idx]["table_name"].lower() for idx, _ in table_results)
        table_recall = len(expected_set & table_set) / len(expected_set)
        results["table_only"].append(table_recall)
        
        print(f"\n[表级别 Sparse Top {TABLE_TOP_K}]")
        for j, (idx, score) in enumerate(table_results[:5], 1):
            table = table_schemas[idx]["table_name"]
            marker = "✅" if table.lower() in expected_set else ""
            print(f"  {j}. {table} ({score:.4f}) {marker}")
        print(f"  召回率: {table_recall:.0%}")
        
        # 列级别 Sparse 检索
        column_results = sparse_retrieve(model, case['question'], column_schemas, COLUMN_TOP_K)
        sorted_tables = aggregate_column_to_table(column_results, column_schemas)
        column_set = set(t.lower() for t, _ in sorted_tables[:TABLE_TOP_K])
        column_recall = len(expected_set & column_set) / len(expected_set)
        results["column_only"].append(column_recall)
        
        print(f"\n[列级别 Sparse Top {COLUMN_TOP_K} → 累加分]")
        for j, (table, score) in enumerate(sorted_tables[:5], 1):
            marker = "✅" if table.lower() in expected_set else ""
            print(f"  {j}. {table} ({score:.4f}) {marker}")
        print(f"  召回率: {column_recall:.0%}")
        
        # 融合（并集）
        fusion_set = table_set | column_set
        fusion_recall = len(expected_set & fusion_set) / len(expected_set)
        results["fusion"].append(fusion_recall)
        
        print(f"\n[融合 - 并集] ({len(fusion_set)} 个表)")
        print(f"  召回率: {fusion_recall:.0%}")
        if fusion_recall < 1.0:
            print(f"  缺失: {expected_set - fusion_set}")
    
    # 4. 汇总
    print("\n" + "=" * 80)
    print("测试汇总（7 个测试用例）")
    print("=" * 80)
    
    for method in ["table_only", "column_only", "fusion"]:
        avg = sum(results[method]) / len(results[method])
        full = sum(1 for r in results[method] if r == 1.0)
        print(f"{method:<15}: {avg:.0%} ({full}/7 完全召回)")
    
    print("\n" + "-" * 60)
    print("逐测试对比")
    print("-" * 60)
    print(f"{'测试':<5} | {'表级别':^10} | {'列级别':^10} | {'融合':^10}")
    print("-" * 45)
    
    for i in range(len(TEST_CASES)):
        t = results["table_only"][i]
        c = results["column_only"][i]
        f = results["fusion"][i]
        print(f"{i+1:<5} | {t:^10.0%} | {c:^10.0%} | {f:^10.0%}")


if __name__ == "__main__":
    run_fusion_test()
