#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE-M3 三种模式对比测试

对比：
1. Dense（稠密向量）
2. Sparse（稀疏向量/词法匹配）
3. ColBERT（多向量）
4. Dense + Sparse 混合
5. Dense + Sparse + ColBERT 全混合

使用 BGE-M3 的 compute_score 官方方法
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel
import numpy as np

# 配置
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"
TOP_K = 10

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
    """加载所有表 Schema，使用 JSON 中的 embedding_text 字段"""
    schemas = []
    schema_dir = Path(TABLE_SCHEMA_DIR)
    
    for json_file in schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("table_name", data.get("meta_data", {}).get("table_name", json_file.stem))
        
        # 使用 JSON 中已有的 embedding_text 字段！
        text = data.get("embedding_text", "")
        if not text:
            # 兜底：如果没有 embedding_text，用 llm_description
            text = data.get("llm_description", f"表名: {table_name}")
        
        schemas.append({"table_name": table_name, "text": text})
    
    return schemas


def compute_recall(retrieved_tables, expected_tables):
    """计算召回率"""
    retrieved_set = set(t.lower() for t in retrieved_tables)
    expected_set = set(t.lower() for t in expected_tables)
    return len(expected_set & retrieved_set) / len(expected_set) if expected_set else 0


def run_all_modes_test():
    print("=" * 80)
    print("BGE-M3 三种模式对比测试")
    print("=" * 80)
    
    # 1. 初始化
    print("\n[初始化] 加载 BGE-M3 模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    print("✅ 模型加载完成")
    
    # 2. 加载 Schema
    print("\n[加载] 读取表 Schema...")
    schemas = load_table_schemas()
    print(f"✅ 加载了 {len(schemas)} 个表 Schema")
    
    # 3. 预先编码所有文档（用于 compute_score）
    print("\n[编码] 预先生成所有文档的嵌入...")
    doc_texts = [s["text"] for s in schemas]
    
    # 4. 测试每个模式
    modes = ["dense", "sparse", "colbert", "sparse+dense", "colbert+sparse+dense"]
    results = {mode: [] for mode in modes}
    
    print("\n" + "=" * 80)
    print("开始测试")
    print("=" * 80)
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}: {case['question'][:40]}...")
        print(f"期望表: {case['expected']}")
        print("-" * 60)
        
        # 构建 query-doc pairs
        sentence_pairs = [[case['question'], doc_text] for doc_text in doc_texts]
        
        # 使用 compute_score 计算所有模式的分数
        scores = model.compute_score(
            sentence_pairs,
            max_passage_length=512,
            weights_for_different_modes=[0.4, 0.3, 0.3]  # [dense, sparse, colbert]
        )
        
        # 对每种模式计算 Top K 并评估
        print(f"\n{'模式':<25} | {'Top 1':^20} | {'召回率':^8}")
        print("-" * 60)
        
        for mode in modes:
            mode_scores = scores[mode]
            
            # 排序获取 Top K
            indexed_scores = list(enumerate(mode_scores))
            indexed_scores.sort(key=lambda x: x[1], reverse=True)
            
            top_k_tables = [schemas[idx]["table_name"] for idx, _ in indexed_scores[:TOP_K]]
            recall = compute_recall(top_k_tables, case['expected'])
            results[mode].append(recall)
            
            top1 = top_k_tables[0] if top_k_tables else "N/A"
            top1_short = top1[:18] + ".." if len(top1) > 18 else top1
            
            print(f"{mode:<25} | {top1_short:^20} | {recall:^8.0%}")
    
    # 5. 汇总
    print("\n" + "=" * 80)
    print("测试汇总（7 个测试用例）")
    print("=" * 80)
    
    print(f"\n{'模式':<25} | {'平均召回率':^12} | {'完全召回':^10}")
    print("-" * 55)
    
    for mode in modes:
        avg_recall = sum(results[mode]) / len(results[mode])
        full_recall = sum(1 for r in results[mode] if r == 1.0)
        print(f"{mode:<25} | {avg_recall:^12.0%} | {full_recall:^10}/{len(TEST_CASES)}")
    
    # 6. 逐测试对比表
    print("\n" + "-" * 80)
    print("逐测试召回率对比")
    print("-" * 80)
    
    header = f"{'测试':<5}"
    for mode in modes:
        header += f" | {mode[:12]:^12}"
    print(header)
    print("-" * 80)
    
    for i, case in enumerate(TEST_CASES):
        row = f"{i+1:<5}"
        for mode in modes:
            recall = results[mode][i]
            status = "✅" if recall == 1.0 else ""
            row += f" | {recall:^10.0%}{status:^2}"
        print(row)
    
    print("=" * 80)


if __name__ == "__main__":
    run_all_modes_test()
