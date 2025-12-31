# spider2_dev 目录说明

**更新日期**: 2024-12-23

本目录包含 netcaredb_ai 数据库的各种 Schema 版本，用于 Text-to-SQL 检索实验。

---

## 目录结构

| 目录 | 文件数 | 说明 | 用途 |
|-----|-------|------|-----|
| **schemas** | 3356 | 原始列级别 Schema | 每个列一个 JSON 文件 |
| **schemas_column_enhanced** | 3353 | LLM 增强的列级别 Schema | 用于列级别向量检索 |
| **schemas_enhanced** | 42 | 早期增强尝试 | ⚠️ 已废弃 |
| **schemas_table_level** | 345 | 表级别 Schema | 包含列信息的表描述 |
| **schemas_table_level_english** | 346 | 英文表级别 Schema | 实验性质 |
| **schemas_table_level_enhanced** | 346 | **LLM 增强的表描述** | 包含 `llm_description` 字段 |
| **schemas_table_level_full** | 344 | 全量表级别 Schema | 完整列信息 |
| **schemas_table_level_llm** | 345 | LLM 生成的表描述 | 早期尝试 |

---

## 核心文件

| 文件 | 说明 |
|-----|-----|
| **schema_embeddings.pkl** | 预计算的 BGE-M3 Sparse Embedding |
| db_info.json | 数据库元信息 |
| tables_preprocessed.json | 预处理后的表信息 |

---

## 当前使用的方案

### ✅ 推荐方案：核心列增强

使用 `schema_embeddings.pkl` 中预计算的 embedding，包含：
- 344 张表的表级别描述
- **7 张核心表的 200 列**增强描述

召回率：**99.7%**（302 问题中 301 个成功）

### 核心表列表

```
t_bz_config_ci_ne_root    # 设备主表
t_bz_config_customer      # 客户表
event_history             # 告警历史表
t_bz_config_region        # 区域表
collector_v2              # 采集机表
ne_type                   # 设备类型表
customer_collector_v2     # 客户采集机关联表
```

---

## 历史实验记录

| 实验 | 召回率 | 结论 |
|-----|-------|-----|
| 全量列增强 (3353列) | 50.3% | ❌ 噪音太大 |
| 核心列增强 (6表) | 97.4% | ✅ 效果好 |
| 核心列增强 (7表) | **99.7%** | ✅ 最佳 |
| 全量表检索 | 2.5% | ❌ 太差 |
| 全量+LLM精选 | 2.5% | ❌ 无改善 |

---

## 相关脚本

- `retrieval/precompute_embeddings.py` - 预计算 embedding
- `scripts/enhance/enhance_column_schema_qwen32b.py` - 列级别增强
- `scripts/test_fair_comparison.py` - 对比测试

---
*文档自动生成*
