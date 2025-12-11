#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版本的 GenerateSchemas
"""

import json
import os
from pathlib import Path
import pandas as pd
from GenerateSchemas import *

# 设置全局变量
save_path = "./spider2_dev/instance_schemas"
schema_path = "./spider2_dev/schemas"
external_info_path = "./spider2_dev/external_knowledge"

# 加载数据库信息
with open('./spider2_dev/db_info.json', 'r', encoding='utf-8') as file:
    db_info = json.load(file)

print("=" * 70)
print("LinkAlign 调试测试".center(70))
print("=" * 70 + "\n")

print(f"配置信息:")
print(f"  save_path: {save_path}")
print(f"  schema_path: {schema_path}")
print(f"  db_info: {db_info}")
print()

# 加载测试数据
val_df = pd.read_json('./spider2_dev/spider2_dev_preprocessed.json')
print(f"测试数据集: {len(val_df)} 条")
print(val_df)
print()

# 测试第一个问题
row = val_df.iloc[0]
instance_id = str(row['instance_id'])
db_id = row['db_id']
question = row['question']

print(f"处理问题:")
print(f"  instance_id: {instance_id}")
print(f"  db_id: {db_id}")
print(f"  question: {question}")
print()

# 检查数据库规模
db_size = [item['count'] for item in db_info if item['db_id'] == db_id][0]
print(f"数据库规模: {db_size} 列")
print()

# 检查文件是否已存在
file_name = instance_id + "_agent"
file_path_check = os.path.join(save_path, f"{file_name}.xlsx")
print(f"检查文件是否存在: {file_path_check}")
if os.path.isfile(file_path_check):
    print(f"  文件已存在，跳过处理")
else:
    print(f"  文件不存在，开始处理...")
    print()

    # 调用 get_schema
    print("调用 get_schema...")
    try:
        result = get_schema(
            db_id=db_id,
            question=question,
            instance_id=instance_id,
            save_path_param=save_path,
            schema_path_param=schema_path,
            db_info_param=db_info,
            external_info_path_param=external_info_path,
            reserve_size=90,
            min_retrival_size=250
        )
        print(f"  结果: {result}")

        # 检查文件是否生成
        if os.path.isfile(file_path_check):
            print(f"\n✅ 文件生成成功: {file_path_check}")
            file_size = os.path.getsize(file_path_check)
            print(f"   文件大小: {file_size} 字节")
        else:
            print(f"\n❌ 文件未生成: {file_path_check}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("测试完成".center(70))
print("=" * 70)
