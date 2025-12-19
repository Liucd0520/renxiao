#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全流程批量测试脚本

测试步骤：
1. 表+列融合检索（找出相关的表）
2. 三种 Schema 格式生成 SQL
3. 输出详细报告
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from openai import OpenAI
from FlagEmbedding import BGEM3FlagModel
from config import QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL

# 配置路径
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
OUTPUT_FILE = "./docs/milestone_20241217_table_column_fusion/full_pipeline_test_report.md"

# 检索配置
TABLE_TOP_K = 10
COLUMN_TOP_K = 200

# 测试问题（6个新问题）
TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "最近一年某客户的告警按照类型统计",
        "description": "需要统计某客户近一年的告警，按告警类型分类"
    },
    {
        "id": 2,
        "question": "哪些设备告警持续时间最长，给出TOP排名",
        "description": "需要计算告警持续时间并排名"
    },
    {
        "id": 3,
        "question": "某客户设备按照区域分别统计数量和设备详情，如设备名称、别名、区域、场所、IP、激活状态等",
        "description": "按区域统计设备信息"
    },
    {
        "id": 4,
        "question": "哪些设备近1个月告警次数最多给出排名",
        "description": "统计近一个月告警次数并排名"
    },
    {
        "id": 5,
        "question": "统计某客户工作日上班时间早上9点至晚上6点之间的告警情况",
        "description": "按工作日时间段统计告警"
    },
    {
        "id": 6,
        "question": "全平台告警级别分别统计",
        "description": "按告警级别统计"
    },
]

# SQL Prompt
SQL_PROMPT = """你是一个资深的 MySQL 专家。请根据用户问题和数据库 Schema，生成正确的 SQL 查询。

## 用户问题
{question}

## 数据库 Schema
{schema}

## 任务
请仔细分析用户问题和数据库 Schema：
1. 深度思考：这个问题需要查询哪些表？表之间如何关联？
2. 反复推敲：选择最准确的字段，确保条件逻辑正确
3. 验证检查：SQL 语法是否正确？能否得到用户想要的结果？

请先进行深度思考，然后输出最终的 SQL 查询。

## SQL 查询
"""


def load_bge_m3():
    """加载 BGE-M3 模型"""
    print("加载 BGE-M3 模型...")
    model = BGEM3FlagModel(
        './embed_model_cache/BAAI/bge-m3',
        use_fp16=True
    )
    print("模型加载完成")
    return model


def load_all_table_schemas():
    """加载所有表级别 Schema"""
    schemas = []
    table_dir = Path(TABLE_SCHEMA_DIR)
    for json_file in table_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            schemas.append({
                "table_name": data.get("table_name", json_file.stem),
                "embedding_text": data.get("embedding_text", ""),
                "llm_description": data.get("llm_description", ""),
                "data": data
            })
    return schemas


def load_all_column_schemas():
    """加载所有列级别 Schema"""
    columns = []
    col_dir = Path(COLUMN_SCHEMA_DIR)
    for json_file in col_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            meta = data.get("meta_data", {})
            embedding_text = data.get("embedding_text", "")
            columns.append({
                "table_name": meta.get("table_name", ""),
                "column_name": data.get("column_name", ""),
                "column_type": data.get("column_types", ""),
                "embedding_text": embedding_text
            })
    return columns


def retrieve_tables_fusion(model, query, table_schemas, column_schemas):
    """表+列融合检索"""
    # 1. 表级别 Sparse 检索
    table_texts = [t["embedding_text"] for t in table_schemas]
    table_pairs = [[query, t] for t in table_texts]
    
    table_scores = model.compute_score(
        table_pairs,
        max_passage_length=512,
        weights_for_different_modes=[0.0, 1.0, 0.0]  # 只用 Sparse
    )
    
    if isinstance(table_scores, dict):
        table_scores = table_scores.get('colbert+sparse+dense', table_scores.get('sparse', []))
    
    table_results = []
    for i, score in enumerate(table_scores):
        table_results.append({
            "table_name": table_schemas[i]["table_name"],
            "score": float(score),
            "source": "table"
        })
    table_results.sort(key=lambda x: x["score"], reverse=True)
    table_top = {r["table_name"]: r["score"] for r in table_results[:TABLE_TOP_K]}
    
    # 2. 列级别 Sparse 检索
    col_texts = [c["embedding_text"] for c in column_schemas if c["embedding_text"]]
    col_pairs = [[query, c] for c in col_texts]
    
    col_scores = model.compute_score(
        col_pairs,
        max_passage_length=512,
        weights_for_different_modes=[0.0, 1.0, 0.0]
    )
    
    if isinstance(col_scores, dict):
        col_scores = col_scores.get('colbert+sparse+dense', col_scores.get('sparse', []))
    
    # 累加列分数到表
    col_table_scores = {}
    valid_cols = [c for c in column_schemas if c["embedding_text"]]
    for i, score in enumerate(col_scores):
        table_name = valid_cols[i]["table_name"]
        if table_name not in col_table_scores:
            col_table_scores[table_name] = 0
        col_table_scores[table_name] += float(score)
    
    col_sorted = sorted(col_table_scores.items(), key=lambda x: x[1], reverse=True)
    col_top = {name: score for name, score in col_sorted[:TABLE_TOP_K]}
    
    # 3. 融合（取并集）
    fusion_tables = set(table_top.keys()) | set(col_top.keys())
    
    return {
        "fusion_tables": list(fusion_tables),
        "table_top": table_top,
        "col_top": col_top
    }


def load_table_data(table_name):
    """加载单个表的详细数据"""
    table_file = Path(TABLE_SCHEMA_DIR) / f"{table_name}.json"
    if table_file.exists():
        with open(table_file, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
    else:
        table_data = {"table_name": table_name}
    
    columns = []
    for col_file in Path(COLUMN_SCHEMA_DIR).glob("*.json"):
        with open(col_file, 'r', encoding='utf-8') as f:
            col_data = json.load(f)
        meta = col_data.get("meta_data", {})
        if meta.get("table_name", "").lower() == table_name.lower():
            columns.append({
                "name": col_data.get("column_name", ""),
                "type": col_data.get("column_types", ""),
                "description": col_data.get("column_description", "")
            })
    return table_data, columns


def format_full(tables):
    """完整格式：列名+类型+描述"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        lines = [f"### 表: {table_name}"]
        if table_data.get("llm_description"):
            lines.append(f"说明: {table_data['llm_description'][:200]}...")
        lines.append("列:")
        for c in columns:
            desc = c.get('description', '')[:50] if c.get('description') else ''
            lines.append(f"  - {c['name']} ({c['type']}): {desc}")
        result.append("\n".join(lines))
    return "\n\n".join(result)


def format_compact(tables):
    """精简格式：列名+类型"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        lines = [f"表: {table_name}"]
        if table_data.get("llm_description"):
            lines.append(f"说明: {table_data['llm_description'][:100]}...")
        col_strs = [f"{c['name']}({c['type'][:20]})" for c in columns]
        lines.append(f"列: {', '.join(col_strs)}")
        result.append("\n".join(lines))
    return "\n\n".join(result)


def format_minimal(tables):
    """最精简格式：只有列名"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        desc = table_data.get("llm_description", "")[:80] + "..." if table_data.get("llm_description") else ""
        col_names = [c['name'] for c in columns]
        result.append(f"{table_name}: {desc}\n  列: {', '.join(col_names)}")
    return "\n\n".join(result)


def extract_sql(text):
    """提取 SQL，清理思考过程"""
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    
    if "```sql" in text:
        match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    elif "```" in text:
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    if "SELECT" in text.upper():
        idx = text.upper().find("SELECT")
        end_idx = len(text)
        for end_char in [";", "\n\n"]:
            pos = text.find(end_char, idx)
            if pos != -1 and pos < end_idx:
                end_idx = pos + 1
        return text[idx:end_idx].strip()
    
    return text.strip()[:500]


def call_llm(prompt):
    """调用 LLM"""
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.1,
            timeout=120.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"


def run_full_pipeline_test():
    print("=" * 80)
    print("全流程批量测试")
    print("=" * 80)
    print(f"模型: {QWEN_MODEL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试问题数: {len(TEST_QUESTIONS)}")
    print("=" * 80)
    
    # 加载模型和数据
    model = load_bge_m3()
    table_schemas = load_all_table_schemas()
    column_schemas = load_all_column_schemas()
    print(f"加载 {len(table_schemas)} 个表, {len(column_schemas)} 个列")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# 全流程批量测试报告\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**模型**: {QWEN_MODEL}\n\n")
        f.write(f"**表数量**: {len(table_schemas)} | **列数量**: {len(column_schemas)}\n\n")
        f.write("---\n\n")
        
        f.write("## 测试概述\n\n")
        f.write("| ID | 问题 |\n")
        f.write("|----|----- |\n")
        for q in TEST_QUESTIONS:
            f.write(f"| {q['id']} | {q['question'][:50]}... |\n")
        f.write("\n---\n\n")
        
        for q in TEST_QUESTIONS:
            print(f"\n{'='*60}")
            print(f"测试 {q['id']}: {q['question'][:40]}...")
            print("=" * 60)
            
            f.write(f"## 测试 {q['id']}: {q['question']}\n\n")
            f.write(f"**描述**: {q['description']}\n\n")
            
            # Step 1: 表检索
            print("  [1/4] 表+列融合检索...")
            retrieval = retrieve_tables_fusion(model, q['question'], table_schemas, column_schemas)
            
            f.write("### 1. 检索结果\n\n")
            f.write(f"**融合后表数**: {len(retrieval['fusion_tables'])} 张\n\n")
            
            f.write("**表级别 Top 5**:\n")
            table_sorted = sorted(retrieval['table_top'].items(), key=lambda x: x[1], reverse=True)[:5]
            for name, score in table_sorted:
                f.write(f"- {name} ({score:.4f})\n")
            f.write("\n")
            
            f.write("**列级别累加分 Top 5**:\n")
            col_sorted = sorted(retrieval['col_top'].items(), key=lambda x: x[1], reverse=True)[:5]
            for name, score in col_sorted:
                f.write(f"- {name} ({score:.4f})\n")
            f.write("\n")
            
            f.write("**融合后表**:\n")
            f.write(f"```\n{', '.join(sorted(retrieval['fusion_tables']))}\n```\n\n")
            
            # Step 2-4: 三种格式生成 SQL
            formats = [
                ("完整格式", format_full),
                ("精简格式", format_compact),
                ("最精简格式", format_minimal)
            ]
            
            for idx, (format_name, format_func) in enumerate(formats, start=2):
                print(f"  [{idx}/4] {format_name} SQL 生成...")
                
                schema = format_func(retrieval['fusion_tables'][:10])  # 限制最多 10 张表
                prompt = SQL_PROMPT.format(question=q['question'], schema=schema)
                raw_response = call_llm(prompt)
                sql = extract_sql(raw_response)
                
                f.write(f"### {idx}. {format_name}\n\n")
                f.write(f"**Schema 字符数**: {len(schema)}\n\n")
                f.write(f"```sql\n{sql}\n```\n\n")
            
            f.write("---\n\n")
        
        # 汇总
        f.write("## 汇总\n\n")
        f.write("| 测试 | 融合表数 | 完整格式 | 精简格式 | 最精简格式 |\n")
        f.write("|-----|---------|---------|---------|----------|\n")
        f.write("| (需人工评估) | - | - | - | - |\n")
        f.write("\n")
        f.write("**注意**: 由于没有正确答案，SQL 质量需要人工评估。\n\n")
        
        f.write("---\n\n")
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"\n报告已保存: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_full_pipeline_test()
