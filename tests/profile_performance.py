#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能分析脚本 - 测量 FusionSQL 和 SQL Researcher 各组件耗时

用法:
    python tests/profile_performance.py
"""

import time
import sys
import os
import asyncio

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class Timer:
    """简单计时器"""
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.elapsed = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start_time
        print(f"  [{self.name}] {self.elapsed:.2f}s")


def profile_fusionsql_components():
    """分析 FusionSQL 各组件耗时"""
    print("\n" + "=" * 60)
    print("FusionSQL 组件性能分析")
    print("=" * 60)

    test_question = "查询客户测试客户名下有多少设备"
    results = {}

    # 1. 测试 FastRetriever 初始化
    print("\n1. FastRetriever 初始化")
    with Timer("加载 embedding 文件") as t:
        import pickle
        embeddings_file = os.path.join(PROJECT_ROOT, "fusionsql/schema_embeddings_v3.pkl")
        with open(embeddings_file, 'rb') as f:
            data = pickle.load(f)
    results["load_embeddings"] = t.elapsed

    with Timer("加载 BGE-M3 模型") as t:
        from FlagEmbedding import BGEM3FlagModel
        LOCAL_MODEL_PATH = "/Users/jason/Documents/实习/理想实习/LinkAlign/embed_model_cache/BAAI/bge-m3"
        model = BGEM3FlagModel(LOCAL_MODEL_PATH, use_fp16=True)
    results["load_bge_m3"] = t.elapsed

    # 2. 测试检索
    print("\n2. 检索性能")
    with Timer("BGE-M3 编码查询") as t:
        query_output = model.encode(
            [test_question],
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
    results["encode_query"] = t.elapsed

    with Timer("计算 lexical matching (全部 schema)") as t:
        query_sparse = query_output["lexical_weights"][0]
        lexical_weights = data["lexical_weights"]
        schemas = data["schemas"]
        scores = []
        for i, schema in enumerate(schemas):
            score = model.compute_lexical_matching_score(query_sparse, lexical_weights[i])
            scores.append((schema.get('table_name'), float(score)))
    results["compute_matching"] = t.elapsed

    # 3. 测试完整 Pipeline
    print("\n3. 完整 Pipeline")
    with Timer("TextToSQL 初始化") as t:
        from fusionsql import TextToSQL
        pipeline = TextToSQL(enable_lsh=False)
    results["pipeline_init"] = t.elapsed

    with Timer("Pipeline.run()") as t:
        sql = pipeline.run(test_question)
    results["pipeline_run"] = t.elapsed

    # 4. 测试 LLM 调用
    print("\n4. LLM 调用")
    with Timer("Qwen3 MoE 单次调用") as t:
        from fusionsql.llm import QwenLLM
        llm = QwenLLM(preset="qwen3_moe")
        response = llm.complete("你好，请用一个词回复")
    results["llm_call_moe"] = t.elapsed

    with Timer("Qwen32B 单次调用") as t:
        llm32b = QwenLLM(preset="qwen32b")
        response = llm32b.complete("你好，请用一个词回复")
    results["llm_call_32b"] = t.elapsed

    # 汇总
    print("\n" + "=" * 60)
    print("耗时汇总")
    print("=" * 60)
    total = sum(results.values())
    for name, elapsed in results.items():
        pct = elapsed / total * 100
        print(f"  {name}: {elapsed:.2f}s ({pct:.1f}%)")
    print(f"\n  总计: {total:.2f}s")

    return results


async def profile_async_pipeline():
    """分析异步 Pipeline 性能"""
    print("\n" + "=" * 60)
    print("异步 Pipeline 性能分析")
    print("=" * 60)

    test_question = "现在平台上有多少家客户"

    from fusionsql.pipeline import AsyncTextToSQL

    with Timer("AsyncTextToSQL 初始化") as t:
        pipeline = AsyncTextToSQL(enable_lsh=False)

    with Timer("异步 Pipeline.run()") as t:
        sql = await pipeline.run(test_question)

    print(f"\n生成的 SQL: {sql[:100]}...")


def profile_db_execution():
    """分析数据库执行性能"""
    print("\n" + "=" * 60)
    print("数据库执行性能分析")
    print("=" * 60)

    import pymysql

    config = {
        "host": "172.31.26.206",
        "port": 3306,
        "user": "ai_test",
        "password": "Netcare@13579",
        "database": "netcaredb_ai",
    }

    test_sqls = [
        "SELECT COUNT(*) FROM t_bz_config_customer",
        "SELECT COUNT(*) FROM t_bz_config_ci_ne_root",
        "SELECT * FROM t_bz_config_customer LIMIT 10",
    ]

    with Timer("数据库连接") as t:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

    for sql in test_sqls:
        with Timer(f"执行: {sql[:40]}...") as t:
            cursor.execute(sql)
            result = cursor.fetchall()

    cursor.close()
    conn.close()


def estimate_full_flow_time():
    """估算完整流程耗时"""
    print("\n" + "=" * 60)
    print("完整流程耗时估算")
    print("=" * 60)

    # 基于测量值估算
    steps = [
        ("clarify_with_user (LLM)", 20, "可跳过"),
        ("decompose_question (LLM)", 25, "必需"),
        ("review_decomposition", 0, "人机交互"),
        ("sql_supervisor (LLM)", 20, "必需"),
        ("sql_researcher (LLM)", 20, "必需"),
        ("fusionsql_query (BGE-M3 + LLM)", 25, "必需"),
        ("execute_sql", 2, "必需"),
        ("compress_sql_research (LLM)", 15, "可简化"),
        ("final_sql_report (LLM)", 20, "必需"),
    ]

    total_current = sum(s[1] for s in steps)
    total_optimized = sum(s[1] for s in steps if s[2] == "必需")

    print("\n当前流程:")
    for name, time_s, status in steps:
        print(f"  {name}: ~{time_s}s ({status})")

    print(f"\n  当前总计: ~{total_current}s ({total_current/60:.1f}分钟)")
    print(f"  优化后估计: ~{total_optimized}s ({total_optimized/60:.1f}分钟)")

    print("\n优化建议:")
    print("  1. 跳过 clarify_with_user: 节省 ~20s")
    print("  2. 简化 decompose_question: 对简单问题直接执行")
    print("  3. 合并 compress + final_report: 节省 ~15s")
    print("  4. 使用更快的模型: Qwen3 MoE vs 32B")
    print("  5. 批量并行处理: 多个子问题并行")


if __name__ == "__main__":
    print("🔍 FusionSQL + SQL Researcher 性能分析")
    print("=" * 60)

    # 运行分析
    try:
        fusionsql_results = profile_fusionsql_components()
    except Exception as e:
        print(f"FusionSQL 分析失败: {e}")

    try:
        asyncio.run(profile_async_pipeline())
    except Exception as e:
        print(f"异步 Pipeline 分析失败: {e}")

    try:
        profile_db_execution()
    except Exception as e:
        print(f"数据库分析失败: {e}")

    estimate_full_flow_time()
