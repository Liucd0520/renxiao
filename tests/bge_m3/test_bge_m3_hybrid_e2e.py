#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE-M3 混合检索端到端测试
使用 Dense + Sparse 向量进行混合检索
"""

import os
import sys
import json
import csv
import re
import time
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

# 添加项目根目录到 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from llms.qwen.QwenModel import QwenModel

# 配置 - 使用 LLM 优化后的 Schema
SCHEMA_DIR = "./spider2_dev/schemas_table_level_llm/netcaredb_ai"
TOP_K = 10
DENSE_WEIGHT = 0.7  # 稠密向量权重
SPARSE_WEIGHT = 0.3  # 稀疏向量权重

# SQL 生成 Prompt
SQL_PROMPT = """你是一个 SQL 专家。根据以下数据库 Schema 信息，回答用户的问题，生成正确的 SQL 查询。

【数据库 Schema】
{schema}

【用户问题】
{question}

【要求】
1. 直接输出 SQL，不要任何解释或思考过程
2. 必须使用 Schema 中实际存在的表名和列名
3. 表名和列名用反引号 ` 包裹
4. 时间条件使用动态函数如 DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
5. 不确定的参数值用 'xxx' 占位
6. 使用 JOIN 连接相关表（如果需要多个表）

SQL:
```sql
"""

# SQL 评判 Prompt
SQL_EVAL_PROMPT = """你是一个 SQL 评审专家。请对比【生成的 SQL】和【正确的 SQL】，评判生成的 SQL 是否能正确回答用户问题。

【用户问题】
{question}

【生成的 SQL】
{generated_sql}

【正确的 SQL】
{correct_sql}

请按以下格式输出（严格遵守格式）：
评分: [0-100]
表选择: [正确/部分正确/错误] - [说明]
列选择: [正确/部分正确/错误] - [说明]
连接条件: [正确/部分正确/错误/不适用] - [说明]
过滤条件: [正确/部分正确/错误] - [说明]
聚合逻辑: [正确/部分正确/错误/不适用] - [说明]
总结: [一句话总结]
"""


class BGEM3HybridRetriever:
    """BGE-M3 混合检索器（Dense + Sparse）"""
    
    def __init__(self, schema_dir: str, dense_weight: float = 0.7):
        self.schema_dir = Path(schema_dir)
        self.dense_weight = dense_weight
        self.sparse_weight = 1 - dense_weight
        self._model = None
        self._table_data = {}  # table_name -> {embedding_text, dense_vec, lexical_weights}
        
    def _load_model(self):
        """加载 BGE-M3 模型"""
        if self._model is not None:
            return
            
        from FlagEmbedding import BGEM3FlagModel
        print("加载 BGE-M3 模型...")
        self._model = BGEM3FlagModel(
            "./embed_model_cache/BAAI/bge-m3",
            use_fp16=True
        )
        print("✅ BGE-M3 模型加载完成")
    
    def build_index(self):
        """构建索引（Dense + Sparse）"""
        self._load_model()
        
        print("构建混合索引...")
        
        # 加载所有表的 embedding_text
        json_files = list(self.schema_dir.glob("*.json"))
        print(f"  找到 {len(json_files)} 个表")
        
        texts = []
        table_names = []
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            table_name = data.get("table_name", json_file.stem)
            embedding_text = data.get("embedding_text", "")
            
            if embedding_text:
                texts.append(embedding_text)
                table_names.append(table_name)
                self._table_data[table_name] = {
                    "embedding_text": embedding_text,
                    "json_path": str(json_file)
                }
        
        # 编码所有文本（同时获取 dense 和 sparse）
        print(f"  编码 {len(texts)} 个表描述...")
        output = self._model.encode(
            texts,
            batch_size=12,
            max_length=8192,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False
        )
        
        # 保存向量
        for i, table_name in enumerate(table_names):
            self._table_data[table_name]["dense_vec"] = output['dense_vecs'][i]
            self._table_data[table_name]["lexical_weights"] = output['lexical_weights'][i]
        
        print(f"✅ 索引构建完成，共 {len(self._table_data)} 个表")
    
    def _compute_sparse_score(self, query_weights: Dict, doc_weights: Dict) -> float:
        """计算稀疏向量相似度（词汇匹配）"""
        score = 0.0
        for token, weight in query_weights.items():
            if token in doc_weights:
                score += weight * doc_weights[token]
        return score
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[str, float, float, float]]:
        """
        混合检索
        返回: [(table_name, hybrid_score, dense_score, sparse_score), ...]
        """
        self._load_model()
        
        # 编码查询
        query_output = self._model.encode(
            [query],
            batch_size=1,
            max_length=8192,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False
        )
        
        query_dense = query_output['dense_vecs'][0]
        query_sparse = query_output['lexical_weights'][0]
        
        # 计算所有表的分数
        results = []
        for table_name, data in self._table_data.items():
            # Dense 相似度（余弦相似度）
            doc_dense = data['dense_vec']
            dense_score = float(np.dot(query_dense, doc_dense) / 
                               (np.linalg.norm(query_dense) * np.linalg.norm(doc_dense)))
            
            # Sparse 相似度（词汇匹配）
            doc_sparse = data['lexical_weights']
            sparse_score = self._compute_sparse_score(query_sparse, doc_sparse)
            
            # 混合分数
            hybrid_score = self.dense_weight * dense_score + self.sparse_weight * sparse_score
            
            results.append((table_name, hybrid_score, dense_score, sparse_score))
        
        # 按混合分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]


def extract_tables_from_sql(sql):
    """从 SQL 中提取表名"""
    if not sql:
        return set()
    patterns = [r'FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?', r'JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?']
    tables = set()
    for p in patterns:
        tables.update(re.findall(p, sql, re.IGNORECASE))
    return tables


def load_test_cases():
    """加载测试用例"""
    test_cases = []
    with open("./cc_result.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            question = row.get('query', '').strip()
            correct_sql = row.get('正确SQL', '') or row.get('sql', '')
            if question:
                test_cases.append({
                    "question": question,
                    "correct_sql": correct_sql,
                    "expected_tables": extract_tables_from_sql(correct_sql)
                })
    return test_cases


def load_table_schema(table_name):
    """从 JSON 文件加载表的完整 Schema"""
    json_path = Path(SCHEMA_DIR) / f"{table_name}.json"
    if not json_path.exists():
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    columns = []
    for col in data.get("columns", []):
        col_info = f"{col['name']}({col.get('type', 'VARCHAR')})"
        if col.get("description"):
            col_info += f" -- {col['description'][:50]}"
        columns.append(col_info)
    
    schema_text = f"### Table `{table_name}`: {data.get('llm_description', '')[:200]}\n"
    schema_text += f"Columns: [{', '.join(columns[:20])}]"
    if len(columns) > 20:
        schema_text += f" ... (共 {len(columns)} 列)"
    
    return schema_text


def evaluate_sql_correctness(llm, question, generated_sql, correct_sql):
    """使用 LLM 评判 SQL 正确性"""
    prompt = SQL_EVAL_PROMPT.format(
        question=question,
        generated_sql=generated_sql,
        correct_sql=correct_sql
    )
    
    try:
        response = llm.complete(prompt).text.strip()
        score_match = re.search(r'评分:\s*(\d+)', response)
        score = int(score_match.group(1)) if score_match else 0
        
        evaluation = {"score": score, "raw_response": response}
        
        patterns = {
            "table_selection": r'表选择:\s*(.+?)(?=\n|$)',
            "column_selection": r'列选择:\s*(.+?)(?=\n|$)',
            "join_condition": r'连接条件:\s*(.+?)(?=\n|$)',
            "filter_condition": r'过滤条件:\s*(.+?)(?=\n|$)',
            "aggregation": r'聚合逻辑:\s*(.+?)(?=\n|$)',
            "summary": r'总结:\s*(.+?)(?=\n|$)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, response)
            evaluation[key] = match.group(1).strip() if match else ""
        
        return evaluation
    except Exception as e:
        return {"score": 0, "error": str(e), "summary": f"评判失败: {str(e)}"}


def run_hybrid_e2e_test():
    print("\n" + "=" * 80)
    print("BGE-M3 混合检索端到端测试 (Dense + Sparse)")
    print(f"权重配置: Dense={DENSE_WEIGHT}, Sparse={SPARSE_WEIGHT}")
    print("=" * 80)
    
    # 1. 初始化
    print("\n[Step 1] 初始化...")
    start_time = time.time()
    
    retriever = BGEM3HybridRetriever(SCHEMA_DIR, dense_weight=DENSE_WEIGHT)
    retriever.build_index()
    
    llm = QwenModel(model_name="qwen-plus", temperature=0.3)
    print(f"  ✅ 初始化完成 ({time.time() - start_time:.1f}s)")
    
    # 2. 加载测试用例
    test_cases = load_test_cases()
    print(f"\n[Step 2] 加载测试用例: {len(test_cases)} 个")
    
    # 3. 运行测试
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试 {i}/{len(test_cases)}")
        print(f"{'=' * 80}")
        print(f"问题: {case['question'][:60]}...")
        print(f"期望表: {case['expected_tables']}")
        print("-" * 80)
        
        result = {
            "test_id": i,
            "question": case['question'],
            "expected_tables": list(case['expected_tables']),
            "correct_sql": case['correct_sql'],
            "steps": []
        }
        
        # Step A: 混合检索
        step_start = time.time()
        retrieved = retriever.retrieve(case['question'], top_k=TOP_K)
        retrieved_tables = [r[0] for r in retrieved]
        
        result["steps"].append({
            "step": "A. 混合检索 (Dense+Sparse)",
            "time": f"{time.time() - step_start:.2f}s",
            "retrieved_tables": retrieved_tables,
            "scores": [{"table": r[0], "hybrid": f"{r[1]:.4f}", "dense": f"{r[2]:.4f}", "sparse": f"{r[3]:.4f}"} for r in retrieved]
        })
        
        print(f"\n[A] 混合检索 (Dense+Sparse) ({time.time() - step_start:.2f}s)")
        print(f"  检索到 {len(retrieved)} 个表:")
        for j, (table, hybrid, dense, sparse) in enumerate(retrieved[:5], 1):
            is_expected = "✅" if table.lower() in [t.lower() for t in case['expected_tables']] else ""
            print(f"    {j}. {table} (hybrid={hybrid:.4f}, dense={dense:.4f}, sparse={sparse:.4f}) {is_expected}")
        if len(retrieved) > 5:
            print(f"    ... 还有 {len(retrieved) - 5} 个")
        
        # 计算表召回率
        expected_set = set(t.lower() for t in case['expected_tables'])
        retrieved_set = set(t.lower() for t in retrieved_tables)
        found_tables = expected_set & retrieved_set
        table_recall = len(found_tables) / len(expected_set) if expected_set else 1.0
        
        result["table_recall"] = table_recall
        result["found_tables"] = list(found_tables)
        result["missing_tables"] = list(expected_set - retrieved_set)
        
        print(f"\n  表召回率: {table_recall:.0%}")
        if result["missing_tables"]:
            print(f"  ❌ 缺失表: {result['missing_tables']}")
        
        # Step B: 加载 Schema
        step_start = time.time()
        schema_parts = []
        for table in retrieved_tables:
            schema = load_table_schema(table)
            if schema:
                schema_parts.append(schema)
        
        full_schema = "\n\n".join(schema_parts)
        
        result["steps"].append({
            "step": "B. 加载完整 Schema",
            "time": f"{time.time() - step_start:.2f}s",
            "schema_tables": len(schema_parts),
            "schema_length": len(full_schema)
        })
        
        print(f"\n[B] 加载完整 Schema ({time.time() - step_start:.2f}s)")
        print(f"  加载了 {len(schema_parts)} 个表的 Schema ({len(full_schema)} 字符)")
        
        # Step C: LLM 生成 SQL
        step_start = time.time()
        prompt = SQL_PROMPT.format(schema=full_schema, question=case['question'])
        
        try:
            response = llm.complete(prompt).text.strip()
            if "```" in response:
                sql_match = re.search(r'```(?:sql)?\s*(.*?)```', response, re.DOTALL)
                generated_sql = sql_match.group(1).strip() if sql_match else response
            else:
                generated_sql = response.replace("```sql", "").replace("```", "").strip()
        except Exception as e:
            generated_sql = f"Error: {str(e)}"
        
        result["steps"].append({
            "step": "C. LLM 生成 SQL",
            "time": f"{time.time() - step_start:.2f}s",
            "sql_length": len(generated_sql)
        })
        result["generated_sql"] = generated_sql
        
        print(f"\n[C] LLM 生成 SQL ({time.time() - step_start:.2f}s)")
        print(f"  {generated_sql[:150]}..." if len(generated_sql) > 150 else f"  {generated_sql}")
        
        # Step D: LLM 评判 SQL 正确性
        step_start = time.time()
        print(f"\n[D] LLM 评判 SQL 正确性...")
        
        evaluation = evaluate_sql_correctness(llm, case['question'], generated_sql, case['correct_sql'])
        
        result["evaluation"] = evaluation
        result["sql_score"] = evaluation.get("score", 0)
        
        result["steps"].append({
            "step": "D. LLM 评判 SQL 正确性",
            "time": f"{time.time() - step_start:.2f}s",
            "score": evaluation.get("score", 0)
        })
        
        print(f"  评分: {evaluation.get('score', 0)}/100")
        print(f"  总结: {evaluation.get('summary', '')}")
        
        results.append(result)
    
    # 4. 生成报告
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    
    full_recall = sum(1 for r in results if r['table_recall'] == 1.0)
    avg_recall = sum(r['table_recall'] for r in results) / len(results)
    avg_sql_score = sum(r.get('sql_score', 0) for r in results) / len(results)
    perfect_sql = sum(1 for r in results if r.get('sql_score', 0) >= 80)
    
    print(f"\n表检索性能:")
    print(f"  - 完全召回: {full_recall}/{len(results)} ({full_recall/len(results)*100:.0f}%)")
    print(f"  - 平均召回率: {avg_recall:.0%}")
    
    print(f"\nSQL 正确性:")
    print(f"  - 平均评分: {avg_sql_score:.0f}/100")
    print(f"  - 优秀(≥80分): {perfect_sql}/{len(results)} ({perfect_sql/len(results)*100:.0f}%)")
    
    # 保存结果
    output_dir = "./docs/bge/hybrid_e2e"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/detailed_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    generate_report(results, output_dir)
    
    print(f"\n结果保存到: {output_dir}/")
    print("=" * 80)


def generate_report(results, output_dir):
    """生成详细的 Markdown 报告"""
    report = []
    report.append("# BGE-M3 混合检索端到端测试报告\n")
    report.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**检索模式**: Dense + Sparse 混合检索\n")
    report.append(f"**权重配置**: Dense={DENSE_WEIGHT}, Sparse={SPARSE_WEIGHT}\n")
    
    # 汇总统计
    full_recall = sum(1 for r in results if r['table_recall'] == 1.0)
    avg_recall = sum(r['table_recall'] for r in results) / len(results)
    avg_sql_score = sum(r.get('sql_score', 0) for r in results) / len(results)
    perfect_sql = sum(1 for r in results if r.get('sql_score', 0) >= 80)
    
    report.append("## 总体统计\n")
    report.append(f"| 指标 | 结果 |")
    report.append(f"|------|------|")
    report.append(f"| 测试用例数 | {len(results)} |")
    report.append(f"| 表完全召回 | {full_recall}/{len(results)} ({full_recall/len(results)*100:.0f}%) |")
    report.append(f"| 平均表召回率 | {avg_recall:.0%} |")
    report.append(f"| **平均 SQL 评分** | **{avg_sql_score:.0f}/100** |")
    report.append(f"| 优秀(≥80分) | {perfect_sql}/{len(results)} ({perfect_sql/len(results)*100:.0f}%) |")
    report.append("")
    
    report.append("---\n")
    
    # 每个测试的详细结果
    for r in results:
        report.append(f"## 测试 {r['test_id']}: {r['question'][:50]}...\n")
        report.append(f"**期望表**: `{', '.join(r['expected_tables'])}`\n")
        report.append(f"**表召回率**: {r['table_recall']:.0%}")
        if r['table_recall'] == 1.0:
            report.append(" ✅\n")
        else:
            report.append(f" ❌ 缺失: `{', '.join(r['missing_tables'])}`\n")
        
        # 检索结果（显示混合分数）
        retrieval_step = r['steps'][0]
        if 'scores' in retrieval_step:
            report.append("\n### 检索结果 (Top 5)\n")
            report.append("| 排名 | 表名 | Hybrid | Dense | Sparse |")
            report.append("|------|------|--------|-------|--------|")
            for j, s in enumerate(retrieval_step['scores'][:5], 1):
                is_expected = "✅" if s['table'].lower() in [t.lower() for t in r['expected_tables']] else ""
                report.append(f"| {j} | {s['table']} {is_expected} | {s['hybrid']} | {s['dense']} | {s['sparse']} |")
        
        # SQL 评判结果
        eval_result = r.get('evaluation', {})
        score = eval_result.get('score', 0)
        score_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        
        report.append(f"\n### SQL 正确性评判: {score}/100 {score_emoji}\n")
        report.append(f"**总结**: {eval_result.get('summary', '-')}\n")
        
        # SQL 对比
        report.append("\n### SQL 对比\n")
        report.append("**生成的 SQL**:")
        report.append(f"```sql\n{r['generated_sql']}\n```\n")
        report.append("**正确的 SQL**:")
        report.append(f"```sql\n{r['correct_sql']}\n```\n")
        
        report.append("---\n")
    
    with open(f"{output_dir}/e2e_report.md", 'w', encoding='utf-8') as f:
        f.write("\n".join(report))


if __name__ == "__main__":
    run_hybrid_e2e_test()
