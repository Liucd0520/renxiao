#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
300 问题检索测试脚本

测试 FastRetriever 在 300 个测试问题上的召回率
"""

import os
import sys
import json
import time
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from our_algorithm.retriever import FastRetriever

# 配置
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"
OUTPUT_DIR = "./docs/milestone_20241224"


def load_questions():
    """加载测试问题"""
    with open(QUESTIONS_FILE, 'r') as f:
        return json.load(f)


def test_retrieval(retriever, questions, top_k=10):
    """测试检索召回率"""
    results = {
        "fusion": {"full": 0, "partial": 0, "fail": 0},
        "table_only": {"full": 0, "partial": 0, "fail": 0},
        "column_only": {"full": 0, "partial": 0, "fail": 0},
        "by_difficulty": defaultdict(lambda: {
            "fusion": {"full": 0, "partial": 0, "fail": 0},
            "table_only": {"full": 0, "partial": 0, "fail": 0},
            "column_only": {"full": 0, "partial": 0, "fail": 0}
        })
    }
    
    fail_cases = []
    
    for i, q in enumerate(questions):
        expected = q.get("tables", [])
        if not expected:
            continue
        
        expected_set = set(t.lower() for t in expected)
        difficulty = q.get("difficulty", "unknown")
        
        # 融合检索
        fusion_result = retriever.retrieve(q["question"], top_k=top_k)
        fusion_set = set(t.lower() for t, _ in fusion_result)
        fusion_matched = expected_set & fusion_set
        
        if len(fusion_matched) == len(expected_set):
            results["fusion"]["full"] += 1
            results["by_difficulty"][difficulty]["fusion"]["full"] += 1
        elif fusion_matched:
            results["fusion"]["partial"] += 1
            results["by_difficulty"][difficulty]["fusion"]["partial"] += 1
            fail_cases.append({
                "q": q["question"][:50], "d": difficulty,
                "expected": list(expected_set), "missed": list(expected_set - fusion_matched)
            })
        else:
            results["fusion"]["fail"] += 1
            results["by_difficulty"][difficulty]["fusion"]["fail"] += 1
            fail_cases.append({
                "q": q["question"][:50], "d": difficulty,
                "expected": list(expected_set), "missed": list(expected_set)
            })
        
        # 表级别检索
        table_result = retriever.retrieve_table_only(q["question"], top_k=top_k)
        table_set = set(t.lower() for t, _ in table_result)
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
        column_result = retriever.retrieve_column_only(q["question"], top_k=top_k)
        column_set = set(t.lower() for t, _ in column_result)
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
        
        if (i + 1) % 50 == 0:
            print(f"  已测试 {i+1}/{len(questions)}")
    
    return results, fail_cases


def generate_report(results, fail_cases, total, elapsed):
    """生成报告"""
    report = f"""# 检索算法测试报告 - 300 问题

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**测试问题**: {total} 个（simple/medium/hard 各 100）  
**目标表**: t_bz_config_ci_ne_root, t_bz_config_customer, event_history  
**检索 TOP-K**: 10  
**耗时**: {elapsed:.1f} 秒

---

## 算法说明

| 方法 | 说明 |
|-----|------|
| **融合** | 表级别 + 列级别 Sparse 检索，累加分聚合 |
| **表级别** | 仅表级别 Sparse 检索 |
| **列级别** | 列级别 Sparse 检索，累加分聚合到表 |

---

## 1. 总体结果

| 方法 | 完全召回 | 部分召回 | 失败 | **召回率** |
|-----|---------|---------|------|----------|
| **融合** | {results['fusion']['full']} | {results['fusion']['partial']} | {results['fusion']['fail']} | **{results['fusion']['full']/total*100:.1f}%** |
| 表级别 | {results['table_only']['full']} | {results['table_only']['partial']} | {results['table_only']['fail']} | {results['table_only']['full']/total*100:.1f}% |
| 列级别 | {results['column_only']['full']} | {results['column_only']['partial']} | {results['column_only']['fail']} | {results['column_only']['full']/total*100:.1f}% |

---

## 2. 按难度分析

| 难度 | 融合 | 表级别 | 列级别 |
|-----|------|-------|-------|
"""
    
    for diff in ["simple", "medium", "hard"]:
        d = results["by_difficulty"][diff]
        t = d["fusion"]["full"] + d["fusion"]["partial"] + d["fusion"]["fail"]
        if t > 0:
            f_rate = d["fusion"]["full"] / t * 100
            t_rate = d["table_only"]["full"] / t * 100
            c_rate = d["column_only"]["full"] / t * 100
            report += f"| {diff} | **{f_rate:.1f}%** | {t_rate:.1f}% | {c_rate:.1f}% |\n"
    
    report += """
---

## 3. 失败案例（前 10 个）

"""
    for c in fail_cases[:10]:
        report += f"- [{c['d']}] {c['q']}...\n  - 缺失: {c['missed']}\n"
    
    report += f"""
---

## 4. 结论

融合检索召回率: **{results['fusion']['full']/total*100:.1f}%**

---
*报告自动生成*
"""
    
    output_path = f"{OUTPUT_DIR}/retrieval_test_300_report.md"
    with open(output_path, 'w') as f:
        f.write(report)
    print(f"报告已保存: {output_path}")
    
    return report


def main():
    print("=" * 60)
    print("检索算法测试 - 300 问题")
    print("=" * 60)
    
    # 加载问题
    print("加载测试问题...")
    questions = load_questions()
    print(f"加载了 {len(questions)} 个问题")
    
    # 初始化检索器
    retriever = FastRetriever()
    
    # 运行测试
    print("\n开始测试...")
    start_time = time.time()
    results, fail_cases = test_retrieval(retriever, questions, top_k=10)
    elapsed = time.time() - start_time
    
    print(f"\n测试完成！耗时: {elapsed:.1f} 秒")
    
    # 生成报告
    total = len(questions)
    generate_report(results, fail_cases, total, elapsed)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("结果摘要")
    print("=" * 60)
    print(f"融合:     {results['fusion']['full']}/{total} ({results['fusion']['full']/total*100:.1f}%)")
    print(f"表级别:   {results['table_only']['full']}/{total} ({results['table_only']['full']/total*100:.1f}%)")
    print(f"列级别:   {results['column_only']['full']}/{total} ({results['column_only']['full']/total*100:.1f}%)")


if __name__ == "__main__":
    main()
