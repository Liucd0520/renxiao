#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
300 问题检索测试脚本 - V4 LLM 全量增强版本
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

# 使用 V4 embedding
EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v4_llm.pkl")

import pickle
from FlagEmbedding import BGEM3FlagModel

MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"
OUTPUT_DIR = "./docs/milestone_20241224"


class FastRetrieverV4:
    """V4 检索器"""
    
    def __init__(self):
        print("加载预计算 embedding (V4)...")
        with open(EMBEDDINGS_FILE, 'rb') as f:
            data = pickle.load(f)
        
        self.schemas = data["schemas"]
        self.lexical_weights = data["lexical_weights"]
        
        print("加载模型...")
        self.model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
        
        table_count = sum(1 for s in self.schemas if s['type'] == 'table')
        column_count = sum(1 for s in self.schemas if s['type'] == 'column')
        print(f"就绪！表级别: {table_count}, 列级别: {column_count}")
    
    def retrieve(self, question, top_k=10):
        """融合检索"""
        query_output = self.model.encode(
            [question], return_dense=False, return_sparse=True, return_colbert_vecs=False
        )
        query_sparse = query_output["lexical_weights"][0]
        
        table_scores = defaultdict(float)
        for i, schema_weight in enumerate(self.lexical_weights):
            score = self.model.compute_lexical_matching_score(query_sparse, schema_weight)
            table_scores[self.schemas[i]["table_name"]] += float(score)
        
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_tables[:top_k]
    
    def retrieve_table_only(self, question, top_k=10):
        """仅表级别"""
        query_output = self.model.encode(
            [question], return_dense=False, return_sparse=True, return_colbert_vecs=False
        )
        query_sparse = query_output["lexical_weights"][0]
        
        results = []
        for i, schema in enumerate(self.schemas):
            if schema['type'] == 'table':
                score = self.model.compute_lexical_matching_score(query_sparse, self.lexical_weights[i])
                results.append((schema['table_name'], float(score)))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def retrieve_column_only(self, question, top_k=10):
        """仅列级别"""
        query_output = self.model.encode(
            [question], return_dense=False, return_sparse=True, return_colbert_vecs=False
        )
        query_sparse = query_output["lexical_weights"][0]
        
        table_scores = defaultdict(float)
        for i, schema in enumerate(self.schemas):
            if schema['type'] == 'column':
                score = self.model.compute_lexical_matching_score(query_sparse, self.lexical_weights[i])
                table_scores[schema['table_name']] += float(score)
        
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_tables[:top_k]


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
        
        for method in ["fusion", "table_only", "column_only"]:
            if method == "fusion":
                result = retriever.retrieve(q["question"], top_k=top_k)
            elif method == "table_only":
                result = retriever.retrieve_table_only(q["question"], top_k=top_k)
            else:
                result = retriever.retrieve_column_only(q["question"], top_k=top_k)
            
            result_set = set(t.lower() for t, _ in result)
            matched = expected_set & result_set
            
            if len(matched) == len(expected_set):
                results[method]["full"] += 1
                results["by_difficulty"][difficulty][method]["full"] += 1
            elif matched:
                results[method]["partial"] += 1
                results["by_difficulty"][difficulty][method]["partial"] += 1
            else:
                results[method]["fail"] += 1
                results["by_difficulty"][difficulty][method]["fail"] += 1
        
        if (i + 1) % 50 == 0:
            print(f"  已测试 {i+1}/{len(questions)}")
    
    return results, fail_cases


def main():
    print("=" * 60)
    print("检索测试 - V4 LLM 全量增强版本")
    print("=" * 60)
    
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"加载了 {len(questions)} 个问题")
    
    retriever = FastRetrieverV4()
    
    print("\n开始测试...")
    start_time = time.time()
    results, _ = test_retrieval(retriever, questions, top_k=10)
    elapsed = time.time() - start_time
    
    print(f"\n测试完成！耗时: {elapsed:.1f} 秒")
    
    total = len(questions)
    
    # 生成报告
    report = f"""# 检索测试报告 - V4 LLM 全量增强

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Schema 版本**: V4 (schemas_table_level_llm + schemas)  
**测试问题**: {total} 个  
**耗时**: {elapsed:.1f} 秒

---

## 总体结果

| 方法 | 完全召回 | 召回率 |
|-----|---------|-------|
| **融合** | {results['fusion']['full']} | **{results['fusion']['full']/total*100:.1f}%** |
| 表级别 | {results['table_only']['full']} | {results['table_only']['full']/total*100:.1f}% |
| 列级别 | {results['column_only']['full']} | {results['column_only']['full']/total*100:.1f}% |

## 按难度分析

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
    
    report += "\n---\n*报告自动生成*\n"
    
    output_path = f"{OUTPUT_DIR}/retrieval_test_300_v4_report.md"
    with open(output_path, 'w') as f:
        f.write(report)
    print(f"报告已保存: {output_path}")
    
    print("\n" + "=" * 60)
    print("结果摘要")
    print("=" * 60)
    print(f"融合:     {results['fusion']['full']}/{total} ({results['fusion']['full']/total*100:.1f}%)")
    print(f"表级别:   {results['table_only']['full']}/{total} ({results['table_only']['full']/total*100:.1f}%)")
    print(f"列级别:   {results['column_only']['full']}/{total} ({results['column_only']['full']/total*100:.1f}%)")


if __name__ == "__main__":
    main()
