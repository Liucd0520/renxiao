# -*- coding: utf-8 -*-
"""
Schema Linking 优化对比测试脚本

测试不同模式和参数配置对 Schema Linking 准确性的影响
"""

import json
import os
import sys
import time
import pandas as pd
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.SchemaLinkingTool import SchemaLinkingTool
from utils import parse_schema_from_df, parse_schemas_from_nodes
from pipes.RagPipeline import RagPipeLines
from llms.qwen.QwenModel import QwenModel
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
TEST_QUESTION = "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？"
EXPECTED_TABLES = ["t_bz_config_customer", "t_bz_config_ci_ne_root", "event_history"]  # 期望的表
DB_ID = "netcaredb_ai"
SCHEMA_PATH = "./spider2_dev/schemas"
OUTPUT_DIR = "./spider2_dev/test_results"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_vector_index(db_id: str, schema_path: str):
    """加载向量索引"""
    vector_dir = os.path.join(schema_path, db_id)
    vector_index = RagPipeLines.build_index_from_source(
        data_source=vector_dir,
        persist_dir=os.path.join(vector_dir, "vector_store"),
        is_vector_store_exist=True,
        index_method="VectorStoreIndex"
    )
    return vector_index


def extract_tables_from_nodes(nodes):
    """从节点中提取表名"""
    tables = set()
    for node in nodes:
        if hasattr(node, 'metadata') and 'table_name' in node.metadata:
            tables.add(node.metadata['table_name'])
        elif hasattr(node, 'node') and hasattr(node.node, 'metadata'):
            meta = node.node.metadata
            if 'table_name' in meta:
                tables.add(meta['table_name'])
    return tables


def extract_tables_from_df(df: pd.DataFrame):
    """从 DataFrame 中提取表名"""
    if 'Table Name' in df.columns:
        return set(df['Table Name'].unique())
    return set()


def calculate_metrics(result_tables: set, expected_tables: list):
    """计算评估指标"""
    expected_set = set(expected_tables)
    
    # 计算召回率 (期望表中有多少被找到)
    found_expected = result_tables.intersection(expected_set)
    recall = len(found_expected) / len(expected_set) if expected_set else 0
    
    # 计算精确率 (返回的表中有多少是期望的)
    precision = len(found_expected) / len(result_tables) if result_tables else 0
    
    # F1 分数
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "total_tables": len(result_tables),
        "expected_found": len(found_expected),
        "expected_missing": list(expected_set - result_tables),
        "noise_tables": len(result_tables) - len(found_expected),
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def test_agent_mode(llm, retriever, question: str, top_k: int, turn_n: int):
    """测试 Agent 模式"""
    logger.info(f"Testing Agent Mode: top_k={top_k}, turn_n={turn_n}")
    
    retriever.similarity_top_k = top_k
    
    start_time = time.time()
    nodes = SchemaLinkingTool.retrieve_complete_by_multi_agent_debate(
        llm=llm, 
        question=question,
        retriever_lis=[retriever],
        open_locate=False,
        output_format="node",
        logger=logger,
        retrieve_turn_n=turn_n
    )
    elapsed = time.time() - start_time
    
    df = parse_schemas_from_nodes(nodes)
    tables = extract_tables_from_df(df)
    
    return {
        "mode": "Agent",
        "top_k": top_k,
        "turn_n": turn_n,
        "time": elapsed,
        "tables": list(tables),
        "df": df
    }


def test_pipeline_mode(llm, retriever, question: str, top_k: int, turn_n: int):
    """测试 Pipeline 模式"""
    logger.info(f"Testing Pipeline Mode: top_k={top_k}, turn_n={turn_n}")
    
    retriever.similarity_top_k = top_k
    
    start_time = time.time()
    nodes = SchemaLinkingTool.retrieve_complete(
        llm=llm,
        question=question,
        retriever_lis=[retriever],
        open_reason_enhance=True,
        output_format="node",
        turn_n=turn_n
    )
    elapsed = time.time() - start_time
    
    # 处理返回值（可能是字符串或节点列表）
    if isinstance(nodes, list):
        df = parse_schemas_from_nodes(nodes)
        tables = extract_tables_from_df(df)
    else:
        df = pd.DataFrame()
        tables = set()
    
    return {
        "mode": "Pipeline",
        "top_k": top_k,
        "turn_n": turn_n,
        "time": elapsed,
        "tables": list(tables),
        "df": df
    }


def run_comparison_tests():
    """运行对比测试"""
    logger.info("=" * 60)
    logger.info("开始 Schema Linking 优化对比测试")
    logger.info("=" * 60)
    logger.info(f"测试问题: {TEST_QUESTION}")
    logger.info(f"期望表: {EXPECTED_TABLES}")
    logger.info("=" * 60)
    
    # 初始化 LLM
    llm = QwenModel(model_name="qwen-turbo", temperature=0.45)
    
    # 加载向量索引
    logger.info("加载向量索引...")
    vector_index = load_vector_index(DB_ID, SCHEMA_PATH)
    retriever = RagPipeLines.get_retriever(index=vector_index)
    
    # 定义测试配置
    test_configs = [
        # Agent 模式测试
        {"mode": "agent", "top_k": 10, "turn_n": 2},  # 当前配置
        {"mode": "agent", "top_k": 5, "turn_n": 1},   # 减少 top_k 和 turn_n
        {"mode": "agent", "top_k": 8, "turn_n": 1},   # 中等 top_k
        
        # Pipeline 模式测试
        {"mode": "pipeline", "top_k": 10, "turn_n": 2},
        {"mode": "pipeline", "top_k": 5, "turn_n": 1},
        {"mode": "pipeline", "top_k": 8, "turn_n": 1},
    ]
    
    results = []
    
    for config in test_configs:
        logger.info("-" * 40)
        
        # 重新获取 retriever（避免状态污染）
        retriever = RagPipeLines.get_retriever(index=vector_index)
        
        try:
            if config["mode"] == "agent":
                result = test_agent_mode(llm, retriever, TEST_QUESTION, config["top_k"], config["turn_n"])
            else:
                result = test_pipeline_mode(llm, retriever, TEST_QUESTION, config["top_k"], config["turn_n"])
            
            # 计算指标
            metrics = calculate_metrics(set(result["tables"]), EXPECTED_TABLES)
            result.update(metrics)
            
            # 保存 DataFrame
            if not result["df"].empty:
                filename = f"{config['mode']}_{config['top_k']}_{config['turn_n']}.xlsx"
                result["df"].to_excel(os.path.join(OUTPUT_DIR, filename), index=False)
            
            results.append(result)
            
            logger.info(f"结果: 共 {metrics['total_tables']} 个表, "
                       f"召回 {metrics['expected_found']}/{len(EXPECTED_TABLES)}, "
                       f"精确率 {metrics['precision']:.2%}, "
                       f"召回率 {metrics['recall']:.2%}, "
                       f"F1 {metrics['f1']:.2%}")
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            results.append({
                "mode": config["mode"],
                "top_k": config["top_k"],
                "turn_n": config["turn_n"],
                "error": str(e)
            })
    
    # 生成报告
    generate_report(results)
    
    return results


def generate_report(results):
    """生成测试报告"""
    report_path = os.path.join(OUTPUT_DIR, "comparison_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Schema Linking 优化对比报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 测试问题\n\n{TEST_QUESTION}\n\n")
        f.write(f"## 期望表\n\n{', '.join(EXPECTED_TABLES)}\n\n")
        f.write("## 测试结果对比\n\n")
        f.write("| 模式 | Top-K | Turn-N | 返回表数 | 召回表数 | 精确率 | 召回率 | F1 | 耗时(s) |\n")
        f.write("|------|-------|--------|----------|----------|--------|--------|-----|--------|\n")
        
        for r in results:
            if "error" in r:
                f.write(f"| {r['mode']} | {r['top_k']} | {r['turn_n']} | 错误 | - | - | - | - | - |\n")
            else:
                f.write(f"| {r['mode']} | {r['top_k']} | {r['turn_n']} | "
                       f"{r['total_tables']} | {r['expected_found']} | "
                       f"{r['precision']:.2%} | {r['recall']:.2%} | {r['f1']:.2%} | "
                       f"{r['time']:.2f} |\n")
        
        f.write("\n## 详细结果\n\n")
        for i, r in enumerate(results):
            if "error" not in r:
                f.write(f"### 配置 {i+1}: {r['mode']} (top_k={r['top_k']}, turn_n={r['turn_n']})\n\n")
                f.write(f"返回的表: {', '.join(sorted(r['tables']))}\n\n")
                if r.get('expected_missing'):
                    f.write(f"缺失的期望表: {', '.join(r['expected_missing'])}\n\n")
    
    logger.info(f"报告已保存到: {report_path}")


if __name__ == "__main__":
    results = run_comparison_tests()
    
    print("\n" + "=" * 60)
    print("测试完成! 请查看以下文件:")
    print(f"  - 对比报告: {OUTPUT_DIR}/comparison_report.md")
    print(f"  - 各配置的 Excel 文件: {OUTPUT_DIR}/*.xlsx")
    print("=" * 60)
