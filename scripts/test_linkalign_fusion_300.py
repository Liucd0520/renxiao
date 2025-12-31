#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkAlign 表+列融合检索测试 - 300 问题
基于 tests/hybrid/test_table_column_fusion.py 改进

算法说明：
- 表级别: BGE-M3 Sparse 模式检索 TOP 10
- 列级别: BGE-M3 Sparse 模式检索 TOP 200，累加分聚合到表，取 TOP 10
- 融合: 并集
"""

import os
import sys
import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

# 配置
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"  # 列级别 Schema
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"

TABLE_TOP_K = 10
COLUMN_TOP_K = 200  # 列级别检索更多


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
        
        meta = data.get("meta_data", {})
        table_name = meta.get("table_name", "")
        column_name = data.get("column_name", "")
        
        text_parts = [f"表: {table_name}", f"列: {column_name}"]
        if data.get("column_descriptions"):
            text_parts.append(f"描述: {data['column_descriptions']}")
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


def run_test_300(questions, model, table_schemas, column_schemas):
    """运行 300 问题测试"""
    results = {
        "table_only": {"full": 0, "partial": 0, "fail": 0},
        "column_only": {"full": 0, "partial": 0, "fail": 0},
        "fusion": {"full": 0, "partial": 0, "fail": 0},
        "by_difficulty": defaultdict(lambda: {
            "table_only": {"full": 0, "partial": 0, "fail": 0},
            "column_only": {"full": 0, "partial": 0, "fail": 0},
            "fusion": {"full": 0, "partial": 0, "fail": 0}
        })
    }
    
    fail_cases = []
    
    for i, case in enumerate(questions):
        expected = case.get("tables", [])
        if not expected:
            continue
        
        expected_set = set(t.lower() for t in expected)
        difficulty = case.get("difficulty", "unknown")
        
        # 表级别检索
        table_results = sparse_retrieve(model, case['question'], table_schemas, TABLE_TOP_K)
        table_set = set(table_schemas[idx]["table_name"].lower() for idx, _ in table_results)
        
        table_matched = expected_set & table_set
        if len(table_matched) == len(expected_set):
            results["table_only"]["full"] += 1
            results["by_difficulty"][difficulty]["table_only"]["full"] += 1
        elif table_matched:
            results["table_only"]["partial"] += 1
            results["by_difficulty"][difficulty]["table_only"]["partial"] += 1
        else:
            results["table_only"]["fail"] += 1
            results["by_difficulty"][difficulty]["table_only"]["fail"] += 1
        
        # 列级别检索
        column_results = sparse_retrieve(model, case['question'], column_schemas, COLUMN_TOP_K)
        sorted_tables = aggregate_column_to_table(column_results, column_schemas)
        column_set = set(t.lower() for t, _ in sorted_tables[:TABLE_TOP_K])
        
        column_matched = expected_set & column_set
        if len(column_matched) == len(expected_set):
            results["column_only"]["full"] += 1
            results["by_difficulty"][difficulty]["column_only"]["full"] += 1
        elif column_matched:
            results["column_only"]["partial"] += 1
            results["by_difficulty"][difficulty]["column_only"]["partial"] += 1
        else:
            results["column_only"]["fail"] += 1
            results["by_difficulty"][difficulty]["column_only"]["fail"] += 1
        
        # 融合（并集）
        fusion_set = table_set | column_set
        fusion_matched = expected_set & fusion_set
        if len(fusion_matched) == len(expected_set):
            results["fusion"]["full"] += 1
            results["by_difficulty"][difficulty]["fusion"]["full"] += 1
        elif fusion_matched:
            results["fusion"]["partial"] += 1
            results["by_difficulty"][difficulty]["fusion"]["partial"] += 1
            fail_cases.append({
                "question": case['question'][:60],
                "difficulty": difficulty,
                "expected": list(expected_set),
                "missed": list(expected_set - fusion_matched)
            })
        else:
            results["fusion"]["fail"] += 1
            results["by_difficulty"][difficulty]["fusion"]["fail"] += 1
            fail_cases.append({
                "question": case['question'][:60],
                "difficulty": difficulty,
                "expected": list(expected_set),
                "missed": list(expected_set)
            })
        
        if (i + 1) % 50 == 0:
            print(f"  已测试 {i+1}/{len(questions)}")
    
    return results, fail_cases


def generate_report(results, fail_cases, total, elapsed, output_path):
    """生成报告"""
    report = f"""# LinkAlign 表+列融合检索测试报告

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**测试问题**: {total} 个（simple/medium/hard 各 100）  
**目标表**: t_bz_config_ci_ne_root, t_bz_config_customer, event_history  
**耗时**: {elapsed:.1f} 秒

---

## 算法说明

| 方法 | 检索策略 |
|-----|---------|
| **表级别** | BGE-M3 Sparse TOP 10 |
| **列级别** | BGE-M3 Sparse TOP 200 → 累加分聚合 → TOP 10 |
| **融合** | 表级别 ∪ 列级别（并集） |

---

## 1. 总体结果

| 方法 | 完全召回 | 部分召回 | 失败 | 召回率 |
|-----|---------|---------|------|-------|
| **表级别** | {results['table_only']['full']} | {results['table_only']['partial']} | {results['table_only']['fail']} | **{results['table_only']['full']/total*100:.1f}%** |
| **列级别** | {results['column_only']['full']} | {results['column_only']['partial']} | {results['column_only']['fail']} | **{results['column_only']['full']/total*100:.1f}%** |
| **融合** | {results['fusion']['full']} | {results['fusion']['partial']} | {results['fusion']['fail']} | **{results['fusion']['full']/total*100:.1f}%** |

---

## 2. 按难度分析

| 难度 | 表级别 | 列级别 | 融合 |
|-----|-------|-------|-----|
"""
    
    for diff in ["simple", "medium", "hard"]:
        d = results["by_difficulty"][diff]
        t_total = d["table_only"]["full"] + d["table_only"]["partial"] + d["table_only"]["fail"]
        if t_total > 0:
            t_rate = d["table_only"]["full"] / t_total * 100
            c_rate = d["column_only"]["full"] / t_total * 100
            f_rate = d["fusion"]["full"] / t_total * 100
            report += f"| {diff} | {t_rate:.1f}% | {c_rate:.1f}% | **{f_rate:.1f}%** |\n"
    
    report += """
---

## 3. 失败案例

"""
    
    for c in fail_cases[:10]:
        report += f"- **{c['difficulty']}**: {c['question']}...\n"
        report += f"  - 缺失: {c['missed']}\n\n"
    
    report += f"""
---

## 4. 结论

- 融合方法召回率: **{results['fusion']['full']/total*100:.1f}%**
- 融合比单独表级别提升: +{(results['fusion']['full'] - results['table_only']['full'])/total*100:.1f}%
- 融合比单独列级别提升: +{(results['fusion']['full'] - results['column_only']['full'])/total*100:.1f}%

---
*报告自动生成*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report


def main():
    print("=" * 70)
    print("LinkAlign 表+列融合检索测试 - 300 问题")
    print("=" * 70)
    
    # 加载问题
    print("加载测试问题...")
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"加载了 {len(questions)} 个问题")
    
    # 初始化模型
    print("\n加载 BGE-M3 模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    print("✅ 模型加载完成")
    
    # 加载 Schema
    print("\n加载 Schema...")
    table_schemas = load_table_schemas()
    column_schemas = load_column_schemas()
    print(f"✅ 表级别: {len(table_schemas)} 个")
    print(f"✅ 列级别: {len(column_schemas)} 个")
    
    # 运行测试
    print("\n开始测试...")
    start_time = time.time()
    results, fail_cases = run_test_300(questions, model, table_schemas, column_schemas)
    elapsed = time.time() - start_time
    
    print(f"\n测试完成！耗时: {elapsed:.1f} 秒")
    
    # 生成报告
    total = len(questions)
    output_path = "./docs/milestone_20241224/linkalign_fusion_test_300_report.md"
    generate_report(results, fail_cases, total, elapsed, output_path)
    print(f"\n报告已保存: {output_path}")
    
    # 打印摘要
    print("\n" + "=" * 70)
    print("结果摘要")
    print("=" * 70)
    print(f"表级别: {results['table_only']['full']}/{total} ({results['table_only']['full']/total*100:.1f}%)")
    print(f"列级别: {results['column_only']['full']}/{total} ({results['column_only']['full']/total*100:.1f}%)")
    print(f"融合:   {results['fusion']['full']}/{total} ({results['fusion']['full']/total*100:.1f}%)")


if __name__ == "__main__":
    main()
