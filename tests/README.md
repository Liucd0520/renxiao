# Tests 目录结构

**整理日期**: 2025-12-16

---

## 目录结构

```
tests/
├── bge_m3/                 # BGE-M3 嵌入模型相关测试
│   ├── test_bge_m3_all_combos.py      # 多语言组合测试
│   ├── test_bge_m3_hybrid_e2e.py      # Dense+Sparse 混合检索端到端
│   ├── test_bge_m3_recall.py          # 召回率测试
│   └── test_max_score_aggregation.py  # 表级别最大分数聚合策略
│
├── table_level/            # 表级别检索相关测试
│   ├── test_table_level_e2e.py        # 表级别端到端测试
│   └── test_table_level_retrieval.py  # 表级别检索测试
│
├── query/                  # 查询处理相关测试
│   └── test_query_translation.py      # 查询翻译测试
│
├── e2e/                    # 端到端/综合测试
│   ├── batch_test.py                  # 批量测试（列级别 LinkAlign）
│   ├── run_test.py                    # 运行测试入口
│   ├── test_complete_flow.py          # 完整流程测试
│   ├── test_comprehensive.py          # 综合测试
│   ├── test_english_full.py           # 英文完整测试
│   ├── test_llm_table_selection_real.py # LLM 表选择真实测试
│   └── test_simple.py                 # 简单测试
│
└── README.md               # 本文件
```

---

## 测试分类说明

| 分类 | 说明 | 数量 |
|------|------|------|
| **bge_m3** | BGE-M3 模型测试：召回率、多语言、混合检索 | 4 |
| **table_level** | 表级别检索策略测试 | 2 |
| **query** | 查询翻译/处理测试 | 1 |
| **e2e** | 端到端流程测试 | 7 |

---

## 运行测试

```bash
# 运行单个测试
.venv/bin/python3 tests/bge_m3/test_bge_m3_hybrid_e2e.py

# 运行批量测试
.venv/bin/python3 tests/e2e/batch_test.py
```

---

## 测试报告位置

测试结果保存在 `docs/` 目录下：

| 测试类型 | 报告位置 |
|---------|---------|
| BGE-M3 Dense/Hybrid | `docs/bge/` |
| 列级别批量测试 | `docs/column_level_batch_test/` |
| 优化分析 | `docs/optimization_direction_analysis.md` |
