#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milvus BGE-M3 混合检索测试

使用 Milvus Lite + BGE-M3 的 Dense + Sparse 混合检索
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

# 添加项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from pymilvus import MilvusClient, DataType
from FlagEmbedding import BGEM3FlagModel
import numpy as np

# 配置
MILVUS_DB_PATH = "./milvus_hybrid.db"  # Milvus Lite 本地数据库
COLLECTION_NAME = "table_schema_hybrid"
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"

# BGE-M3 模型
MODEL_PATH = "./embed_model_cache/BAAI/bge-m3"

# 测试用例（完整 7 个）
TEST_CASES = [
    {
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected": ["event_history", "t_bz_config_ci_ne_root"]
    },
    {
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected": ["t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"]
    },
    {
        "question": "现在平台上有多少家客户",
        "expected": ["t_bz_config_customer"]
    },
    {
        "question": "现在平台上有多少台设备",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "上个月上线的新设备有多少",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "上个月下线的设备有多少",
        "expected": ["t_bz_config_ci_ne_root"]
    },
    {
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]
    },
]


def load_table_schemas():
    """加载所有表 Schema"""
    schemas = []
    schema_dir = Path(TABLE_SCHEMA_DIR)
    
    for json_file in schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("table_name", json_file.stem)
        
        # 构建 embedding text
        text_parts = [f"表名: {table_name}"]
        if data.get("llm_description"):
            text_parts.append(f"描述: {data['llm_description']}")
        elif data.get("table_comment"):
            text_parts.append(f"描述: {data['table_comment']}")
        
        # 添加列信息
        columns = data.get("columns", [])
        if columns:
            col_names = [c.get("name", "") for c in columns[:20]]  # 最多 20 列
            text_parts.append(f"列: {', '.join(col_names)}")
        
        text = "\n".join(text_parts)
        
        schemas.append({
            "table_name": table_name,
            "text": text,
            "file_path": str(json_file)
        })
    
    return schemas


def build_milvus_hybrid_index(model, schemas):
    """使用 Milvus Lite 构建混合索引（Dense + Sparse）"""
    from pymilvus import FieldSchema, CollectionSchema, Collection, connections
    from scipy.sparse import csr_array
    
    print(f"\n[构建索引] 共 {len(schemas)} 个表")
    
    # 初始化 Milvus Lite
    client = MilvusClient(MILVUS_DB_PATH)
    
    # 删除旧集合
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
    
    # 使用 Schema 方式创建集合（支持 Sparse Vector）
    schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    
    # 添加字段
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
    schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
    schema.add_field(field_name="table_name", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2000)
    
    # 创建索引
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="FLAT",
        metric_type="IP"
    )
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP"
    )
    
    # 创建集合
    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=schema,
        index_params=index_params
    )
    
    # 批量生成嵌入
    texts = [s["text"] for s in schemas]
    print("生成 Dense + Sparse 嵌入...")
    
    output = model.encode(
        texts,
        batch_size=12,
        max_length=8192,
        return_dense=True,
        return_sparse=True
    )
    
    # 准备数据
    data = []
    for i, schema in enumerate(schemas):
        dense_vec = output['dense_vecs'][i].tolist()
        sparse_vec = output['lexical_weights'][i]
        
        data.append({
            "id": i,
            "vector": dense_vec,
            "sparse_vector": sparse_vec,
            "table_name": schema["table_name"],
            "text": schema["text"][:1990]  # 限制长度
        })
    
    # 插入数据
    client.insert(collection_name=COLLECTION_NAME, data=data)
    print(f"✅ 索引构建完成，共 {len(data)} 条记录")
    
    return client


def hybrid_search(client, model, query, top_k=10, dense_weight=0.7, sparse_weight=0.3):
    """执行真正的混合检索（Dense + Sparse）"""
    from pymilvus import AnnSearchRequest, RRFRanker, WeightedRanker
    
    # 生成查询嵌入
    output = model.encode(
        [query],
        batch_size=1,
        max_length=8192,
        return_dense=True,
        return_sparse=True
    )
    
    dense_vec = output['dense_vecs'][0].tolist()
    sparse_vec = output['lexical_weights'][0]
    
    # 创建 Dense 检索请求
    dense_search_params = {"metric_type": "IP"}
    dense_req = AnnSearchRequest(
        data=[dense_vec],
        anns_field="vector",
        param=dense_search_params,
        limit=top_k
    )
    
    # 创建 Sparse 检索请求
    sparse_search_params = {"metric_type": "IP"}
    sparse_req = AnnSearchRequest(
        data=[sparse_vec],
        anns_field="sparse_vector",
        param=sparse_search_params,
        limit=top_k
    )
    
    # 使用加权融合
    reranker = WeightedRanker(dense_weight, sparse_weight)
    
    # 执行混合检索
    results = client.hybrid_search(
        collection_name=COLLECTION_NAME,
        reqs=[dense_req, sparse_req],
        ranker=reranker,
        limit=top_k,
        output_fields=["table_name", "text"]
    )
    
    return results[0]


def run_hybrid_test():
    print("=" * 80)
    print("Milvus BGE-M3 混合检索测试")
    print("=" * 80)
    
    # 1. 初始化模型
    print("\n[初始化] 加载 BGE-M3 模型...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    print("✅ 模型加载完成")
    
    # 2. 加载 Schema
    print("\n[加载] 读取表 Schema...")
    schemas = load_table_schemas()
    print(f"✅ 加载了 {len(schemas)} 个表 Schema")
    
    # 3. 构建索引
    client = build_milvus_hybrid_index(model, schemas)
    
    # 4. 测试检索
    print("\n" + "=" * 80)
    print("开始测试")
    print("=" * 80)
    
    results_summary = []
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n--- 测试 {i}: {case['question'][:40]}... ---")
        print(f"期望表: {case['expected']}")
        
        expected_set = set(t.lower() for t in case['expected'])
        
        # 执行检索
        results = hybrid_search(client, model, case['question'], top_k=10)
        
        retrieved_tables = []
        print("\nTop 10 结果:")
        for j, hit in enumerate(results, 1):
            table = hit['entity']['table_name']
            score = hit['distance']
            is_exp = "✅" if table.lower() in expected_set else ""
            print(f"  {j}. {table} ({score:.4f}) {is_exp}")
            retrieved_tables.append(table.lower())
        
        retrieved_set = set(retrieved_tables)
        recall = len(expected_set & retrieved_set) / len(expected_set)
        print(f"\n召回率: {recall:.0%}")
        results_summary.append(recall)
    
    # 5. 汇总
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    
    avg_recall = sum(results_summary) / len(results_summary)
    full_recall = sum(1 for r in results_summary if r == 1.0)
    print(f"平均召回率: {avg_recall:.0%}")
    print(f"完全召回: {full_recall}/{len(results_summary)}")
    
    # 清理
    client.close()


if __name__ == "__main__":
    run_hybrid_test()
