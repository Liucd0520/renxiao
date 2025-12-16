# 文档目录

**项目**: LinkAlign (Text-to-SQL Schema Linking)  
**更新日期**: 2025-12-16

---

## 📊 测试报告

### BGE-M3 向量检索

| 报告 | 描述 |
|-----|------|
| [bge_m3_optimization_report.md](./bge_m3_optimization_report.md) | BGE-M3 向量检索优化报告，召回率 57%→76% |
| [bge/dense_vs_hybrid_comparison.md](./bge/dense_vs_hybrid_comparison.md) | Dense vs Hybrid 检索对比 |
| [bge/table_level_evaluation_report.md](./bge/table_level_evaluation_report.md) | 表级别方案最终评估报告 |
| [bge/dense_e2e/](./bge/dense_e2e/) | Dense 检索端到端详细结果 |
| [bge/hybrid_e2e/](./bge/hybrid_e2e/) | Hybrid 检索端到端详细结果 |

### 方案对比与分析

| 报告 | 描述 |
|-----|------|
| [column_vs_table_level_comparison.md](./column_vs_table_level_comparison.md) | 列级别 vs 表级别检索对比 |
| [optimization_direction_analysis.md](./optimization_direction_analysis.md) | 优化方向分析（三个可优化环节）|
| [pure_llm_table_selection_report.md](./pure_llm_table_selection_report.md) | 纯 LLM 表选择方案测试 |

### 其他报告

| 报告 | 描述 |
|-----|------|
| [database_vs_spider_comparison.md](./database_vs_spider_comparison.md) | 数据库与 Spider 数据集对比 |
| [language_alignment_test_report.md](./language_alignment_test_report.md) | 语言对齐测试报告 |
| [linkalign_analysis_report.md](./linkalign_analysis_report.md) | LinkAlign 方案分析 |
| [validation_report.md](./validation_report.md) | 验证报告 |

---

## 📝 实习日志

| 日志 | 描述 |
|-----|------|
| [internship_log_2025-12-16.md](./internship_log_2025-12-16.md) | 2025-12-16 工作日志 |

---

## 📁 子目录

| 目录 | 描述 |
|-----|------|
| [bge/](./bge/) | BGE-M3 相关测试结果 |
| [column_level_batch_test/](./column_level_batch_test/) | 列级别批量测试结果 |

---

## 🔑 核心发现

1. **表级别召回率**: 74% (LLM 优化描述) / 76% (手动优化描述)
2. **表级别 vs 列级别**: 表级别更优 (76% vs 52%)，且速度快 100 倍
3. **Hybrid 检索效果有限**: 74% ≈ Dense-only，Sparse 贡献不大
4. **主要瓶颈**: 表描述无法体现数据值和表间关联

---

*文档索引自动生成于 2025-12-16*
