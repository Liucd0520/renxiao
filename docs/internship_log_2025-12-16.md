# 实习日志：2025年12月16日

**项目**: LinkAlign (Text-to-SQL Schema Linking 优化)  
**今日主题**: 表级别检索方案全面评估与优化实验

---

## 一、今日工作概述

今天是一个非常充实的工作日，围绕 LinkAlign 的 **表级别检索方案** 完成了从基准测试到深入优化的完整实验闭环。生成了 **6 份技术报告**，整理了 **14 个测试脚本**，并得出了关于检索策略选择的重要结论。

---

## 二、工作流程与报告产出

### 2.1 上午：基准测试与方案对比

#### [报告 1] BGE-M3 向量检索优化报告
- **位置**: `docs/bge_m3_optimization_report.md`
- **核心发现**：通过增强 3 个核心表的描述，召回率从 **57.1% 提升到 76.2%**
- **关键改动**：
  - `event_history`: 加入"告警"关键词
  - `t_bz_config_ci_ne_root`: 标识为"设备主表/核心表"
  - `t_bz_config_customer`: 标识为"客户主表"

#### [报告 2] 列级别 vs 表级别对比
- **位置**: `docs/column_vs_table_level_comparison.md`
- **结论**：表级别方案（76.2%）优于列级别 LinkAlign（52%）
- **发现 LinkAlign 的"劣根性"**：核心表在 LLM 过滤阶段被误删

---

### 2.2 下午：混合检索实验

#### [报告 3] Dense vs Hybrid 对比
- **位置**: `docs/bge/dense_vs_hybrid_comparison.md`
- **实验**：Dense:Sparse = 0.7:0.3 混合检索
- **结果**：召回率没有显著提升（74% vs 74%）
- **原因分析**：表描述缺乏关键词，Sparse 向量无法发挥作用

#### [报告 4-5] 端到端测试详细结果
- **位置**: `docs/bge/dense_e2e/` 和 `docs/bge/hybrid_e2e/`
- **内容**：7 个测试用例的完整执行过程、检索结果、SQL 生成和评判

---

### 2.3 傍晚：深度分析与重构

#### [报告 6] 优化方向分析
- **位置**: `docs/optimization_direction_analysis.md`
- **识别 3 个可优化环节**：
  1. 向量检索召回率（表描述增强）
  2. 检索数量 Top K 调整
  3. 列级别 Schema 优化

#### [报告 7] 表级别评估总报告
- **位置**: `docs/bge/table_level_evaluation_report.md`
- **核心问题**：表描述无法体现数据值（如 ciscoA）
- **建议**：探索列级别检索或两阶段混合方案

---

### 2.4 代码重构工作

#### Schema 提取脚本优化（重要改动）

**修改文件**: `extract_table_level_schema.py`

**具体改动**：
- 修改 `generate_embedding_text()` 函数，**移除 `max_columns` 参数限制**
- 之前：只取前 20 列 → `display_columns = sorted_columns[:max_columns]`
- 现在：包含所有列 → `for col in sorted_columns:`

**验证结果**：
| 表 | 之前（20列限制）| 现在（无限制）|
|---|----------------|--------------|
| `t_bz_config_ci_ne_root` | 20 列 | **75 列** |
| `HOST_NAME` 列 | ❌ 被截断 | ✅ 已包含 |
| `embedding_text` 长度 | ~500 字符 | **1451 字符** |

#### LLM 批量优化表描述（系统化方案）

**修改文件**: 新建 `enhance_schema_with_llm.py`

**说明**：
- **无手动修改**：LLM 自动为 344 个表生成描述，没有针对任何测试用例做特殊处理
- **对比**：

| 表 | 之前手动优化 | 现在 LLM 生成 |
|---|------------|--------------|
| `event_history` | 【告警/事件主表】存储所有设备告警... | 事件历史记录表，存储系统中所有事件的详细信息... |
| `t_bz_config_ci_ne_root` | 【设备主表/核心表】... | 根网元配置表，存储网络设备的基础信息与状态... |

> ⚠️ **注意**：LLM 生成的描述没有"告警"、"主表/核心表"等标识词，这是召回率从 76% 降到 74% 的原因。

#### 测试脚本整理
- 创建 `tests/` 目录结构
- 将 14 个测试脚本分类：
  - `tests/bge_m3/` (4)：BGE-M3 相关
  - `tests/table_level/` (2)：表级别检索
  - `tests/e2e/` (7)：端到端测试
  - `tests/query/` (1)：查询处理

---

## 三、核心发现总结

### 3.1 召回率对比

| 方案 | 召回率 | 执行时间 |
|-----|-------|---------|
| 列级别 LinkAlign | 52% | ~15 分钟 |
| 表级别（手动优化描述）| **76.2%** | ~10 秒 |
| 表级别（LLM 优化描述）| 74% | ~10 秒 |
| 表级别 + Hybrid 检索 | 74% | ~10 秒 |

### 3.2 关键问题识别

1. **数据值匹配问题**：用户问"设备 ciscoA"，但 ciscoA 只存在于数据库数据中，不在 embedding_text 里
2. **相似表混淆**：`customer` vs `t_bz_config_customer`，LLM 容易选错
3. **业务规则缺失**：LLM 不知道 `IS_ACTIVE=1` 等必要过滤条件

### 3.3 表级别方案局限性

- 无法匹配具体数据值
- 表间关联语义难以体现
- 语义被 50+ 列稀释

---

## 四、技术收获

### 4.1 关于 BGE-M3 混合检索

- **Dense 向量**：语义相似性（"告警" ≈ "事件"）
- **Sparse 向量**：关键词匹配（BM25 风格）
- **混合效果**：当描述缺乏关键词时，Sparse 权重再高也没用

### 4.2 关于 LLM 自动优化

- LLM **只能根据列名推断业务含义**
- **无法知道表间隐含关联**（如设备表与告警表通过 NE_ID 关联）
- 需要人工审核核心表描述

### 4.3 工程思考

- **避免面向结果编程**：针对测试失败案例手动优化是短视的
- **系统化优化优于逐个优化**：LLM 批量处理 + 人工校准

---

## 五、后续计划

| 优先级 | 方向 | 描述 |
|-------|-----|------|
| P0 | **列级别检索** | 探索更细粒度的检索策略 |
| P1 | 查询重写 | 将"ciscoA"→"设备主表某设备" |
| P2 | 两阶段混合 | 表级粗召回 + 列级精排序 |

---

## 六、今日产出清单

### 报告文档（7 份）
1. `docs/bge_m3_optimization_report.md` - 12KB
2. `docs/column_vs_table_level_comparison.md` - 4KB
3. `docs/optimization_direction_analysis.md` - 5KB
4. `docs/bge/dense_vs_hybrid_comparison.md` - 3KB
5. `docs/bge/table_level_evaluation_report.md` - 4KB
6. `docs/bge/dense_e2e/e2e_report.md` - 端到端测试报告
7. `docs/bge/hybrid_e2e/e2e_report.md` - 混合检索测试报告

### 代码修改
- `extract_table_level_schema.py` - 移除列数限制
- `enhance_schema_with_llm.py` - 新建（LLM 批量优化）
- `tests/bge_m3/test_bge_m3_hybrid_e2e.py` - 混合检索端到端测试

### 目录整理
- 创建 `tests/` 目录结构
- 整理 14 个测试脚本到对应分类

---

*今日工作时长：约 8 小时*  
*代码变更：3 个新脚本，2 个脚本修改*  
*生成文档：7 份技术报告*
