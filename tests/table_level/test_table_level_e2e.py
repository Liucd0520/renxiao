#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表级别方案端到端测试
1. 使用 BGE-M3 检索 Top 10 表
2. 加载完整列信息生成 Schema
3. 调用 LLM 生成 SQL
4. 对比正确 SQL
5. 生成详细报告
"""

import os
import sys
import json
import csv
import re
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.core.retrievers import VectorIndexRetriever
from embed_model.BGEM3Embedding import BGEM3Embedding
from llms.qwen.QwenModel import QwenModel

# 配置
SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
PERSIST_DIR = f"{SCHEMA_DIR}/table_vector_store_bge_m3"
TOP_K = 10

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


def extract_tables_from_sql(sql):
    """从 SQL 中提取表名"""
    if not sql:
        return set()
    patterns = [r'FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?', r'JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?']
    tables = set()
    for p in patterns:
        tables.update(re.findall(p, sql, re.IGNORECASE))
    return tables


# SQL 正确性评判 Prompt
SQL_EVAL_PROMPT = """你是一个 SQL 评审专家。请对比【生成的 SQL】和【正确的 SQL】，评判生成的 SQL 是否能正确回答用户问题。

【用户问题】
{question}

【生成的 SQL】
{generated_sql}

【正确的 SQL】
{correct_sql}

【评判要求】
1. 评分（0-100）：
   - 100分：完全正确，能得到正确结果
   - 80-99分：基本正确，有小问题但能得到大部分正确结果
   - 60-79分：部分正确，能得到部分结果但有明显错误
   - 40-59分：方向正确，但有重大错误导致结果错误
   - 0-39分：完全错误，无法得到正确结果

2. 分析以下方面：
   - 表选择：使用的表是否正确
   - 列选择：SELECT 的列是否正确
   - 连接条件：JOIN 条件是否正确
   - 过滤条件：WHERE 条件是否正确
   - 聚合逻辑：GROUP BY / COUNT 等是否正确

请按以下格式输出（严格遵守格式）：
评分: [0-100]
表选择: [正确/部分正确/错误] - [说明]
列选择: [正确/部分正确/错误] - [说明]
连接条件: [正确/部分正确/错误/不适用] - [说明]
过滤条件: [正确/部分正确/错误] - [说明]
聚合逻辑: [正确/部分正确/错误/不适用] - [说明]
总结: [一句话总结]
"""


def evaluate_sql_correctness(llm, question, generated_sql, correct_sql):
    """使用 LLM 评判 SQL 正确性"""
    prompt = SQL_EVAL_PROMPT.format(
        question=question,
        generated_sql=generated_sql,
        correct_sql=correct_sql
    )
    
    try:
        response = llm.complete(prompt).text.strip()
        
        # 解析评分
        score_match = re.search(r'评分:\s*(\d+)', response)
        score = int(score_match.group(1)) if score_match else 0
        
        # 解析各项评判
        evaluation = {
            "score": score,
            "raw_response": response,
            "table_selection": "",
            "column_selection": "",
            "join_condition": "",
            "filter_condition": "",
            "aggregation": "",
            "summary": ""
        }
        
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
            if match:
                evaluation[key] = match.group(1).strip()
        
        return evaluation
        
    except Exception as e:
        return {
            "score": 0,
            "error": str(e),
            "summary": f"评判失败: {str(e)}"
        }


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
    
    # 构建 Schema 文本
    columns = []
    for col in data.get("columns", []):
        col_info = f"{col['name']}({col.get('type', 'VARCHAR')})"
        if col.get("description"):
            col_info += f" -- {col['description'][:50]}"
        columns.append(col_info)
    
    schema_text = f"### Table `{table_name}`: {data.get('llm_description', '')[:200]}\n"
    schema_text += f"Columns: [{', '.join(columns[:20])}]"  # 限制列数
    if len(columns) > 20:
        schema_text += f" ... (共 {len(columns)} 列)"
    
    return schema_text


def run_e2e_test():
    print("\n" + "=" * 80)
    print("表级别方案端到端测试")
    print("=" * 80)
    
    # 1. 初始化
    print("\n[Step 1] 初始化模型和索引...")
    start_time = time.time()
    
    embed_model = BGEM3Embedding()
    Settings.embed_model = embed_model
    
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    retriever = VectorIndexRetriever(index=index, similarity_top_k=TOP_K)
    
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
        
        # Step A: 向量检索
        step_start = time.time()
        nodes = retriever.retrieve(case['question'])
        retrieved_tables = [node.metadata.get("table_name", "") for node in nodes]
        
        result["steps"].append({
            "step": "A. 表级别向量检索",
            "time": f"{time.time() - step_start:.1f}s",
            "retrieved_tables": retrieved_tables,
            "retrieved_scores": [f"{node.score:.4f}" for node in nodes]
        })
        
        print(f"\n[A] 表级别向量检索 ({time.time() - step_start:.1f}s)")
        print(f"  检索到 {len(retrieved_tables)} 个表:")
        for j, (table, node) in enumerate(zip(retrieved_tables[:5], nodes[:5]), 1):
            is_expected = "✅" if table.lower() in [t.lower() for t in case['expected_tables']] else ""
            print(f"    {j}. {table} (score: {node.score:.4f}) {is_expected}")
        if len(retrieved_tables) > 5:
            print(f"    ... 还有 {len(retrieved_tables) - 5} 个")
        
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
            "time": f"{time.time() - step_start:.1f}s",
            "schema_tables": len(schema_parts),
            "schema_length": len(full_schema)
        })
        
        print(f"\n[B] 加载完整 Schema ({time.time() - step_start:.1f}s)")
        print(f"  加载了 {len(schema_parts)} 个表的 Schema ({len(full_schema)} 字符)")
        
        # Step C: LLM 生成 SQL
        step_start = time.time()
        prompt = SQL_PROMPT.format(schema=full_schema, question=case['question'])
        
        try:
            response = llm.complete(prompt).text.strip()
            # 提取 SQL
            if "```" in response:
                sql_match = re.search(r'```(?:sql)?\s*(.*?)```', response, re.DOTALL)
                generated_sql = sql_match.group(1).strip() if sql_match else response
            else:
                generated_sql = response.replace("```sql", "").replace("```", "").strip()
        except Exception as e:
            generated_sql = f"Error: {str(e)}"
        
        result["steps"].append({
            "step": "C. LLM 生成 SQL",
            "time": f"{time.time() - step_start:.1f}s",
            "sql_length": len(generated_sql)
        })
        result["generated_sql"] = generated_sql
        
        print(f"\n[C] LLM 生成 SQL ({time.time() - step_start:.1f}s)")
        print(f"  生成的 SQL:")
        print(f"  {generated_sql[:200]}..." if len(generated_sql) > 200 else f"  {generated_sql}")
        
        # Step D: LLM 评判 SQL 正确性
        step_start = time.time()
        print(f"\n[D] LLM 评判 SQL 正确性...")
        
        evaluation = evaluate_sql_correctness(
            llm, case['question'], generated_sql, case['correct_sql']
        )
        
        result["evaluation"] = evaluation
        result["sql_score"] = evaluation.get("score", 0)
        
        result["steps"].append({
            "step": "D. LLM 评判 SQL 正确性",
            "time": f"{time.time() - step_start:.1f}s",
            "score": evaluation.get("score", 0),
            "summary": evaluation.get("summary", "")
        })
        
        print(f"  评分: {evaluation.get('score', 0)}/100")
        print(f"  表选择: {evaluation.get('table_selection', '')}")
        print(f"  列选择: {evaluation.get('column_selection', '')}")
        print(f"  连接条件: {evaluation.get('join_condition', '')}")
        print(f"  过滤条件: {evaluation.get('filter_condition', '')}")
        print(f"  聚合逻辑: {evaluation.get('aggregation', '')}")
        print(f"  总结: {evaluation.get('summary', '')}")
        
        # 表匹配分析（仍保留）
        gen_tables = extract_tables_from_sql(generated_sql)
        correct_tables = case['expected_tables']
        gen_tables_lower = set(t.lower() for t in gen_tables)
        correct_tables_lower = set(t.lower() for t in correct_tables)
        tables_match = gen_tables_lower == correct_tables_lower
        tables_partial = len(gen_tables_lower & correct_tables_lower) > 0
        
        result["generated_tables"] = list(gen_tables)
        result["tables_match"] = tables_match
        result["tables_partial"] = tables_partial
        
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
    
    # 保存详细结果
    output_dir = "./table_level_e2e_results"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/detailed_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成 Markdown 报告
    generate_report(results, output_dir)
    
    print(f"\n结果保存到: {output_dir}/")
    print("=" * 80)


def generate_report(results, output_dir):
    """生成详细的 Markdown 报告"""
    report = []
    report.append("# 表级别方案端到端测试报告\n")
    report.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
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
        
        # 处理步骤
        report.append("\n### 处理步骤\n")
        report.append("| 步骤 | 耗时 | 详情 |")
        report.append("|------|------|------|")
        for step in r['steps']:
            step_name = step['step']
            step_time = step.get('time', '-')
            if 'retrieved_tables' in step:
                detail = f"检索 {len(step['retrieved_tables'])} 表"
            elif 'schema_tables' in step:
                detail = f"加载 {step['schema_tables']} 表 ({step['schema_length']} 字符)"
            elif 'sql_length' in step:
                detail = f"生成 {step['sql_length']} 字符 SQL"
            elif 'tables_match' in step:
                detail = "✅ 匹配" if step['tables_match'] else "⚠️ 部分匹配" if step['tables_partial'] else "❌ 不匹配"
            else:
                detail = "-"
            report.append(f"| {step_name} | {step_time} | {detail} |")
        
        # SQL 评判结果
        eval_result = r.get('evaluation', {})
        score = eval_result.get('score', 0)
        score_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        
        report.append(f"\n### SQL 正确性评判: {score}/100 {score_emoji}\n")
        report.append(f"| 评判项 | 结果 |")
        report.append(f"|--------|------|")
        report.append(f"| 表选择 | {eval_result.get('table_selection', '-')} |")
        report.append(f"| 列选择 | {eval_result.get('column_selection', '-')} |")
        report.append(f"| 连接条件 | {eval_result.get('join_condition', '-')} |")
        report.append(f"| 过滤条件 | {eval_result.get('filter_condition', '-')} |")
        report.append(f"| 聚合逻辑 | {eval_result.get('aggregation', '-')} |")
        report.append(f"\n**总结**: {eval_result.get('summary', '-')}\n")
        
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
    run_e2e_test()
