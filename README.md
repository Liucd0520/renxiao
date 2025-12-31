# FusionSQL

基于 **BGE-M3 融合检索**（表级别 + 列级别 Sparse 并集）的 Text-to-SQL 解决方案。

## 核心特点

- **融合检索策略**：表 TOP-K ∪ 列 TOP-K，召回率 95.7%
- **BGE-M3 多语言模型**：支持中英文混合查询
- **Qwen LLM 生成**：支持 Qwen3 MoE 和 Qwen2.5-32B
- **预计算 Embedding**：毫秒级检索速度

## 性能指标

| 指标 | 数值 |
|------|------|
| 检索召回率 | 95.7% (K=10) |
| SQL 生成正确率 | 63.3% |
| 检索速度 | < 100ms |

### 难度分布

| 难度 | 检索召回率 | SQL 正确率 |
|------|-----------|-----------|
| Simple | 100% | 82% |
| Medium | 96% | 68% |
| Hard | 91% | 36% |

## 快速开始

### 安装

```bash
cd FusionSQL
pip install -r requirements.txt
```

### 命令行模式

```bash
# 交互模式
python -m fusionsql.run

# 单次查询
python -m fusionsql.run -q "查询平台上有多少客户"

# 使用 32B 模型
python -m fusionsql.run -q "查询告警" --model 32b

# 显示检索到的表
python -m fusionsql.run -q "查询告警" --show-tables
```

### Python 代码调用

```python
from fusionsql import TextToSQL

pipeline = TextToSQL()
sql = pipeline.run("查询客户测试客户名下有多少设备")
print(sql)
```

### 切换模型

```python
from fusionsql import QwenLLM

# 默认使用 Qwen3 MoE
llm = QwenLLM()

# 切换到 Qwen2.5-32B
llm = QwenLLM.create_32b()
```

## 目录结构

```
FusionSQL/
├── fusionsql/              # 主代码包
│   ├── __init__.py         # 包入口
│   ├── pipeline.py         # 统一 Pipeline
│   ├── retriever.py        # 融合检索器
│   ├── sql_generator.py    # SQL 生成器
│   ├── config.py           # 配置文件
│   ├── run.py              # 命令行入口
│   ├── llm/                # LLM 封装
│   │   ├── __init__.py
│   │   └── qwen.py
│   ├── schema_extractor.py # Schema 提取工具
│   ├── schema_enhancer.py  # 枚举值增强工具
│   ├── precompute.py       # Embedding 预计算
│   ├── schemas/            # Schema 文件（347 张表）
│   └── schema_embeddings_v3.pkl  # 预计算 Embedding
├── tests/                  # 测试文件
├── docs/                   # 开发文档
├── requirements.txt
└── README.md
```

## 检索策略

**融合检索（表 TOP-K ∪ 列 TOP-K）**

1. **表级别检索**：使用 BGE-M3 Sparse 匹配表的 `embedding_text`
2. **列级别检索**：匹配列信息，累加分数聚合到表
3. **融合**：取两者的并集（K=10 时最多 20 张表）

## 模型配置

### 预设模型

| 预设 | 模型 | API 地址 |
|------|------|----------|
| `qwen3_moe`（默认） | qwen3_30b_a3b_2507 | http://172.31.24.112:8502/v1 |
| `qwen32b` | Qwen2.5-Coder-32B-Instruct | http://172.31.24.112:33080/v1 |

### 自定义模型

```python
from fusionsql import QwenLLM

llm = QwenLLM(
    model_name="your-model",
    base_url="http://your-server/v1",
    api_key="your-key",
)
```

## 首次运行

首次运行时，BGE-M3 模型会自动从 HuggingFace 下载到 `~/.cache/huggingface/`（约 2.2GB）。

## 依赖

- `FlagEmbedding>=1.0.0` - BGE-M3 模型
- `openai>=1.0.0` - LLM API 客户端
- `pymysql>=1.0.0` - 数据库连接（可选，用于 Schema 提取）

## 文档

详细的开发文档和测试报告请查看 `docs/` 目录。

---

*FusionSQL - 融合检索驱动的 Text-to-SQL 解决方案*
