#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LinkAlign 环境配置是否正确
"""

import sys
import os

def test_imports():
    """测试必要的包是否能正确导入"""
    print("=" * 60)
    print("测试 1: 检查包导入")
    print("=" * 60)

    try:
        import torch
        print(f"✅ PyTorch 版本: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch 导入失败: {e}")
        return False

    try:
        import transformers
        print(f"✅ Transformers 版本: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers 导入失败: {e}")
        return False

    try:
        import llama_index.core
        try:
            version = llama_index.core.__version__
        except:
            version = "已安装"
        print(f"✅ LlamaIndex 版本: {version}")
    except ImportError as e:
        print(f"❌ LlamaIndex 导入失败: {e}")
        return False

    try:
        from llama_index.core import VectorStoreIndex
        print("✅ LlamaIndex Core 导入成功")
    except ImportError as e:
        print(f"❌ LlamaIndex Core 导入失败: {e}")
        return False

    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        print("✅ LlamaIndex HuggingFace Embeddings 导入成功")
    except ImportError as e:
        print(f"❌ LlamaIndex HuggingFace Embeddings 导入失败: {e}")
        return False

    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers 导入成功")
    except ImportError as e:
        print(f"❌ Sentence Transformers 导入失败: {e}")
        return False

    try:
        import pandas as pd
        print(f"✅ Pandas 版本: {pd.__version__}")
    except ImportError as e:
        print(f"❌ Pandas 导入失败: {e}")
        return False

    try:
        import openai
        print(f"✅ OpenAI 版本: {openai.__version__}")
    except ImportError as e:
        print(f"❌ OpenAI 导入失败: {e}")
        return False

    print()
    return True


def test_llamaindex_modifications():
    """测试 LlamaIndex 源码是否已正确修改"""
    print("=" * 60)
    print("测试 2: 检查 LlamaIndex 源码修改")
    print("=" * 60)

    try:
        from llama_index.core.indices.vector_store import VectorIndexRetriever

        # 检查是否有 index 属性
        if hasattr(VectorIndexRetriever, 'index'):
            print("✅ VectorIndexRetriever.index 属性存在")
        else:
            print("❌ VectorIndexRetriever.index 属性不存在 - 源码修改可能未生效")
            return False

        # 检查是否有 change_node_ids 方法
        if hasattr(VectorIndexRetriever, 'change_node_ids'):
            print("✅ VectorIndexRetriever.change_node_ids 方法存在")
        else:
            print("❌ VectorIndexRetriever.change_node_ids 方法不存在 - 源码修改可能未生效")
            return False

        # 检查是否有 back_to_original_ids 方法
        if hasattr(VectorIndexRetriever, 'back_to_original_ids'):
            print("✅ VectorIndexRetriever.back_to_original_ids 方法存在")
        else:
            print("❌ VectorIndexRetriever.back_to_original_ids 方法不存在 - 源码修改可能未生效")
            return False

    except Exception as e:
        print(f"❌ 检查 LlamaIndex 修改时出错: {e}")
        return False

    print()
    return True


def test_config():
    """测试配置文件"""
    print("=" * 60)
    print("测试 3: 检查配置文件")
    print("=" * 60)

    try:
        import config
        print(f"✅ config.py 导入成功")
        print(f"   - 项目根目录: {config.PROJECT_ROOT}")
        print(f"   - 数据目录: {config.ALL_DATABASE_DATA_SOURCE}")
        print(f"   - 日志目录: {config.LOG_DIR}")
        print(f"   - 嵌入模型: {config.EMBED_MODEL_NAME}")
        print(f"   - LLM 名称: {config.LLM_NAME}")

        # 检查 API Key 是否已配置
        if config.QWEN_API_KEY == "your_qwen_api_key_here":
            print("⚠️  警告: QWEN_API_KEY 尚未配置")
        else:
            print("✅ QWEN_API_KEY 已配置")

        if config.ZHIPU_API_KEY == "your_zhipu_api_key_here":
            print("⚠️  警告: ZHIPU_API_KEY 尚未配置")
        else:
            print("✅ ZHIPU_API_KEY 已配置")

        if config.DEEPSEEK_API == "your_deepseek_api_key_here":
            print("⚠️  警告: DEEPSEEK_API 尚未配置")
        else:
            print("✅ DEEPSEEK_API 已配置")

    except Exception as e:
        print(f"❌ 配置文件检查失败: {e}")
        return False

    print()
    return True


def test_directories():
    """测试目录结构"""
    print("=" * 60)
    print("测试 4: 检查目录结构")
    print("=" * 60)

    required_dirs = [
        'data',
        'logs',
        'dataset',
        'spider2_dev',
        'spider2_dev/instance_schemas',
        'spider2_dev/schema_links',
        'spider2_dev/external_knowledge',
    ]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = os.path.join(os.path.dirname(__file__), dir_name)
        if os.path.exists(dir_path):
            print(f"✅ {dir_name} 目录存在")
        else:
            print(f"❌ {dir_name} 目录不存在")
            all_exist = False

    print()
    return all_exist


def test_project_files():
    """测试项目文件是否存在"""
    print("=" * 60)
    print("测试 5: 检查项目文件")
    print("=" * 60)

    required_files = [
        'GenerateSchemas.py',
        'config.py',
        'utils.py',
        'requirements.txt',
        'tools/SchemaLinkingTool.py',
        'pipes/RagPipeline.py',
    ]

    all_exist = True
    for file_name in required_files:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        if os.path.exists(file_path):
            print(f"✅ {file_name} 存在")
        else:
            print(f"❌ {file_name} 不存在")
            all_exist = False

    print()
    return all_exist


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "     LinkAlign 环境配置测试".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    results = []

    # 运行所有测试
    results.append(("包导入", test_imports()))
    results.append(("LlamaIndex 源码修改", test_llamaindex_modifications()))
    results.append(("配置文件", test_config()))
    results.append(("目录结构", test_directories()))
    results.append(("项目文件", test_project_files()))

    # 输出总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print()
    if all_passed:
        print("🎉 所有测试通过！环境配置正确。")
        print()
        print("下一步:")
        print("1. 在 config.py 中配置你的 API Keys")
        print("2. 准备数据文件放入 spider2_dev/ 目录")
        print("3. 运行 GenerateSchemas.py 开始使用")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")

    print("\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
