# 全流程批量测试报告

**测试时间**: 2025-12-19 09:52:37

**模型**: Qwen3-14B-awq

**表数量**: 344 | **列数量**: 3353

---

## 测试概述

| ID | 问题 |
|----|----- |
| 1 | 最近一年某客户的告警按照类型统计... |
| 2 | 哪些设备告警持续时间最长，给出TOP排名... |
| 3 | 某客户设备按照区域分别统计数量和设备详情，如设备名称、别名、区域、场所、IP、激活状态等... |
| 4 | 哪些设备近1个月告警次数最多给出排名... |
| 5 | 统计某客户工作日上班时间早上9点至晚上6点之间的告警情况... |
| 6 | 全平台告警级别分别统计... |

---

## 测试 1: 最近一年某客户的告警按照类型统计

**描述**: 需要统计某客户近一年的告警，按告警类型分类

### 1. 检索结果

**融合后表数**: 10 张

**表级别 Top 5**:
- event_history (0.1788)
- report_new_dev (0.1516)
- t_dc_incident_finish (0.1479)
- event_sdn (0.1415)
- t_dc_incident_accident_type (0.1368)

**列级别累加分 Top 5**:

**融合后表**:
```
event_history, event_knowledge, event_sdn, report_new_dev, t_bz_incident_event_record, t_bz_sdn_alarm, t_dc_incident_accident_type, t_dc_incident_finish, t_dc_release_type, t_gn_traffic_abnormality
```

### 2. 完整格式

**Schema 字符数**: 4587

```sql
SELECT EVENT_TYPE_NAME, COUNT(*) AS num
FROM event_history
WHERE CUSTOMER_ID = ? AND EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
GROUP BY EVENT_TYPE_NAME;
```

### 3. 精简格式

**Schema 字符数**: 3841

```sql
SELECT EVENT_TYPE_ID, COUNT(*) AS num
FROM event_history
WHERE CUSTOMER_NAME = '某客户' AND EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
GROUP BY EVENT_TYPE_ID;
```

### 4. 最精简格式

**Schema 字符数**: 2249

```sql
SELECT 
    t.TYPE_NAME AS alarm_type,
    COUNT(*) AS count
FROM 
    event_history eh
JOIN 
    t_dc_release_type t ON eh.EVENT_TYPE_ID = t.TYPE_ID
WHERE 
    eh.CUSTOMER_NAME = '某客户'
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
GROUP BY 
    t.TYPE_NAME;
```

---

## 测试 2: 哪些设备告警持续时间最长，给出TOP排名

**描述**: 需要计算告警持续时间并排名

### 1. 检索结果

**融合后表数**: 10 张

**表级别 Top 5**:
- event_history (0.1960)
- ne_business_severity (0.1711)
- report_ne_reachability (0.1655)
- event_yjk_history (0.1641)
- trap (0.1624)

**列级别累加分 Top 5**:

**融合后表**:
```
collector_monitor, event_history, event_sdn, event_yjk_history, ne_business_severity, report_ne_reachability, t_bz_incident_event_record, t_bz_sdn_alarm, t_gn_traffic_abnormality, trap
```

### 2. 完整格式

**Schema 字符数**: 6113

```sql
SELECT NE_ID, SUM(TIMESTAMPDIFF(SECOND, EVENT_TIME, RECOVER_TIME)) AS total_duration
FROM event_history
WHERE RECOVER_TIME IS NOT NULL
GROUP BY NE_ID
ORDER BY total_duration DESC;
```

### 3. 精简格式

**Schema 字符数**: 5079

```sql
SELECT device, SUM(TIMESTAMPDIFF(SECOND, trigger_time, recover_time)) AS total_duration
FROM event_yjk_history
WHERE recover_time IS NOT NULL
GROUP BY device
ORDER BY total_duration DESC
LIMIT 10;
```

### 4. 最精简格式

**Schema 字符数**: 2863

```sql
<think>
好的，我现在需要解决用户的问题：“哪些设备告警持续时间最长，给出TOP排名”。首先，我得仔细分析用户提供的数据库Schema，看看哪些表可能包含告警的持续时间信息，以及如何关联这些表来获取所需的数据。

用户提到的表有event_sdn、ne_business_severity、t_gn_traffic_abnormality、report_ne_reachability、event_history、collector_monitor、t_bz_sdn_alarm、event_yjk_history、t_bz_incident_event_record和trap。我需要逐一查看这些表的列，找出与告警持续时间相关的字段。

首先看event_sdn表，它有time_created，但可能没有恢复时间，所以可能无法直接计算持续时间。不过，可能有其他表包含恢复时间。比如event_history表中有EVENT_TIME（告警时间）和recover_time（恢复时间），这两个字段可以用来计算持续时间。同样，t_bz_sdn_alarm表有OCCUR_TIME（发生时间）和L
```

---

## 测试 3: 某客户设备按照区域分别统计数量和设备详情，如设备名称、别名、区域、场所、IP、激活状态等

**描述**: 按区域统计设备信息

### 1. 检索结果

**融合后表数**: 10 张

**表级别 Top 5**:
- t_bz_config_ci_ne_root (0.2125)
- uptime (0.1998)
- t_gn_all_net_device (0.1925)
- customer (0.1903)
- origin_availability (0.1819)

**列级别累加分 Top 5**:

**融合后表**:
```
cc_cmdb_sync_history, customer, day_availability, month_availability, origin_availability, t_bz_config_ci_ne_root, t_bz_config_region, t_bz_ip_region_manage, t_gn_all_net_device, uptime
```

### 2. 完整格式

**Schema 字符数**: 6481

```sql
SELECT 
    r.REGION_NAME,
    COUNT(*) OVER (PARTITION BY r.REGION_NAME) AS total_devices,
    t.* 
FROM 
    t_bz_config_ci_ne_root t
JOIN 
    t_bz_config_region r ON t.REGION_ID = r.REGION_ID
WHERE 
    t.IS_DELETED = 0 AND r.IS_ACTIVE = 1;
```

### 3. 精简格式

**Schema 字符数**: 5367

```sql
SELECT中使用COUNT(*)来统计数量，同时列出设备的各个字段。不过，这样会导致每个设备的详细信息被列出，而数量是每个区域的总数。但这样可能需要使用GROUP_CONCAT或者类似的函数来合并详情，不过用户可能希望每个区域的设备详情单独列出，同时显示该区域的设备数量。这可能需要使用子查询或者窗口函数来为每个设备行添加区域的总数。
```

### 4. 最精简格式

**Schema 字符数**: 2893

```sql
SELECT中的列需要是聚合函数或者GROUP BY的列。所以如果用户需要每个区域的设备数量，以及每个设备的详细信息，可能需要两个不同的查询，或者使用窗口函数来计算每个区域的总数，同时列出每个设备的信息。
```

---

## 测试 4: 哪些设备近1个月告警次数最多给出排名

**描述**: 统计近一个月告警次数并排名

### 1. 检索结果

**融合后表数**: 10 张

**表级别 Top 5**:
- event_history (0.1730)
- trap (0.1633)
- ne_business_severity (0.1497)
- trap_snmp (0.1460)
- t_gn_traffic_abnormality (0.1444)

**列级别累加分 Top 5**:

**融合后表**:
```
event_history, event_history_sdwan, event_to_cloudcare_record, event_yjk_history, ne_business_severity, report_ne_reachability, t_gn_traffic_abnormality, t_rl_priority_config, trap, trap_snmp
```

### 2. 完整格式

**Schema 字符数**: 6021

```sql
SELECT NE_ID, COUNT(*) AS alert_count
FROM event_history
WHERE EVENT_TIME >= NOW() - INTERVAL 1 MONTH
GROUP BY NE_ID
ORDER BY alert_count DESC;
```

### 3. 精简格式

**Schema 字符数**: 4987

```sql
<think>
好的，我现在需要解决用户的问题：“哪些设备近1个月告警次数最多给出排名”。首先，我得仔细分析用户的需求，然后看看数据库里的各个表结构，确定需要查询哪些表以及它们之间的关联方式。

用户的问题是关于设备告警次数的排名，时间范围是近一个月。所以，我需要找到所有设备在最近一个月内触发告警的次数，然后按次数从高到低排序。

接下来，看看数据库中的各个表。首先，用户提到的告警信息可能存储在多个表中，比如event_history、event_yjk_history、event_history_sdwan，可能还有trap_snmp和trap表。不过，根据表的说明，event_history是告警/事件主表，存储所有设备告警和事件的历史记录，包括告警时间、恢复时间、告警级别等。而event_yjk_history和event_history_sdwan可能分别对应云监控和SD-WAN的告警历史。另外，trap_snmp和trap可能存储告警配置信息，但用户的问题是关于告警次数的统计，可能需要的是实际发生的告警事件，而不是配置信息。因此，可能主要需要从event_history、ev
```

### 4. 最精简格式

**Schema 字符数**: 2807

```sql
SELECT NE_ID, COUNT(*) AS alert_count
FROM event_history
WHERE EVENT_TIME >= NOW() - INTERVAL 1 MONTH
AND EVENT_STATUS = 'open'  -- 假设只有触发的告警才被计数
GROUP BY NE_ID
ORDER BY alert_count DESC;
```

---

## 测试 5: 统计某客户工作日上班时间早上9点至晚上6点之间的告警情况

**描述**: 按工作日时间段统计告警

### 1. 检索结果

**融合后表数**: 10 张

**表级别 Top 5**:
- t_bz_config_work_policy_new (0.2030)
- report_new_dev (0.1936)
- event_yjk_history (0.1930)
- t_gn_all_net_event (0.1923)
- ne_business_severity (0.1864)

**列级别累加分 Top 5**:

**融合后表**:
```
day_availability, event, event_yjk_history, ne_business_severity, origin_availability, report_new_dev, t_bz_config_ci_entity, t_bz_config_work_policy_new, t_bz_release_work_info, t_gn_all_net_event
```

### 2. 完整格式

**Schema 字符数**: 5294

```sql
<think>
好的，我现在需要帮用户解决这个问题：统计某客户工作日上班时间早上9点至晚上6点之间的告警情况。首先，我得仔细分析用户的问题和提供的数据库Schema，确定需要查询哪些表以及它们之间的关联。

用户的问题是关于告警情况的统计，所以首先应该看看哪些表存储了告警信息。根据Schema说明，event_yjk_history表记录了客户云监控告警的历史，包含客户编号、名称、告警级别、内容、设备、触发时间等信息，这可能是一个关键的表。另外，t_gn_all_net_event表存储了客户网络事件告警信息，记录了告警数量和严重等级，可能也相关。不过用户的问题特别提到工作日的上班时间，可能需要结合工作策略配置来判断哪些时间属于工作时间。

接下来，用户提到的“工作日上班时间早上9点至晚上6点”可能需要参考t_bz_config_work_policy_new表，这个表存储了客户的工作策略配置，包括工作时间和非工作时间的规则，以及时区设置。因此，可能需要从这个表中获取客户的工作时间规则，然后根据这些规则来判断告警是否发生在工作时间。

不过，用户的问题可能更倾向于直接统计在特定时间范围
```

### 3. 精简格式

**Schema 字符数**: 4384

```sql
SELECT 
    COUNT(*) AS total_alerts,
    DATE(trigger_time
```

### 4. 最精简格式

**Schema 字符数**: 2408

```sql
SELECT COUNT(*) AS alert_count, severity_name
FROM event_yjk_history
WHERE customer_id = '指定客户ID'
AND DAYOFWEEK(trigger_time) BETWEEN 2 AND 6
AND HOUR(trigger_time) BETWEEN 9 AND 17
GROUP BY severity_name;
```

---

## 测试 6: 全平台告警级别分别统计

**描述**: 按告警级别统计

### 1. 检索结果

**融合后表数**: 10 张

**表级别 Top 5**:
- event_history (0.1635)
- event_yjk_history (0.1571)
- event_sdn (0.1406)
- syslog_facility (0.1390)
- t_bz_sdn_alarm (0.1292)

**列级别累加分 Top 5**:

**融合后表**:
```
event_history, event_history_sdwan, event_sdn, event_yjk_history, report_new_dev, syslog_facility, syslog_severity, t_bz_sdn_alarm, t_gn_traffic_abnormality, t_rl_priority_config
```

### 2. 完整格式

**Schema 字符数**: 5762

```sql
SELECT perceived_severity AS severity_level, COUNT(*) AS count FROM event_sdn GROUP BY perceived_severity
UNION ALL
SELECT SEVERITY_NAME, COUNT(*) FROM event_history_sdwan GROUP BY SEVERITY_NAME
UNION ALL
SELECT ALARM_LEVEL, COUNT(*) FROM t_bz_sdn_alarm GROUP BY ALARM_LEVEL
UNION ALL
SELECT priority, COUNT(*) FROM event_yjk_history GROUP BY priority
UNION ALL
SELECT SEVERITY_NAME, COUNT(*) FROM event_history GROUP BY SEVERITY_NAME;
```

### 3. 精简格式

**Schema 字符数**: 4794

```sql
SELECT perceived_severity AS severity, COUNT(*) AS count FROM event_sdn GROUP BY perceived_severity
UNION ALL
SELECT SEVERITY_NAME, COUNT(*) FROM event_history_sdwan GROUP BY SEVERITY_NAME
UNION ALL
SELECT ALARM_LEVEL, COUNT(*) FROM t_bz_sdn_alarm GROUP BY ALARM_LEVEL
UNION ALL
SELECT priority, COUNT(*) FROM event_yjk_history GROUP BY priority
UNION ALL
SELECT SEVERITY_NAME, COUNT(*) FROM event_history GROUP BY SEVERITY_NAME;
```

### 4. 最精简格式

**Schema 字符数**: 2727

```sql
<think>
好的，我现在需要帮用户解决“全平台告警级别分别统计”的问题。首先，我得仔细分析用户的需求和提供的数据库Schema。

用户的问题是要统计全平台各个告警级别的数量，也就是每个告警级别有多少条记录。这里的“全平台”可能指的是所有相关的告警表，所以需要检查所有可能包含告警级别的表。

接下来，我查看各个表的列信息。首先，event_sdn表有perceived_severity字段，可能表示告警的严重程度。event_history_sdwan表有SEVERITY_NAME和SEVERITY_ID，这两个可能都是告警级别。event_history表有SEVERITY_ID和SEVERITY_NAME，同样可能包含告警级别。t_bz_sdn_alarm表有ALARM_LEVEL，这应该也是告警级别。event_yjk_history表有priority字段，可能对应告警级别。而syslog_severity表存储的是系统日志的严重性级别，可能和告警级别相关，但不确定是否需要包含进来。report_new_dev表有TYPE和NUM，可能已经统计好了，但用户可能需要实时数据，
```

---

## 汇总

| 测试 | 融合表数 | 完整格式 | 精简格式 | 最精简格式 |
|-----|---------|---------|---------|----------|
| (需人工评估) | - | - | - | - |

**注意**: 由于没有正确答案，SQL 质量需要人工评估。

---

*报告生成时间: 2025-12-19 10:02:00*
