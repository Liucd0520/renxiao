#!/usr/bin/env python3
"""
融合方案测试：使用预计算 embedding + LLM 精选
借鉴 CHESS 的思想，在现有检索基础上加入 LLM 精选步骤
"""

import os
import sys
import json
import time
from collections import defaultdict
from openai import OpenAI

# 设置路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from retrieval.precompute_embeddings import FastRetriever

# 配置
QUESTIONS_FILE = "./docs/milestone_20241219/test_questions_300_v2.json"

# Qwen API 配置
QWEN_API_KEY = "yfzx202510"
QWEN_BASE_URL = "http://172.31.24.112:33080/v1"
QWEN_MODEL = "Qwen2.5-Coder-32B-Instruct"

# LLM 精选 Prompt
LLM_SELECT_PROMPT = """你是一个数据库专家。根据用户问题和候选表列表，选出真正需要的表。

用户问题: {question}

候选表（共 {num_tables} 张）:
{table_list}

请分析问题，从候选表中选出真正需要的表（通常 1-5 张）。

要求：
1. 只返回表名列表，用逗号分隔
2. 不要返回其他内容
3. 表名必须是候选表中的

返回格式：表名1, 表名2, 表名3"""


def load_questions(n_per_difficulty=20):
    """加载测试问题：简单、中等、困难各 n 个"""
    with open(QUESTIONS_FILE, 'r') as f:
        all_questions = json.load(f)
    
    simple = [q for q in all_questions if q.get("difficulty") == "simple"][:n_per_difficulty]
    medium = [q for q in all_questions if q.get("difficulty") == "medium"][:n_per_difficulty]
    hard = [q for q in all_questions if q.get("difficulty") == "hard"][:n_per_difficulty]
    
    return simple + medium + hard


class HybridRetrieverWithLLM:
    """融合检索器：预计算 embedding + LLM 精选"""
    
    def __init__(self):
        # 使用现有的 FastRetriever（已有核心列增强）
        self.base_retriever = FastRetriever()
        
        # 初始化 LLM 客户端
        self.llm_client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL
        )
        print("融合检索器就绪！")
    
    def retrieve_original(self, question, top_k=10):
        """原方法：使用 FastRetriever"""
        results = self.base_retriever.retrieve(question, top_k=top_k)
        return [t for t, _ in results]
    
    def retrieve_hybrid(self, question, coarse_k=20, final_k=10):
        """融合方法：粗召回 + LLM 精选"""
        # Step 1: 粗召回 TOP 20
        coarse_tables = self.retrieve_original(question, top_k=coarse_k)
        
        # Step 2: LLM 精选
        table_list = "\n".join([f"- {t}" for t in coarse_tables])
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
                # 如果 LLM 返回无效，回退到粗召回结果
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
                "hybrid": hybrid_status
            })
        
        print(f"[{i+1}/{len(questions)}] 原: {original_status}, 融合: {hybrid_status}")
    
    return results, diff_cases


def main():
    print("=" * 60)
    print("融合方案测试：预计算 embedding + LLM 精选")
    print("=" * 60)
    
    # 加载问题
    questions = load_questions(n_per_difficulty=20)
    print(f"测试问题: {len(questions)} 个（简单/中等/困难各 20 个）")
    
    # 初始化检索器
    retriever = HybridRetrieverWithLLM()
    
    # 运行测试
    print("\n开始测试...")
    start_time = time.time()
    results, diff_cases = test_retrieval(retriever, questions)
    elapsed = time.time() - start_time
    print(f"\n测试完成！耗时: {elapsed:.1f} 秒")
    
    # 计算总数
    total = results["original"]["success"] + results["original"]["partial"] + results["original"]["fail"]
    
    # 生成报告
    report = f"""# 融合方案测试报告：预计算 embedding + LLM 精选

**日期**: 2024-12-23  
**测试问题**: {total} 个（简单、中等、困难各 20 个）
**耗时**: {elapsed:.1f} 秒

---

## 1. 总体结果

| 方法 | 完全召回 | 部分召回 | 失败 | 召回率 |
|-----|---------|---------|------|-------|
| **原方法** (核心列增强) | {results['original']['success']} | {results['original']['partial']} | {results['original']['fail']} | **{results['original']['success']/total*100:.1f}%** |
| **融合方法** (粗召回+LLM精选) | {results['hybrid']['success']} | {results['hybrid']['partial']} | {results['hybrid']['fail']} | **{results['hybrid']['success']/total*100:.1f}%** |

---

## 2. 效果对比

| 指标 | 原方法 | 融合方法 | 差异 |
|-----|-------|---------|-----|
| 完全召回 | {results['original']['success']} | {results['hybrid']['success']} | {results['hybrid']['success'] - results['original']['success']:+d} |
| 召回率 | {results['original']['success']/total*100:.1f}% | {results['hybrid']['success']/total*100:.1f}% | {(results['hybrid']['success']-results['original']['success'])/total*100:+.1f}% |

---

## 3. 差异案例（共 {len(diff_cases)} 个）

"""
    
    # 添加差异案例
    positive = [c for c in diff_cases if c["hybrid"] == "success" and c["original"] != "success"]
    negative = [c for c in diff_cases if c["original"] == "success" and c["hybrid"] != "success"]
    
    report += f"### 3.1 融合方法更好的案例（{len(positive)} 个）\n\n"
    for c in positive[:5]:
        report += f"- **{c['difficulty']}**: {c['question']} | 原: {c['original']} → 融合: {c['hybrid']}\n"
    
    report += f"\n### 3.2 原方法更好的案例（{len(negative)} 个）\n\n"
    for c in negative[:5]:
        report += f"- **{c['difficulty']}**: {c['question']} | 原: {c['original']} → 融合: {c['hybrid']}\n"
    
    report += """
---

## 4. 结论

### 融合方法分析
- **思路**: 先用向量检索粗召回 TOP 20，再用 LLM 精选最相关的表
- **优势**: LLM 能理解问题语义，可能选出更精准的表
- **劣势**: 增加 1 次 LLM 调用，速度变慢，成本增加

### 建议
基于测试结果决定是否采用融合方案。

---
*报告生成时间: 2024-12-23*
"""
    
    output_path = "./docs/milestone_20241219/hybrid_retrieval_test_report.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {output_path}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("结果摘要")
    print("=" * 60)
    print(f"原方法召回率: {results['original']['success']}/{total} ({results['original']['success']/total*100:.1f}%)")
    print(f"融合方法召回率: {results['hybrid']['success']}/{total} ({results['hybrid']['success']/total*100:.1f}%)")
    print(f"差异: {results['hybrid']['success'] - results['original']['success']:+d}")


if __name__ == "__main__":
    main()
