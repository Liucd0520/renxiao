#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE-M3 混合检索测试（无需 Milvus）

直接使用 BGE-M3 的 compute_score 方法计算 Dense + Sparse 混合分数
适合小规模场景（< 1000 文档）
"""

import os
import sys
import json
import time
from pathlib import Path
from collections import defaultdict

# 添加项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel
import numpy as np

# 配置
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"

# 混合权重 [dense, sparse, colbert]
HYBRID_WEIGHTS = [0.6, 0.3, 0.1]  # 可调整

# 测试用例
TEST_CASES = [
    {
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected": ["event_history", "t_bz_config_ci_ne_root"]
    },
    {
        "question": "现在平台上有多少台设备",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "现在平台上有多少家客户",
        "expected": ["t_bz_config_customer"]
    },
    {
        "question": "上个月上线的新设备有多少",
        "expected": ["t_bz_config_ci_ne_root"]
    },
]


def load_table_schemas():
    """加载所有表 Schema"""
    schemas = []
    schema_dir = Path(TABLE_SCHEMA_DIR)
    
    print(f"从 {TABLE_SCHEMA_DIR} 加载 Schema...")
    
    for json_file in schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("table_name", json_file.stem)
        
        # 构建 embedding text
        text_parts = [f"表名: {table_name}"]
        if data.get("llm_description"):
            text_parts.append(f"描述: {data['llm_description']}")
        elif data.get("table_comment"):
            text_parts.append(f"描述: {data['table_comment']}")
        
        # 添加列信息
        columns = data.get("columns", [])
        if columns:
            col_names = [c.get("name", "") for c in columns[:20]]
            text_parts.append(f"列: {', '.join(col_names)}")
        
        text = "\n".join(text_parts)
        
        schemas.append({
            "table_name": table_name,
            "text": text
        })
    
    print(f"✅ 加载了 {len(schemas)} 个表 Schema")
    return schemas


def hybrid_search_with_compute_score(model, query, schemas, top_k=10):
    """
    使用 BGE-M3 的 compute_score 进行混合检索
    
    compute_score 返回:
    {
      'colbert': [...],
      'sparse': [...],
      'dense': [...],
      'sparse+dense': [...],
      'colbert+sparse+dense': [...]
    }
    """
    # 构建查询-文档对
    sentence_pairs = [[query, s["text"]] for s in schemas]
    
    # 使用 compute_score 计算混合分数
    scores = model.compute_score(
        sentence_pairs,
        max_passage_length=512,  # 限制长度加速
        weights_for_different_modes=HYBRID_WEIGHTS
    )
    
    # 获取混合分数 (sparse+dense 或 colbert+sparse+dense)
    hybrid_scores = scores['colbert+sparse+dense']  # 使用全混合分数
    
    # 排序并返回 Top K
    indexed_scores = list(enumerate(hybrid_scores))
    indexed_scores.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    for idx, score in indexed_scores[:top_k]:
        results.append({
            "table_name": schemas[idx]["table_name"],
            "score": score,
            "dense_score": scores['dense'][idx],
            "sparse_score": scores['sparse'][idx],
            "colbert_score": scores['colbert'][idx]
        })
    
    return results


def run_hybrid_test():
    print("=" * 80)
    print("BGE-M3 混合检索测试（compute_score 方式）")
    print("=" * 80)
    print(f"混合权重: Dense={HYBRID_WEIGHTS[0]}, Sparse={HYBRID_WEIGHTS[1]}, ColBERT={HYBRID_WEIGHTS[2]}")
    print("=" * 80)
    
    # 1. 初始化模型
    print("\n[初始化] 加载 BGE-M3 模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    print("✅ 模型加载完成")
    
    # 2. 加载 Schema
    schemas = load_table_schemas()
    
    # 3. 测试检索
    print("\n" + "=" * 80)
    print("开始测试")
    print("=" * 80)
    
    results_summary = []
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}: {case['question'][:40]}...")
        print(f"期望表: {case['expected']}")
        print("-" * 60)
        
        expected_set = set(t.lower() for t in case['expected'])
        
        # 执行混合检索
        start_time = time.time()
        results = hybrid_search_with_compute_score(model, case['question'], schemas, top_k=10)
        elapsed = time.time() - start_time
        
        print(f"耗时: {elapsed:.2f}s")
        print("\nTop 10 结果:")
        print(f"{'排名':<4} | {'表名':<35} | {'混合分':>8} | {'Dense':>7} | {'Sparse':>7} | {'ColBERT':>7}")
        print("-" * 80)
        
        retrieved_tables = []
        for j, r in enumerate(results, 1):
            is_exp = "✅" if r['table_name'].lower() in expected_set else ""
            print(f"{j:<4} | {r['table_name']:<35} | {r['score']:>8.4f} | {r['dense_score']:>7.4f} | {r['sparse_score']:>7.4f} | {r['colbert_score']:>7.4f} {is_exp}")
            retrieved_tables.append(r['table_name'].lower())
        
        retrieved_set = set(retrieved_tables)
        recall = len(expected_set & retrieved_set) / len(expected_set)
        
        print(f"\n召回率: {recall:.0%}")
        if recall < 1.0:
            print(f"❌ 缺失: {expected_set - retrieved_set}")
        
        results_summary.append(recall)
    
    # 4. 汇总
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    
    avg_recall = sum(results_summary) / len(results_summary)
    full_recall = sum(1 for r in results_summary if r == 1.0)
    
    print(f"平均召回率: {avg_recall:.0%}")
    print(f"完全召回: {full_recall}/{len(results_summary)}")
    
    for i, recall in enumerate(results_summary, 1):
        status = "✅" if recall == 1.0 else "❌"
        print(f"  Case {i}: {recall:.0%} {status}")


if __name__ == "__main__":
    run_hybrid_test()
