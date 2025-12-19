#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
100 个测试问题的表召回率测试（按难度分类）
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

# 配置
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
QUESTIONS_FILE = "./test_questions_100.json"
OUTPUT_FILE = "./docs/milestone_20241219/recall_test_100_by_difficulty.md"

TABLE_TOP_K = 10


def load_bge_m3():
    print("加载 BGE-M3 模型...")
    model = BGEM3FlagModel('./embed_model_cache/BAAI/bge-m3', use_fp16=True)
    print("模型加载完成")
    return model


def load_all_table_schemas():
    schemas = []
    table_dir = Path(TABLE_SCHEMA_DIR)
    for json_file in table_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            schemas.append({
                "table_name": data.get("table_name", json_file.stem),
                "embedding_text": data.get("embedding_text", ""),
            })
    return schemas


def load_all_column_schemas():
    columns = []
    col_dir = Path(COLUMN_SCHEMA_DIR)
    for json_file in col_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            meta = data.get("meta_data", {})
            columns.append({
                "table_name": meta.get("table_name", ""),
                "embedding_text": data.get("embedding_text", "")
            })
    return columns


def load_test_questions():
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def retrieve_tables_fusion(model, query, table_schemas, column_schemas):
    # 表级别 Sparse 检索
    table_texts = [t["embedding_text"] for t in table_schemas]
    table_pairs = [[query, t] for t in table_texts]
    
    table_scores = model.compute_score(
        table_pairs, max_passage_length=512,
        weights_for_different_modes=[0.0, 1.0, 0.0]
    )
    
    if isinstance(table_scores, dict):
        table_scores = table_scores.get('colbert+sparse+dense', table_scores.get('sparse', []))
    
    table_results = []
    for i, score in enumerate(table_scores):
        table_results.append({"table_name": table_schemas[i]["table_name"], "score": float(score)})
    table_results.sort(key=lambda x: x["score"], reverse=True)
    table_top = {r["table_name"]: r["score"] for r in table_results[:TABLE_TOP_K]}
    
    # 列级别 Sparse 检索
    col_texts = [c["embedding_text"] for c in column_schemas if c["embedding_text"]]
    col_pairs = [[query, c] for c in col_texts]
    
    col_scores = model.compute_score(
        col_pairs, max_passage_length=512,
        weights_for_different_modes=[0.0, 1.0, 0.0]
    )
    
    if isinstance(col_scores, dict):
        col_scores = col_scores.get('colbert+sparse+dense', col_scores.get('sparse', []))
    
    col_table_scores = {}
    valid_cols = [c for c in column_schemas if c["embedding_text"]]
    for i, score in enumerate(col_scores):
        table_name = valid_cols[i]["table_name"]
        if table_name not in col_table_scores:
            col_table_scores[table_name] = 0
        col_table_scores[table_name] += float(score)
    
    col_sorted = sorted(col_table_scores.items(), key=lambda x: x[1], reverse=True)
    col_top = {name: score for name, score in col_sorted[:TABLE_TOP_K]}
    
    fusion_tables = set(table_top.keys()) | set(col_top.keys())
    return list(fusion_tables)


def run_recall_test():
    print("=" * 70)
    print("100 个测试问题的表召回率测试（按难度分类）")
    print("=" * 70)
    
    model = load_bge_m3()
    table_schemas = load_all_table_schemas()
    column_schemas = load_all_column_schemas()
    questions = load_test_questions()
    
    print(f"表数量: {len(table_schemas)}")
    print(f"测试问题: {len(questions)} 个")
    
    # 按难度分类的统计
    stats = {
        "easy": {"total": 0, "full": 0, "partial": 0, "none": 0, "recall_sum": 0},
        "medium": {"total": 0, "full": 0, "partial": 0, "none": 0, "recall_sum": 0},
        "hard": {"total": 0, "full": 0, "partial": 0, "none": 0, "recall_sum": 0}
    }
    
    # 按表使用频率统计
    table_usage = {}
    table_recall = {}  # 每个表被召回的次数
    
    results = []
    
    for i, q in enumerate(questions):
        question = q['question']
        expected_tables = q.get('tables', [])
        difficulty = q.get('difficulty', 'medium')
        
        print(f"\r[{i+1}/{len(questions)}] 测试中...", end="", flush=True)
        
        # 统计表使用
        for t in expected_tables:
            table_usage[t] = table_usage.get(t, 0) + 1
        
        # 检索
        retrieved = retrieve_tables_fusion(model, question, table_schemas, column_schemas)
        retrieved_lower = {t.lower() for t in retrieved}
        expected_lower = {t.lower() for t in expected_tables}
        
        # 计算召回
        if expected_lower:
            matched = expected_lower & retrieved_lower
            recall = len(matched) / len(expected_lower)
            
            # 统计每个表的召回
            for t in expected_tables:
                if t.lower() in retrieved_lower:
                    table_recall[t] = table_recall.get(t, 0) + 1
        else:
            recall = 1.0
            matched = set()
        
        # 更新统计
        stats[difficulty]["total"] += 1
        stats[difficulty]["recall_sum"] += recall
        
        if recall == 1.0:
            stats[difficulty]["full"] += 1
            status = "✅"
        elif recall > 0:
            stats[difficulty]["partial"] += 1
            status = "⚠️"
        else:
            stats[difficulty]["none"] += 1
            status = "❌"
        
        results.append({
            "id": i + 1,
            "question": question[:40],
            "difficulty": difficulty,
            "expected": expected_tables,
            "matched": list(matched),
            "recall": recall,
            "status": status
        })
    
    print(f"\n完成！")
    
    # 保存报告
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# 100 个测试问题表召回率测试报告\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 问题集概览
        f.write("## 问题集概览\n\n")
        f.write("| 难度 | 数量 | 占比 |\n")
        f.write("|-----|------|------|\n")
        for d in ["easy", "medium", "hard"]:
            pct = stats[d]["total"] / len(questions) * 100
            f.write(f"| {d} | {stats[d]['total']} | {pct:.0f}% |\n")
        f.write(f"| **总计** | **{len(questions)}** | **100%** |\n\n")
        
        f.write("---\n\n")
        
        # 按难度分类的召回率
        f.write("## 按难度分类的召回率\n\n")
        f.write("| 难度 | 完全召回 | 部分召回 | 未召回 | **成功率** | **平均召回率** |\n")
        f.write("|-----|---------|---------|-------|-----------|---------------|\n")
        
        for d in ["easy", "medium", "hard"]:
            s = stats[d]
            if s["total"] > 0:
                success_rate = s["full"] / s["total"] * 100
                avg_recall = s["recall_sum"] / s["total"] * 100
            else:
                success_rate = 0
                avg_recall = 0
            f.write(f"| {d} | {s['full']}/{s['total']} | {s['partial']} | {s['none']} | **{success_rate:.1f}%** | {avg_recall:.1f}% |\n")
        
        # 总计
        total_full = sum(s["full"] for s in stats.values())
        total_partial = sum(s["partial"] for s in stats.values())
        total_none = sum(s["none"] for s in stats.values())
        total_recall = sum(s["recall_sum"] for s in stats.values())
        f.write(f"| **总计** | **{total_full}/{len(questions)}** | {total_partial} | {total_none} | **{total_full/len(questions)*100:.1f}%** | {total_recall/len(questions)*100:.1f}% |\n")
        
        f.write("\n---\n\n")
        
        # 表召回率统计
        f.write("## 核心表召回率\n\n")
        f.write("| 表名 | 被需要次数 | 被召回次数 | **召回率** |\n")
        f.write("|-----|----------|----------|----------|\n")
        sorted_usage = sorted(table_usage.items(), key=lambda x: x[1], reverse=True)[:15]
        for t, used in sorted_usage:
            recalled = table_recall.get(t, 0)
            rate = recalled / used * 100 if used > 0 else 0
            f.write(f"| {t} | {used} | {recalled} | **{rate:.0f}%** |\n")
        
        f.write("\n---\n\n")
        
        # 失败案例（按难度分组）
        f.write("## 失败案例（未召回）\n\n")
        failed = [r for r in results if r['recall'] == 0]
        
        for d in ["easy", "medium", "hard"]:
            failed_d = [r for r in failed if r['difficulty'] == d]
            if failed_d:
                f.write(f"### {d.upper()} ({len(failed_d)} 个)\n\n")
                for r in failed_d[:5]:
                    f.write(f"- **#{r['id']}**: {r['question']}... → 期望: {', '.join(r['expected'][:2])}\n")
                f.write("\n")
        
        f.write("---\n\n")
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"\n报告已保存: {OUTPUT_FILE}")
    
    # 打印汇总
    print("\n" + "=" * 60)
    print("按难度分类的召回率汇总")
    print("=" * 60)
    for d in ["easy", "medium", "hard"]:
        s = stats[d]
        if s["total"] > 0:
            rate = s["full"] / s["total"] * 100
            print(f"{d:8s}: {s['full']}/{s['total']} = {rate:.1f}%")


if __name__ == "__main__":
    run_recall_test()
