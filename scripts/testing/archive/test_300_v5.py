#!/usr/bin/env python3
"""300 问题检索测试 - V5 Full 版本"""

import os, sys, json, time, pickle
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "spider2_dev/schema_embeddings_v5_full.pkl")
MODEL_PATH = os.path.join(PROJECT_ROOT, "embed_model_cache/BAAI/bge-m3")
QUESTIONS_FILE = "./docs/milestone_20241224/test_questions_3tables_300.json"

from FlagEmbedding import BGEM3FlagModel

class FastRetrieverV5:
    def __init__(self):
        print("加载预计算 embedding (V5)...")
        with open(EMBEDDINGS_FILE, 'rb') as f:
            data = pickle.load(f)
        self.schemas = data["schemas"]
        self.lexical_weights = data["lexical_weights"]
        print("加载模型...")
        self.model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
        print(f"就绪！表: {sum(1 for s in self.schemas if s['type']=='table')}, 列: {sum(1 for s in self.schemas if s['type']=='column')}")
    
    def _get_query_sparse(self, question):
        return self.model.encode([question], return_dense=False, return_sparse=True, return_colbert_vecs=False)["lexical_weights"][0]
    
    def retrieve(self, question, top_k=10):
        qsp = self._get_query_sparse(question)
        scores = defaultdict(float)
        for i, sw in enumerate(self.lexical_weights):
            scores[self.schemas[i]["table_name"]] += float(self.model.compute_lexical_matching_score(qsp, sw))
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    def retrieve_table_only(self, question, top_k=10):
        qsp = self._get_query_sparse(question)
        results = [(self.schemas[i]["table_name"], float(self.model.compute_lexical_matching_score(qsp, self.lexical_weights[i])))
                   for i in range(len(self.schemas)) if self.schemas[i]['type'] == 'table']
        return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
    
    def retrieve_column_only(self, question, top_k=10):
        qsp = self._get_query_sparse(question)
        scores = defaultdict(float)
        for i, s in enumerate(self.schemas):
            if s['type'] == 'column':
                scores[s["table_name"]] += float(self.model.compute_lexical_matching_score(qsp, self.lexical_weights[i]))
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

def main():
    print("=" * 60)
    print("检索测试 - V5 Full 版本")
    print("=" * 60)
    
    with open(QUESTIONS_FILE, 'r') as f:
        questions = json.load(f)
    print(f"加载了 {len(questions)} 个问题")
    
    retriever = FastRetrieverV5()
    
    results = {"fusion": {"full": 0}, "table_only": {"full": 0}, "column_only": {"full": 0},
               "by_difficulty": defaultdict(lambda: {"fusion": {"full": 0}, "table_only": {"full": 0}, "column_only": {"full": 0}})}
    
    print("\n开始测试...")
    start = time.time()
    for i, q in enumerate(questions):
        expected = set(t.lower() for t in q.get("tables", []))
        if not expected: continue
        diff = q.get("difficulty", "unknown")
        
        for method, fn in [("fusion", retriever.retrieve), ("table_only", retriever.retrieve_table_only), ("column_only", retriever.retrieve_column_only)]:
            result_set = set(t.lower() for t, _ in fn(q["question"], top_k=10))
            if expected & result_set == expected:
                results[method]["full"] += 1
                results["by_difficulty"][diff][method]["full"] += 1
        
        if (i + 1) % 50 == 0: print(f"  已测试 {i+1}/{len(questions)}")
    
    elapsed = time.time() - start
    total = len(questions)
    
    # 生成报告
    report = f"""# 检索测试报告 - V5 Full

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Schema 版本**: V5 (schemas_table_level_full + schemas)  
**测试问题**: {total} 个  
**耗时**: {elapsed:.1f} 秒

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
    for d in ["simple", "medium", "hard"]:
        t = 100
        report += f"| {d} | **{results['by_difficulty'][d]['fusion']['full']}%** | {results['by_difficulty'][d]['table_only']['full']}% | {results['by_difficulty'][d]['column_only']['full']}% |\n"
    
    report += "\n---\n*报告自动生成*\n"
    
    with open("./docs/milestone_20241224/retrieval_test_300_v5_report.md", 'w') as f:
        f.write(report)
    
    print(f"\n测试完成！耗时: {elapsed:.1f} 秒")
    print(f"融合:     {results['fusion']['full']}/{total} ({results['fusion']['full']/total*100:.1f}%)")
    print(f"表级别:   {results['table_only']['full']}/{total} ({results['table_only']['full']/total*100:.1f}%)")
    print(f"列级别:   {results['column_only']['full']}/{total} ({results['column_only']['full']/total*100:.1f}%)")

if __name__ == "__main__":
    main()
