#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkAlign 简单测试 - 使用单个问题测试
"""

import json
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel
from utils import parse_schemas_from_file, parse_schema_from_df
from config import QWEN_MODEL, QWEN_API_KEY, QWEN_BASE_URL


def main():
    print("\n" + "=" * 70)
    print("LinkAlign 简单测试".center(70))
    print("=" * 70 + "\n")

    # 初始化 Qwen LLM
    print("步骤 1: 初始化 Qwen 模型...")
    llm = QwenModel(
        model_name=QWEN_MODEL,
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=0.45
    )
    print("✅ Qwen 模型初始化成功\n")

    # 数据库信息
    db_id = "netcaredb_ai"
    schema_path = Path("./spider2_dev/schemas")

    # 测试问题
    test_question = "查询最近24小时内发生的所有告警事件，按照严重程度排序"

    print(f"步骤 2: 加载数据库 Schema")
    print(f"  数据库: {db_id}")
    print(f"  Schema 路径: {schema_path}/{db_id}/")

    # 从文件加载 schema
    try:
        df = parse_schemas_from_file(
            db_id=db_id,
            schema_path=schema_path,
            output_format="dataframe"
        )
        print(f"✅ 成功加载 {len(df)} 个字段的 schema\n")
    except Exception as e:
        print(f"❌ 加载 schema 失败: {e}")
        return 1

    # 转换为文本格式
    print("步骤 3: 将 Schema 转换为文本格式...")
    schema_text = parse_schema_from_df(df)

    # 只显示前 500 个字符
    print(f"Schema 样例:\n{schema_text[:500]}...\n")
    print(f"✅ Schema 文本生成完成 (总长度: {len(schema_text)} 字符)\n")

    # 构建测试 prompt
    print("步骤 4: 构建 Schema Linking Prompt...")
    prompt = f"""Given the following database schema:

{schema_text[:5000]}

Question: {test_question}

Please identify the relevant tables and columns needed to answer this question.
Output format: table_name.column_name, separated by commas.
Only output the relevant schema elements, nothing else.
"""

    print(f"✅ Prompt 构建完成 (长度: {len(prompt)} 字符)\n")

    # 调用 LLM
    print("步骤 5: 调用 Qwen 进行 Schema Linking...")
    print(f"问题: {test_question}\n")

    try:
        response = llm.complete(prompt)
        result = response.text

        print("=" * 70)
        print("Schema Linking 结果:")
        print("=" * 70)
        print(result)
        print("=" * 70 + "\n")

        # 解析结果
        print("步骤 6: 解析结果...")

        # 简单提取表名和列名
        lines = result.split('\n')
        relevant_schemas = []
        for line in lines:
            if '.' in line:
                # 移除markdown符号等
                cleaned = line.replace('`', '').replace('*', '').strip()
                if cleaned and '.' in cleaned:
                    relevant_schemas.append(cleaned)

        if relevant_schemas:
            print("✅ 识别到的相关 Schema:")
            for schema in relevant_schemas[:10]:  # 只显示前10个
                print(f"  - {schema}")
        else:
            print("⚠️  未能从响应中提取结构化的 schema")

        print("\n" + "=" * 70)
        print("✅ 测试完成！".center(70))
        print("=" * 70 + "\n")

        return 0

    except Exception as e:
        print(f"❌ 调用 Qwen 失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
