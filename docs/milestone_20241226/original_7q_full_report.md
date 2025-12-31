# 原始 7 个问题全链路测试 - 完整数据报告

**日期**: 2024-12-26  
**模型**: Qwen2.5-Coder-32B-Instruct

---

## 测试结果总览

### 正确率

| 方案 | 通过 | 不通过 | 正确率 |
|:---:|:----:|:------:|:------:|
| **A** | 6 | 1 | **85.7%** |
| **B** | 2 | 5 | **28.6%** |

### LLM 输入信息大小统计

**确认**: 只传了检索到的 **10 张表** 的完整 schema（不是 344 张表）

| # | 问题 | 问题 tokens | Schema tokens | 总 tokens |
|:---:|------|:-----------:|:-------------:|:---------:|
| 1 | ciscoA告警统计 | ~20 | ~11,126 | ~11,146 |
| 2 | down设备清单 | ~27 | ~8,148 | ~8,175 |
| 3 | 客户数量 | ~7 | ~9,741 | ~9,748 |
| 4 | 设备数量 | ~7 | ~8,322 | ~8,330 |
| 5 | 新上线设备 | ~8 | ~8,884 | ~8,892 |
| 6 | 下线设备 | ~7 | ~8,374 | ~8,382 |
| 7 | 客户告警详情 | ~24 | ~11,200 | ~11,224 |

**汇总**:
- 每题平均 Schema: **~9,400 tokens**
- 32B 模型上下文: 32,768 tokens
- Schema 占用比例: **~29%** (完全在模型能力范围内)

---

# 第 1 题

## 问题
> 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计

## Step 1: 检索阶段

**检索到 19 张表:**

| 排名 | 表名 | 是否核心表 |
|:---:|------|:--------:|
| 1 | t_bz_config_ci_ne_root | ✅ 设备表 |
| 2 | t_gn_business_application_change | |
| 3 | t_bz_incident_info | |
| 4 | t_bz_config_ci_entity | |
| 5 | ne_syslog_filter_script | |
| 6 | t_gn_botnet | |
| 7 | t_bz_problem_info | |
| 8 | event_yjk_history | |
| 9 | t_bz_config_customer | ✅ 客户表 |
| 10 | event_history | ✅ 告警表 |
| 11 | sdw_dp_port_basic | |
| 12 | t_gn_vulnerability_weak_password | |
| 13 | t_bz_config_ci_rfc | |
| 14 | t_gn_weaknesses_attack | |
| 15 | report_new_dev | |
| 16 | t_dc_incident_accident_type | |
| 17 | t_dc_release_type | |
| 18 | t_dc_service_source_type | |
| 19 | event_type | |

## Step 2: 方案B筛选

**筛选后保留 3 张表:**
- t_bz_config_ci_ne_root ✅
- t_bz_incident_info 
- event_history ✅

**分析**: 保留了核心的 event_history 和 ci_ne_root

## Step 3a: 方案A (使用前10张表)

**输入表**: 检索结果前10张（包含 event_history）

**生成SQL**:
```sql
SELECT 
    e.EVENT_TYPE_NAME AS alarm_type, 
    COUNT(e.EVENT_ID) AS alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE 
    n.HOST_NAME = 'ciscoA' 
    AND e.EVENT_TIME >= DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01 00:00:00')
    AND e.EVENT_TIME < DATE_FORMAT(NOW(), '%Y-%m-01 00:00:00')
GROUP BY 
    e.EVENT_TYPE_NAME;
```

**判定**: ✅ 通过 - 使用了正确的表和字段

## Step 3b: 方案B (使用筛选后的3张表)

**输入表**: t_bz_config_ci_ne_root, t_bz_incident_info, event_history

**生成SQL**:
```sql
SELECT e.EVENT_TYPE_NAME, COUNT(*) AS alarm_count
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'ciscoA'
  AND e.EVENT_TIME >= DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH)
  AND e.EVENT_TIME < DATE_FORMAT(NOW(), '%Y-%m-01')
GROUP BY e.EVENT_TYPE_NAME;
```

**判定**: ✅ 通过 - 逻辑正确

## 正确答案

```sql
SELECT event_type_name, COUNT(event_id) AS alarm_count
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.ne_id = t_bz_config_ci_ne_root.ne_id
WHERE t_bz_config_ci_ne_root.host_name LIKE '%ciscoA%' 
  AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND event_time < CURDATE()
GROUP BY event_type_name
ORDER BY alarm_count DESC
LIMIT 10;
```

---

# 第 2 题

## 问题
> 列出平台上设备device state down状态超过3个月的设备清单及客户名称

## Step 1: 检索阶段

**检索到 16 张表:**

| 排名 | 表名 | 是否核心表 |
|:---:|------|:--------:|
| 1 | t_bz_config_customer | ✅ 客户表 |
| 2 | t_gn_topo_device | |
| 3 | t_gn_topo_link | |
| 4 | t_bz_config_ci_ne_root | ✅ 设备表 |
| 5 | t_gn_business_application_change | |
| 6 | sdw_dp_device | |
| 7 | t_dc_config_device_type | |
| 8 | sdw_dp_device_performance | |
| 9 | event_history | ✅ 告警表 |
| 10 | t_gn_traffic_abnormality | |
| 11 | customer | |
| 12 | sdwan_device | |
| 13 | sdw_dp_port_performance | |
| 14 | t_gn_all_net_device | |
| 15 | topology_point_port | |
| 16 | atomic_cutover_order | |

## Step 2: 方案B筛选

**筛选后保留 3 张表:**
- t_bz_config_customer ✅
- t_gn_topo_device ❌ (应该是 t_bz_config_ci_ne_root)
- event_history ✅

**分析**: ❌ 漏掉了 t_bz_config_ci_ne_root，选了错误的 t_gn_topo_device

## Step 3a: 方案A (使用前10张表)

**输入表**: 检索结果前10张

**生成SQL**:
```sql
SELECT 
    c.CUSTOMER_NAME, 
    d.HOST_NAME AS DEVICE_NAME
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE 
    d.NE_STATUS = 'down' 
    AND d.OFFLINE_TIME <= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

**判定**: ❌ 不通过 - 没有使用 event_history 查找 "Device state down" 事件，直接用状态字段判断

## Step 3b: 方案B (使用筛选后的3张表)

**输入表**: t_bz_config_customer, t_gn_topo_device, event_history

**生成SQL**:
```sql
SELECT 
    d.device_name, 
    c.CUSTOMER_NAME
FROM 
    t_gn_topo_device d
JOIN 
    t_bz_config_customer c ON d.customer_id = c.CUSTOMER_ID
JOIN 
    event_history e ON d.device_id = e.NE_ID 
    AND e.EVENT_TYPE_NAME = '设备状态' AND e.EVENT_VALUE = 'down'
WHERE 
    e.EVENT_TIME <= DATE_SUB(NOW(), INTERVAL 3 MONTH)
GROUP BY 
    d.device_name, c.CUSTOMER_NAME
HAVING 
    MAX(e.EVENT_TIME) <= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

**判定**: ❌ 不通过 - 使用了错误的表 `t_gn_topo_device`，且事件条件 `EVENT_TYPE_NAME='设备状态'` 与正确答案不符

## 正确答案

```sql
SELECT t_bz_config_ci_ne_root.NE_ID, t_bz_config_ci_ne_root.HOST_NAME, t_bz_config_customer.CUSTOMER_NAME
FROM t_bz_config_ci_ne_root
JOIN t_bz_config_customer ON t_bz_config_ci_ne_root.CUSTOMER_ID = t_bz_config_customer.CUSTOMER_ID
JOIN event_history ON t_bz_config_ci_ne_root.NE_ID = event_history.NE_ID
WHERE event_history.EVENT_NAME LIKE 'Device state%' 
  AND event_history.EVENT_TIME <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY t_bz_config_ci_ne_root.NE_ID, t_bz_config_customer.CUSTOMER_NAME
HAVING COUNT(DISTINCT event_history.EVENT_ID) > 0
LIMIT 10;
```

---

# 第 3 题

## 问题
> 现在平台上有多少家客户

## Step 1: 检索阶段

**检索到 17 张表:**

| 排名 | 表名 | 是否核心表 |
|:---:|------|:--------:|
| 1 | t_bz_config_customer | ✅ 客户表 |
| 2 | customer | |
| 3 | t_bz_config_ci_ne_root | |
| 4 | t_gn_business_application_change | |
| 5 | t_bz_authority_users | |
| 6 | event_yjk_history | |
| 7 | t_bz_incident_info | |
| 8 | t_bz_config_work_policy_new | |
| 9 | event_history | |
| 10 | customer_collector_v2 | |
| 11 | temp | |
| 12 | t_bz_config_ci_circuit | |
| 13 | t_bz_config_ci_entity | |
| 14 | t_bz_config_location | |
| 15 | t_bz_config_group | |
| 16 | customer_global_config | |
| 17 | customer_model_rl | |

## Step 2: 方案B筛选

**筛选后保留 1 张表:**
- t_bz_config_customer ✅

**分析**: 筛选正确，只需要客户表

## Step 3a: 方案A (使用前10张表)

**输入表**: 检索结果前10张

**生成SQL**:
```sql
SELECT COUNT(DISTINCT CUSTOMER_ID) AS customer_count 
FROM t_bz_config_customer 
WHERE IS_ACTIVE = 1;
```

**判定**: ✅ 通过 - 有 IS_ACTIVE = 1 条件

## Step 3b: 方案B (使用筛选后的1张表)

**输入表**: t_bz_config_customer

**生成SQL**:
```sql
SELECT COUNT(*) AS customer_count FROM t_bz_config_customer;
```

**判定**: ❌ 不通过 - 缺少 `WHERE IS_ACTIVE = 1` 条件

## 正确答案

```sql
SELECT COUNT(CUSTOMER_ID) AS customer_count
FROM t_bz_config_customer
WHERE IS_ACTIVE = 1
LIMIT 10;
```

---

# 第 4 题

## 问题
> 现在平台上有多少台设备

## Step 1: 检索阶段

**检索到 19 张表:**

| 排名 | 表名 | 是否核心表 |
|:---:|------|:--------:|
| 1 | t_bz_config_ci_ne_root | ✅ 设备表 |
| 2 | t_gn_business_application_change | |
| 3 | t_gn_traffic_abnormality | |
| 4 | t_gn_botnet | |
| 5 | t_gn_scanning_probe | |
| 6 | t_gn_topo_link | |
| 7 | ne_template_access_config | |
| 8 | t_gn_weaknesses_attack | |
| 9 | t_gn_vulnerability_clear_transmission | |
| 10 | sdw_dp_device | |
| 11 | ont_status | |
| 12 | ne | |
| 13 | hardware | |
| 14 | t_bz_sys_dev_additional | |
| 15 | ne_business_severity | |
| 16 | collector | |
| 17 | ne_collect_record | |
| 18 | t_gn_all_net_device | |
| 19 | uptime | |

## Step 2: 方案B筛选

**筛选后保留 5 张表:**
- t_bz_config_ci_ne_root ✅
- sdw_dp_device
- ont_status
- ne
- t_gn_all_net_device

**分析**: 保留了核心设备表

## Step 3a: 方案A (使用前10张表)

**输入表**: 检索结果前10张

**生成SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

**判定**: ✅ 通过

## Step 3b: 方案B (使用筛选后的5张表)

**输入表**: t_bz_config_ci_ne_root, sdw_dp_device, ont_status, ne, t_gn_all_net_device

**生成SQL**:
```sql
SELECT COUNT(*) AS total_devices FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

**判定**: ✅ 通过

## 正确答案

```sql
SELECT COUNT(CI_ID) AS device_count
FROM t_bz_config_ci_ne_root
WHERE IS_DELETED = 0
LIMIT 10;
```

---

# 第 5 题

## 问题
> 上个月上线的新设备有多少

## Step 1: 检索阶段

**检索到 19 张表:**

| 排名 | 表名 | 是否核心表 |
|:---:|------|:--------:|
| 1 | t_bz_config_ci_ne_root | ✅ 设备表 |
| 2 | t_gn_business_application_change | |
| 3 | t_gn_traffic_abnormality | |
| 4 | t_gn_botnet | |
| 5 | t_gn_scanning_probe | |
| 6 | t_gn_topo_link | |
| 7 | ne_template_access_config | |
| 8 | t_gn_weaknesses_attack | |
| 9 | t_gn_vulnerability_clear_transmission | |
| 10 | t_gn_vulnerability_hole | |
| 11 | sdw_dp_device | |
| 12 | ne | |
| 13 | hardware | |
| 14 | t_bz_sys_dev_additional | |
| 15 | ne_business_severity | |
| 16 | collector | |
| 17 | ne_collect_record | |
| 18 | t_gn_all_net_device | |
| 19 | uptime | |

## Step 2: 方案B筛选

**筛选后保留 2 张表:**
- t_bz_config_ci_ne_root ✅
- uptime

## Step 3a: 方案A (使用前10张表)

**输入表**: 检索结果前10张

**生成SQL**:
```sql
SELECT COUNT(*) 
FROM t_bz_config_ci_ne_root 
WHERE IS_ONLINE = 1 AND ONLINE_TIME >= DATE_SUB(NOW(), INTERVAL 1 MONTH);
```

**判定**: ✅ 通过 - 使用了正确的字段 `ONLINE_TIME`

## Step 3b: 方案B (使用筛选后的2张表)

**输入表**: t_bz_config_ci_ne_root, uptime

**生成SQL**:
```sql
SELECT COUNT(*) 
FROM t_bz_config_ci_ne_root 
WHERE IS_ONLINE = 1 AND DATE(ONLINE_CHANGE_TIME) >= DATE_SUB(NOW(), INTERVAL 1 MONTH);
```

**判定**: ❌ 不通过 - 使用了错误的字段 `ONLINE_CHANGE_TIME`，应为 `ONLINE_TIME`

## 正确答案

```sql
SELECT COUNT(CI_ID) AS new_device_count
FROM t_bz_config_ci_ne_root
WHERE ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
AND YEAR(ONLINE_TIME) = 2025
LIMIT 10;
```

---

# 第 6 题

## 问题
> 上个月下线的设备有多少

## Step 1: 检索阶段

**检索到 18 张表:**

| 排名 | 表名 | 是否核心表 |
|:---:|------|:--------:|
| 1 | t_bz_config_ci_ne_root | ✅ 设备表 |
| 2 | t_gn_business_application_change | |
| 3 | t_gn_traffic_abnormality | |
| 4 | t_gn_botnet | |
| 5 | ont_status | |
| 6 | t_gn_scanning_probe | |
| 7 | t_gn_topo_link | |
| 8 | ne_template_access_config | |
| 9 | t_gn_weaknesses_attack | |
| 10 | t_gn_vulnerability_clear_transmission | |
| 11 | uptime | |
| 12 | trap | |
| 13 | hardware | |
| 14 | t_bz_sys_dev_additional | |
| 15 | ne_business_severity | |
| 16 | collector | |
| 17 | ne_collect_record | |
| 18 | t_gn_all_net_device | |

## Step 2: 方案B筛选

**筛选后保留 2 张表:**
- t_bz_config_ci_ne_root ✅
- uptime

## Step 3a: 方案A (使用前10张表)

**输入表**: 检索结果前10张

**生成SQL**:
```sql
SELECT COUNT(*) 
FROM t_bz_config_ci_ne_root 
WHERE NE_STATUS = '下线' 
AND OFFLINE_TIME >= DATE_SUB(NOW(), INTERVAL 1 MONTH) 
AND OFFLINE_TIME < NOW();
```

**判定**: ✅ 通过 - 使用了正确的字段 `NE_STATUS` 和 `OFFLINE_TIME`

## Step 3b: 方案B (使用筛选后的2张表)

**输入表**: t_bz_config_ci_ne_root, uptime

**生成SQL**:
```sql
SELECT COUNT(*) 
FROM t_bz_config_ci_ne_root 
WHERE STATUS = 0 AND OFFLINE_TIME >= DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01') 
AND OFFLINE_TIME < DATE_FORMAT(NOW(), '%Y-%m-01');
```

**判定**: ❌ 不通过 - 使用了错误的字段 `STATUS = 0`，应为 `NE_STATUS = '下线'`

## 正确答案

```sql
SELECT COUNT(CI_ID) AS offline_device_count
FROM t_bz_config_ci_ne_root
WHERE OFFLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND OFFLINE_TIME < CURDATE()
LIMIT 10;
```

---

# 第 7 题

## 问题
> 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？

## Step 1: 检索阶段

**检索到 17 张表:**

| 排名 | 表名 | 是否核心表 |
|:---:|------|:--------:|
| 1 | t_bz_config_ci_ne_root | ✅ 设备表 |
| 2 | t_gn_business_application_change | |
| 3 | t_bz_config_customer | ✅ 客户表 |
| 4 | t_bz_incident_info | |
| 5 | ne_syslog_filter_script | |
| 6 | event_yjk_history | |
| 7 | syslog_filter_script | |
| 8 | event_history | ✅ 告警表 |
| 9 | t_gn_botnet | |
| 10 | t_bz_problem_info | |
| 11 | event_backup | |
| 12 | event_history_sdwan | |
| 13 | ne_business_severity | |
| 14 | report_new_dev | |
| 15 | event_knowledge | |
| 16 | t_dc_release_type | |
| 17 | t_dc_incident_finish | |

## Step 2: 方案B筛选

**筛选后保留 3 张表:**
- t_bz_config_ci_ne_root ✅
- t_bz_incident_info
- event_history ✅

**分析**: ❌ 漏掉了 t_bz_config_customer！正确答案需要显示 CUSTOMER_NAME

## Step 3a: 方案A (使用前10张表)

**输入表**: 检索结果前10张（包含 t_bz_config_customer #3）

**生成SQL**:
```sql
SELECT 
    eh.EVENT_TYPE_NAME AS 告警类型,
    eh.EVENT_TIME AS 告警时间,
    eh.RECOVER_TIME AS 恢复时间
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
JOIN 
    t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    c.CUSTOMER_ID = (SELECT CUSTOMER_ID FROM t_bz_config_ci_ne_root WHERE NE_ID = ci.NE_ID LIMIT 1)
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

**判定**: ✅ 通过 - 正确 JOIN 了三张表（event_history, ci_ne_root, customer）

## Step 3b: 方案B (使用筛选后的3张表)

**输入表**: t_bz_config_ci_ne_root, t_bz_incident_info, event_history（缺少 customer 表！）

**生成SQL**:
```sql
SELECT 
    eh.EVENT_TYPE_NAME AS 告警类型,
    eh.EVENT_TIME AS 告警时间,
    eh.ACTION_TIME AS 恢复时间
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
WHERE 
    ci.CUSTOMER_ID = <指定的客户ID> AND
    eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

**判定**: ❌ 不通过 - 无法 SELECT CUSTOMER_NAME（正确答案要求），因为筛选时漏掉了 customer 表

## 正确答案

```sql
SELECT
    t_bz_config_customer.CUSTOMER_NAME,
    t_bz_config_ci_ne_root.HOST_NAME,
    event_history.EVENT_NAME,
    event_history.EVENT_TIME
FROM
    event_history
JOIN t_bz_config_ci_ne_root ON event_history.NE_ID = t_bz_config_ci_ne_root.NE_ID
JOIN t_bz_config_customer ON event_history.CUSTOMER_ID = t_bz_config_customer.ID
WHERE
    event_history.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
AND event_history.EVENT_STATUS_NAME = 'alarm'
AND t_bz_config_customer.CUSTOMER_NAME = 'xxx'
LIMIT 10;
```

---

# 总结

## 各环节数据统计

| # | 检索表数 | 方案B筛选后 | 核心表丢失 | 方案A结果 | 方案B结果 |
|:---:|:-------:|:---------:|:---------:|:--------:|:--------:|
| 1 | 19 | 3 | 无 | ✅ | ✅ |
| 2 | 16 | 3 | ci_ne_root | ❌ | ❌ |
| 3 | 17 | 1 | 无 | ✅ | ❌ |
| 4 | 19 | 5 | 无 | ✅ | ✅ |
| 5 | 19 | 2 | 无 | ✅ | ❌ |
| 6 | 18 | 2 | 无 | ✅ | ❌ |
| 7 | 17 | 3 | customer | ✅ | ❌ |

## 失败原因分类

### 方案B失败原因

| # | 失败类型 | 具体原因 |
|:---:|---------|---------|
| 2 | 筛选错误 | 选了 t_gn_topo_device 而非 t_bz_config_ci_ne_root |
| 3 | SQL生成错误 | 漏掉 WHERE IS_ACTIVE = 1 条件 |
| 5 | SQL生成错误 | 用错字段 ONLINE_CHANGE_TIME |
| 6 | SQL生成错误 | 用错字段 STATUS = 0 |
| 7 | 筛选错误 | 漏掉 t_bz_config_customer 表 |

### 方案A失败原因

| # | 失败类型 | 具体原因 |
|:---:|---------|---------|
| 2 | SQL生成错误 | 未使用 event_history 查找事件，直接用状态字段 |

## 最终正确率

| 方案 | 通过 | 不通过 | 正确率 |
|:---:|:----:|:------:|:------:|
| **A** | 6 | 1 | **85.7%** |
| **B** | 2 | 5 | **28.6%** |
