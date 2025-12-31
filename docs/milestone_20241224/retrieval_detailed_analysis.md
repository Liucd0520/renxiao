# 检索算法详细分析报告

**日期**: 2025-12-24 14:15  
**Schema 版本**: V2 (schemas_table_level_enhanced + schemas)  
**测试问题**: 300 个（simple/medium/hard 各 100）  
**目标表**: t_bz_config_ci_ne_root, t_bz_config_customer, event_history

---

## 1. 不同 TOP-K 的完全召回率对比

| TOP-K | 融合(并集) | 表级别 | 列级别 |
|------|-----------|-------|-------|
| 5 | **76.3%** (229) | 34.3% (103) | 39.7% (119) |
| 10 | **95.7%** (287) | 37.3% (112) | 67.0% (201) |
| 15 | **99.0%** (297) | 38.7% (116) | 79.7% (239) |
| 20 | **99.7%** (299) | 39.7% (119) | 89.3% (268) |
| 30 | **99.7%** (299) | 43.7% (131) | 97.0% (291) |

> **结论**: 增加 TOP-K 可以显著提升召回率，但边际效益递减。

---

## 2. 按难度分析（完全召回数）

### TOP-10 配置

| 难度 | 融合 | 表级别 | 列级别 |
|-----|------|-------|-------|
| simple | **100** | 96 | 75 |
| medium | **96** | 16 | 65 |
| hard | **91** | 0 | 61 |

### TOP-20 配置

| 难度 | 融合 | 表级别 | 列级别 |
|-----|------|-------|-------|
| simple | **100** | 97 | 95 |
| medium | **100** | 22 | 88 |
| hard | **99** | 0 | 85 |

---

## 3. 目标表排名统计

| 方法 | 平均排名 | 中位数 | TOP10内 | TOP20内 | TOP30内 |
|-----|---------|-------|---------|---------|---------|
| 表级别 | 58.2 | 12 | 294 | 328 | 351 |
| 列级别 | 5.6 | 2 | 505 | 572 | 596 |

> 总共 605 个目标表需要检索

---

## 4. TOP-10 融合失败案例（13 个）

### [medium] 统计上个月每个客户产生的告警总数，包括没有告警的客户...
- **期望**: ['event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['report_new_dev', 'event_yjk_history', 'day_availability', 't_gn_all_net_event', 'ne_business_severity']...
- **列级别 TOP10**: ['t_bz_config_customer', 'event_sdn', 'syslog_filter_script', 'ne_syslog_filter_script', 't_bz_config_ci_ne_root']...

### [medium] 统计本月每个客户产生的次要告警的平均恢复时长（分钟），只统计已恢复的告警...
- **期望**: ['event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['origin_availability', 'day_availability', 'month_availability', 'week_availability', 'report_new_dev']...
- **列级别 TOP10**: ['t_bz_config_customer', 'event_sdn', 'syslog_filter_script', 'ne_syslog_filter_script', 'event_yjk_history']...

### [medium] 统计上个月每个客户的告警总数，包括未产生告警的客户...
- **期望**: ['event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['report_new_dev', 'event_yjk_history', 'day_availability', 't_gn_all_net_event', 'ne_business_severity']...
- **列级别 TOP10**: ['t_bz_config_customer', 'event_sdn', 'syslog_filter_script', 'ne_syslog_filter_script', 't_bz_config_ci_ne_root']...

### [medium] 统计上个月每个客户产生的告警总数，包括没有告警的客户...
- **期望**: ['event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['report_new_dev', 'event_yjk_history', 'day_availability', 't_gn_all_net_event', 'ne_business_severity']...
- **列级别 TOP10**: ['t_bz_config_customer', 'event_sdn', 'syslog_filter_script', 'ne_syslog_filter_script', 't_bz_config_ci_ne_root']...

### [hard] 找出过去三个月内，从未发生过告警的客户，并统计这些客户下激活设备的总数...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['event_yjk_history', 'ne_business_severity', 'report_new_dev', 'day_availability', 'report_cust_reachability_ext']...
- **列级别 TOP10**: ['t_bz_config_customer', 't_bz_config_ci_ne_root', 'ne_syslog_filter_script', 'syslog_filter_script', 'event_sdn']...

### [hard] 找出所有告警类型为Trap event或Syslog event，且发生在今天，同时设备处于离线状态的告警详情...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['event_history', 'event_sdn', 'event_knowledge', 'event_backup', 'trap_ne_policy']...
- **列级别 TOP10**: ['t_bz_config_ci_ne_root', 'event_history', 'event_backup', 'ne_syslog_filter_script', 'event_yjk_history']...

### [hard] 找出过去三个月内，告警发生次数呈月度增长趋势的客户（即每个月的告警数都比上个月多）...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['event_yjk_history', 't_gn_all_net_event', 'ne_business_severity', 't_bz_config_ci_entity', 'event_history_sdwan']...
- **列级别 TOP10**: ['t_bz_config_customer', 'event_sdn', 'syslog_filter_script', 'ne_syslog_filter_script', 't_bz_config_ci_ne_root']...

### [hard] 找出所有在最近24小时内有新告警产生，且客户联系方式（邮箱或电话）非空的客户，并通知他们...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['t_rl_config_ci_contact', 't_rl_config_group_contact', 't_bz_config_contact', 't_rl_config_contact_policy', 't_bz_config_ci_entity']...
- **列级别 TOP10**: ['t_bz_config_customer', 't_bz_config_ci_ne_root', 'event_sdn', 'ne_syslog_filter_script', 'syslog_filter_script']...

### [hard] 查询设备名为demo-switch-01或test-router-02的所有历史告警，并计算从告警发生到恢复的平均时间、最长时间和最短时间...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['event_history', 'event_yjk_history', 'event_history_sdwan', 'ne_business_severity', 'ne_collect_history_record']...
- **列级别 TOP10**: ['t_bz_config_ci_ne_root', 'ne_syslog_filter_script', 'event_sdn', 'syslog_filter_script', 'event_yjk_history']...

### [hard] 计算每个客户在过去7天内告警数量的日环比增长率（(今天-昨天)/昨天），仅显示增长率超过50%的客户...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['t_gn_all_net_event', 'event_yjk_history', 'report_cust_reachability_ext', 'ne_business_severity', 'event_history_sdwan']...
- **列级别 TOP10**: ['t_bz_config_customer', 'syslog_filter_script', 'ne_syslog_filter_script', 'event_sdn', 't_bz_config_ci_ne_root']...

### [hard] 查询每个客户在过去7天内，每小时'Ping event'与'Trap event'告警数量的相关系数（近似计算）...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['event_history', 'event_yjk_history', 'event', 'event_condition', 'event_knowledge']...
- **列级别 TOP10**: ['event_history', 'event_backup', 'event_yjk_history', 't_bz_config_customer', 'event_sdn']...

### [hard] 查询'测试客户'下，过去7天内每天'Ping event'和'Trap event'告警数量的对比，显示日期、Ping告警数、Trap告警数和告警总数。...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['event', 'event_history', 'event_yjk_history', 'event_knowledge', 'event_condition']...
- **列级别 TOP10**: ['event_history', 'event_yjk_history', 'event_backup', 't_bz_config_customer', 'event_sdn']...

### [hard] 找出过去7天内，每小时告警数超过该小时平均告警数2倍的时间段，并关联显示该时间段内告警最多的客户。...
- **期望**: ['t_bz_config_ci_ne_root', 'event_history', 't_bz_config_customer']
- **表级别 TOP10**: ['ne_business_severity', 'day_availability', 't_bz_incident_ci_record', 'event_yjk_history', 't_gn_all_net_event']...
- **列级别 TOP10**: ['t_bz_config_customer', 'syslog_filter_script', 'ne_syslog_filter_script', 't_bz_config_ci_ne_root', 'event_sdn']...


---

## 5. 结论与优化建议

### 核心结论
1. **V2 配置 + TOP-10 融合召回率: 95.7%** (287/300) ✅
2. **TOP-15 融合召回率可达: 99.0%** (297/300)
3. simple 问题 100% 完全召回，hard 问题 91% 完全召回

### 失败案例特点
- 共 13 个失败案例（4 medium + 9 hard）
- 主要问题：包含"告警"关键词的问题，`event_history` 被 `event_yjk_history`、`event_sdn` 等干扰

### 优化方向
1. **增加 TOP-K 到 15**：召回率从 95.7% 提升到 99.0%
2. **表级别对 simple 问题效果好**（96/100），hard 问题需要列级别辅助
3. **列级别检索对 hard 问题关键**：hard 问题表级别 0%，但列级别 61%

---
*报告自动生成*
