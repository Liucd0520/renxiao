#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析失败 case 中目标表的排名位置
检查是否增加 Top K 到 15-20 能帮助
"""

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel
import numpy as np

TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"

# 失败的测试用例
FAILED_CASES = [
    {
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected": ["event_history", "t_bz_config_ci_ne_root"]
    },
    {
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected": ["t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"]
    },
    {
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]
    },
]


def load_table_schemas():
    schemas = []
    schema_dir = Path(TABLE_SCHEMA_DIR)
    
    for json_file in schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("table_name", json_file.stem)
        text_parts = [f"表名: {table_name}"]
        if data.get("llm_description"):
            text_parts.append(f"描述: {data['llm_description']}")
        columns = data.get("columns", [])
        if columns:
            col_names = [c.get("name", "") for c in columns[:20]]
            text_parts.append(f"列: {', '.join(col_names)}")
        
        text = "\n".join(text_parts)
        schemas.append({"table_name": table_name, "text": text})
    
    return schemas


def run_ranking_analysis():
    print("=" * 80)
    print("失败 Case 排名分析")
    print("=" * 80)
    
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    schemas = load_table_schemas()
    doc_texts = [s["text"] for s in schemas]
    
    for i, case in enumerate(FAILED_CASES, 1):
        print(f"\n{'=' * 60}")
        print(f"Case {i}: {case['question'][:50]}...")
        print(f"期望表: {case['expected']}")
        print("-" * 60)
        
        sentence_pairs = [[case['question'], doc_text] for doc_text in doc_texts]
        scores = model.compute_score(
            sentence_pairs,
            max_passage_length=512,
            weights_for_different_modes=[0.4, 0.3, 0.3]
        )
        
        # 分析每种模式下期望表的排名
        modes = ["dense", "sparse", "colbert"]
        
        for mode in modes:
            mode_scores = scores[mode]
            indexed_scores = list(enumerate(mode_scores))
            indexed_scores.sort(key=lambda x: x[1], reverse=True)
            
            rankings = {}
            for rank, (idx, score) in enumerate(indexed_scores, 1):
                table_name = schemas[idx]["table_name"]
                if table_name.lower() in [t.lower() for t in case['expected']]:
                    rankings[table_name] = rank
            
            print(f"\n[{mode.upper()}] 期望表排名:")
            for table in case['expected']:
                rank = rankings.get(table, "未找到")
                in_top_k = ""
                if isinstance(rank, int):
                    if rank <= 10:
                        in_top_k = "✅ 在 Top 10"
                    elif rank <= 15:
                        in_top_k = "⚠️ 在 Top 15"
                    elif rank <= 20:
                        in_top_k = "⚠️ 在 Top 20"
                    else:
                        in_top_k = f"❌ 需要 Top {rank}"
                print(f"  {table}: #{rank} {in_top_k}")


if __name__ == "__main__":
    run_ranking_analysis()
