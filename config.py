# -*- coding: utf-8 -*-
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 本地文件存储目录 (需要根据实际情况配置)
ALL_DATABASE_DATA_SOURCE = os.path.join(PROJECT_ROOT, "data")

# 训练数据存储目录
DATASET_PATH = os.path.join(PROJECT_ROOT, "dataset")

# 索引保存目录
PERSIST_DIR = os.path.join(ALL_DATABASE_DATA_SOURCE, "vector_store")

# 日志目录
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# SummaryIndex 索引文件存储目录
ALL_DATABASE_SUMMARY_PERSIST_DIR = os.path.join(ALL_DATABASE_DATA_SOURCE, "vector_store", "SummaryIndex")

# VectorStoreIndex 索引文件存储目录
ALL_DATABASE_VECTOR_PERSIST_DIR = os.path.join(ALL_DATABASE_DATA_SOURCE, "vector_store", "VectorStoreIndex")

# 本地索引文件存储目录
VECTOR_STORE_PERSIST_DIR = os.path.join(PROJECT_ROOT, "vector_store")

# 文件存储目录索引是否存在。注意：更新文件目录后第一次使用需要设置为 False
IS_VECTOR_STORE_EXIST = False

# 嵌入模型名称 (使用 HuggingFace 的 BGE 模型)
EMBED_MODEL_NAME = "BAAI/bge-large-en-v1.5"

# 底层大模型名称
LLM_NAME = "qwen"  # 可选: "qwen", "zhipu", "deepseek"

# 过程可视化
VERBOSE = True

# ==== 本地 Qwen 配置 ====
# 本地部署的 Qwen2.5-Coder-32B-Instruct
QWEN_API_KEY = "yfzx202510"
QWEN_MODEL = "Qwen2.5-Coder-32B-Instruct"  # 32B 模型
QWEN_BASE_URL = "http://172.31.24.112:33080/v1"  # 32B 模型 API 地址

# 其他 API Keys（如果不使用可以保持默认）
ZHIPU_API_KEY = "your_zhipu_api_key_here"
ZHIPU_MODEL = "glm-4-flash"

DEEPSEEK_API = "your_deepseek_api_key_here"
DEEPSEEK_MODEL = "deepseek-chat"

# 两个模型的公共参数
TEMPERATURE = 0.45

MAX_OUTPUT_TOKENS = 4096

CONTEXT_WINDOW = 120000

