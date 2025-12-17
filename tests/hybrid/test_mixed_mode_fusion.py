#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表级别 Dense + 列级别 Sparse 混合检索测试

创新点：
- 表级别使用 Dense 模式：利用表描述的语义丰富性
- 列级别使用 Sparse 模式：利用列名/样本数据的关键词精确匹配
- 融合策略：并集
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
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"

TABLE_TOP_K = 10
COLUMN_TOP_K = 200

# 测试用例
TEST_CASES = [
    {"question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计", "expected": ["event_history", "t_bz_config_ci_ne_root"]},
    {"question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称", "expected": ["t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"]},
    {"question": "现在平台上有多少家客户", "expected": ["t_bz_config_customer"]},
    {"question": "现在平台上有多少台设备", "expected": ["t_bz_config_ci_ne_root"]},
    {"question": "上个月上线的新设备有多少", "expected": ["t_bz_config_ci_ne_root"]},
    {"question": "上个月下线的设备有多少", "expected": ["t_bz_config_ci_ne_root"]},
    {"question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？", "expected": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]},
]


def load_table_schemas():
    schemas = []
    for json_file in Path(TABLE_SCHEMA_DIR).glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data.get("table_name", data.get("meta_data", {}).get("table_name", json_file.stem))
        text = data.get("embedding_text", data.get("llm_description", f"表名: {table_name}"))
        schemas.append({"table_name": table_name, "text": text})
    return schemas


def load_column_schemas():
    schemas = []
    for json_file in Path(COLUMN_SCHEMA_DIR).glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        meta = data.get("meta_data", {})
        table_name = meta.get("table_name", "")
        column_name = data.get("column_name", "")
        text_parts = [f"表: {table_name}", f"列: {column_name}"]
        if data.get("column_descriptions"):
            text_parts.append(f"描述: {data['column_descriptions']}")
        if data.get("sample_rows"):
            text_parts.append(f"示例: {', '.join(str(s) for s in data['sample_rows'][:5])}")
        schemas.append({"table_name": table_name, "text": "\n".join(text_parts)})
    return schemas


def dense_retrieve(model, query, schemas, top_k):
    """表级别使用 Dense 模式"""
    sentence_pairs = [[query, s["text"]] for s in schemas]
    scores = model.compute_score(sentence_pairs, max_passage_length=512, weights_for_different_modes=[1.0, 0.0, 0.0])
    indexed = sorted(enumerate(scores['dense']), key=lambda x: x[1], reverse=True)
    return indexed[:top_k]


def sparse_retrieve(model, query, schemas, top_k):
    """列级别使用 Sparse 模式"""
    sentence_pairs = [[query, s["text"]] for s in schemas]
    scores = model.compute_score(sentence_pairs, max_passage_length=512, weights_for_different_modes=[0.0, 1.0, 0.0])
    indexed = sorted(enumerate(scores['sparse']), key=lambda x: x[1], reverse=True)
    return indexed[:top_k]


def run_mixed_mode_test():
    print("=" * 80)
    print("创新策略：表级别 Dense + 列级别 Sparse 融合检索")
    print("=" * 80)
    print(f"表级别: Dense Top {TABLE_TOP_K}")
    print(f"列级别: Sparse Top {COLUMN_TOP_K} → 累加分 → Top {TABLE_TOP_K}")
    print("融合策略: 并集")
    print("=" * 80)
    
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    table_schemas = load_table_schemas()
    column_schemas = load_column_schemas()
    
    print(f"\n✅ 表: {len(table_schemas)} | 列: {len(column_schemas)}")
    
    results = {"table_dense": [], "column_sparse": [], "fusion": []}
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n--- 测试 {i}: {case['question'][:40]}... ---")
        expected_set = set(t.lower() for t in case['expected'])
        
        # 表级别 Dense
        table_results = dense_retrieve(model, case['question'], table_schemas, TABLE_TOP_K)
        table_set = set(table_schemas[idx]["table_name"].lower() for idx, _ in table_results)
        table_recall = len(expected_set & table_set) / len(expected_set)
        results["table_dense"].append(table_recall)
        
        # 列级别 Sparse
        column_results = sparse_retrieve(model, case['question'], column_schemas, COLUMN_TOP_K)
        table_scores = defaultdict(float)
        for idx, score in column_results:
            table_scores[column_schemas[idx]["table_name"]] += score
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        column_set = set(t.lower() for t, _ in sorted_tables[:TABLE_TOP_K])
        column_recall = len(expected_set & column_set) / len(expected_set)
        results["column_sparse"].append(column_recall)
        
        # 融合
        fusion_set = table_set | column_set
        fusion_recall = len(expected_set & fusion_set) / len(expected_set)
        results["fusion"].append(fusion_recall)
        
        print(f"  表Dense: {table_recall:.0%} | 列Sparse: {column_recall:.0%} | 融合: {fusion_recall:.0%}")
    
    # 汇总
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    
    for m in ["table_dense", "column_sparse", "fusion"]:
        avg = sum(results[m]) / len(results[m])
        full = sum(1 for r in results[m] if r == 1.0)
        print(f"{m:<15}: {avg:.0%} ({full}/7 完全召回)")


if __name__ == "__main__":
    run_mixed_mode_test()
