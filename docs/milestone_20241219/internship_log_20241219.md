# 实习日志 - 2025年12月19日

## 今日工作概述

今天的工作重点是**构建测试数据集并进行系统性评估**，为 Text-to-SQL 系统建立了完整的测试基准。

---

## 主要工作内容

### 1. 使用 DeepSeek 生成 100 个测试问题

**背景**: 之前的测试样本量太少，无法进行系统性评估。

**实现**:
- 编写 `scripts/generate_test_questions.py` 脚本
- 使用 DeepSeek API (`deepseek-chat` 模型)
- 读取全部 344 张表的 Schema，让 LLM 生成覆盖多种场景的问题

**生成结果**:
| 难度 | 数量 | 说明 |
|-----|------|------|
| easy | 29 | 单表简单统计/查询 |
| medium | 52 | 2-3表关联、条件过滤 |
| hard | 19 | 多表 JOIN、复杂聚合 |

**核心表使用频率**:
1. `t_bz_config_ci_ne_root` - 33 次
2. `t_bz_config_customer` - 29 次
3. `event_history` - 13 次

---

### 2. 表召回率测试

**方法**: 使用表+列融合检索（BGE-M3 Sparse 模式）

**总体结果**:
| 指标 | 结果 |
|-----|------|
| 完全召回 | 65% |
| 部分召回 | 28% |
| 未召回 | 7% |
| **平均召回率** | **78.8%** |

**按难度分类**:
| 难度 | 完全召回率 |
|-----|-----------|
| easy | **93.1%** |
| medium | **69.2%** |
| hard | **52.6%** |

**关键发现**:
- Easy 问题表现优秀，单表查询基本没问题
- Hard 问题挑战大，多表 JOIN 场景召回不足
- `t_bz_config_ci_ne_root` 和 `t_bz_config_customer` 在多表查询时容易缺失

---

### 3. SQL 生成测试（Qwen2.5-Coder-32B-Instruct）

**测试配置**:
- 模型: Qwen2.5-Coder-32B-Instruct
- API: http://172.31.24.112:33080/v1
- 测试问题: 100 个

**对比两种 Prompt 模式**:
| 模式 | 正确数 | 正确率 |
|-----|-------|-------|
| 不开 Thinking | 60/100 | **60%** |
| 开 Thinking | 66/100 | **66%** |

**结论**: 开 Thinking（让模型先思考再回答）提升了 **6 个百分点**

**两种模式结果不同的典型案例**:
- 端口流量使用率 TOP10：不开 ❌ → 开 ✅
- 未配置联系人的客户：不开 ❌ → 开 ✅
- 采集机健康状态异常：不开 ❌ → 开 ✅

---

### 4. 模型 Thinking 能力调研

**问题**: Qwen2.5-Coder-32B-Instruct 是否支持原生 thinking 模式？

**测试结果**:
- API 层面支持 `enable_thinking` 参数（不报错）
- 但模型实际没有输出 `<think>...</think>` 标签
- **结论**: Qwen2.5-Coder-32B-Instruct 不是原生 thinking 模型，但可以通过 Prompt 引导思考

---

## 产出文件

| 文件 | 说明 |
|-----|------|
| `test_questions_100.json` | 100 个测试问题（JSON） |
| `test_questions_100.csv` | 100 个测试问题（CSV） |
| `recall_test_100_report.md` | 表召回率测试报告 |
| `sql_generation_100_test_report.md` | SQL 生成测试报告 |

---

## 关键结论

1. **测试数据集已建立**: 100 个问题覆盖 easy/medium/hard 三种难度
2. **召回率瓶颈明确**: Hard 问题只有 52.6% 完全召回，需要优化多表检索策略
3. **Thinking 模式有效**: 开 Thinking 比不开提升 6% 正确率
4. **主要错误类型**: 缺少 ORDER BY、SELECT 字段不匹配、缺少 JOIN

---

## 下一步计划

1. **优化核心表召回**: 为 `t_bz_config_ci_ne_root` 和 `t_bz_config_customer` 增加白名单机制
2. **改进 Hard 问题处理**: 研究如何提高多表 JOIN 场景的召回率
3. **优化 SQL 生成 Prompt**: 针对主要错误类型（ORDER BY 缺失）改进提示词

---

*日志日期: 2025-12-19*
