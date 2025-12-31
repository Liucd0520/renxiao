# 原始 7 个问题全链路测试详细报告

**日期**: 2024-12-26  
**模型**: Qwen2.5-Coder-32B-Instruct

---

## 测试结果总览

### 正确率

| 方案 | 通过 | 不通过 | 正确率 |
|:---:|:----:|:------:|:------:|
| **A** | 6 | 1 | **85.7%** |
| **B** | 2 | 5 | **28.6%** |

### 详细结果

| # | 问题 | 方案 A | 方案 B | 失败原因 |
|:---:|------|:------:|:------:|---------|
| 1 | ciscoA告警统计 | ✅ | ✅ | - |
| 2 | down设备清单 | ❌ | ❌ | A:未用event_history; B:字段条件错误 |
| 3 | 客户数量 | ✅ | ❌ | 漏 IS_ACTIVE=1 条件 |
| 4 | 设备数量 | ✅ | ✅ | - |
| 5 | 新上线设备 | ✅ | ❌ | 用错字段 ONLINE_CHANGE_TIME |
| 6 | 下线设备 | ✅ | ❌ | 用错字段 STATUS=0 |
| 7 | 客户告警详情 | ✅ | ❌ | 未JOIN customer表，无法获取CUSTOMER_NAME |

---

## 逐题详细分析

### 第 1 题：设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计

**检索**: 19张表（含 event_history #10, t_bz_config_ci_ne_root #1）  
**方案B筛选**: t_bz_config_ci_ne_root, t_bz_incident_info, event_history

#### 正确答案
```sql
SELECT event_type_name, COUNT(event_id) AS alarm_count
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.ne_id = t_bz_config_ci_ne_root.ne_id
WHERE t_bz_config_ci_ne_root.host_name LIKE '%ciscoA%' 
  AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY event_type_name ORDER BY alarm_count DESC;
```

#### 方案 A ✅
```sql
SELECT e.EVENT_TYPE_NAME AS alarm_type, COUNT(e.EVENT_ID) AS alarm_count
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'ciscoA' 
  AND e.EVENT_TIME >= DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01')
GROUP BY e.EVENT_TYPE_NAME;
```
**判定**: 使用 event_history ✅, JOIN ci_ne_root ✅, GROUP BY event_type_name ✅

#### 方案 B ✅
```sql
SELECT e.EVENT_TYPE_NAME, COUNT(*) AS alarm_count
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'ciscoA'
  AND e.EVENT_TIME >= DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY e.EVENT_TYPE_NAME;
```
**判定**: 逻辑与正确答案一致 ✅

---

### 第 2 题：列出平台上设备device state down状态超过3个月的设备清单及客户名称

**检索**: 16张表（含 event_history #9, t_bz_config_ci_ne_root #4, t_bz_config_customer #1）  
**方案B筛选**: t_bz_config_customer, t_gn_topo_device, event_history

#### 正确答案
```sql
SELECT t_bz_config_ci_ne_root.NE_ID, t_bz_config_ci_ne_root.HOST_NAME, t_bz_config_customer.CUSTOMER_NAME
FROM t_bz_config_ci_ne_root
JOIN t_bz_config_customer ON ...
JOIN event_history ON ...
WHERE event_history.EVENT_NAME LIKE 'Device state%' 
  AND event_history.EVENT_TIME <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
```

#### 方案 A ❌
```sql
SELECT c.CUSTOMER_NAME, d.HOST_NAME AS DEVICE_NAME
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE d.NE_STATUS = 'down' AND d.OFFLINE_TIME <= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```
**判定**: ❌ 没有使用 event_history 查找 "Device state down" 事件，逻辑简化

#### 方案 B ❌
```sql
SELECT d.device_name, c.CUSTOMER_NAME
FROM t_gn_topo_device d
JOIN t_bz_config_customer c ON d.customer_id = c.CUSTOMER_ID
JOIN event_history e ON d.device_id = e.NE_ID 
  AND e.EVENT_TYPE_NAME = '设备状态' AND e.EVENT_VALUE = 'down'
WHERE e.EVENT_TIME <= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```
**判定**: ❌ 使用了错误的表 `t_gn_topo_device`（应为 `t_bz_config_ci_ne_root`），且事件条件 `EVENT_TYPE_NAME='设备状态'` 不等于正确答案的 `EVENT_NAME LIKE 'Device state%'`

---

### 第 3 题：现在平台上有多少家客户

**检索**: 17张表（含 t_bz_config_customer #1）  
**方案B筛选**: t_bz_config_customer

#### 正确答案
```sql
SELECT COUNT(CUSTOMER_ID) AS customer_count FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```

#### 方案 A ✅
```sql
SELECT COUNT(DISTINCT CUSTOMER_ID) AS customer_count FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```
**判定**: ✅ 有 IS_ACTIVE = 1 条件

#### 方案 B ❌
```sql
SELECT COUNT(*) AS customer_count FROM t_bz_config_customer;
```
**判定**: ❌ 缺少 `WHERE IS_ACTIVE = 1` 条件

---

### 第 4 题：现在平台上有多少台设备

**检索**: 19张表（含 t_bz_config_ci_ne_root #1）  
**方案B筛选**: t_bz_config_ci_ne_root, sdw_dp_device, ont_status, ne, t_gn_all_net_device

#### 正确答案
```sql
SELECT COUNT(CI_ID) AS device_count FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

#### 方案 A ✅
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

#### 方案 B ✅
```sql
SELECT COUNT(*) AS total_devices FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

---

### 第 5 题：上个月上线的新设备有多少

**检索**: 19张表（含 t_bz_config_ci_ne_root #1）  
**方案B筛选**: t_bz_config_ci_ne_root, uptime

#### 正确答案
```sql
SELECT COUNT(CI_ID) FROM t_bz_config_ci_ne_root WHERE ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
```

#### 方案 A ✅
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root 
WHERE IS_ONLINE = 1 AND ONLINE_TIME >= DATE_SUB(NOW(), INTERVAL 1 MONTH);
```
**判定**: ✅ 使用了正确的字段 `ONLINE_TIME`

#### 方案 B ❌
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root 
WHERE IS_ONLINE = 1 AND DATE(ONLINE_CHANGE_TIME) >= DATE_SUB(NOW(), INTERVAL 1 MONTH);
```
**判定**: ❌ 使用了错误的字段 `ONLINE_CHANGE_TIME`，应为 `ONLINE_TIME`

---

### 第 6 题：上个月下线的设备有多少

**检索**: 18张表（含 t_bz_config_ci_ne_root #1）  
**方案B筛选**: t_bz_config_ci_ne_root, uptime

#### 正确答案
```sql
SELECT COUNT(CI_ID) FROM t_bz_config_ci_ne_root 
WHERE OFFLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
```

#### 方案 A ✅
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root 
WHERE NE_STATUS = '下线' AND OFFLINE_TIME >= DATE_SUB(NOW(), INTERVAL 1 MONTH);
```
**判定**: ✅ 使用了正确的字段名

#### 方案 B ❌
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root 
WHERE STATUS = 0 AND OFFLINE_TIME >= DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01');
```
**判定**: ❌ 使用了错误的字段 `STATUS = 0`，应为 `NE_STATUS = '下线'`

---

### 第 7 题：某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？

**检索**: 17张表（含 event_history #8, t_bz_config_ci_ne_root #1, t_bz_config_customer #3）  
**方案B筛选**: t_bz_config_ci_ne_root, t_bz_incident_info, event_history（**漏掉 customer 表！**）

#### 正确答案
```sql
SELECT t_bz_config_customer.CUSTOMER_NAME, t_bz_config_ci_ne_root.HOST_NAME, 
       event_history.EVENT_NAME, event_history.EVENT_TIME
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.NE_ID = t_bz_config_ci_ne_root.NE_ID
JOIN t_bz_config_customer ON event_history.CUSTOMER_ID = t_bz_config_customer.ID
WHERE event_history.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
  AND t_bz_config_customer.CUSTOMER_NAME = 'xxx';
```

#### 方案 A ✅
```sql
SELECT eh.EVENT_TYPE_NAME AS 告警类型, eh.EVENT_TIME AS 告警时间, eh.RECOVER_TIME AS 恢复时间
FROM event_history eh
JOIN t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_ID = (...) AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```
**判定**: ✅ 正确 JOIN 了三张表

#### 方案 B ❌
```sql
SELECT eh.EVENT_TYPE_NAME AS 告警类型, eh.EVENT_TIME AS 告警时间, eh.ACTION_TIME AS 恢复时间
FROM event_history eh
JOIN t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
WHERE ci.CUSTOMER_ID = <指定的客户ID> AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```
**判定**: ❌ 没有 JOIN customer 表，无法获取 CUSTOMER_NAME（正确答案要求 SELECT CUSTOMER_NAME）

---

## 结论

| 指标 | 方案 A | 方案 B |
|:---:|:------:|:------:|
| **正确率** | **85.7%** (6/7) | **28.6%** (2/7) |

**方案 A 明显优于方案 B**

### 方案 B 失败原因分析

1. **#2**: 用错表（t_gn_topo_device）和事件条件
2. **#3**: 漏掉 IS_ACTIVE 过滤条件
3. **#5**: 用错字段（ONLINE_CHANGE_TIME vs ONLINE_TIME）
4. **#6**: 用错字段（STATUS vs NE_STATUS）
5. **#7**: 筛选时漏掉 customer 表，导致无法 JOIN

**核心问题**: 方案 B 的 LLM 筛选和 SQL 生成在细节上存在较多错误。
