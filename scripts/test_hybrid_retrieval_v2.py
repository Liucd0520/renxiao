#!/usr/bin/env python3
"""
融合方案测试 V2：使用增强描述 + LLM 精选
给 LLM 提供增强后的表描述，而不是只有表名
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

from retrieval.precompute_embeddings import FastRetriever

# 配置
QUESTIONS_FILE = "./docs/milestone_20241219/test_questions_300_v2.json"
TABLE_ENHANCED_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"

# Qwen API 配置
QWEN_API_KEY = "yfzx202510"
QWEN_BASE_URL = "http://172.31.24.112:33080/v1"
QWEN_MODEL = "Qwen2.5-Coder-32B-Instruct"

# LLM 精选 Prompt（提供完整描述）
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


def load_table_descriptions():
    """加载增强后的表描述"""
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


class HybridRetrieverV2:
    """融合检索器 V2：使用增强描述 + LLM 精选"""
    
    def __init__(self, table_descs):
        # 使用现有的 FastRetriever
        self.base_retriever = FastRetriever()
        self.table_descs = table_descs
        
        # 初始化 LLM 客户端
        self.llm_client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL
        )
        print("融合检索器 V2 就绪！")
    
    def retrieve_original(self, question, top_k=10):
        """原方法：使用 FastRetriever"""
        results = self.base_retriever.retrieve(question, top_k=top_k)
        return [t for t, _ in results]
    
    def retrieve_hybrid(self, question, coarse_k=20, final_k=10):
        """融合方法 V2：粗召回 + LLM 精选（带完整描述）"""
        # Step 1: 粗召回 TOP 20
        coarse_tables = self.retrieve_original(question, top_k=coarse_k)
        
        # Step 2: 构建表描述列表
        table_list_items = []
        for t in coarse_tables:
            desc = self.table_descs.get(t, "无描述")
            # 截断过长的描述
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
            # 过滤有效表名（不区分大小写）
            coarse_lower = {t.lower(): t for t in coarse_tables}
            valid_tables = []
            for t in selected_tables:
                t_lower = t.lower()
                if t_lower in coarse_lower:
                    valid_tables.append(coarse_lower[t_lower])
            
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
        
        # 测试原方法
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
        
        # 测试融合方法
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
        
        # 记录差异案例
        if original_status != hybrid_status:
            diff_cases.append({
                "question": q["question"][:50] + "...",
                "difficulty": q.get("difficulty", "unknown"),
                "expected": list(expected),
                "original": original_status,
                "hybrid": hybrid_status,
                "original_tables": original_tables[:5],
                "hybrid_tables": hybrid_tables[:5]
            })
        
        print(f"[{i+1}/{len(questions)}] 原: {original_status}, 融合V2: {hybrid_status}")
    
    return results, diff_cases


def main():
    print("=" * 60)
    print("融合方案测试 V2：增强描述 + LLM 精选")
    print("=" * 60)
    
    # 加载表描述
    table_descs = load_table_descriptions()
    print(f"加载了 {len(table_descs)} 张表的增强描述")
    
    # 加载问题
    questions = load_questions(n_per_difficulty=20)
    print(f"测试问题: {len(questions)} 个（简单/中等/困难各 20 个）")
    
    # 初始化检索器
    retriever = HybridRetrieverV2(table_descs)
    
    # 运行测试
    print("\n开始测试...")
    start_time = time.time()
    results, diff_cases = test_retrieval(retriever, questions)
    elapsed = time.time() - start_time
    print(f"\n测试完成！耗时: {elapsed:.1f} 秒")
    
    # 计算总数
    total = results["original"]["success"] + results["original"]["partial"] + results["original"]["fail"]
    
    # 生成报告
    positive = [c for c in diff_cases if c["hybrid"] == "success" and c["original"] != "success"]
    negative = [c for c in diff_cases if c["original"] == "success" and c["hybrid"] != "success"]
    
    report = f"""# 融合方案测试报告 V2：增强描述 + LLM 精选

**日期**: 2024-12-23  
**改进**: 给 LLM 提供增强后的表描述（而不是只有表名）  
**测试问题**: {total} 个（简单、中等、困难各 20 个）  
**耗时**: {elapsed:.1f} 秒

---

## 1. 总体结果

| 方法 | 完全召回 | 部分召回 | 失败 | 召回率 |
|-----|---------|---------|------|-------|
| **原方法** (核心列增强) | {results['original']['success']} | {results['original']['partial']} | {results['original']['fail']} | **{results['original']['success']/total*100:.1f}%** |
| **融合方法 V2** (增强描述+LLM) | {results['hybrid']['success']} | {results['hybrid']['partial']} | {results['hybrid']['fail']} | **{results['hybrid']['success']/total*100:.1f}%** |

---

## 2. 效果对比

| 指标 | 原方法 | 融合V2 | 差异 |
|-----|-------|--------|-----|
| 完全召回 | {results['original']['success']} | {results['hybrid']['success']} | {results['hybrid']['success'] - results['original']['success']:+d} |
| 召回率 | {results['original']['success']/total*100:.1f}% | {results['hybrid']['success']/total*100:.1f}% | {(results['hybrid']['success']-results['original']['success'])/total*100:+.1f}% |

---

## 3. 差异案例（共 {len(diff_cases)} 个）

### 3.1 融合V2更好的案例（{len(positive)} 个）

"""
    
    for i, c in enumerate(positive[:5]):
        report += f"{i+1}. **{c['difficulty']}**: {c['question']} | 原: {c['original']} → V2: {c['hybrid']}\n"
    
    report += f"\n### 3.2 原方法更好的案例（{len(negative)} 个）\n\n"
    
    for i, c in enumerate(negative[:5]):
        report += f"{i+1}. **{c['difficulty']}**: {c['question']} | 原: {c['original']} → V2: {c['hybrid']}\n"
    
    report += """
---

## 4. 结论

### 改进点
- V1（只有表名）: LLM 无法理解表的用途
- **V2（增强描述）**: LLM 能看到如 "【设备主表】存储设备基础信息" 这样的描述

### 建议
基于测试结果决定是否采用融合方案。

---
*报告生成时间: 2024-12-23*
"""
    
    output_path = "./docs/milestone_20241219/hybrid_retrieval_v2_test_report.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {output_path}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("结果摘要")
    print("=" * 60)
    print(f"原方法召回率: {results['original']['success']}/{total} ({results['original']['success']/total*100:.1f}%)")
    print(f"融合V2召回率: {results['hybrid']['success']}/{total} ({results['hybrid']['success']/total*100:.1f}%)")
    print(f"差异: {results['hybrid']['success'] - results['original']['success']:+d}")


if __name__ == "__main__":
    main()
