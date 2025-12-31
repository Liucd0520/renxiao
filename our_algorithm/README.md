# Text-to-SQL 全链路算法

## 核心流程

```
数据库
  │
  ▼ schema_extractor.py
┌─────────────────────────────┐
│ 1. 提取表结构               │
│ 2. LLM 生成中文语义描述     │
└─────────────────────────────┘
  │
  ▼ schema_enhancer.py
┌─────────────────────────────┐
│ 3. 自动检测枚举类型列       │
│ 4. 添加 TOP10 常见值        │
└─────────────────────────────┘
  │
  ▼ precompute.py
┌─────────────────────────────┐
│ 5. BGE-M3 预计算 Embedding  │
└─────────────────────────────┘
  │
  ▼ pipeline.py
┌─────────────────────────────┐
│ 6. 检索相关表（并集策略）   │
│ 7. LLM 生成 SQL             │
└─────────────────────────────┘
  │
  ▼
SQL 输出
```

---

## 快速开始

### 命令行模式

```bash
cd our_algorithm

# 交互模式
python run.py

# 单次查询
python run.py -q "查询平台上有多少客户"

# 使用 32B 模型
python run.py -q "查询告警" --model 32b

# 显示检索到的表
python run.py -q "查询告警" --show-tables
```

### Python 代码调用

```python
from our_algorithm import TextToSQL

pipeline = TextToSQL()
sql = pipeline.run("查询客户测试客户名下有多少设备")
print(sql)
```

### 切换模型

```python
from our_algorithm import QwenLLM

# 默认使用 Qwen3 MoE
llm = QwenLLM()

# 切换到 Qwen2.5-32B
llm = QwenLLM.create_32b()
```

---

## 完整流程

### 第一步：提取 Schema（含 LLM 描述增强）

```bash
python our_algorithm/schema_extractor.py \
    --host 172.31.26.206 \
    --database netcaredb_ai \
    --output ./our_algorithm/schemas
```

### 第二步：枚举值增强（添加 TOP10）

```bash
python our_algorithm/schema_enhancer.py \
    --host 172.31.26.206 \
    --database netcaredb_ai \
    --schema-dir ./our_algorithm/schemas
```

### 第三步：预计算 Embedding

```bash
python our_algorithm/precompute.py
```

---

## 目录结构

```
our_algorithm/
├── __init__.py           # 包入口
├── pipeline.py           # 统一 Pipeline（问题→SQL）
├── retriever.py          # 检索器（融合检索：表∪列）
├── sql_generator.py      # SQL 生成器
├── config.py             # 配置文件
├── llm/                  # LLM 封装
│   ├── __init__.py
│   └── qwen.py           # Qwen3 MoE(默认) / Qwen2.5-32B
├── schema_extractor.py   # Schema 提取 + LLM 描述增强
├── schema_enhancer.py    # 枚举值 TOP10 增强
├── precompute.py         # Embedding 预计算
├── schemas/              # Schema 文件（JSON）
└── schema_embeddings_v3.pkl  # 预计算 Embedding
```

---

## 检索策略

**融合检索（表 TOP-K ∪ 列 TOP-K）**

| 组件 | 说明 |
|:-----|:-----|
| 表级别 | BGE-M3 Sparse 匹配，取 TOP-K |
| 列级别 | BGE-M3 Sparse 匹配，累加分聚合到表，取 TOP-K |
| 融合 | 并集（K=10 时最多 20 张表） |

---

## 性能指标

### 检索成功率（300题）

| 难度 | 成功率 |
|:-----|:------:|
| Simple | 100% |
| Medium | 95% |
| Hard | 91% |
| **总计** | **95.3%** |

### SQL 生成正确率

| 模型 | Simple | Medium | Hard | 总计 |
|:-----|:------:|:------:|:----:|:----:|
| Qwen2.5-32B | 100% | 58% | 32% | 63.3% |
| Qwen3 MoE | 98% | 70% | 22% | 63.3% |

---

## 模型配置

### 预设模型

| 预设 | 模型 | API 地址 |
|:-----|:-----|:---------|
| `qwen3_moe`（默认） | qwen3_30b_a3b_2507 | http://172.31.24.112:8502/v1 |
| `qwen32b` | Qwen2.5-Coder-32B-Instruct | http://172.31.24.112:33080/v1 |

### 自定义模型

```python
from our_algorithm import QwenLLM

llm = QwenLLM(
    model_name="your-model",
    base_url="http://your-server/v1",
    api_key="your-key",
)
```

---

## 依赖

```
FlagEmbedding>=1.0.0    # BGE-M3 模型
openai>=1.0.0           # LLM API
pymysql>=1.0.0          # 数据库连接
```

---

*更新时间: 2024-12-31*
