# FusionSQL

> **Text-to-SQL 系统：融合多路检索与 Entity Linking 的智能 SQL 生成框架**

---

## 📌 项目概述

FusionSQL 是一个高精度的 Text-to-SQL 系统，核心创新在于**多路检索融合策略**和**LSH Entity Linking**，专为复杂业务数据库场景设计。

### 核心特性

- 🎯 **表级别 + 列级别双路检索**: 基于 BGE-M3 的混合检索，召回率达 95%+
- 🔗 **LSH Entity Linking**: 基于 CHESS 论文，用 LLM 提取关键词 + LSH 匹配数据库值
- ⚡ **并行执行优化**: BGE 检索与 Entity Linking 并行，减少延迟
- 🤖 **支持多模型**: Qwen3-MoE、Qwen2.5-Coder-32B 等

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FusionSQL Framework                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   输入：自然语言问题 Q                                                        │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │              Step 1 & 2: 并行执行                                    │   │
│   │  ┌───────────────────────────┐    ┌───────────────────────────┐     │   │
│   │  │    BGE-M3 检索             │    │   LLM + LSH Entity Linking│     │   │
│   │  │  ┌─────────┬─────────┐    │    │                           │     │   │
│   │  │  │表级别检索│列级别检索│    │    │  1. LLM 提取关键词         │     │   │
│   │  │  │ TOP-10  │ TOP-200 │    │    │  2. LSH 搜索匹配值        │     │   │
│   │  │  └────┬────┴────┬────┘    │    │  3. 生成值匹配提示        │     │   │
│   │  │       │  聚合到表 │         │    │                           │     │   │
│   │  │       └────┬────┘         │    └───────────────────────────┘     │   │
│   │  │            ▼              │                  │                   │   │
│   │  │       UNION 并集融合       │                  │                   │   │
│   │  │            ▼              │                  ▼                   │   │
│   │  │       ≤ 20 张表           │           值匹配提示                  │   │
│   │  └───────────────────────────┘                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     Step 3: SQL 生成 (LLM)                          │   │
│   │                                                                     │   │
│   │   Prompt = Schema信息 + 值匹配提示 + 用户问题                         │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│                            输出：SQL 语句                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 核心模块

### 1. BGE-M3 双路检索 (`fusionsql/retriever.py`)

```
表级别检索 (Table-Level)          列级别检索 (Column-Level)
BGE-M3 Sparse                    BGE-M3 Sparse
        │                                │
        ▼                                ▼
   Table TOP-10                   Column TOP-200
        │                                │
        │                         聚合到表 (Aggregate)
        │                                │
        │                                ▼
        │                         Table TOP-10
        │                                │
        └────────────┬───────────────────┘
                     ▼
               UNION 并集融合  ← 核心创新：取并集而非分数累加
                     │
                     ▼
             最终结果：≤ 20 张表
```

**核心创新**：使用 UNION 取并集而非分数累加，避免漏召关键表。

### 2. LSH Entity Linking (`fusionsql/pipeline.py`, `fusionsql/value_search/`)

基于 [CHESS 论文](https://arxiv.org/abs/2405.16755) 的实现：

```
用户问题: "设备ciscoA上个月告警统计"
        │
        ▼
┌─────────────────────────────────────┐
│ Step 1: LLM 关键词提取               │
│ → 提取关键词: ['ciscoA']             │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 2: LSH 值匹配                   │
│ → 'ciscoA' 相似匹配: 'cisco'         │
│   (MinHash 相似度 0.82)              │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 3: 生成值匹配提示               │
│ → "问题中的值可能对应: 'cisco'"      │
│   (不含表名，避免误导)               │
└─────────────────────────────────────┘
```

**设计要点**：
- 只对英文/数字关键词使用 LSH（中文 n-gram 匹配不可靠）
- 提示中不包含表名，避免误导 LLM 使用错误的表

### 3. SQL 生成器 (`fusionsql/sql_generator.py`)

- 同步版 `SQLGenerator` 和异步版 `AsyncSQLGenerator`
- 支持 Qwen3-MoE、Qwen2.5-Coder-32B 等模型
- 自动加载 Schema 信息

---

## 🚀 快速开始

### 安装依赖

```bash
cd FusionSQL
pip install -r requirements.txt
```

### 基本使用

```python
from fusionsql.pipeline import TextToSQL

# 初始化 Pipeline（启用 LSH Entity Linking）
pipeline = TextToSQL(enable_lsh=True)

# 执行 Text-to-SQL
question = "设备ciscoA上个月发生了几次告警"
sql = pipeline.run(question)
print(sql)
```

### 获取详细信息

```python
result = pipeline.run_with_details(question)
print(f"检索到的表: {result['retrieved_tables']}")
print(f"LSH 匹配值: {result['matched_values']}")
print(f"生成的 SQL: {result['sql']}")
```

---

## 📁 目录结构

```
FusionSQL/
├── fusionsql/                    # 核心模块
│   ├── pipeline.py               # Text-to-SQL Pipeline
│   ├── retriever.py              # BGE-M3 双路检索
│   ├── sql_generator.py          # SQL 生成器
│   ├── precompute.py             # Schema Embedding 预计算
│   ├── value_search/             # LSH 值搜索
│   │   ├── search.py             # LSH 搜索器
│   │   └── preprocess.py         # LSH 索引构建
│   ├── lsh_index/                # 预构建的 LSH 索引
│   ├── schema/                   # 数据库 Schema 定义
│   └── llm/                      # LLM 封装
│       └── qwen.py               # Qwen 模型适配
├── sql_researcher/               # SQL Researcher 集成
│   ├── sql_deep_researcher.py    # LangGraph 工作流
│   └── tools/                    # 工具封装
│       ├── fusionsql_tool.py     # FusionSQL 工具
│       └── sql_executor_tool.py  # SQL 执行工具
├── tests/                        # 测试脚本
├── docs/                         # 文档和报告
└── requirements.txt
```

---

## 📊 性能测试

### 7 题标准测试集

| 指标 | 结果 |
|------|------|
| **通过率** | 6/7 (85.7%) |
| **表召回率** | 95.2% |
| **模型** | Qwen3-30B-A3B (MoE) |

### LSH Entity Linking 效果

| 问题 | LLM 提取关键词 | LSH 匹配值 |
|------|---------------|-----------|
| 设备ciscoA上个月告警 | `ciscoA` | `'cisco'` ✅ |
| device state down超过3个月 | `down` | `'down'` ✅ |
| 现在平台上有多少家客户 | (无) | (无实体) |

---

## 📚 相关文档

- [LSH Entity Linking 集成报告](docs/20260116/lsh_entity_linking_report.md)
- [BGE-M3 混合检索测试报告](docs/bge/hybrid_e2e/e2e_report.md)
- [参考论文: CHESS](https://arxiv.org/abs/2405.16755)

---

## 🔗 与 SQL Researcher 集成

FusionSQL 已集成到 SQL Researcher（基于 LangGraph 的深度研究代理）：

```python
# sql_researcher/tools/fusionsql_tool.py
_sync_pipeline = TextToSQL(enable_lsh=True)  # LSH 已启用
```

通过 Web UI 或 API 调用时，会自动使用 FusionSQL 进行 SQL 生成。

---

## 📝 License

MIT License
