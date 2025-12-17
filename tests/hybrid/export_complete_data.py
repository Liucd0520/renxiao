#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出完整检索数据（200列 + 10表）
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
OUTPUT_DIR = "./docs/retrieval_data"

TABLE_TOP_K = 10
COLUMN_TOP_K = 200

TEST_CASES = [
    {"id": 1, "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计", "expected": ["event_history", "t_bz_config_ci_ne_root"]},
    {"id": 2, "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称", "expected": ["t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"]},
]


def load_table_schemas():
    schemas = []
    for json_file in sorted(Path(TABLE_SCHEMA_DIR).glob("*.json")):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data.get("table_name", data.get("meta_data", {}).get("table_name", json_file.stem))
        text = data.get("embedding_text", data.get("llm_description", f"表名: {table_name}"))
        schemas.append({"table_name": table_name, "text": text})
    return schemas


def load_column_schemas():
    schemas = []
    for json_file in sorted(Path(COLUMN_SCHEMA_DIR).glob("*.json")):
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
        schemas.append({"table_name": table_name, "column_name": column_name, "text": "\n".join(text_parts)})
    return schemas


def sparse_retrieve(model, query, schemas, top_k):
    sentence_pairs = [[query, s["text"]] for s in schemas]
    scores = model.compute_score(sentence_pairs, max_passage_length=512, weights_for_different_modes=[0.0, 1.0, 0.0])
    indexed = sorted(enumerate(scores['sparse']), key=lambda x: x[1], reverse=True)
    return indexed[:top_k]


def export_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("加载模型和数据...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    table_schemas = load_table_schemas()
    column_schemas = load_column_schemas()
    print(f"表: {len(table_schemas)}, 列: {len(column_schemas)}")
    
    for case in TEST_CASES:
        print(f"\n处理测试 {case['id']}: {case['question'][:30]}...")
        expected_set = set(t.lower() for t in case['expected'])
        
        # 表级别
        table_results = sparse_retrieve(model, case['question'], table_schemas, TABLE_TOP_K)
        
        # 列级别
        column_results = sparse_retrieve(model, case['question'], column_schemas, COLUMN_TOP_K)
        
        # 累加分
        table_scores = defaultdict(float)
        for idx, score in column_results:
            table_scores[column_schemas[idx]["table_name"]] += score
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 保存为 Markdown
        output_file = f"{OUTPUT_DIR}/test_{case['id']}_complete_data.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 测试 {case['id']} 完整检索数据\n\n")
            f.write(f"**问题**: {case['question']}\n\n")
            f.write(f"**期望表**: {case['expected']}\n\n")
            f.write("---\n\n")
            
            # 表级别 Top 10
            f.write("## 一、表级别 Sparse Top 10\n\n")
            f.write("| 排名 | 表名 | 分数 | 命中 |\n")
            f.write("|-----|------|------|-----|\n")
            for j, (idx, score) in enumerate(table_results, 1):
                table = table_schemas[idx]["table_name"]
                hit = "✅" if table.lower() in expected_set else ""
                f.write(f"| {j} | {table} | {score:.4f} | {hit} |\n")
            
            table_set = set(table_schemas[idx]["table_name"].lower() for idx, _ in table_results)
            f.write(f"\n**表级别召回**: {len(expected_set & table_set)}/{len(expected_set)}\n\n")
            
            # 列级别 Top 200
            f.write("---\n\n")
            f.write("## 二、列级别 Sparse Top 200\n\n")
            f.write("| 排名 | 表名 | 列名 | 分数 |\n")
            f.write("|-----|------|------|-----|\n")
            for j, (idx, score) in enumerate(column_results, 1):
                table = column_schemas[idx]["table_name"]
                col = column_schemas[idx]["column_name"]
                f.write(f"| {j} | {table} | {col} | {score:.4f} |\n")
            
            # 累加分 Top 10
            f.write("\n---\n\n")
            f.write("## 三、列级别累加分 Top 10 表\n\n")
            f.write("| 排名 | 表名 | 累加分 | 命中 |\n")
            f.write("|-----|------|-------|-----|\n")
            for j, (table, score) in enumerate(sorted_tables[:TABLE_TOP_K], 1):
                hit = "✅" if table.lower() in expected_set else ""
                f.write(f"| {j} | {table} | {score:.4f} | {hit} |\n")
            
            column_set = set(t.lower() for t, _ in sorted_tables[:TABLE_TOP_K])
            f.write(f"\n**列级别召回**: {len(expected_set & column_set)}/{len(expected_set)}\n\n")
            
            # 融合
            fusion_set = table_set | column_set
            f.write("---\n\n")
            f.write("## 四、融合结果\n\n")
            f.write(f"- 表级别贡献: {len(table_set)} 个表\n")
            f.write(f"- 列级别贡献: {len(column_set)} 个表\n")
            f.write(f"- 融合并集: {len(fusion_set)} 个表\n")
            f.write(f"- **融合召回**: {len(expected_set & fusion_set)}/{len(expected_set)}\n")
            if expected_set - fusion_set:
                f.write(f"- **缺失**: {expected_set - fusion_set}\n")
        
        print(f"  保存到: {output_file}")
    
    print(f"\n完成！数据保存到 {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_data()
