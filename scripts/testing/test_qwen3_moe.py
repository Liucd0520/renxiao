#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3 MoE 模型测试脚本

使用 qwen3_30b_a3b_2507 模型进行测试
服务器: 172.31.24.112:8502
API key: 不需要

保持解耦，不修改原有代码
"""

import os
import sys
import json
import csv
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from llms.qwen.QwenModel import QwenModel

# ========== Qwen3 MoE 模型配置 ==========
QWEN3_MOE_CONFIG = {
    "model_name": "qwen3_30b_a3b_2507",
    "base_url": "http://172.31.24.112:8502/v1",
    "api_key": "EMPTY",  # 不需要 API key
    "temperature": 0.1,
}

# ========== 测试配置 ==========
SCHEMA_DIR = os.path.join(PROJECT_ROOT, "spider2_dev/schemas_table_level_enhanced/netcaredb_ai")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs/milestone_20241230_qwen3_moe")


def get_qwen3_moe_model():
    """获取 Qwen3 MoE 模型实例"""
    return QwenModel(
        model_name=QWEN3_MOE_CONFIG["model_name"],
        base_url=QWEN3_MOE_CONFIG["base_url"],
        api_key=QWEN3_MOE_CONFIG["api_key"],
        temperature=QWEN3_MOE_CONFIG["temperature"],
    )


def test_model_connection():
    """测试模型连接"""
    print("=" * 60)
    print("测试 Qwen3 MoE 模型连接")
    print("=" * 60)
    print(f"模型: {QWEN3_MOE_CONFIG['model_name']}")
    print(f"服务器: {QWEN3_MOE_CONFIG['base_url']}")
    
    try:
        model = get_qwen3_moe_model()
        response = model.complete("你好，请简短回复。").text
        print(f"\n✅ 连接成功！")
        print(f"回复: {response[:100]}...")
        return True
    except Exception as e:
        print(f"\n❌ 连接失败！")
        print(f"错误: {e}")
        return False


def load_schemas(table_names):
    """加载表的 Schema"""
    schemas = {}
    for name in table_names:
        schema_file = os.path.join(SCHEMA_DIR, f"{name}.json")
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                schemas[name] = json.load(f)
    return schemas


def build_schema_text(schemas):
    """构建 Schema 文本"""
    parts = []
    for table_name, data in schemas.items():
        lines = [f"### 表: {table_name}"]
        llm_desc = data.get("llm_description", "")
        if llm_desc:
            lines.append(f"说明: {llm_desc}")
        
        columns = data.get("columns", [])
        lines.append("列:")
        for col in columns:
            col_str = f"  - {col['name']} ({col['type']})"
            if col.get('description'):
                col_str += f": {col['description']}"
            lines.append(col_str)
        
        parts.append("\n".join(lines))
    
    return "\n\n".join(parts)


SQL_GENERATION_PROMPT = """你是一个 MySQL 数据库专家。根据用户问题和相关表的 Schema，生成正确的 SQL 查询。

## 用户问题
{question}

## 相关表 Schema
{schema_text}

## 要求
1. 只输出一个完整的 SQL 语句
2. 不要解释，不要输出其他内容
3. 使用 MySQL 语法
4. 如果需要日期时间，使用 NOW() 函数

## SQL:
"""


def generate_sql_with_qwen3(model, question, table_names):
    """使用 Qwen3 生成 SQL"""
    schemas = load_schemas(table_names)
    schema_text = build_schema_text(schemas)
    
    prompt = SQL_GENERATION_PROMPT.format(
        question=question,
        schema_text=schema_text
    )
    
    response = model.complete(prompt).text.strip()
    
    # 清理响应
    import re
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
    response = re.sub(r'```sql\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    response = re.sub(r'^(SQL|sql):\s*', '', response.strip())
    
    return response.strip()


def test_7_questions():
    """测试 7 个原始问题"""
    print("\n" + "=" * 60)
    print("Qwen3 MoE 7 题测试")
    print("=" * 60)
    
    # 读取问题
    csv_file = os.path.join(PROJECT_ROOT, "cc_result.csv")
    questions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['query'].strip():
                questions.append({
                    "question": row['query'],
                    "correct_sql": row.get('正确SQL', '') or row['sql']
                })
    
    print(f"加载 {len(questions)} 个问题")
    
    # 加载检索器
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "our_algorithm"))
    from retriever import FastRetriever
    
    retriever = FastRetriever()
    model = get_qwen3_moe_model()
    
    results = []
    
    for i, q in enumerate(questions):
        print(f"\n[{i+1}/{len(questions)}] {q['question'][:40]}...")
        
        # 检索
        retrieved_raw = retriever.retrieve(q['question'], top_k=10)
        if retrieved_raw and isinstance(retrieved_raw[0], tuple):
            retrieved = [t[0] for t in retrieved_raw]
        else:
            retrieved = retrieved_raw
        
        print(f"  检索到 {len(retrieved)} 张表")
        
        # 使用前 10 张表生成 SQL（方案 A）
        sql = generate_sql_with_qwen3(model, q['question'], retrieved[:10])
        
        print(f"  生成 SQL: {sql[:60]}...")
        
        results.append({
            "id": i + 1,
            "question": q['question'],
            "correct_sql": q['correct_sql'],
            "retrieved_tables": retrieved,
            "qwen3_sql": sql
        })
    
    # 保存结果
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "qwen3_moe_7q_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    return results


def test_300_questions():
    """测试 300 个问题"""
    print("\n" + "=" * 60)
    print("Qwen3 MoE 300 题测试")
    print("=" * 60)
    
    # 读取 300 个问题
    questions_file = os.path.join(PROJECT_ROOT, "docs/milestone_20241224/test_questions_3tables_300.json")
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    print(f"加载 {len(questions)} 个问题")
    
    # 加载检索器
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "our_algorithm"))
    from retriever import FastRetriever
    
    retriever = FastRetriever()
    model = get_qwen3_moe_model()
    
    results = []
    
    for i, q in enumerate(questions):
        if (i + 1) % 10 == 0:
            print(f"[{i+1}/{len(questions)}]...")
        
        question = q.get('question', q.get('query', ''))
        
        # 检索
        retrieved_raw = retriever.retrieve(question, top_k=10)
        if retrieved_raw and isinstance(retrieved_raw[0], tuple):
            retrieved = [t[0] for t in retrieved_raw]
        else:
            retrieved = retrieved_raw
        
        # 使用前 10 张表生成 SQL（方案 A）
        sql = generate_sql_with_qwen3(model, question, retrieved[:10])
        
        results.append({
            "id": i + 1,
            "question": question,
            "retrieved_tables": retrieved,
            "qwen3_sql": sql
        })
    
    # 保存结果
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "qwen3_moe_300q_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Qwen3 MoE 模型测试")
    parser.add_argument("--test", choices=["connect", "7q", "300q", "all"], 
                        default="connect", help="测试类型")
    args = parser.parse_args()
    
    if args.test == "connect":
        test_model_connection()
    elif args.test == "7q":
        if test_model_connection():
            test_7_questions()
    elif args.test == "300q":
        if test_model_connection():
            test_300_questions()
    elif args.test == "all":
        if test_model_connection():
            test_7_questions()
            test_300_questions()
