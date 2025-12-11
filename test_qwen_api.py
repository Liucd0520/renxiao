#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地 Qwen API 连接
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel
from config import QWEN_MODEL, QWEN_API_KEY, QWEN_BASE_URL


def test_qwen_connection():
    """测试 Qwen API 连接"""
    print("\n" + "=" * 60)
    print("Qwen API 连接测试".center(60))
    print("=" * 60)

    print(f"\n配置信息:")
    print(f"  模型名称: {QWEN_MODEL}")
    print(f"  API 地址: {QWEN_BASE_URL}")
    print(f"  API Key: {QWEN_API_KEY}")

    print("\n正在初始化 Qwen 模型...")

    try:
        # 创建 QwenModel 实例
        llm = QwenModel(
            model_name=QWEN_MODEL,
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL,
            temperature=0.7,
            max_token=512
        )
        print("✅ Qwen 模型初始化成功")

    except Exception as e:
        print(f"❌ Qwen 模型初始化失败: {e}")
        return False

    # 测试简单对话
    print("\n" + "-" * 60)
    print("测试 1: 简单对话")
    print("-" * 60)

    test_prompt = "你好，请用一句话介绍你自己。"
    print(f"\n问题: {test_prompt}")

    try:
        response = llm.complete(test_prompt)
        print(f"\n回答: {response.text}")
        print("\n✅ 简单对话测试通过")

    except Exception as e:
        print(f"\n❌ 简单对话测试失败: {e}")
        return False

    # 测试 Schema Linking 相关任务
    print("\n" + "-" * 60)
    print("测试 2: Schema Linking 任务")
    print("-" * 60)

    schema_prompt = """给定以下数据库表结构：
### Table event, columns = [id(Type: INT), event_type(Type: VARCHAR(50)), severity(Type: VARCHAR(20)), create_time(Type: DATETIME)]
### Table customer, columns = [id(Type: INT), name(Type: VARCHAR(100)), type(Type: VARCHAR(50))]

问题: 查询最近24小时内发生的所有告警事件，按照严重程度排序

请分析这个问题需要用到哪些表和列。只输出相关的表名.列名，用逗号分隔。"""

    print(f"\n问题: {schema_prompt}")

    try:
        response = llm.complete(schema_prompt)
        print(f"\n回答: {response.text}")
        print("\n✅ Schema Linking 测试通过")

    except Exception as e:
        print(f"\n❌ Schema Linking 测试失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！Qwen API 工作正常。".center(60))
    print("=" * 60 + "\n")

    return True


if __name__ == "__main__":
    success = test_qwen_connection()
    sys.exit(0 if success else 1)
