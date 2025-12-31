"""
FusionSQL 配置文件

可以通过环境变量或直接修改此文件来配置
"""

import os

# fusionsql 包目录
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# LLM 配置
# ============================================================

# Qwen 模型配置
QWEN_MODEL_NAME = os.environ.get("QWEN_MODEL_NAME", "Qwen2.5-Coder-32B-Instruct")
QWEN_BASE_URL = os.environ.get("QWEN_BASE_URL", "http://172.31.24.112:33080/v1")
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "yfzx202510")

# Qwen3 MoE 配置（默认）
QWEN3_MOE_MODEL_NAME = os.environ.get("QWEN3_MOE_MODEL_NAME", "qwen3_30b_a3b_2507")
QWEN3_MOE_BASE_URL = os.environ.get("QWEN3_MOE_BASE_URL", "http://172.31.24.112:8502/v1")
QWEN3_MOE_API_KEY = os.environ.get("QWEN3_MOE_API_KEY", "EMPTY")

# LLM 通用配置
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "4096"))

# ============================================================
# 检索配置
# ============================================================

# BGE-M3 模型：自动从 HuggingFace 下载
BGE_M3_MODEL_NAME = os.environ.get("BGE_M3_MODEL_NAME", "BAAI/bge-m3")

# 预计算 Embedding 文件（默认使用包内文件）
EMBEDDINGS_FILE = os.environ.get(
    "EMBEDDINGS_FILE",
    os.path.join(PACKAGE_DIR, "schema_embeddings_v3.pkl")
)

# Schema 目录（默认使用包内目录）
SCHEMA_DIR = os.environ.get(
    "SCHEMA_DIR",
    os.path.join(PACKAGE_DIR, "schemas")
)

# 检索 TOP-K
RETRIEVAL_TOP_K = int(os.environ.get("RETRIEVAL_TOP_K", "10"))

# ============================================================
# 数据库配置（用于 Schema 提取）
# ============================================================

DB_HOST = os.environ.get("DB_HOST", "172.31.26.206")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "ai_test")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Netcare@13579")
DB_NAME = os.environ.get("DB_NAME", "netcaredb_ai")
