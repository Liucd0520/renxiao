# 300 问题完整召回测试报告

**测试时间**: 2024-12-22
**检索方式**: 表级别 + 增强列级别融合（预计算 Embedding）
**总耗时**: 10.9 秒（平均 36 毫秒/问题）

---

## 1. 总体结果

| 状态 | 数量 | 比例 |
|-----|-----|-----|
| ✅ 完全成功 | 294 | **97.4%** |
| 🔶 部分成功 | 8 | 2.6% |
| ❌ 完全失败 | 0 | 0.0% |

**平均召回率**: 99.5%

---

## 2. 按难度分类

| 难度 | 总数 | 完全成功 | 部分成功 | 失败 | 平均召回率 |
|-----|-----|---------|---------|-----|-----------|
| easy | 100 | 100 (100%) | 0 | 0 | 100.0% |
| medium | 101 | 101 (100%) | 0 | 0 | 100.0% |
| hard | 101 | 93 (92%) | 8 | 0 | 98.5% |

---

## 3. 缺失表分析

以下是检索中最常被遗漏的表：

| 表名 | 遗漏次数 | 分析 |
|-----|---------|-----|
| customer_collector_v2 | 8 | 需要增加该表的列级别增强描述 |

---

## 4. 部分成功案例分析

### 问题 229: 查询采集机测试用的和客户专用采集机所监控的设备中，在上一周（从上周一到上周日）告警级别为严重的告警数...
- **难度**: hard
- **期望表**: t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root
- **缺失表**: **customer_collector_v2**
- **召回率**: 80%
- **原因**: 缺失表可能未被列级别增强覆盖

### 问题 232: 统计每个采集机（使用采集机名）在最近一个月内监控的设备所产生的Interface event告警总数...
- **难度**: hard
- **期望表**: t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root
- **缺失表**: **customer_collector_v2**
- **召回率**: 80%
- **原因**: 缺失表可能未被列级别增强覆盖

### 问题 233: 找出在最近7天内，告警恢复时间超过1小时的Indicate event告警，并关联出对应的设备名、客...
- **难度**: hard
- **期望表**: t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root
- **缺失表**: **customer_collector_v2**
- **召回率**: 80%
- **原因**: 缺失表可能未被列级别增强覆盖

### 问题 236: 查询由采集机poller1和v6-dcs21监控的，设备类型为Power Supply或FRU Po...
- **难度**: hard
- **期望表**: ne_type, t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root
- **缺失表**: **customer_collector_v2**
- **召回率**: 83%
- **原因**: 缺失表可能未被列级别增强覆盖

### 问题 240: 找出由采集机测试采集机和胡浩test监控的，设备类型为Huawei NQA Udp Jitter或T...
- **难度**: hard
- **期望表**: ne_type, t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root
- **缺失表**: **customer_collector_v2**
- **召回率**: 83%
- **原因**: 缺失表可能未被列级别增强覆盖

### 问题 243: 找出在最近一周内，同时被采集机demo 03和测试001监控的客户有哪些？并列出这些客户在同期内产生...
- **难度**: hard
- **期望表**: t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root
- **缺失表**: **customer_collector_v2**
- **召回率**: 80%
- **原因**: 缺失表可能未被列级别增强覆盖

### 问题 246: 查询由采集机208监控的，且位于区域上海或南京市内的设备，在最近24小时内产生的告警详情，包括设备名...
- **难度**: hard
- **期望表**: t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root, t_bz_config_region
- **缺失表**: **customer_collector_v2**
- **召回率**: 83%
- **原因**: 缺失表可能未被列级别增强覆盖

### 问题 250: 找出那些在最近一周内，由同一个采集机监控，且产生了相同告警类型（EVENT_TYPE_NAME）超过...
- **难度**: hard
- **期望表**: t_bz_config_customer, collector_v2, event_history, customer_collector_v2, t_bz_config_ci_ne_root
- **缺失表**: **customer_collector_v2**
- **召回率**: 80%
- **原因**: 缺失表可能未被列级别增强覆盖

---

## 5. 失败案例分析

---

## 6. 改进建议

### 6.1 针对缺失表
1. **扩展列级别增强**：目前只增强了 6 张核心表的 163 列，建议扩展到更多常用表
2. **检查缺失表的描述**：确保表级别和列级别 Schema 包含问题中可能出现的关键词

### 6.2 针对部分成功
- 部分成功通常是缺少 1-2 张表
- 这些表可能是：JOIN 表、辅助表、较少使用的表
- 建议：为这些表添加更丰富的描述

### 6.3 针对检索流程
- 当前 TOP_K = 10，可以尝试增加到 15 观察效果
- 可以考虑添加核心表白名单机制

---

## 7. 总结

| 指标 | 值 |
|-----|-----|
| 测试问题 | 302 |
| 完全召回率 | 97.4% |
| 平均召回率 | 99.5% |
| 检索速度 | 36 ms/问题 |

**结论**: 通过列级别 LLM 增强 + Embedding 预计算，召回率达到 97.4%，检索速度 36ms/问题，满足生产环境需求。

---

*报告生成时间: 2024-12-22*
