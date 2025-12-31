#!/usr/bin/env python3
"""
公平对比测试：向量检索 vs 向量检索+LLM精选
使用全量 Schema（344张表），不使用核心列增强

对比方案：
1. 原方法：BGE-M3 Sparse 检索全量 Schema → TOP 10
2. 融合方法：BGE-M3 检索 TOP 20 → LLM 精选（使用增强表描述）
"""

import os
import sys
import json
import time
import glob
from collections import defaultdict
from openai import OpenAI

# 设置路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from FlagEmbedding import BGEM3FlagModel

# 配置
QUESTIONS_FILE = "./docs/milestone_20241219/test_questions_300_v2.json"
# 使用全量表级别 Schema（不是核心列增强版）
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level/netcaredb_ai"
# 使用增强后的表描述给 LLM
TABLE_ENHANCED_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"

# Qwen API 配置
QWEN_API_KEY = "yfzx202510"
QWEN_BASE_URL = "http://172.31.24.112:33080/v1"
QWEN_MODEL = "Qwen2.5-Coder-32B-Instruct"

# LLM 精选 Prompt
LLM_SELECT_PROMPT = """你是一个数据库专家。根据用户问题和候选表列表，选出真正需要的表。

用户问题: {question}

候选表（共 {num_tables} 张）:
{table_list}

请分析问题，从候选表中选出真正需要用到的表（通常 1-5 张）。

要求：
1. 仔细阅读每张表的描述，选择与问题相关的表
2. 只返回表名列表，用逗号分隔
3. 不要返回其他内容

返回格式：表名1, 表名2, 表名3"""


def load_all_tables_schema():
    """加载全量表 Schema（用于向量检索）"""
    tables = {}
    for f in glob.glob(f"{TABLE_SCHEMA_DIR}/*.json"):
        if f.endswith("_table.json"):
            continue
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                table_name = data.get("meta_data", {}).get("table_name", "")
                if table_name:
                    # 构建表描述文本
                    cols = data.get("columns", [])[:10]
                    col_texts = [f"{c['name']}: {c.get('description', '')}" for c in cols]
                    text = f"表名: {table_name}\n列: {', '.join(col_texts)}"
                    tables[table_name] = text
        except:
            continue
    return tables


def load_table_descriptions():
    """加载增强后的表描述（用于 LLM 精选）"""
    table_descs = {}
    for f in glob.glob(f"{TABLE_ENHANCED_DIR}/*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                table_name = data.get("meta_data", {}).get("table_name", "")
                if table_name:
                    desc = data.get("llm_description", "")
                    if not desc:
                        desc = data.get("table_comment", "") or "无描述"
                    table_descs[table_name] = desc
        except:
            continue
    return table_descs


def load_questions(n_per_difficulty=20):
    """加载测试问题：简单、中等、困难各 n 个"""
    with open(QUESTIONS_FILE, 'r') as f:
        all_questions = json.load(f)
    
    simple = [q for q in all_questions if q.get("difficulty") == "simple"][:n_per_difficulty]
    medium = [q for q in all_questions if q.get("difficulty") == "medium"][:n_per_difficulty]
    hard = [q for q in all_questions if q.get("difficulty") == "hard"][:n_per_difficulty]
    
    return simple + medium + hard


class FairComparisonRetriever:
    """公平对比检索器：使用全量 Schema + LLM 精选"""
    
    def __init__(self, table_schemas, table_descs):
        print("加载 BGE-M3 模型...")
        self.model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
        self.table_names = list(table_schemas.keys())
        self.table_texts = [table_schemas[t] for t in self.table_names]
        self.table_descs = table_descs
        
        print("编码全量 Schema（344 张表）...")
        output = self.model.encode(
            self.table_texts,
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        self.schema_sparse_vecs = output["lexical_weights"]
        
        # 初始化 LLM 客户端
        self.llm_client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL
        )
        print(f"就绪！共 {len(self.table_names)} 张表")
    
    def retrieve_original(self, question, top_k=10):
        """原方法：纯向量检索 TOP K"""
        query_out = self.model.encode(
            [question],
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        query_sparse = query_out["lexical_weights"][0]
        
        scores = []
        for i, schema_sparse in enumerate(self.schema_sparse_vecs):
            score = self.model.compute_lexical_matching_score(query_sparse, schema_sparse)
            scores.append((self.table_names[i], float(score)))
        
        sorted_tables = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        return [t for t, _ in sorted_tables]
    
    def retrieve_hybrid(self, question, coarse_k=20, final_k=10):
        """融合方法：向量粗召回 + LLM 精选（带增强描述）"""
        # Step 1: 向量粗召回 TOP 20
        coarse_tables = self.retrieve_original(question, top_k=coarse_k)
        
        # Step 2: 构建表描述列表（使用增强描述）
        table_list_items = []
        for t in coarse_tables:
            desc = self.table_descs.get(t, "无描述")
            if len(desc) > 100:
                desc = desc[:100] + "..."
            table_list_items.append(f"- **{t}**: {desc}")
        table_list = "\n".join(table_list_items)
        
        prompt = LLM_SELECT_PROMPT.format(
            question=question,
            num_tables=len(coarse_tables),
            table_list=table_list
        )
        
        try:
            response = self.llm_client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500
            )
            selected_text = response.choices[0].message.content.strip()
            
            # 解析返回的表名
            selected_tables = [t.strip() for t in selected_text.split(",")]
            coarse_lower = {t.lower(): t for t in coarse_tables}
            valid_tables = [coarse_lower[t.lower()] for t in selected_tables if t.lower() in coarse_lower]
            
            if not valid_tables:
                return coarse_tables[:final_k]
            
            return valid_tables[:final_k]
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return coarse_tables[:final_k]


def test_retrieval(retriever, questions):
    """测试召回率"""
    results = {
        "original": {"success": 0, "partial": 0, "fail": 0},
        "hybrid": {"success": 0, "partial": 0, "fail": 0}
    }
    diff_cases = []
    
    for i, q in enumerate(questions):
        expected = set(t.lower() for t in q.get("tables", []))
        if not expected:
            continue
        
        # 原方法
        original_tables = retriever.retrieve_original(q["question"])
        original_set = set(t.lower() for t in original_tables)
        original_matched = expected & original_set
        
        if len(original_matched) == len(expected):
            results["original"]["success"] += 1
            original_status = "success"
        elif original_matched:
            results["original"]["partial"] += 1
            original_status = "partial"
        else:
            results["original"]["fail"] += 1
            original_status = "fail"
        
        # 融合方法
        hybrid_tables = retriever.retrieve_hybrid(q["question"])
        hybrid_set = set(t.lower() for t in hybrid_tables)
        hybrid_matched = expected & hybrid_set
        
        if len(hybrid_matched) == len(expected):
            results["hybrid"]["success"] += 1
            hybrid_status = "success"
        elif hybrid_matched:
            results["hybrid"]["partial"] += 1
            hybrid_status = "partial"
        else:
            results["hybrid"]["fail"] += 1
            hybrid_status = "fail"
        
        if original_status != hybrid_status:
            diff_cases.append({
                "question": q["question"][:60] + "...",
                "difficulty": q.get("difficulty", "unknown"),
                "expected": list(expected),
                "original": original_status,
                "hybrid": hybrid_status
            })
        
        print(f"[{i+1}/{len(questions)}] 全量原方法: {original_status}, 融合: {hybrid_status}")
    
    return results, diff_cases


def main():
    print("=" * 60)
    print("公平对比测试：全量 Schema + LLM 精选")
    print("=" * 60)
    
    # 加载全量 Schema
    table_schemas = load_all_tables_schema()
    print(f"加载了 {len(table_schemas)} 张表的全量 Schema")
    
    # 加载增强描述
    table_descs = load_table_descriptions()
    print(f"加载了 {len(table_descs)} 张表的增强描述")
    
    # 加载问题
    questions = load_questions(n_per_difficulty=20)
    print(f"测试问题: {len(questions)} 个")
    
    # 初始化检索器
    retriever = FairComparisonRetriever(table_schemas, table_descs)
    
    print("\n开始测试...")
    start_time = time.time()
    results, diff_cases = test_retrieval(retriever, questions)
    elapsed = time.time() - start_time
    print(f"\n测试完成！耗时: {elapsed:.1f} 秒")
    
    total = results["original"]["success"] + results["original"]["partial"] + results["original"]["fail"]
    
    positive = [c for c in diff_cases if c["hybrid"] == "success" and c["original"] != "success"]
    negative = [c for c in diff_cases if c["original"] == "success" and c["hybrid"] != "success"]
    
    # 生成报告
    report = f"""# 公平对比测试报告：全量 Schema + LLM 精选

**日期**: 2024-12-23  
**测试配置**: 使用全量 344 张表（非核心列增强版本）  
**测试问题**: {total} 个（简单、中等、困难各 20 个）  
**耗时**: {elapsed:.1f} 秒

---

## 1. 总体结果

| 方法 | 完全召回 | 部分召回 | 失败 | 召回率 |
|-----|---------|---------|------|-------|
| **全量向量检索** (BGE-M3 TOP 10) | {results['original']['success']} | {results['original']['partial']} | {results['original']['fail']} | **{results['original']['success']/total*100:.1f}%** |
| **融合方法** (TOP 20 + LLM精选) | {results['hybrid']['success']} | {results['hybrid']['partial']} | {results['hybrid']['fail']} | **{results['hybrid']['success']/total*100:.1f}%** |

---

## 2. 效果对比

| 指标 | 全量检索 | 融合方法 | 差异 |
|-----|---------|---------|-----|
| 完全召回 | {results['original']['success']} | {results['hybrid']['success']} | {results['hybrid']['success'] - results['original']['success']:+d} |
| 召回率 | {results['original']['success']/total*100:.1f}% | {results['hybrid']['success']/total*100:.1f}% | {(results['hybrid']['success']-results['original']['success'])/total*100:+.1f}% |

---

## 3. 差异案例（共 {len(diff_cases)} 个）

### 3.1 融合方法更好的案例（{len(positive)} 个）

"""
    
    for i, c in enumerate(positive[:5]):
        report += f"{i+1}. **{c['difficulty']}**: {c['question']} | 全量: {c['original']} → 融合: {c['hybrid']}\n"
    
    report += f"\n### 3.2 全量检索更好的案例（{len(negative)} 个）\n\n"
    
    for i, c in enumerate(negative[:5]):
        report += f"{i+1}. **{c['difficulty']}**: {c['question']} | 全量: {c['original']} → 融合: {c['hybrid']}\n"
    
    report += """
---

## 4. 结论

### 公平对比结果
- 使用相同的全量 Schema（344 张表）
- 对比纯向量检索 vs 向量检索+LLM精选

### 关键发现
基于测试结果分析 LLM 精选是否能在全量 Schema 场景下提升召回率。

---
*报告生成时间: 2024-12-23*
"""
    
    output_path = "./docs/milestone_20241219/fair_comparison_test_report.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {output_path}")
    
    print("\n" + "=" * 60)
    print("结果摘要")
    print("=" * 60)
    print(f"全量向量检索: {results['original']['success']}/{total} ({results['original']['success']/total*100:.1f}%)")
    print(f"融合方法: {results['hybrid']['success']}/{total} ({results['hybrid']['success']/total*100:.1f}%)")
    print(f"差异: {results['hybrid']['success'] - results['original']['success']:+d}")


if __name__ == "__main__":
    main()
