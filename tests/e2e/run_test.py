#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端测试脚本：Schema Linking + SQL 生成

设计原则：
1. 核心表配置：只需配置少量核心业务表及其用途（一次配置）
2. 自动分析：其他逻辑从 schema 自动推断
3. 表格增量更新时：只需更新 schema 文件，不需要改代码
"""

import json
import os
import sys
import time
import re
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel
from config import QWEN_MODEL, QWEN_API_KEY, QWEN_BASE_URL


# ============ 配置 ============
SCHEMA_PATH = "./spider2_dev/schemas/netcaredb_ai"
TEST_FILE = "./test_ground_truth.json"
OUTPUT_DIR = "./test_output"


# ============ 核心表配置（一次性配置，不需要频繁更新） ============
# 这是唯一需要人工配置的部分：定义核心业务表及其用途
# 当数据库有新表时，如果是核心表才需要添加这里
CORE_TABLES_CONFIG = {
    # 格式: "表名": ["触发关键词1", "触发关键词2", ...]
    # 当问题中包含这些关键词时，会优先选择对应的表

    # 事件/告警相关
    "event_history": ["告警", "事件", "alarm", "event", "down", "状态", "state", "发生"],

    # 设备相关
    "t_bz_config_ci_ne_root": ["设备", "device", "网元", "ne", "主机"],

    # 客户相关
    "t_bz_config_customer": ["客户", "customer"],
}

# 表之间的关联关系配置（可选，用于自动扩展相关表）
TABLE_RELATIONSHIPS_CONFIG = {
    # 格式: "表名": ["关联表1", "关联表2", ...]
    "event_history": ["t_bz_config_ci_ne_root", "t_bz_config_customer"],
    "t_bz_config_ci_ne_root": ["t_bz_config_customer"],
}


def load_test_cases():
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_schemas():
    tables = {}
    for filename in os.listdir(SCHEMA_PATH):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(SCHEMA_PATH, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        table_name = data['meta_data']['table_name']
        if table_name not in tables:
            tables[table_name] = {
                'columns': [],
                'db_id': data['meta_data']['db_id']
            }

        col_info = {
            'name': data['column_name'],
            'type': data['column_types'],
            'description': data.get('column_descriptions', ''),
            'samples': data.get('sample_rows', [])
        }
        tables[table_name]['columns'].append(col_info)

    return tables


def schema_linking(question: str, all_tables: dict) -> list:
    """
    Schema Linking：基于核心表配置 + 自动扩展
    """
    question_lower = question.lower()
    selected_tables = set()

    # Step 1: 根据核心表配置匹配
    for table_name, keywords in CORE_TABLES_CONFIG.items():
        for kw in keywords:
            if kw in question or kw in question_lower:
                selected_tables.add(table_name)
                break

    # Step 2: 自动扩展关联表
    tables_to_expand = list(selected_tables)
    for table in tables_to_expand:
        if table in TABLE_RELATIONSHIPS_CONFIG:
            for related_table in TABLE_RELATIONSHIPS_CONFIG[table]:
                selected_tables.add(related_table)

    # Step 3: 如果没匹配到核心表，降级到关键词匹配
    if not selected_tables:
        # 从问题中提取英文单词
        english_words = [w.lower() for w in re.findall(r'[a-zA-Z]+', question)]
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', question)

        table_scores = defaultdict(float)

        for table_name, table_info in all_tables.items():
            table_lower = table_name.lower()

            # 表名匹配
            for word in english_words:
                if word in table_lower:
                    table_scores[table_name] += 2.0

            # 列名和描述匹配
            for col in table_info['columns']:
                col_lower = col['name'].lower()
                desc = col['description'] or ''

                for word in english_words:
                    if word in col_lower:
                        table_scores[table_name] += 1.0

                for cw in chinese_words:
                    if cw in desc:
                        table_scores[table_name] += 1.5

        # 选择得分最高的表
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        selected_tables = set(t[0] for t in sorted_tables[:5] if t[1] > 0)

    return list(selected_tables)


def format_schema_for_sql(tables: dict, table_names: list) -> str:
    """将 schema 格式化为 SQL 生成可用的文本"""
    lines = []

    for table_name in table_names:
        if table_name not in tables:
            continue

        table_info = tables[table_name]
        lines.append(f"### 表: {table_name}")

        for col in table_info['columns']:
            samples = col['samples'][:3] if col['samples'] else []
            sample_str = ', '.join(f"'{s}'" for s in samples) if samples else ''
            desc = col['description'] if col['description'] else ''

            line = f"  - {col['name']} ({col['type']})"
            if desc:
                line += f": {desc}"
            if sample_str:
                line += f" [示例: {sample_str}]"
            lines.append(line)

        lines.append("")

    return '\n'.join(lines)


def infer_table_relationships(tables: dict, table_names: list) -> str:
    """自动推断表之间的关联关系"""
    relationships = []

    for table in table_names:
        if table not in tables:
            continue

        for col in tables[table]['columns']:
            col_name_upper = col['name'].upper()

            if col_name_upper.endswith('_ID'):
                prefix = col_name_upper[:-3].lower()

                for other_table in table_names:
                    if other_table == table:
                        continue

                    other_lower = other_table.lower()
                    if prefix in other_lower:
                        for other_col in tables[other_table]['columns']:
                            other_col_upper = other_col['name'].upper()
                            if other_col_upper == col_name_upper or other_col_upper == 'ID':
                                relationships.append(
                                    f"- {table}.{col['name']} = {other_table}.{other_col['name']}"
                                )
                                break

    if relationships:
        return "### 表关联关系\n" + '\n'.join(set(relationships))
    return ""


# ============ SQL 生成 ============
SQL_GENERATION_PROMPT = """你是一个专业的 MySQL 数据库专家。请根据用户问题生成正确的 SQL 查询。

## 数据库表结构
{schema}

{relationships}

## 用户问题
{question}

## 要求
1. 只使用上面列出的表和列，不要使用不存在的表或列
2. 注意使用正确的 JOIN 条件连接表
3. 时间条件使用 DATE_SUB(CURDATE(), INTERVAL x MONTH/DAY) 函数
4. 注意查看列的示例值来确定正确的过滤条件

直接输出 SQL 语句：
"""


def generate_sql(llm, question: str, schema_text: str, relationships: str) -> str:
    prompt = SQL_GENERATION_PROMPT.format(
        schema=schema_text,
        relationships=relationships,
        question=question
    )

    response = llm.complete(prompt)
    sql = response.text.strip()

    # 清理 <think> 标签
    if '<think>' in sql:
        sql = re.sub(r'<think>.*?</think>', '', sql, flags=re.DOTALL).strip()

    # 清理 markdown 代码块
    if sql.startswith('```'):
        lines = sql.split('\n')
        end_idx = len(lines)
        for i, line in enumerate(lines[1:], 1):
            if line.strip().startswith('```'):
                end_idx = i
                break
        sql = '\n'.join(lines[1:end_idx])

    return sql.strip()


def evaluate_schema_linking(predicted_tables: list, expected_tables: list) -> dict:
    predicted_set = set(t.lower() for t in predicted_tables)
    expected_set = set(t.lower() for t in expected_tables)

    recalled = predicted_set & expected_set

    recall = len(recalled) / len(expected_set) if expected_set else 0
    precision = len(recalled) / len(predicted_set) if predicted_set else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'predicted_tables': list(predicted_tables),
        'expected_tables': list(expected_tables),
        'recalled_tables': list(recalled),
        'missing_tables': list(expected_set - predicted_set),
        'extra_tables': list(predicted_set - expected_set),
        'recall': recall,
        'precision': precision,
        'f1': f1
    }


def run_test():
    print("=" * 70)
    print("LinkAlign 端到端测试")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n[1] 初始化 LLM...")
    llm = QwenModel(
        model_name=QWEN_MODEL,
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=0.1
    )
    print(f"    模型: {QWEN_MODEL}")

    print("\n[2] 加载数据...")
    test_cases = load_test_cases()
    all_tables = load_all_schemas()
    print(f"    测试用例: {len(test_cases)} 个")
    print(f"    数据库表: {len(all_tables)} 个")
    print(f"    核心表配置: {len(CORE_TABLES_CONFIG)} 个")

    print("\n[3] 开始测试...")
    results = []

    for i, test_case in enumerate(test_cases):
        print(f"\n{'─' * 70}")
        print(f"测试 {i+1}/{len(test_cases)}: {test_case['instance_id']}")
        print(f"问题: {test_case['question']}")

        start_time = time.time()

        # Step 1: Schema Linking
        print("\n  [Step 1] Schema Linking...")
        predicted_tables = schema_linking(test_case['question'], all_tables)

        sl_eval = evaluate_schema_linking(predicted_tables, test_case['expected_tables'])
        print(f"    预测表: {predicted_tables}")
        print(f"    期望表: {test_case['expected_tables']}")
        print(f"    召回率: {sl_eval['recall']:.2%} | 精确率: {sl_eval['precision']:.2%}")
        if sl_eval['missing_tables']:
            print(f"    ⚠ 缺失: {sl_eval['missing_tables']}")

        # Step 2: 准备 Schema
        print("\n  [Step 2] 准备 Schema...")
        schema_text = format_schema_for_sql(all_tables, predicted_tables)
        relationships = infer_table_relationships(all_tables, predicted_tables)
        print(f"    使用 {len(predicted_tables)} 个表")

        # Step 3: 生成 SQL
        print("\n  [Step 3] 生成 SQL...")
        try:
            generated_sql = generate_sql(llm, test_case['question'], schema_text, relationships)
            sql_preview = generated_sql.replace('\n', ' ')[:120]
            print(f"    生成: {sql_preview}...")
        except Exception as e:
            generated_sql = f"ERROR: {e}"
            print(f"    错误: {e}")

        elapsed = time.time() - start_time

        result = {
            'instance_id': test_case['instance_id'],
            'question': test_case['question'],
            'expected_tables': test_case['expected_tables'],
            'predicted_tables': predicted_tables,
            'schema_linking_recall': sl_eval['recall'],
            'schema_linking_precision': sl_eval['precision'],
            'schema_linking_f1': sl_eval['f1'],
            'missing_tables': sl_eval['missing_tables'],
            'generated_sql': generated_sql,
            'ground_truth_sql': test_case['ground_truth_sql'],
            'elapsed_seconds': elapsed
        }
        results.append(result)

        print(f"\n  耗时: {elapsed:.2f} 秒")

    # 汇总
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)

    avg_recall = sum(r['schema_linking_recall'] for r in results) / len(results)
    avg_precision = sum(r['schema_linking_precision'] for r in results) / len(results)
    avg_f1 = sum(r['schema_linking_f1'] for r in results) / len(results)

    print(f"\nSchema Linking:")
    print(f"  召回率: {avg_recall:.2%}")
    print(f"  精确率: {avg_precision:.2%}")
    print(f"  F1:     {avg_f1:.2%}")

    output_file = os.path.join(OUTPUT_DIR, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {output_file}")

    # SQL 对比
    print("\n" + "=" * 70)
    print("SQL 对比")
    print("=" * 70)

    for result in results:
        print(f"\n### {result['instance_id']}")
        print(f"问题: {result['question']}")
        print(f"\n期望:")
        print(f"  {result['ground_truth_sql']}")
        print(f"\n生成:")
        print(f"  {result['generated_sql']}")
        print("-" * 70)

    return results


if __name__ == "__main__":
    run_test()
