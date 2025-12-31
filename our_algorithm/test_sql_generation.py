#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 A：SQL 生成测试

流程：问题 → 检索 10-20 表 → 直接生成 SQL
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from our_algorithm.retriever import FastRetriever
from our_algorithm.sql_generator import SQLGenerator


# 配置
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"
OUTPUT_DIR = "./docs/milestone_20241225"
TOP_K = 10  # 检索参数


def normalize_sql(sql):
    """标准化 SQL 用于比较"""
    if not sql:
        return ""
    # 转小写，去除多余空格
    sql = sql.lower().strip()
    sql = " ".join(sql.split())
    # 去除末尾分号
    sql = sql.rstrip(";")
    return sql


def sql_match(generated, expected):
    """判断 SQL 是否匹配"""
    gen_norm = normalize_sql(generated)
    exp_norm = normalize_sql(expected)
    return gen_norm == exp_norm


def main():
    print("=" * 70)
    print("方案 A：SQL 生成测试")
    print("流程：问题 → 检索 10-20 表 → 直接生成 SQL")
    print("=" * 70)
    
    # 加载测试问题
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"加载了 {len(questions)} 个测试问题")
    
    # 初始化检索器和生成器
    print("\n初始化检索器...")
    retriever = FastRetriever()
    
    print("初始化 SQL 生成器...")
    generator = SQLGenerator(
        schema_dir="./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
    )
    
    # 统计
    stats = {
        "simple": {"total": 0, "correct": 0, "errors": []},
        "medium": {"total": 0, "correct": 0, "errors": []},
        "hard": {"total": 0, "correct": 0, "errors": []}
    }
    
    results = []
    start_time = time.time()
    
    print(f"\n开始测试（TOP-K={TOP_K}）...\n")
    
    for i, q in enumerate(questions):
        question = q["question"]
        expected_sql = q.get("sql", "")
        difficulty = q.get("difficulty", "simple")
        expected_tables = q.get("tables", [])
        
        stats[difficulty]["total"] += 1
        
        # 1. 检索
        retrieved = retriever.retrieve(question, top_k=TOP_K)
        retrieved_tables = [name for name, _ in retrieved]
        
        # 2. 生成 SQL
        try:
            generated_sql = generator.generate_sql(question, retrieved_tables)
        except Exception as e:
            generated_sql = f"ERROR: {str(e)}"
        
        # 3. 判断正确性
        is_correct = sql_match(generated_sql, expected_sql)
        
        if is_correct:
            stats[difficulty]["correct"] += 1
        else:
            # 记录错误案例（只记录前 5 个）
            if len(stats[difficulty]["errors"]) < 5:
                stats[difficulty]["errors"].append({
                    "question": question[:50],
                    "expected": expected_sql[:100],
                    "generated": generated_sql[:100]
                })
        
        # 记录结果
        results.append({
            "id": i + 1,
            "question": question,
            "difficulty": difficulty,
            "expected_tables": expected_tables,
            "retrieved_tables": retrieved_tables,
            "expected_sql": expected_sql,
            "generated_sql": generated_sql,
            "is_correct": is_correct
        })
        
        if (i + 1) % 20 == 0:
            elapsed = time.time() - start_time
            print(f"  已测试 {i+1}/{len(questions)}... ({elapsed:.1f}秒)")
    
    total_time = time.time() - start_time
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("测试结果")
    print("=" * 70)
    
    total_correct = sum(s["correct"] for s in stats.values())
    total_count = sum(s["total"] for s in stats.values())
    
    print(f"\n总体: {total_correct}/{total_count} ({total_correct/total_count*100:.1f}%)")
    print(f"耗时: {total_time:.1f}秒")
    
    print("\n按难度:")
    print(f"{'难度':<10} | {'正确':>6} | {'总数':>6} | {'正确率':>8}")
    print("-" * 40)
    for d in ["simple", "medium", "hard"]:
        s = stats[d]
        rate = s["correct"] / s["total"] * 100 if s["total"] > 0 else 0
        print(f"{d:<10} | {s['correct']:>6} | {s['total']:>6} | {rate:>7.1f}%")
    
    # 保存详细结果
    output_file = Path(OUTPUT_DIR) / "sql_generation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果保存到: {output_file}")
    
    # 生成报告
    report = f"""# SQL 生成测试报告 - 方案 A

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**测试问题**: {len(questions)} 个
**检索配置**: TOP-K = {TOP_K}（最多 {TOP_K * 2} 张表）
**耗时**: {total_time:.1f} 秒

---

## 总体结果

| 难度 | 正确 | 总数 | 正确率 |
|-----|------|------|-------|
| simple | {stats['simple']['correct']} | {stats['simple']['total']} | {stats['simple']['correct']/stats['simple']['total']*100:.1f}% |
| medium | {stats['medium']['correct']} | {stats['medium']['total']} | {stats['medium']['correct']/stats['medium']['total']*100:.1f}% |
| hard | {stats['hard']['correct']} | {stats['hard']['total']} | {stats['hard']['correct']/stats['hard']['total']*100:.1f}% |
| **总计** | **{total_correct}** | **{total_count}** | **{total_correct/total_count*100:.1f}%** |

---

## 错误案例（每类前 5 个）

"""
    for d in ["simple", "medium", "hard"]:
        if stats[d]["errors"]:
            report += f"### {d}\n\n"
            for e in stats[d]["errors"]:
                report += f"**问题**: {e['question']}...\n"
                report += f"- 期望: `{e['expected']}...`\n"
                report += f"- 生成: `{e['generated']}...`\n\n"
    
    report += """---
*报告自动生成*
"""
    
    report_file = Path(OUTPUT_DIR) / "sql_generation_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"报告保存到: {report_file}")


if __name__ == "__main__":
    main()
