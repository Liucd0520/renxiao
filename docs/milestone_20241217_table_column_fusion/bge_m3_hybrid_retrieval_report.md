# BGE-M3 多粒度检索研究报告

**日期**: 2025-12-17  
**作者**: LinkAlign 项目组  
**目标**: 达到 90%+ 表级别召回率

---

## 一、研究背景

### 问题描述

在 Text-to-SQL 任务中，Schema Linking 是关键环节。需要从大规模数据库（344 张表、3353 个列）中精准检索出与自然语言问题相关的表。

### 原有方案局限

| 方案 | 召回率 | 问题 |
|-----|-------|-----|
| LinkAlign 原版（列级别 + LLM 过滤）| ~52% | LLM 投票机制导致核心表丢失 |
| 纯 Dense 向量检索 | 45% | 语义匹配不精确 |

---

## 二、最终方案：多粒度 Sparse 融合检索

### 核心结论

> **表级别 Sparse + 列级别 Sparse + 并集融合 = 95% 召回率 ✅**

| 方案 | 召回率 | 完全召回 | 目标达成 |
|-----|-------|---------|---------|
| 表级别 Sparse | 74% | 4/7 | ❌ |
| 列级别 Sparse | 83% | 4/7 | ❌ |
| **表+列 Sparse 融合** | **95%** | **6/7** | ✅ |

---

## 三、方案对比实验

### 3.1 表级别模式对比

| 模式 | 表级别召回率 | 完全召回 |
|-----|-------------|---------|
| Dense | 45% | 2/7 |
| **Sparse** | **74%** | 4/7 |
| ColBERT | 74% | 4/7 |

**结论**：**Sparse 在中文 Schema 检索中显著优于 Dense（74% vs 45%）**

### 3.2 表 Dense + 列 Sparse vs 纯 Sparse 对比

我们对比了两种融合策略：

| 配置 | 表级别模式 | 列级别模式 | 表召回 | 列召回 | **融合召回** |
|-----|-----------|-----------|-------|-------|-------------|
| 方案 A | Dense | Sparse | 45% | 83% | **95%** |
| **方案 B** | **Sparse** | **Sparse** | **74%** | **83%** | **95%** |

**逐测试对比**：

| # | 测试问题 | 方案A 表Dense | 方案B 表Sparse | 融合 |
|---|---------|--------------|---------------|------|
| 1 | 设备ciscoA告警 | 50% | 50% | 100% |
| 2 | 设备down超3个月 | 33% | 33% | **67%** ❌ |
| 3 | 平台客户数 | **0%** | **100%** | 100% |
| 4 | 平台设备数 | **0%** | **100%** | 100% |
| 5 | 上月新设备 | 100% | 100% | 100% |
| 6 | 上月下线设备 | 100% | 100% | 100% |
| 7 | 客户设备告警 | 33% | 33% | 100% |

**结论**：
- 两种方案融合后召回率相同（95%）
- 但**方案 B（纯 Sparse）表级别召回更高**（74% vs 45%）
- 测试 3/4 中，Dense 表级别召回 0%，Sparse 召回 100%
- **推荐使用方案 B：表 Sparse + 列 Sparse**

---

## 四、唯一失败 Case 深度分析

### 4.1 问题描述

**测试 2**: "列出平台上设备device state down状态超过3个月的设备清单及客户名称"

| 期望表 | 表 Sparse | 列 Sparse | 融合 |
|-------|----------|-----------|------|
| t_bz_config_ci_ne_root | ✅ (#1-2) | ✅ | ✅ |
| t_bz_config_customer | ❌ (#103) | ✅ (#2) | ✅ |
| **event_history** | **❌ (#32)** | **❌ (#247)** | **❌** |

### 4.2 为什么所有方案都检索不到 event_history？

**问题关键词分析**：
- 问题："设备device state down状态超过3个月"
- 关键词：设备、状态、down、3个月

**event_history 表描述**：
- 包含关键词：事件、告警、历史
- **不包含**："状态"、"down"

**排名分析**：

| 模式 | event_history 排名 | 需要 Top K |
|-----|-------------------|-----------|
| Dense | #32 | 32+ |
| Sparse | #247 | 247+ |
| ColBERT | #29 | 29+ |

**根本原因**：
> 问题描述的语义方向（"设备状态"）与事件表（"告警历史"）不匹配。
> 即使增加 Top K 到 30+，也无法可靠解决。

### 4.3 为什么其他 Case 能通过融合解决，但 Case 2 不行？

| Case | 表级别找到 | 列级别找到 | 融合后 |
|-----|----------|----------|-------|
| 1 | event_history | t_bz_config_ci_ne_root | ✅ 互补 |
| 7 | event_history | ci_ne_root + customer | ✅ 互补 |
| **2** | ci_ne_root | customer | **❌ 缺 event_history** |

**差异分析**：
- Case 1/7 的问题包含"告警"关键词 → 能检索到 event_history
- Case 2 的问题只有"状态/down" → 检索不到 event_history

---

## 五、下一步可行方案

### 5.1 外键推理（推荐）

**原理**：检索到设备表 → 自动扩展外键关联的事件表

```python
FK_RELATIONS = {
    "t_bz_config_ci_ne_root": ["event_history", "t_bz_config_customer"],
    "event_history": ["t_bz_config_ci_ne_root"],
    ...
}

def expand_with_fk(retrieved_tables):
    expanded = set(retrieved_tables)
    for table in retrieved_tables:
        if table in FK_RELATIONS:
            expanded.update(FK_RELATIONS[table])
    return expanded
```

**预期效果**：Case 2 检索到 ci_ne_root → 自动关联 event_history → 100%

### 5.2 查询增强

**原理**：LLM 分析问题，补充可能缺失的关键词

```
原问题: "设备device state down状态超过3个月"
增强后: "设备状态、告警事件、event_history、down超过3个月"
```

### 5.3 增大 Top K（效果有限）

| Top K | 能覆盖 event_history? |
|------|---------------------|
| 10 | ❌ |
| 20 | ❌ |
| 30 | 可能（Dense #32） |
| 50 | 可能 |

**问题**：Top K 过大会引入噪声，降低精度

### 5.4 优先级排序

| 方案 | 可行性 | 预期效果 | 实现难度 |
|-----|-------|---------|---------|
| **外键推理** | ⭐⭐⭐ | ⭐⭐⭐ | 中 |
| 查询增强 | ⭐⭐ | ⭐⭐ | 高（需 LLM） |
| 增大 Top K | ⭐ | ⭐ | 低 |

---

## 六、系统架构

```
用户自然语言问题
         ↓
┌────────────────────────────────────────────────┐
│          BGE-M3 多功能检索模型                   │
│  (支持 Dense + Sparse + ColBERT 三种模式)        │
└────────────────────────────────────────────────┘
         ↓
┌──────────────────┬──────────────────────────────┐
│   表级别检索      │      列级别检索               │
│                  │                              │
│  模式: Sparse     │  模式: Sparse                │
│  Top K: 10       │  Top K: 200                  │
│  输入: 表描述     │  输入: 列名+描述+样本数据      │
│                  │  聚合: 累加分 → Top 10        │
└────────┬─────────┴───────────────┬──────────────┘
         │                        │
         └────────┬───────────────┘
                  ↓
         ┌───────────────┐
         │   并集融合     │
         └───────────────┘
                  ↓
         ┌───────────────┐
         │  外键推理扩展   │ ← 下一步实现
         └───────────────┘
                  ↓
         最终检索结果
```

---

## 七、配置参数

| 参数 | 值 | 说明 |
|-----|---|------|
| TABLE_TOP_K | 10 | 表级别检索数量 |
| COLUMN_TOP_K | 200 | 列级别检索数量 |
| 表级别模式 | **Sparse** | `[0.0, 1.0, 0.0]` |
| 列级别模式 | **Sparse** | `[0.0, 1.0, 0.0]` |
| 列聚合策略 | 累加分 | 同表多列分数相加 |
| 融合策略 | 并集 | `table_set | column_set` |

---

## 八、测试脚本清单

| 脚本 | 用途 |
|-----|------|
| `tests/hybrid/test_all_modes_comparison.py` | Dense/Sparse/ColBERT 对比 |
| `tests/hybrid/test_table_column_fusion.py` | 纯 Sparse 表+列融合（最终方案）|
| `tests/hybrid/test_mixed_mode_fusion.py` | 表 Dense + 列 Sparse 融合 |
| `tests/hybrid/test_ranking_analysis.py` | 失败 Case 排名分析 |

---

## 九、总结

### 关键发现

1. **Sparse 优于 Dense**：表级别 74% vs 45%
2. **多粒度融合有效**：表+列并集从 74%/83% 提升到 95%
3. **唯一失败点**：Case 2 的 event_history 需要外键推理解决

### 最终方案

> **表 Sparse + 列 Sparse + 并集融合 = 95% 召回率**

### 下一步

1. 实现外键推理 → 预期 100% 召回
2. Milvus 部署 → 加速检索
3. 端到端验证 → SQL 生成准确率

---

## 附录：详细检索过程示例

### A.1 测试 1：设备ciscoA告警统计（成功案例）

**问题**: "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计"

**期望表**: `event_history`, `t_bz_config_ci_ne_root`

#### 表级别 Sparse Top 10

| 排名 | 表名 | 分数 | 命中 |
|-----|------|------|-----|
| 1 | t_dc_release_type | 0.1940 |  |
| 2 | t_dc_incident_accident_type | 0.1917 |  |
| **3** | **event_history** | **0.1870** | ✅ |
| 4 | t_bz_config_ci_rfc | 0.1681 |  |
| 5 | t_gn_weaknesses_attack | 0.1617 |  |

**表级别召回**: 1/2（缺 t_bz_config_ci_ne_root）

#### 列级别 Sparse Top 5 列

| 排名 | 表名 | 列名 | 分数 |
|-----|------|------|-----|
| 1 | **t_bz_config_ci_ne_root** | ALARM_TYPE | 0.1589 |
| 2 | t_gn_weaknesses_attack | classify1_id | 0.1501 |
| 3 | t_gn_botnet | classify1_id | 0.1477 |
| 4 | t_bz_config_ci_rfc | MODIFY_CLASSIFY | 0.1467 |
| 5 | t_gn_vulnerability_hole | classify1_id | 0.1422 |

#### 列级别累加分 Top 5 表

| 排名 | 表名 | 累加分 | 命中 |
|-----|------|-------|-----|
| **1** | **t_bz_config_ci_ne_root** | **1.2052** | ✅ |
| 2 | event_sdn | 0.8150 |  |
| 3 | t_gn_business_application_change | 0.7916 |  |

**列级别召回**: 1/2（缺 event_history）

#### 融合结果

- 表级别贡献: 10 表（含 event_history）
- 列级别贡献: 10 表（含 t_bz_config_ci_ne_root）
- 融合并集: 19 表
- **融合召回: 2/2 ✅**

**关键洞察**: 表级别找到 event_history，列级别找到 t_bz_config_ci_ne_root，**互补成功**！

---

### A.2 测试 2：设备down超3个月（失败案例）

**问题**: "列出平台上设备device state down状态超过3个月的设备清单及客户名称"

**期望表**: `t_bz_config_ci_ne_root`, `t_bz_config_customer`, `event_history`

#### 表级别 Sparse Top 10

| 排名 | 表名 | 分数 | 命中 |
|-----|------|------|-----|
| **1** | **t_bz_config_ci_ne_root** | **0.1742** | ✅ |
| 2 | sdw_dp_device | 0.1720 |  |
| 3 | t_gn_all_net_device | 0.1658 |  |

**表级别召回**: 1/3

#### 列级别 Sparse Top 5 列

| 排名 | 表名 | 列名 | 分数 |
|-----|------|------|-----|
| 1 | t_gn_topo_device | device_status | 0.1946 |
| 2 | sdw_dp_device_performance | device_status | 0.1455 |
| 3 | sdw_dp_port_performance | port_state | 0.1404 |

#### 列级别累加分 Top 5 表

| 排名 | 表名 | 累加分 | 命中 |
|-----|------|-------|-----|
| 1 | t_gn_topo_device | 1.1563 |  |
| 2 | t_gn_topo_link | 1.0702 |  |
| **3** | **t_bz_config_customer** | **1.0427** | ✅ |
| 4 | sdw_dp_device | 0.8267 |  |
| **10** | **t_bz_config_ci_ne_root** | **0.3073** | ✅ |

**列级别召回**: 2/3

#### 融合结果

- 融合并集: 14 表
- **融合召回: 2/3 ❌**
- **缺失**: `event_history`

**失败原因**: 问题关键词"设备状态/down"与 event_history 表（"告警/事件"）语义不匹配，两个级别都检索不到。

---

*报告完成时间: 2025-12-17 14:00*
