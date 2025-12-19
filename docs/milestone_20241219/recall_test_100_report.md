# 100 个测试问题表召回率测试报告

**测试时间**: 2025-12-19 11:26:50

---

## 问题集概览

| 难度 | 数量 | 占比 | 说明 |
|-----|------|------|------|
| easy | 29 | 29% | 单表简单统计/查询 |
| medium | 52 | 52% | 2-3表关联、条件过滤 |
| hard | 19 | 19% | 多表 JOIN、复杂聚合 |
| **总计** | **100** | **100%** | |

---

## 总体召回率汇总

| 指标 | 数量 | 占比 |
|-----|------|------|
| ✅ 完全召回 | 65 | 65.0% |
| ⚠️ 部分召回 | 28 | 28.0% |
| ❌ 未召回 | 7 | 7.0% |
| **总计** | **100** | **100%** |

**平均召回率**: 78.8%

---

## 按难度分类的召回率

| 难度 | 完全召回 | 部分召回 | 未召回 | **完全召回率** |
|-----|---------|---------|-------|---------------|
| easy | 27/29 | 1 | 1 | **93.1%** |
| medium | 36/52 | 12 | 4 | **69.2%** |
| hard | 10/19 | 7 | 2 | **52.6%** |
| **总计** | **73/100** | 20 | 7 | **73%** |

---

## 核心表使用频率

| 排名 | 表名 | 被需要次数 |
|-----|------|----------|
| 1 | `t_bz_config_ci_ne_root` | 33 |
| 2 | `t_bz_config_customer` | 29 |
| 3 | `event_history` | 13 |
| 4 | `collector_v2` | 5 |
| 5 | `ne_service_package` | 4 |
| 6 | `ne_type` | 4 |
| 7 | `framework_user` | 4 |
| 8 | `framework_user_role` | 4 |
| 9 | `framework_role` | 4 |
| 10 | `t_bz_config_region` | 4 |

---

## 失败案例（未召回）

### EASY (1 个)

| ID | 问题 | 期望表 |
|----|------|-------|
| 6 | 查询当前处于'挂起'状态的告警工单数量 | `t_bz_incident_info` |

### MEDIUM (4 个)

| ID | 问题 | 期望表 |
|----|------|-------|
| 5 | 列出上个月新增设备数量最多的前5个客户 | `t_bz_config_ci_ne_root`, `t_bz_config_customer` |
| 7 | 统计每个客户配置的服务包数量，并列出数量大于3 | `t_bz_config_customer`, `ne_service_package` |
| 20 | 统计当前系统中，各严重等级的未确认告警数量 | `event_history` |
| 32 | 统计每个客户拥有的设备数量 | `t_bz_config_customer`, `t_bz_config_ci_ne_root` |

### HARD (2 个)

| ID | 问题 | 期望表 |
|----|------|-------|
| 18 | 列出最近30天内，处理时长超过24小时的告警工单 | `t_bz_incident_info` |
| 75 | 列出最近24小时内CPU使用率持续超过90%的设备 | `sdw_dp_device_performance`, `t_bz_config_ci_ne_root`, `t_bz_config_customer` |

---

## 部分召回案例（前10个）

| ID | 问题 | 召回率 | 匹配表 | 缺失表 |
|----|----- |--------|-------|-------|
| 10 | 统计各设备类型下的设备数量 | 50% | ne_type | t_bz_config_ci_ne_root |
| 11 | 端口流量使用率最高的前10个设备端口 | 50% | report_port_info | t_bz_config_ci_ne_root |
| 12 | 列出所有未配置任何联系人的客户 | 50% | t_rl_config_ci_contact | t_bz_config_customer |
| 13 | 统计上个月每个客户产生的告警事件总数 | 33% | event_history | t_bz_config_ci_ne_root, t_bz_config_customer |
| 14 | 查询所有'管理员'角色的用户数量 | 67% | framework_role, framework_user_role | framework_user |
| 24 | 统计每个区域下的设备数量 | 67% | t_bz_config_ci_ne_root_region_location_relation | t_bz_config_ci_ne_root |
| 31 | 查询未确认且严重程度为'严重'的告警 | 50% | event_history | t_bz_config_ci_ne_root |
| 44 | 统计每个区域下有多少个客户 | 50% | t_bz_config_region | t_bz_config_customer |
| 54 | 列出客户'ABC公司'名下所有设备的ID和名称 | 50% | t_bz_config_ci_ne_root | t_bz_config_customer |
| 65 | 查询'严重'级别未确认告警，关联设备和联系人 | 25% | event_history | t_bz_config_ci_ne_root, t_bz_config_contact |

---

## 关键发现

1. **Easy 问题表现优秀**: 93.1% 完全召回率，单表查询基本没问题
2. **Medium 问题有下降**: 69.2% 完全召回率，多表关联时容易漏表
3. **Hard 问题挑战大**: 52.6% 完全召回率，复杂查询召回不足
4. **核心表缺失问题**: `t_bz_config_ci_ne_root` 和 `t_bz_config_customer` 是最常被需要的表，但在多表查询时容易缺失

---

*报告生成时间: 2025-12-19 15:14:43*
