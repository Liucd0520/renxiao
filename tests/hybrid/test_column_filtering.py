#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列级别过滤测试

流程：
1. 表级别+列级别融合 → 获取候选表（Top 10-20）
2. 对候选表的每个列计算 Sparse 相似度
3. 过滤掉低分列，只保留相关列
4. 评估：是否保留了 SQL 中需要的列？
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

TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"

# 测试用例：问题 + 期望表 + SQL中需要的列
TEST_CASES = [
    {
        "id": 1,
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root"],
        "expected_columns": {
            "event_history": ["event_type_name", "event_id", "ne_id", "event_time"],
            "t_bz_config_ci_ne_root": ["ne_id", "host_name"]
        }
    },
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "expected_tables": ["t_bz_config_customer"],
        "expected_columns": {
            "t_bz_config_customer": ["customer_id", "is_active"]
        }
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "expected_columns": {
            "t_bz_config_ci_ne_root": ["ci_id", "is_deleted"]
        }
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "expected_columns": {
            "t_bz_config_ci_ne_root": ["ci_id", "online_time"]
        }
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "expected_columns": {
            "t_bz_config_ci_ne_root": ["ci_id", "offline_time"]
        }
    },
]


def load_table_schemas():
    schemas = {}
    for json_file in Path(TABLE_SCHEMA_DIR).glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data.get("table_name", data.get("meta_data", {}).get("table_name", json_file.stem))
        text = data.get("embedding_text", data.get("llm_description", f"表名: {table_name}"))
        schemas[table_name.lower()] = {"table_name": table_name, "text": text}
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
            text_parts.append(f"示例: {', '.join(str(s) for s in data['sample_rows'][:3])}")
        schemas.append({
            "table_name": table_name.lower(),
            "column_name": column_name.lower(),
            "text": "\n".join(text_parts)
        })
    return schemas


def sparse_scores(model, query, texts):
    """计算 Sparse 相似度分数"""
    sentence_pairs = [[query, t] for t in texts]
    scores = model.compute_score(sentence_pairs, max_passage_length=512, weights_for_different_modes=[0.0, 1.0, 0.0])
    return scores['sparse']


def test_column_filtering():
    print("=" * 80)
    print("列级别过滤测试")
    print("=" * 80)
    
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    table_schemas = load_table_schemas()
    column_schemas = load_column_schemas()
    
    print(f"表: {len(table_schemas)}, 列: {len(column_schemas)}")
    
    # 阈值测试
    thresholds = [0.05, 0.08, 0.10, 0.12]
    
    for case in TEST_CASES:
        print(f"\n{'=' * 60}")
        print(f"测试 {case['id']}: {case['question'][:40]}...")
        print(f"期望表: {case['expected_tables']}")
        
        # 假设我们已经通过表+列融合得到了正确的候选表
        candidate_tables = [t.lower() for t in case['expected_tables']]
        
        # 获取候选表的所有列
        candidate_columns = [c for c in column_schemas if c['table_name'] in candidate_tables]
        print(f"候选表的总列数: {len(candidate_columns)}")
        
        # 计算每个列的 Sparse 分数
        column_texts = [c['text'] for c in candidate_columns]
        scores = sparse_scores(model, case['question'], column_texts)
        
        # 添加分数到列信息
        for i, c in enumerate(candidate_columns):
            c['score'] = scores[i]
        
        # 按分数排序，展示 Top 10
        sorted_cols = sorted(candidate_columns, key=lambda x: x['score'], reverse=True)
        print("\n列分数 Top 10:")
        for i, c in enumerate(sorted_cols[:10], 1):
            table = c['table_name']
            col = c['column_name']
            expected = case['expected_columns'].get(table, [])
            hit = "✅" if col in [e.lower() for e in expected] else ""
            print(f"  {i}. {table}.{col} ({c['score']:.4f}) {hit}")
        
        # 测试不同阈值
        print("\n阈值测试:")
        for threshold in thresholds:
            kept_cols = [c for c in candidate_columns if c['score'] >= threshold]
            
            # 计算召回率
            total_expected = 0
            total_recalled = 0
            for table, expected_cols in case['expected_columns'].items():
                table_lower = table.lower()
                expected_cols_lower = [c.lower() for c in expected_cols]
                total_expected += len(expected_cols_lower)
                
                kept_in_table = [c for c in kept_cols if c['table_name'] == table_lower]
                recalled = sum(1 for c in kept_in_table if c['column_name'] in expected_cols_lower)
                total_recalled += recalled
            
            recall = total_recalled / total_expected if total_expected > 0 else 0
            reduction = 1 - len(kept_cols) / len(candidate_columns) if candidate_columns else 0
            
            print(f"  阈值 {threshold:.2f}: 保留 {len(kept_cols):3d} 列 (减少 {reduction:.0%}), 召回 {recall:.0%}")
    
    print("\n" + "=" * 80)
    print("测试完成")


if __name__ == "__main__":
    test_column_filtering()
