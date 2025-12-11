#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为数据库 schema 建立向量索引
"""

import os
from pipes.RagPipeline import RagPipeLines

# 配置
db_id = "netcaredb_ai"
schema_path = "./spider2_dev/schemas"

# schema 文件目录
data_source = os.path.join(schema_path, db_id)
# 向量索引存储目录
persist_dir = os.path.join(data_source, "vector_store")

print(f"数据源目录: {data_source}")
print(f"向量索引将保存到: {persist_dir}")

# 建立向量索引
print("\n开始建立向量索引...")
print("这可能需要几分钟时间，因为有 3353 个列需要向量化...")

vector_index = RagPipeLines.build_index_from_source(
    data_source=data_source,
    persist_dir=persist_dir,
    is_vector_store_exist=False,  # 首次创建，设置为 False
    index_method="VectorStoreIndex"
)

print(f"\n✅ 向量索引建立完成！")
print(f"   索引文件保存在: {persist_dir}")
