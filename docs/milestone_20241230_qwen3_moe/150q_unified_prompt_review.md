# Qwen2.5-32B vs Qwen3 MoE 150题人工审核报告

**日期**: 2024-12-30
**提示词**: 统一版本

---

## 汇总统计

| 难度 | Qwen2.5-32B | Qwen3 MoE |
|:-----|:-----------:|:---------:|
| Simple | 36/50 (72%) | 41/50 (82%) |
| Medium | 30/50 (60%) | 34/50 (68%) |
| Hard | 14/50 (28%) | 19/50 (38%) |
| **总计** | **80/150 (53.3%)** | **94/150 (62.7%)** |

---

## 逐题详细审核

## 第 1 题 [simple]

**问题**: 查询所有设备的基础信息
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    CI_ID,
    NE_ID,
    LOCATION_ID,
    REGION_ID,
    DEPARTMENT_ID,
    CUSTOMER_ID,
    NE_IP,
    NE_MODEL,
    IS_ACTIVE,
    IS_ONLINE,
    IS_DISCOVERY,
    DEVICE_TYPE_ID,
    VENDOR_ID,
    ACCOUNT,
    PASSWORD,
    SERIAL_NO_PACKETEER,
    GROUP_NAME,
    GROUP_ID,
    DC_IP,
 
```

---

## 第 2 题 [simple]

**问题**: 查询所有在线设备的ID和主机名
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT CI_ID, HOST_NAME 
FROM t_bz_config_ci_ne_root 
WHERE IS_ONLINE = 1 AND IS_DELETED = 0;
```

---

## 第 3 题 [simple]

**问题**: 查询所有已激活的设备数量
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 1
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT COUNT(*) AS active_device_count FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 1;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT COUNT(*) AS total_active_devices
FROM t_bz_config_ci_ne_root
WHERE IS_ACTIVE = 1 AND IS_DELETED = 0;
```

---

## 第 4 题 [simple]

**问题**: 查询设备型号为ciscoA的所有设备
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL = 'ciscoA'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL = 'ciscoA';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL = 'ciscoA';
```

---

## 第 5 题 [simple]

**问题**: 查询主机名包含shanghai的设备
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%';
```

---

## 第 6 题 [simple]

**问题**: 查询主机名为tdk-shanghai-b的设备的IP地址
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT NE_IP FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'tdk-shanghai-b'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT NE_IP FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'tdk-shanghai-b';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT NE_IP 
FROM t_bz_config_ci_ne_root 
WHERE HOST_NAME = 'tdk-shanghai-b' 
  AND IS_DELETED = 0;
```

---

## 第 7 题 [simple]

**问题**: 查询所有离线设备的ID和名称
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 0
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 0;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT CI_ID, HOST_NAME 
FROM t_bz_config_ci_ne_root 
WHERE IS_ONLINE = 0 AND IS_DELETED = 0;
```

---

## 第 8 题 [simple]

**问题**: 查询所有客户的信息
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_customer
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer;
```

---

## 第 9 题 [simple]

**问题**: 查询客户名称为测试客户的所有信息
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户';
```

---

## 第 10 题 [simple]

**问题**: 查询所有已激活的客户数量
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_customer WHERE IS_ACTIVE = 1
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT COUNT(*) AS active_customer_count FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT COUNT(*) AS total_active_customers
FROM t_bz_config_customer
WHERE IS_ACTIVE = 1;
```

---

## 第 11 题 [simple]

**问题**: 查询客户简称是上海理想公司的客户ID和联系电话
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_ID, CUSTOMER_PHONE FROM t_bz_config_customer WHERE CUSTOMER_ABB = '上海理想公司'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT CUSTOMER_ID, CUSTOMER_PHONE FROM t_bz_config_customer WHERE CUSTOMER_ABB = '上海理想公司';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT CUSTOMER_ID, CUSTOMER_PHONE
FROM t_bz_config_customer
WHERE CUSTOMER_ABB = '上海理想';
```

---

## 第 12 题 [simple]

**问题**: 查询客户名称为中国电信上海理想的客户邮箱
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_EMAIL FROM t_bz_config_customer WHERE CUSTOMER_NAME = '中国电信上海理想'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT CUSTOMER_EMAIL FROM t_bz_config_customer WHERE CUSTOMER_NAME = '中国电信上海理想';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.CUSTOMER_EMAIL
FROM t_bz_config_customer c
WHERE c.CUSTOMER_NAME = '中国电信上海理想';
```

---

## 第 13 题 [simple]

**问题**: 查询今天发生的所有告警记录
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE()
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE DATE(time_created) = CURDATE();
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE DATE(time_created) = CURDATE();
```

---

## 第 14 题 [simple]

**问题**: 查询昨天发生的所有告警数量
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE DATE(EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT COUNT(*) 
FROM event_sdn 
WHERE DATE(time_created) = CURDATE() - INTERVAL 1 DAY;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE DATE(EVENT_TIME) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY));
```

---

## 第 15 题 [simple]

**问题**: 查询最近7天发生的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE time_created >= NOW() - INTERVAL 7 DAY;
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT *
FROM event_sdn
WHERE time_created >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

---

## 第 16 题 [simple]

**问题**: 查询最近30天发生的告警数量
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT COUNT(*) AS alarm_count
FROM event_sdn
WHERE time_created >= NOW() - INTERVAL 30 DAY;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

---

## 第 17 题 [simple]

**问题**: 查询本月发生的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE YEAR(EVENT_TIME) = YEAR(CURDATE()) AND MONTH(EVENT_TIME) = MONTH(CURDATE())
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE YEAR(time_created) = YEAR(CURDATE()) AND MONTH(time_created) = MONTH(CURDATE());
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT *
FROM event_history
WHERE EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH);
```

---

## 第 18 题 [simple]

**问题**: 查询上个月发生的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE YEAR(EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(EVENT_TIME) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE time_created >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND time_created < CURDATE();
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT *
FROM event_history
WHERE EVENT_TIME >= DATE_SUB(DATE_TRUNC('month', CURRENT_DATE), INTERVAL 1 MONTH)
  AND EVENT_TIME < DATE_TRUNC('month', CURRENT_DATE);
```

---

## 第 19 题 [simple]

**问题**: 查询过去三个月发生的告警数量
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT COUNT(*) AS alarm_count
FROM event_sdn
WHERE time_created >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT COUNT(*) AS alarm_count
FROM event_sdn
WHERE time_created >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
```

---

## 第 20 题 [simple]

**问题**: 查询告警级别为严重的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE SEVERITY = 1
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE perceived_severity = '严重';
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE perceived_severity = '严重';
```

---

## 第 21 题 [simple]

**问题**: 查询告警类型为Ping event的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

---

## 第 22 题 [simple]

**问题**: 查询告警状态为已恢复的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 2
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = '已恢复';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 3 AND EVENT_STATUS_NAME = '已恢复';
```

---

## 第 23 题 [simple]

**问题**: 查询告警级别为警告的所有告警数量
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE SEVERITY = 4
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT COUNT(*) FROM event_sdn WHERE perceived_severity = '警告';
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT COUNT(*) AS warning_count
FROM event_sdn
WHERE perceived_severity = '警告';
```

---

## 第 24 题 [simple]

**问题**: 查询告警类型为Trap event的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event';
```

---

## 第 25 题 [simple]

**问题**: 查询告警状态为活动的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 1
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE is-acked = '活动';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 1 AND EVENT_STATUS_NAME = '活动';
```

---

## 第 26 题 [simple]

**问题**: 查询所有在线的设备数量
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT COUNT(*) AS online_device_count FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT COUNT(*) AS online_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 1 AND IS_DELETED = 0;
```

---

## 第 27 题 [simple]

**问题**: 查询所有已激活的客户列表
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_NAME FROM t_bz_config_customer WHERE IS_ACTIVE = 1
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```

---

## 第 28 题 [simple]

**问题**: 查询今天发生的所有告警记录
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE()
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE DATE(time_created) = CURDATE();
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE DATE(time_created) = CURDATE();
```

---

## 第 29 题 [simple]

**问题**: 查询主机名为 ciscoA 的设备信息
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'ciscoA'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'ciscoA';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'ciscoA';
```

---

## 第 30 题 [simple]

**问题**: 查询客户名称为 测试客户 的详细信息
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户';
```

---

## 第 31 题 [simple]

**问题**: 查询昨天发生的所有严重级别的告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE() - INTERVAL 1 DAY AND SEVERITY = 1
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE DATE(time_created) = CURDATE() - INTERVAL 1 DAY AND perceived_severity = '严重';
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT *
FROM event_sdn
WHERE perceived_severity = '严重'
  AND DATE(time_created) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY));
```

---

## 第 32 题 [simple]

**问题**: 查询所有设备型号
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT NE_MODEL FROM t_bz_config_ci_ne_root
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT DISTINCT NE_MODEL FROM t_bz_config_ci_ne_root UNION SELECT DISTINCT equipment_model FROM t_gn_business_application_change UNION SELECT DISTINCT dev_model FROM sdw_dp_device;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT NE_MODEL 
FROM t_bz_config_ci_ne_root 
WHERE IS_DELETED = 0 AND NE_MODEL IS NOT NULL AND NE_MODEL != '';
```

---

## 第 33 题 [simple]

**问题**: 查询所有告警类型名称
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT EVENT_TYPE_NAME FROM event_history
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT DISTINCT EVENT_TYPE_NAME FROM event_history;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT EVENT_TYPE_NAME 
FROM event_history 
WHERE EVENT_TYPE_NAME IS NOT NULL 
ORDER BY EVENT_TYPE_NAME;
```

---

## 第 34 题 [simple]

**问题**: 查询主机名为 poller1 的设备是否在线
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME, IS_ONLINE FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'poller1'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT IS_ONLINE FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'poller1';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT IS_ONLINE 
FROM t_bz_config_ci_ne_root 
WHERE HOST_NAME = 'poller1';
```

---

## 第 35 题 [simple]

**问题**: 查询客户简称是 ngg-319009 的客户ID
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_ABB = 'ngg-319009'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_ABB = 'ngg-319009';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT CUSTOMER_ID 
FROM t_bz_config_customer 
WHERE CUSTOMER_ABB = 'ngg-319009';
```

---

## 第 36 题 [simple]

**问题**: 查询最近7天内发生的所有告警事件ID和名称
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT EVENT_ID, EVENT_NAME FROM event_history WHERE EVENT_TIME >= CURDATE() - INTERVAL 7 DAY
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT e.EVENT_ID, e.EVENT_NAME
FROM event_history e
WHERE e.EVENT_TIME >= NOW() - INTERVAL 7 DAY;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT e.EVENT_ID, e.EVENT_NAME
FROM event_history e
WHERE e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
```

---

## 第 37 题 [simple]

**问题**: 查询所有设备类型ID
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT NE_TYPE_ID FROM t_bz_config_ci_ne_root
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT DISTINCT DEVICE_TYPE_ID FROM t_bz_config_ci_ne_root;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT DEVICE_TYPE_ID FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

---

## 第 38 题 [simple]

**问题**: 查询所有状态为已恢复的告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 2
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = '已恢复';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT *
FROM event_history
WHERE EVENT_STATUS = '已恢复'
   OR EVENT_STATUS_NAME = '已恢复'
   OR EVENT_STATUS = 3
   OR EVENT_STATUS_NAME = '3';
```

---

## 第 39 题 [simple]

**问题**: 查询本月创建的所有客户
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_NAME FROM t_bz_config_customer WHERE MONTH(CREATE_TIME) = MONTH(CURDATE()) AND YEAR(CREATE_TIME) = YEAR(CURDATE())
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_customer WHERE DATE_FORMAT(CREATE_TIME, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m');
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT *
FROM t_bz_config_customer
WHERE CREATE_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND CREATE_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH);
```

---

## 第 40 题 [simple]

**问题**: 查询设备型号为空的设备有哪些
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE NE_MODEL IS NULL OR NE_MODEL = ''
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL IS NULL OR NE_MODEL = '';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT CI_ID, NE_ID, NE_IP, NE_MODEL, HOST_NAME, SERIAL_NUMBER
FROM t_bz_config_ci_ne_root
WHERE NE_MODEL IS NULL OR NE_MODEL = '';
```

---

## 第 41 题 [simple]

**问题**: 查询告警类型为 Ping event 的所有告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

---

## 第 42 题 [simple]

**问题**: 查询客户 南京研发中心 的联系电话和邮箱
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_PHONE, CUSTOMER_EMAIL FROM t_bz_config_customer WHERE CUSTOMER_NAME = '南京研发中心'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT CUSTOMER_PHONE, CUSTOMER_EMAIL FROM t_bz_config_customer WHERE CUSTOMER_NAME = '南京研发中心';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_PHONE,
    c.CUSTOMER_EMAIL
FROM 
    t_bz_config_customer c
WHERE 
    c.CUSTOMER_NAME = '南京研发中心';
```

---

## 第 43 题 [simple]

**问题**: 查询所有未激活的设备
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 0
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 0;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 0 AND IS_DELETED = 0;
```

---

## 第 44 题 [simple]

**问题**: 查询过去三个月内发生的所有主要级别告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= CURDATE() - INTERVAL 3 MONTH AND SEVERITY = 2
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT * FROM event_sdn WHERE perceived_severity = '主要' AND time_created >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT *
FROM event_sdn
WHERE perceived_severity IN ('Major', 'Critical', 'Emergency')
  AND time_created >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

---

## 第 45 题 [simple]

**问题**: 查询主机名包含 shanghai 的设备
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%';
```

---

## 第 46 题 [simple]

**问题**: 查询上个月创建的所有设备
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE MONTH(CREATE_TIME) = MONTH(CURDATE() - INTERVAL 1 MONTH) AND YEAR(CREATE_TIME) = YEAR(CURDATE() - INTERVAL 1 MONTH)
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CREATE_TIME < CURDATE();
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT *
FROM t_bz_config_ci_ne_root
WHERE CREATE_TIME >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01 00:00:00')
  AND CREATE_TIME < DATE_FORMAT(CURDATE(), '%Y-%m-01 00:00:00')
  AND IS_DELETED = 0;
```

---

## 第 47 题 [simple]

**问题**: 查询告警级别为警告的所有告警名称
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT EVENT_NAME FROM event_history WHERE SEVERITY = 4
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT native_probable_cause FROM event_sdn WHERE perceived_severity = '警告';
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT DISTINCT native_probable_cause AS alarm_name
FROM event_sdn
WHERE perceived_severity = '警告';
```

---

## 第 48 题 [simple]

**问题**: 查询客户 上海理想公司 的创建时间
**期望表**: `t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT CREATE_TIME FROM t_bz_config_customer WHERE CUSTOMER_NAME = '上海理想公司'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT CREATE_TIME FROM t_bz_config_customer WHERE CUSTOMER_NAME = '上海理想公司';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT CREATE_TIME 
FROM t_bz_config_customer 
WHERE CUSTOMER_NAME = '上海理想公司';
```

---

## 第 49 题 [simple]

**问题**: 查询最近30天内发生的所有 Trap event 类型告警
**期望表**: `event_history`

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= CURDATE() - INTERVAL 30 DAY AND EVENT_TYPE_NAME = 'Trap event'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event' AND EVENT_TIME >= NOW() - INTERVAL 30 DAY;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT *
FROM event_history
WHERE EVENT_TYPE_NAME = 'Trap event'
  AND EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

---

## 第 50 题 [simple]

**问题**: 统计设备表里有多少个不同的区域ID
**期望表**: `t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(DISTINCT REGION_ID) FROM t_bz_config_ci_ne_root
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT COUNT(DISTINCT REGION_ID) FROM t_bz_config_ci_ne_root;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT COUNT(DISTINCT REGION_ID) AS distinct_region_count
FROM t_bz_config_ci_ne_root
WHERE IS_DELETED = 0;
```

---

## 第 51 题 [medium]

**问题**: 查询客户南京研发中心名下所有设备的名称和IP地址
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_IP FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '南京研发中心'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.HOST_NAME, ci.NE_IP 
FROM t_bz_config_ci_ne_root ci 
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID 
WHERE c.CUSTOMER_NAME = '南京研发中心';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.HOST_NAME AS 设备名称, c.NE_IP AS IP地址
FROM t_bz_config_ci_ne_root c
JOIN t_bz_config_customer cu ON c.CUSTOMER_ID = cu.CUSTOMER_ID
WHERE cu.CUSTOMER_NAME = '南京研发中心' AND c.IS_DELETED = 0;
```

---

## 第 52 题 [medium]

**问题**: 统计每个客户拥有的在线设备数量，并按数量降序排列
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS online_count FROM t_bz_config_customer cus LEFT JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID AND ne.IS_ONLINE = 1 GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME ORDER BY online_count DESC
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(ci.CI_ID) AS online_device_count
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE ci.IS_ONLINE = 1
GROUP BY c.CUSTOMER_NAME
ORDER BY online_device_count DESC;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(*) AS online_device_count
FROM 
    t_bz_config_ci_ne_root n
JOIN 
    t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    n.IS_ONLINE = 1 
    AND n.IS_DELETED = 0
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME
ORDER BY 
    onl
```

---

## 第 53 题 [medium]

**问题**: 查询设备名为tdk-shanghai-b的所有历史告警记录，并显示告警名称和发生时间
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'tdk-shanghai-b'
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT e.native_probable_cause AS 告警名称, e.time_created AS 发生时间
FROM event_sdn e
JOIN t_bz_config_ci_ne_root n ON e.ip_ddress = n.NE_IP
WHERE n.HOST_NAME = 'tdk-shanghai-b';
```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
SELECT e.EVENT_NAME, e.EVENT_TIME
FROM t_bz_incident_event_record e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'tdk-shanghai-b' OR n.ALIAS = 'tdk-shanghai-b';
```

---

## 第 54 题 [medium]

**问题**: 统计最近7天内，每个客户产生的严重告警数量
**期望表**: `t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS severe_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.SEVERITY = 1 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_ID, 
    c.CUSTOMER_NAME, 
    COUNT(e.EVENT_ID) AS severe_alarm_count
FROM 
    t_bz_config_customer c
JOIN 
    event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    e.SEVERITY_NAME = '严重' 
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    c.CUSTOME
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.EVENT_ID) AS severe_alert_count
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND e.SEVERITY_NAME IN ('Critical', 'Major', 'Severe')
GROUP BY 
    c.C
```

---

## 第 55 题 [medium]

**问题**: 查询客户ngg-319009名下所有设备的型号和激活状态
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_MODEL, ne.IS_ACTIVE FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = 'ngg-319009'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.NE_MODEL, c.IS_ACTIVE
FROM t_bz_config_ci_ne_root c
JOIN t_bz_config_customer cu ON c.CUSTOMER_ID = cu.CUSTOMER_ID
WHERE cu.CUSTOMER_NO = 'ngg-319009';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT c.NE_MODEL AS 设备型号, c.IS_ACTIVE AS 激活状态
FROM t_bz_config_ci_ne_root c
JOIN t_bz_config_customer cu ON c.CUSTOMER_ID = cu.CUSTOMER_ID
WHERE cu.CUSTOMER_NO = 'ngg-319009';
```

---

## 第 56 题 [medium]

**问题**: 统计本月发生的所有Trap event告警，并关联显示对应的设备名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TYPE_NAME = 'Trap event' AND YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE())
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, eh.ROOT_NE_NAME AS DEVICE_NAME
FROM event_history eh
WHERE eh.EVENT_TYPE_NAME = 'Trap event' AND YEAR(eh.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(eh.EVENT_TIME) = MONTH(CURDATE());
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_NAME,
    eh.EVENT_TIME,
    eh.SEVERITY_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    eh.EVENT_DESC
FROM 
    event_history eh
WHERE 
    eh.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND eh.EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), IN
```

---

## 第 57 题 [medium]

**问题**: 查询客户中国电信上海理想名下所有离线设备的名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '中国电信上海理想' AND ne.IS_ONLINE = 0
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT t_bz_config_ci_ne_root.HOST_NAME 
FROM t_bz_config_ci_ne_root 
JOIN t_bz_config_customer ON t_bz_config_ci_ne_root.CUSTOMER_ID = t_bz_config_customer.CUSTOMER_ID 
WHERE t_bz_config_customer.CUSTOMER_NAME = '中国电信上海理想' AND t_bz_config_ci_ne_root.IS_ONLINE = 0;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT n.HOST_NAME
FROM t_bz_config_ci_ne_root n
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '中国电信上海理想'
  AND n.IS_ONLINE = 0
  AND n.IS_DELETED = 0;
```

---

## 第 58 题 [medium]

**问题**: 统计昨天发生的所有告警，并按告警级别分组统计数量
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.SEVERITY, COUNT(*) AS count FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE DATE(ev.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY) GROUP BY ev.SEVERITY
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT perceived_severity, COUNT(*) as count 
FROM event_sdn 
WHERE DATE(time_created) = CURDATE() - INTERVAL 1 DAY 
GROUP BY perceived_severity;
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT perceived_severity, COUNT(*) AS alarm_count
FROM event_sdn
WHERE DATE(time_created) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY))
GROUP BY perceived_severity;
```

---

## 第 59 题 [medium]

**问题**: 查询设备名为ciscoA和ngg-rt-01的所有告警记录，包括告警类型和状态
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_TYPE_NAME, ev.EVENT_STATUS_NAME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME IN ('ciscoA', 'ngg-rt-01')
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT e.EVENT_NAME, e.EVENT_TYPE_NAME, e.EVENT_STATUS_NAME
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME IN ('ciscoA', 'ngg-rt-01');
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    eh.EVENT_NAME AS alarm_type,
    eh.EVENT_STATUS_NAME AS status
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root cnr ON eh.NE_ID = cnr.NE_ID
WHERE 
    cnr.HOST_NAME IN ('ciscoA', 'ngg-rt-01')
```

---

## 第 60 题 [medium]

**问题**: 统计每个客户名下设备型号为空的设备数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS null_model_count FROM t_bz_config_customer cus LEFT JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID AND (ne.NE_MODEL IS NULL OR ne.NE_MODEL = '') GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT c.CUSTOMER_NAME, COUNT(d.dev_id) AS device_count
FROM t_bz_config_customer c
LEFT JOIN sdw_dp_device d ON c.CUSTOMER_ID = d.customer_id
WHERE d.dev_model IS NULL OR d.dev_model = ''
GROUP BY c.CUSTOMER_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(*) AS device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE n.NE_MODEL IS NULL OR n.NE_MODEL = ''
GROUP BY c.CUSTOMER_NAME;
```

---

## 第 61 题 [medium]

**问题**: 查询过去三个月内，客户测试客户产生的所有主要告警的详细信息
**期望表**: `event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME, ev.EVENT_DESC FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '测试客户' AND ev.SEVERITY = 2 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT eh.*
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.IS_TRIAL = 1 AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT e.*
FROM event_history e
JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '客户测试客户'
  AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
  AND e.SEVERITY_NAME IN ('Major', 'Critical', 'Emergency')
  AND e.EVENT_STATUS = 1
  AND c.IS_ACTIVE = 1;
```

---

## 第 62 题 [medium]

**问题**: 统计每个客户名下，处于活动状态的告警数量
**期望表**: `t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS active_alarm_count FROM t_bz_config_customer cus LEFT JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID AND ev.EVENT_STATUS = 1 GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(e.EVENT_ID) AS active_alarm_count
FROM t_bz_config_customer c
JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE c.IS_ACTIVE = 1 AND e.EVENT_STATUS = 1
GROUP BY c.CUSTOMER_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.EVENT_ID) AS active_alarm_count
FROM 
    t_bz_config_customer c
    INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    c.IS_ACTIVE = 1
    AND e.EVENT_STATUS = 1
    AND e.IS_ACK = 0
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME;
```

---

## 第 63 题 [medium]

**问题**: 查询设备名为v6-dcs21和poller1的创建时间和客户名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.CREATE_TIME, cus.CUSTOMER_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ne.HOST_NAME IN ('v6-dcs21', 'poller1')
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    ci.HOST_NAME AS 设备名称,
    ci.CREATE_TIME AS 创建时间,
    c.CUSTOMER_NAME AS 客户名称
FROM 
    t_bz_config_ci_ne_root ci
JOIN 
    t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    ci.HOST_NAME IN ('v6-dcs21', 'poller1');
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, nc.CREATE_TIME
FROM t_bz_config_ci_ne_root nc
JOIN t_bz_config_customer c ON nc.CUSTOMER_ID = c.CUSTOMER_ID
WHERE nc.HOST_NAME IN ('v6-dcs21', 'poller1');
```

---

## 第 64 题 [medium]

**问题**: 统计最近30天内，每种告警类型发生的次数
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_TYPE_NAME, COUNT(*) AS count FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) GROUP BY ev.EVENT_TYPE_NAME
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT EVENT_TYPE_NAME, COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY EVENT_TYPE_NAME;
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    e.EVENT_TYPE_NAME AS alarm_type,
    COUNT(*) AS alarm_count
FROM 
    event_history e
WHERE 
    e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY 
    e.EVENT_TYPE_NAME
ORDER BY 
    alarm_count DESC;
```

---

## 第 65 题 [medium]

**问题**: 查询客户上海理想公司名下，所有已恢复的告警记录及恢复时间
**期望表**: `event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME, ev.RECOVER_TIME FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '上海理想公司' AND ev.EVENT_STATUS = 2
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT eh.EVENT_NAME, eh.RECOVER_TIME
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '上海理想公司' AND eh.EVENT_STATUS_NAME = '已恢复';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    e.EVENT_ID,
    e.EVENT_NAME,
    e.EVENT_TIME AS alarm_time,
    e.RECOVER_TIME AS recovery_time
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    c.CUSTOMER_NAME = '上海理想'
    AND e.RECOVER_TIME IS NOT NULL
    AND e.EVENT_STATUS = 1;
```

---

## 第 66 题 [medium]

**问题**: 查询设备名为demo-switch-01和test-router-02的客户联系邮箱
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, cus.CUSTOMER_EMAIL FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ne.HOST_NAME IN ('demo-switch-01', 'test-router-02')
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT DISTINCT c.CUSTOMER_EMAIL
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE d.HOST_NAME IN ('demo-switch-01', 'test-router-02');
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT c.CUSTOMER_EMAIL
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE n.HOST_NAME IN ('demo-switch-01', 'test-router-02');
```

---

## 第 67 题 [medium]

**问题**: 统计今天发生的所有Threshold event告警，并显示对应的设备IP地址
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_IP, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TYPE_NAME = 'Threshold event' AND DATE(ev.EVENT_TIME) = CURDATE()
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT EVENT_ID, EVENT_NAME, ADDRESS AS DEVICE_IP
FROM event_history
WHERE EVENT_TYPE_NAME = 'Threshold event' AND DATE(EVENT_TIME) = CURDATE();
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT DISTINCT eh.ADDRESS AS device_ip
FROM event_history eh
WHERE DATE(eh.EVENT_TIME) = CURDATE()
  AND eh.EVENT_TYPE_NAME = 'Threshold event';
```

---

## 第 68 题 [medium]

**问题**: 查询客户南京研发中心名下，所有未激活的设备名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '南京研发中心' AND ne.IS_ACTIVE = 0
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.HOST_NAME 
FROM t_bz_config_ci_ne_root ci 
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID 
WHERE c.CUSTOMER_NAME = '南京研发中心' AND ci.IS_ACTIVE = 0;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT n.HOST_NAME
FROM t_bz_config_ci_ne_root n
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '南京研发中心'
  AND n.IS_ACTIVE = 0;
```

---

## 第 69 题 [medium]

**问题**: 统计每个客户名下，设备数量最多的前三个客户
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS device_count FROM t_bz_config_customer cus LEFT JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME ORDER BY device_count DESC LIMIT 3
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(bci.CI_ID) AS device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root bci ON c.CUSTOMER_ID = bci.CUSTOMER_ID
GROUP BY c.CUSTOMER_NAME
ORDER BY device_count DESC
LIMIT 3;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(d.CI_ID) AS device_count
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE 
    d.IS_DELETED = 0
    AND d.IS_ACTIVE = 1
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME
ORDER BY 
    device_count DESC
LIMIT 
```

---

## 第 70 题 [medium]

**问题**: 查询设备名为cx-sx-cc002的所有Syslog event告警的描述信息
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_DESC, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'cx-sx-cc002' AND ev.EVENT_TYPE_NAME = 'Syslog event'
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT EVENT_DESC FROM event_history WHERE ROOT_NE_NAME = 'cx-sx-cc002';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT eh.EVENT_DESC
FROM event_history eh
JOIN t_bz_config_ci_ne_root cnr ON eh.ROOT_NE_NAME = cnr.HOST_NAME
WHERE cnr.HOST_NAME = 'cx-sx-cc002';
```

---

## 第 71 题 [medium]

**问题**: 统计最近7天内，告警级别为警告且状态为已确认的告警数量，按客户分组
**期望表**: `t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS confirmed_warning_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.SEVERITY = 4 AND ev.EVENT_STATUS = 3 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY cus.CUSTOMER_ID, cus.CUSTOME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME, 
    COUNT(e.EVENT_ID) AS WARNING_CONFIRMED_ALERT_COUNT
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.SEVERITY_NAME = '警告' 
    AND e.IS_ACK = 1 
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 

```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(*) AS alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND e.SEVERITY_NAME = '警告'
    AND e.IS_ACK = 1
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_
```

---

## 第 72 题 [medium]

**问题**: 查询所有发生过Ping event告警的设备名称和客户简称
**期望表**: `t_bz_config_ci_ne_root, event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT ne.HOST_NAME, cus.CUSTOMER_ABB FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ev.EVENT_TYPE_NAME = 'Ping event'
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT DISTINCT eh.ROOT_NE_NAME AS 设备名称, tbc.CUSTOMER_ABB AS 客户简称
FROM event_history eh
JOIN t_bz_config_customer tbc ON eh.CUSTOMER_ID = tbc.CUSTOMER_ID
WHERE eh.EVENT_NAME LIKE '%Ping event%';
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT DISTINCT eh.ROOT_NE_NAME AS 设备名称, c.CUSTOMER_ABB AS 客户简称
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE eh.EVENT_TYPE_NAME = 'Ping event' AND eh.EVENT_STATUS = 1;
```

---

## 第 73 题 [medium]

**问题**: 查询客户ngg-319009名下，所有设备的最后更新时间
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.UPDATE_TIME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = 'ngg-319009' ORDER BY ne.UPDATE_TIME DESC
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.CI_ID, ci.HOST_NAME, MAX(ci.UPDATE_TIME) AS last_update_time
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer cust ON ci.CUSTOMER_ID = cust.CUSTOMER_ID
WHERE cust.CUSTOMER_NO = 'ngg-319009'
GROUP BY ci.CI_ID, ci.HOST_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT MAX(tbc.UPDATE_TIME) AS last_update_time
FROM t_bz_config_ci_ne_root tbc
JOIN t_bz_config_customer tcc ON tbc.CUSTOMER_ID = tcc.CUSTOMER_ID
WHERE tcc.CUSTOMER_NO = 'ngg-319009';
```

---

## 第 74 题 [medium]

**问题**: 查询客户ngg-319009名下所有设备的主机名和IP地址
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_IP FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = 'ngg-319009'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT t_bz_config_ci_ne_root.HOST_NAME, t_bz_config_ci_ne_root.NE_IP 
FROM t_bz_config_ci_ne_root 
JOIN t_bz_config_customer ON t_bz_config_ci_ne_root.CUSTOMER_ID = t_bz_config_customer.CUSTOMER_ID 
WHERE t_bz_config_customer.CUSTOMER_NAME = 'ngg-319009';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.HOST_NAME, c.NE_IP
FROM t_bz_config_ci_ne_root c
JOIN t_bz_config_customer cu ON c.CUSTOMER_ID = cu.CUSTOMER_ID
WHERE cu.CUSTOMER_NO = 'ngg-319009';
```

---

## 第 75 题 [medium]

**问题**: 统计每个客户拥有的在线设备数量，并列出客户名称和数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS online_device_count FROM t_bz_config_customer cus JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID WHERE ne.IS_ONLINE = 1 GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(b.CI_ID) AS online_device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root b ON c.CUSTOMER_ID = b.CUSTOMER_ID
WHERE b.IS_ONLINE = 1
GROUP BY c.CUSTOMER_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.CI_ID) AS online_device_count
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root e ON c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    e.IS_ONLINE = 1 
    AND e.IS_ACTIVE = 1 
    AND e.IS_DELETED = 0
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME;
```

---

## 第 76 题 [medium]

**问题**: 查询设备名为ciscoA的所有历史告警记录，包括告警名称和发生时间
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'ciscoA'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT e.EVENT_NAME, e.EVENT_TIME
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'ciscoA';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT e.EVENT_NAME, e.EVENT_TIME
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'ciscoA';
```

---

## 第 77 题 [medium]

**问题**: 统计最近7天内，每个客户产生的严重级别告警数量
**期望表**: `t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS critical_alarm_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.SEVERITY = 1 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME, 
    COUNT(eh.EVENT_ID) AS severe_alert_count
FROM 
    t_bz_config_customer c
JOIN 
    event_history eh ON c.CUSTOMER_ID = eh.CUSTOMER_ID
WHERE 
    eh.SEVERITY_NAME = '严重' 
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    c.CUSTOMER_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.EVENT_ID) AS severe_alert_count
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND e.SEVERITY_NAME IN ('严重', '紧急', 'Critical', 'Major')
GROUP BY 
    c
```

---

## 第 78 题 [medium]

**问题**: 查询客户中国电信上海理想名下，所有处于离线状态的设备名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '中国电信上海理想' AND ne.IS_ONLINE = 0
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.HOST_NAME 
FROM t_bz_config_ci_ne_root ci 
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID 
WHERE c.CUSTOMER_NAME = '中国电信上海理想' AND ci.IS_ONLINE = 0;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT n.HOST_NAME
FROM t_bz_config_ci_ne_root n
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '中国电信上海理想'
  AND n.IS_ONLINE = 0
  AND n.IS_ACTIVE = 1
  AND n.IS_DELETED = 0;
```

---

## 第 79 题 [medium]

**问题**: 查询昨天发生的所有Trap event告警，并关联显示对应的设备名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TYPE_NAME = 'Trap event' AND DATE(ev.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, eh.ROOT_NE_NAME AS DEVICE_NAME
FROM event_history eh
WHERE eh.EVENT_TYPE_NAME = 'Trap' AND DATE(eh.EVENT_TIME) = CURDATE() - INTERVAL 1 DAY;
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_NAME,
    eh.EVENT_TIME,
    eh.SEVERITY_NAME,
    eh.EVENT_STATUS_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    eh.ADDRESS
FROM 
    event_history eh
WHERE 
    DATE(eh.EVENT_TIME) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY))
    AND eh.EVENT_TYPE_NAME = 'Trap'
ORDE
```

---

## 第 80 题 [medium]

**问题**: 统计本月每个设备型号产生的告警总数，按数量降序排列
**期望表**: `t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_MODEL, COUNT(ev.EVENT_ID) AS alarm_count FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID WHERE YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE()) GROUP BY ne.NE_MODEL ORDER BY alarm_count DESC
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT t_bz_config_ci_ne_root.NE_MODEL, COUNT(t_bz_incident_event_record.EVENT_ID) AS alarm_count
FROM t_bz_config_ci_ne_root
JOIN t_bz_incident_event_record ON t_bz_config_ci_ne_root.NE_ID = t_bz_incident_event_record.NE_ID
WHERE MONTH(t_bz_incident_event_record.EVENT_TIME) = MONTH(CURDATE()) AND Y
```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
SELECT 
    c.NE_MODEL AS device_model,
    COUNT(e.EVENT_ID) AS alarm_count
FROM 
    t_bz_config_ci_ne_root c
JOIN 
    t_bz_incident_event_record e ON c.NE_ID = e.NE_ID
WHERE 
    e.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND e.EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01')
```

---

## 第 81 题 [medium]

**问题**: 查询客户上海理想公司名下，所有发生过严重告警的设备名称
**期望表**: `t_bz_config_ci_ne_root, event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '上海理想公司' AND ev.SEVERITY = 1
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT DISTINCT ci.HOST_NAME
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
JOIN event_history eh ON ci.NE_ID = eh.NE_ID
WHERE c.CUSTOMER_NAME = '上海理想' AND eh.SEVERITY_NAME = '严重';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT c.HOST_NAME
FROM t_bz_config_ci_ne_root c
JOIN event_history e ON c.NE_ID = e.NE_ID AND c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE c.CUSTOMER_ID = (
    SELECT CUSTOMER_ID
    FROM t_bz_config_customer
    WHERE CUSTOMER_NAME = '上海理想'
)
AND e.SEVERITY_ID IN (1, 2, 3) -- 假设严重告警级别为1、2、3，根据实际业
```

---

## 第 82 题 [medium]

**问题**: 查询设备tdk-shanghai-b在过去三个月内的所有告警，按发生时间倒序排列
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TYPE_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'tdk-shanghai-b' AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) ORDER BY ev.EVENT_TIME DESC
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT e.*
FROM event_yjk_history e
JOIN t_bz_config_ci_ne_root d ON e.device = d.HOST_NAME
WHERE d.HOST_NAME = 'tdk-shanghai-b' AND e.trigger_time >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
ORDER BY e.trigger_time DESC;
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT e.*
FROM event_sdn e
JOIN t_bz_config_ci_ne_root n ON e.ip_ddress = n.NE_IP
WHERE n.HOST_NAME = 'tdk-shanghai-b'
  AND e.time_created >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
ORDER BY e.time_created DESC;
```

---

## 第 83 题 [medium]

**问题**: 查询今天所有状态为已恢复的告警，并显示对应的客户简称
**期望表**: `event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, cus.CUSTOMER_ABB, ev.RECOVER_TIME FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ev.EVENT_STATUS = 2 AND DATE(ev.RECOVER_TIME) = CURDATE()
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, eh.RECOVER_TIME, c.CUSTOMER_ABB
FROM event_history eh
JOIN customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE DATE(eh.RECOVER_TIME) = CURDATE() AND eh.EVENT_STATUS_NAME = '已恢复';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    e.CUSTOMER_ABB AS 客户简称,
    h.recover_time AS 恢复时间,
    h.name AS 告警名称,
    h.priority AS 告警级别,
    h.trigger_time AS 触发时间
FROM 
    event_history h
JOIN 
    t_bz_config_customer c ON h.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    h.EVENT_STATUS = 1 
    AND h.recover_time >= CURDATE() 
    A
```

---

## 第 84 题 [medium]

**问题**: 查询设备v6-dcs21产生的所有Threshold event告警的详细描述
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_DESC, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'v6-dcs21' AND ev.EVENT_TYPE_NAME = 'Threshold event'
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT EVENT_DESC 
FROM event_history 
WHERE ROOT_NE_NAME = 'v6-dcs21' AND EVENT_TYPE_NAME LIKE '%Threshold event%';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT eh.EVENT_DESC
FROM event_history eh
JOIN t_bz_config_ci_ne_root t ON eh.ROOT_NE_NAME = t.HOST_NAME OR eh.ADDRESS = t.NE_IP
WHERE t.HOST_NAME = 'v6-dcs21'
  AND eh.EVENT_TYPE_NAME LIKE '%Threshold%'
  AND eh.EVENT_STATUS = 1;
```

---

## 第 85 题 [medium]

**问题**: 统计每个客户名下，设备型号为空的设备数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS null_model_count FROM t_bz_config_customer cus JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID WHERE ne.NE_MODEL IS NULL OR ne.NE_MODEL = '' GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(d.CI_ID) AS device_count
FROM t_bz_config_customer c
LEFT JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE d.NE_MODEL IS NULL OR d.NE_MODEL = ''
GROUP BY c.CUSTOMER_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(*) AS device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE n.NE_MODEL IS NULL OR n.NE_MODEL = ''
GROUP BY c.CUSTOMER_NAME;
```

---

## 第 86 题 [medium]

**问题**: 查询最近30天内，告警级别为主要的告警，并关联显示设备IP地址
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_IP, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.SEVERITY = 2 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT e.ALARM_NAME, e.DEVICE_IP
FROM t_bz_sdn_alarm e
JOIN t_bz_config_ci_ne_root d ON e.DEVICE_IP = d.NE_IP
WHERE e.ALARM_LEVEL = '主要'
  AND e.OCCUR_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
SELECT DISTINCT e.DEVICE_IP, e.ALARM_LEVEL, e.OCCUR_TIME, c.NE_IP, c.HOST_NAME
FROM t_bz_sdn_alarm e
JOIN t_bz_config_ci_ne_root c ON e.DEVICE_IP = c.NE_IP
WHERE e.OCCUR_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
  AND e.ALARM_LEVEL = 'Major'
  AND c.IS_ACTIVE = 1
  AND c.IS_ONLINE = 1
  AND c.IS_DELE
```

---

## 第 87 题 [medium]

**问题**: 查询客户测试客户名下，所有已激活设备的最近更新时间
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.UPDATE_TIME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '测试客户' AND ne.IS_ACTIVE = 1 ORDER BY ne.UPDATE_TIME DESC
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.CUSTOMER_ID, ci.HOST_NAME, MAX(eh.EVENT_TIME) AS LAST_UPDATE_TIME
FROM t_bz_config_ci_ne_root ci
JOIN event_history eh ON ci.CI_ID = eh.NE_ID
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '测试客户名' AND ci.IS_ACTIVE = 1
GROUP BY ci.CUSTOMER_ID, ci.HOST_
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, MAX(n.UPDATE_TIME) AS last_update_time
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE c.IS_ACTIVE = 1 AND n.IS_ACTIVE = 1
GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME;
```

---

## 第 88 题 [medium]

**问题**: 统计本月每种告警类型发生的次数
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_TYPE_NAME, COUNT(ev.EVENT_ID) AS count FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE()) GROUP BY ev.EVENT_TYPE_NAME
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT EVENT_TYPE_NAME, COUNT(*) AS alarm_count
FROM event_history
WHERE YEAR(EVENT_TIME) = YEAR(CURDATE()) AND MONTH(EVENT_TIME) = MONTH(CURDATE())
GROUP BY EVENT_TYPE_NAME;
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    e.EVENT_TYPE_NAME AS alarm_type,
    COUNT(*) AS alarm_count
FROM 
    event_history e
WHERE 
    e.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND e.EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY 
    e.EVENT_TYPE_NAME;
```

---

## 第 89 题 [medium]

**问题**: 查询设备poller1和demo-switch-01的所有告警记录，包括告警状态名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_NAME, ev.EVENT_STATUS_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME IN ('poller1', 'demo-switch-01')
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT e.EVENT_ID, e.EVENT_NAME, e.EVENT_TIME, e.EVENT_STATUS_NAME
FROM event_history e
JOIN t_bz_config_ci_ne_root d ON e.NE_ID = d.NE_ID
WHERE d.HOST_NAME IN ('poller1', 'demo-switch-01');
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    e.EVENT_ID,
    e.EVENT_NAME,
    e.EVENT_VALUE,
    e.EVENT_STATUS,
    e.EVENT_STATUS_NAME,
    e.EVENT_TIME,
    e.SEVERITY_NAME,
    e.NE_NAME,
    e.ADDRESS,
    e.ROOT_NE_NAME
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE 
    n.HOST_NAME I
```

---

## 第 90 题 [medium]

**问题**: 查询客户南京研发中心名下，设备创建时间在最近一年的所有设备
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_MODEL, ne.CREATE_TIME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '南京研发中心' AND ne.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.*
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '南京研发中心'
AND ci.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT c.*
FROM t_bz_config_ci_ne_root c
JOIN t_bz_config_customer cu ON c.CUSTOMER_ID = cu.CUSTOMER_ID
WHERE cu.CUSTOMER_NAME = '南京研发中心'
  AND c.CREATE_TIME >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND c.IS_DELETED = 0;
```

---

## 第 91 题 [medium]

**问题**: 统计过去三个月内，每个设备产生的警告级别告警数量，只显示数量大于5的设备
**期望表**: `t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, COUNT(ev.EVENT_ID) AS warning_count FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID WHERE ev.SEVERITY = 4 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) GROUP BY ne.NE_ID, ne.HOST_NAME HAVING warning_count > 5
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT ci.CI_ID, ci.HOST_NAME, COUNT(e.EVENT_ID) AS warning_count
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_incident_event_record e ON ci.NE_ID = e.NE_ID
WHERE e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
AND e.EVENT_TYPE_ID = 'WARNING'
GROUP BY ci.CI_ID, ci.HOST_NAME
HAVING warning_count > 
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT 
    t.CI_ID AS device_id,
    COUNT(e.event_id) AS warning_alarm_count
FROM 
    t_bz_config_ci_ne_root t
    INNER JOIN event_sdn e ON t.NE_ID = e.ip_ddress
WHERE 
    e.time_created >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    AND e.perceived_severity = 'warning'
GROUP BY 
    t.CI_ID
HAVI
```

---

## 第 92 题 [medium]

**问题**: 查询所有Syslog event告警，并关联显示对应的客户名称和告警发生时间
**期望表**: `event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ev.EVENT_TYPE_NAME = 'Syslog event' ORDER BY ev.EVENT_TIME DESC
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT eh.EVENT_NAME, eh.CUSTOMER_NAME, eh.EVENT_TIME
FROM event_history eh
WHERE eh.EVENT_TYPE_NAME = 'Syslog'
ORDER BY eh.EVENT_TIME;
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_NAME,
    eh.EVENT_TYPE_NAME,
    eh.EVENT_STATUS_NAME,
    eh.EVENT_TIME,
    eh.CUSTOMER_NAME,
    eh.SEVERITY_NAME,
    eh.NE_NAME,
    eh.ROOT_NE_NAME,
    eh.SYSTEM_NAME,
    eh.EVENT_DESC
FROM 
    event_history eh
WHERE 
    eh.EVENT_TYPE_NAME = 'Syslog' 
```

---

## 第 93 题 [medium]

**问题**: 查询设备test-router-02的最后一次告警记录详情
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TYPE_NAME, ev.SEVERITY, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'test-router-02' ORDER BY ev.EVENT_TIME DESC LIMIT 1
```

**Qwen2.5-32B** ❌ 用错表:event_sdn
```sql
SELECT es.*
FROM event_sdn es
JOIN t_bz_config_ci_ne_root ci ON es.ip_ddress = ci.NE_IP
WHERE ci.HOST_NAME = 'test-router-02'
ORDER BY es.time_created DESC
LIMIT 1;
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT e.*
FROM event_sdn e
JOIN t_bz_config_ci_ne_root n ON e.ip_ddress = n.NE_IP
WHERE n.HOST_NAME = 'test-router-02'
ORDER BY e.time_created DESC
LIMIT 1;
```

---

## 第 94 题 [medium]

**问题**: 统计每个客户名下，当前在线的设备数量与总设备数量的比例
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS total, SUM(CASE WHEN ne.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online FROM t_bz_config_customer cus JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN ci.IS_ONLINE = 1 THEN 1 ELSE 0 END) / COUNT(ci.CI_ID) AS online_ratio,
    COUNT(ci.CI_ID) AS total_devices
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
GROUP BY 
    c.CUSTOMER_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN n.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_device_count,
    COUNT(*) AS total_device_count,
    ROUND(SUM(CASE WHEN n.IS_ONLINE = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS online_ratio
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_ro
```

---

## 第 95 题 [medium]

**问题**: 查询昨天所有状态为活动的告警，并显示对应的设备型号
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_MODEL, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_STATUS = 1 AND DATE(ev.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT e.EVENT_ID, e.EVENT_NAME, e.EVENT_TIME, c.NE_MODEL
FROM event_history e
JOIN t_bz_config_ci_ne_root c ON e.NE_ID = c.NE_ID
WHERE e.EVENT_STATUS = 1 AND DATE(e.EVENT_TIME) = CURDATE() - INTERVAL 1 DAY;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT c.NE_MODEL
FROM t_bz_config_ci_ne_root c
JOIN event_history e ON c.NE_ID = e.NE_ID
WHERE c.IS_ACTIVE = 1
  AND DATE(e.EVENT_TIME) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY));
```

---

## 第 96 题 [medium]

**问题**: 查询设备ngg-rt-01产生的所有次要告警，按发生时间正序排列
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_DESC, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'ngg-rt-01' AND ev.SEVERITY = 3 ORDER BY ev.EVENT_TIME ASC
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT * 
FROM event_yjk_history 
WHERE device LIKE '%ngg-rt-01%' AND priority = '次要' 
ORDER BY trigger_time ASC;
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT e.*
FROM event_sdn e
JOIN t_bz_config_ci_ne_root n ON e.ip_ddress = n.NE_IP
WHERE n.HOST_NAME = 'ngg-rt-01'
  AND e.perceived_severity IN ('minor', 'warning', 'major', 'critical')
ORDER BY e.time_created ASC;
```

---

## 第 97 题 [medium]

**问题**: 统计本月每个客户产生的Ping event告警数量
**期望表**: `t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS ping_event_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.EVENT_TYPE_NAME = 'Ping event' AND YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE()) GROUP BY cus.CUSTOMER
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT CUSTOMER_ID, CUSTOMER_NAME, COUNT(*) AS ping_event_count
FROM event_history
WHERE EVENT_TYPE_NAME = 'Ping event' AND YEAR(EVENT_TIME) = YEAR(CURDATE()) AND MONTH(EVENT_TIME) = MONTH(CURDATE())
GROUP BY CUSTOMER_ID, CUSTOMER_NAME;
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    COUNT(*) AS ping_event_count
FROM 
    event_history eh
WHERE 
    eh.EVENT_TYPE_NAME = 'Ping' 
    AND eh.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND eh.EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GRO
```

---

## 第 98 题 [medium]

**问题**: 查询设备cx-sx-cc002的所有告警恢复记录，包括恢复时间和告警名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.RECOVER_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'cx-sx-cc002' AND ev.RECOVER_TIME IS NOT NULL ORDER BY ev.RECOVER_TIME DESC
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT eh.recover_time, eh.event_name
FROM event_history eh
JOIN t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
WHERE ci.HOST_NAME = 'cx-sx-cc002' AND eh.EVENT_STATUS_NAME = '恢复';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    eh.recover_time,
    eh.EVENT_NAME
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root cnr ON eh.NE_ID = cnr.NE_ID
WHERE 
    cnr.HOST_NAME = 'cx-sx-cc002'
    AND eh.EVENT_STATUS = 2
    AND eh.recover_time IS NOT NULL;
```

---

## 第 99 题 [medium]

**问题**: 查询客户中国电信上海理想名下所有设备的名称和IP地址
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT n.HOST_NAME, n.NE_IP FROM t_bz_config_ci_ne_root n JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID WHERE c.CUSTOMER_NAME = '中国电信上海理想'
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.HOST_NAME, ci.NE_IP 
FROM t_bz_config_ci_ne_root ci 
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID 
WHERE c.CUSTOMER_NAME = '中国电信上海理想';
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT n.HOST_NAME AS 设备名称, n.NE_IP AS IP地址
FROM t_bz_config_ci_ne_root n
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '中国电信上海理想' AND n.IS_DELETED = 0;
```

---

## 第 100 题 [medium]

**问题**: 统计每个客户拥有的在线设备数量，并列出客户名称和数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(n.CI_ID) AS online_device_count FROM t_bz_config_customer c LEFT JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID AND n.IS_ONLINE = 1 GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(b.CI_ID) AS online_device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root b ON c.CUSTOMER_ID = b.CUSTOMER_ID
WHERE b.IS_ONLINE = 1
GROUP BY c.CUSTOMER_NAME;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.CI_ID) AS online_device_count
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root e ON c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    e.IS_ONLINE = 1 
    AND e.IS_ACTIVE = 1 
    AND e.IS_DELETED = 0
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME;
```

---

## 第 101 题 [hard]

**问题**: 找出最近30天内发生过严重告警，并且设备型号为特定型号的所有设备，同时显示其所属客户名称和告警发生次数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.NE_MODEL, COUNT(e.EVENT_ID) AS alarm_count FROM t_bz_config_ci_ne_root n INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.SEVERITY = 1 AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    ci.HOST_NAME AS DEVICE_NAME,
    COUNT(e.EVENT_ID) AS ALARM_COUNT
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
JOIN 
    event_history e ON ci.NE_ID = e.NE_ID
WHERE 
    ci.NE_MODEL = '特定型号'
    AND e.SEVERITY
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    n.HOST_NAME AS device_name,
    n.NE_MODEL,
    COUNT(e.EVENT_ID) AS alarm_count
FROM 
    event_history e
    INNER JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
    INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TIME >= D
```

---

## 第 102 题 [hard]

**问题**: 统计本月每个客户产生的每种告警类型的数量，即使某些客户本月没有告警也要显示出来
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, e.EVENT_TYPE_NAME, COUNT(e.EVENT_ID) AS type_count FROM t_bz_config_customer c LEFT JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND YEAR(e.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(e.EVENT_TIME) = MONTH(CURDATE()) LEFT JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_I
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    e.EVENT_TYPE_NAME,
    COUNT(e.EVENT_ID) AS ALARM_COUNT
FROM 
    t_bz_config_customer c
LEFT JOIN 
    event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND YEAR(e.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(e.EVENT_TIME) = MONTH(CURDATE())
GROUP BY 
 
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COALESCE(e.ALARM_TYPE, '无告警') AS ALARM_TYPE,
    COALESCE(COUNT(e.EVENT_ID), 0) AS ALARM_COUNT
FROM 
    t_bz_config_customer c
CROSS JOIN (
    SELECT DISTINCT ALARM_TYPE 
    FROM event_history 
    WHERE EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-
```

---

## 第 103 题 [hard]

**问题**: 查询上个月告警总数最多的前3个客户，并列出这些客户下所有在线设备的名称和IP地址
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.NE_IP, COUNT(e.EVENT_ID) AS total_alarms FROM t_bz_config_customer c INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND YEAR(e.EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(e.EVENT_TIME) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, ci.HOST_NAME, ci.NE_IP
FROM (
    SELECT CUSTOMER_ID, COUNT(*) AS alarm_count
    FROM event_history
    WHERE EVENT_TIME >= DATE_FORMAT(CURDATE() - INTERVAL DAYOFMONTH(CURDATE()) DAY, '%Y-%m-01')
      AND EVENT_TIME < DATE_FORMAT(CURDATE() - INTERVAL DAYOFMONTH(CURDATE()) D
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    ne.HOST_NAME,
    ne.NE_IP
FROM t_bz_config_customer c
INNER JOIN t_bz_config_ci_ne_root ne ON c.CUSTOMER_ID = ne.CUSTOMER_ID
INNER JOIN (
    SELECT 
        CUSTOMER_ID,
        COUNT(*) AS alarm_count
    FROM event_history
    WHERE EVENT_TIME >= DATE_FORMAT(DATE
```

---

## 第 104 题 [hard]

**问题**: 查询昨天发生告警且告警状态为已恢复的设备，需要显示设备名、客户名、告警类型和告警恢复时间
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT n.HOST_NAME, c.CUSTOMER_NAME, e.EVENT_TYPE_NAME, e.RECOVER_TIME FROM t_bz_config_ci_ne_root n INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.EVENT_STATUS = 2 AND DATE(e.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    ci.HOST_NAME AS 设备名,
    cust.CUSTOMER_NAME AS 客户名,
    eh.EVENT_TYPE_NAME AS 告警类型,
    eh.RECOVER_TIME AS 告警恢复时间
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
JOIN 
    t_bz_config_customer cust ON eh.CUSTOMER_ID = cust.CUSTOMER_ID
WHERE 
    DATE
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.NE_NAME AS 设备名,
    cu.CUSTOMER_NAME AS 客户名,
    e.EVENT_TYPE_NAME AS 告警类型,
    e.RECOVER_TIME AS 告警恢复时间
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root c ON e.NE_ID = c.NE_ID
JOIN 
    t_bz_config_customer cu ON e.CUSTOMER_ID = cu.CUSTOMER_ID
WHERE 
    e.EVENT_STATUS = 2 

```

---

## 第 105 题 [hard]

**问题**: 统计每个客户在最近7天内，每种告警级别的发生次数，并只显示告警总次数大于5次的客户
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, e.SEVERITY, COUNT(e.EVENT_ID) AS severity_count FROM t_bz_config_customer c INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) INNER JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID GROUP BY c.CUSTOMER_NAME, e
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_ID, 
    c.CUSTOMER_NAME, 
    e.priority AS alarm_level, 
    COUNT(e.id) AS alarm_count
FROM 
    t_bz_config_customer c
JOIN 
    event_yjk_history e ON c.CUSTOMER_NO = e.customer_no
WHERE 
    e.trigger_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    c.CUSTOMER_ID, 

```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_NAME,
    e.priority AS alarm_level,
    COUNT(*) AS alarm_count
FROM 
    t_bz_config_customer c
    INNER JOIN event_yjk_history e ON c.CUSTOMER_NO = e.customer_no
WHERE 
    e.trigger_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    c.CUSTOMER_NAME, e.priority
HAVING 

```

---

## 第 106 题 [hard]

**问题**: 找出客户名为中国电信上海理想或南京研发中心，且设备名为cx-sx-cc002或v6-dcs21的所有历史告警记录，按告警发生时间倒序排列
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, e.EVENT_NAME, e.EVENT_TYPE_NAME, e.EVENT_TIME, e.SEVERITY FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE c.CUSTOMER_NAME IN ('中国电信上海理想', '南京研发中心') AND n.HOST_N
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT * 
FROM event_history 
WHERE CUSTOMER_NAME IN ('中国电信上海理想', '南京研发中心') 
  AND ROOT_NE_NAME IN ('cx-sx-cc002', 'v6-dcs21') 
ORDER BY EVENT_TIME DESC;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT e.*
FROM event_history e
JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE c.CUSTOMER_NAME IN ('中国电信上海理想', '南京研发中心')
  AND n.HOST_NAME IN ('cx-sx-cc002', 'v6-dcs21')
  AND e.EVENT_TIME IS NOT NULL
ORDER BY e.EVENT_TIME DESC;
```

---

## 第 107 题 [hard]

**问题**: 查询本月告警数量最多的设备，并显示该设备所属的客户信息以及设备的具体型号
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.NE_MODEL, COUNT(e.EVENT_ID) AS month_alarm_count FROM t_bz_config_ci_ne_root n INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND YEAR(e.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(e.EVENT_TIME) = 
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_NAME, 
    c.CUSTOMER_DESC, 
    ci.NE_MODEL, 
    COUNT(e.EVENT_ID) AS alarm_count
FROM 
    t_bz_incident_event_record e
JOIN 
    t_bz_config_ci_ne_root ci ON e.NE_ID = ci.NE_ID
JOIN 
    t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    DATE_FORMAT(e.EVEN
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT 
    c.CUSTOMER_NAME AS 客户名称,
    c.CUSTOMER_DESC AS 客户描述,
    c.CUSTOMER_NO AS 客户编号,
    ne.NE_MODEL AS 设备型号,
    COUNT(e.event_id) AS 本月告警数量
FROM 
    event_sdn e
    INNER JOIN t_bz_config_ci_ne_root ne ON e.ip_ddress = ne.NE_IP
    INNER JOIN t_bz_config_customer c ON ne.CUSTOMER_ID = c.C
```

---

## 第 108 题 [hard]

**问题**: 统计过去三个月每个客户下，产生过告警的设备数量与总设备数量的比例
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT n.CI_ID) AS total_devices, COUNT(DISTINCT CASE WHEN e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) THEN n.NE_ID END) AS alarmed_devices, ROUND(COUNT(DISTINCT CASE WHEN e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) THEN n.NE_ID END) / COUNT(DISTIN
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(DISTINCT CASE WHEN e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) THEN ci.CI_ID END) AS ALERTED_DEVICE_COUNT,
    COUNT(DISTINCT ci.CI_ID) AS TOTAL_DEVICE_COUNT,
    (COUNT(DISTINCT CASE WHEN e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVA
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(DISTINCT CASE WHEN e.time_created >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) THEN e.ip_ddress END) AS alarm_devices_count,
    COUNT(DISTINCT n.CI_ID) AS total_devices_count,
    ROUND(
        COUNT(DISTINCT CASE WHEN e.time_created >= DATE_SU
```

---

## 第 109 题 [hard]

**问题**: 查询最近30天内，告警级别为次要或警告，且尚未恢复（状态为活动）的告警，关联显示设备及其客户信息
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, e.EVENT_NAME, e.EVENT_TYPE_NAME, e.EVENT_TIME, e.EVENT_DESC FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.SEVERITY IN (3, 4) AND e.EVENT_STATUS = 1 AND e.EV
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_NAME,
    eh.SEVERITY_NAME AS alarm_level,
    eh.EVENT_TIME,
    ci.HOST_NAME AS device_name,
    cc.CUSTOMER_NAME,
    cc.CUSTOMER_NO
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
JOIN 
    t_bz_config_customer cc ON ci.
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    e.EVENT_ID,
    e.EVENT_NAME,
    e.EVENT_TIME,
    e.SEVERITY_NAME AS alarm_level,
    e.EVENT_STATUS_NAME AS status,
    e.NE_NAME AS device_name,
    e.ADDRESS AS device_ip,
    c.CUSTOMER_NAME AS customer_name,
    c.CUSTOMER_NO AS customer_no,
    c.CUSTOMER_DESC AS customer_desc,
 
```

---

## 第 110 题 [hard]

**问题**: 找出上个月平均每天告警次数超过3次的客户，并列出这些客户下所有设备的名称
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, COUNT(e.EVENT_ID)/DAY(LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))) AS avg_daily_alarms FROM t_bz_config_customer c INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND YEAR(e.EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(e.EVE
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, ci.HOST_NAME
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
WHERE c.CUSTOMER_ID IN (
    SELECT e.CUSTOMER_ID
    FROM event_history e
    WHERE e.EVENT_TIME >= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
      AND e.EVE
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    n.HOST_NAME
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
    INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    e.EVENT_TIME >= DATE_SUB(DATE_SUB(CURDATE(), INTERVA
```

---

## 第 111 题 [hard]

**问题**: 查询设备名为ciscoA或ngg-rt-01的所有历史告警，并按客户分组统计每个客户的告警总数和最近一次告警时间
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(e.EVENT_ID) AS total_alarms, MAX(e.EVENT_TIME) AS last_alarm_time FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE n.HOST_NAME IN ('ciscoA', 'ngg-rt-01') GROUP BY c.CUS
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.id) AS alarm_count,
    MAX(e.trigger_time) AS latest_alarm_time
FROM 
    t_bz_config_ci_ne_root n
JOIN 
    event_yjk_history e ON e.device LIKE CONCAT('%', n.HOST_NAME, '%')
JOIN 
    t_bz_config_customer c ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE 
    n.HOS
```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.event_id) AS alarm_count,
    MAX(e.time_created) AS last_alarm_time
FROM 
    event_yjk_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.device = n.HOST_NAME OR e.device = n.NE_IP
JOIN 
    t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    
```

---

## 第 112 题 [hard]

**问题**: 找出最近7天内，同时产生过Ping event和Threshold event两种告警类型的设备，并显示其客户信息
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT c.CUSTOMER_NAME, n.HOST_NAME FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND e.EVENT_TYPE_NAME = 'Ping event' AND n.NE_ID IN 
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT DISTINCT eh.CUSTOMER_ID, eh.CUSTOMER_NAME
FROM event_history eh
WHERE eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
AND eh.EVENT_TYPE_NAME IN ('Ping event', 'Threshold event')
GROUP BY eh.CUSTOMER_ID, eh.CUSTOMER_NAME
HAVING COUNT(DISTINCT eh.EVENT_TYPE_NAME) = 2;
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
SELECT DISTINCT eh.CUSTOMER_ID, eh.CUSTOMER_NAME
FROM event_history eh
WHERE eh.EVENT_TYPE_NAME IN ('Ping event', 'Threshold event')
  AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND EXISTS (
    SELECT 1
    FROM event_history eh2
    WHERE eh2.CUSTOMER_ID = eh.CUSTOMER_ID
      AND eh2.
```

---

## 第 113 题 [hard]

**问题**: 统计每个客户在昨天发生的不同告警级别的数量，并以客户名称和告警级别作为行，数量作为列进行展示
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.SEVERITY = 1 THEN 1 ELSE 0 END) AS '严重', SUM(CASE WHEN e.SEVERITY = 2 THEN 1 ELSE 0 END) AS '主要', SUM(CASE WHEN e.SEVERITY = 3 THEN 1 ELSE 0 END) AS '次要', SUM(CASE WHEN e.SEVERITY = 4 THEN 1 ELSE 0 END) AS '警告' FROM t_bz_config_customer c LEFT JOIN event_histo
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    e.SEVERITY_NAME,
    COUNT(DISTINCT e.EVENT_ID) AS ALARM_COUNT
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    DATE(e.EVENT_TIME) = CURDATE() - INTERVAL 1 DAY
GROUP BY 
    c.CUSTOMER_NAME, e.SEVERITY_NAME
ORDER 
```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_NAME,
    e.priority AS alarm_level,
    COUNT(*) AS alarm_count
FROM 
    event_yjk_history e
JOIN 
    t_bz_config_customer c ON e.customer_no = c.CUSTOMER_NO
WHERE 
    DATE(e.trigger_time) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY))
GROUP BY 
    c.CUSTOMER_NAME, e.priority
OR
```

---

## 第 114 题 [hard]

**问题**: 查询所有设备创建时间在一年以内，且在过去三个月内产生过严重或主要告警的设备清单，包含客户名
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.CREATE_TIME, COUNT(e.EVENT_ID) AS recent_alarms FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID AND n.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND e.EVEN
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT ci.CI_ID, ci.HOST_NAME, cust.CUSTOMER_NAME
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer cust ON ci.CUSTOMER_ID = cust.CUSTOMER_ID
JOIN event_history eh ON ci.CI_ID = eh.NE_ID
WHERE ci.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTE
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT DISTINCT c.CUSTOMER_NAME, n.HOST_NAME, n.CREATE_TIME
FROM t_bz_config_ci_ne_root n
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
JOIN event_history e ON n.NE_ID = e.NE_ID
WHERE n.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
  AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTER
```

---

## 第 115 题 [hard]

**问题**: 找出本月告警恢复平均时间最长的前5个设备，并显示其所属客户和平均恢复时间（分钟）
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, AVG(TIMESTAMPDIFF(MINUTE, e.EVENT_TIME, e.RECOVER_TIME)) AS avg_recover_minutes FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE YEAR(e.EVENT_TIME) = YEAR(CURDAT
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    ci.HOST_NAME AS DEVICE_NAME,
    AVG(TIMESTAMPDIFF(MINUTE, e.EVENT_TIME, e.RECOVER_TIME)) AS AVG_RECOVERY_TIME_MINUTES
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root ci ON e.NE_ID = ci.NE_ID
JOIN 
    t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME AS 客户,
    n.HOST_NAME AS 设备,
    AVG(TIMESTAMPDIFF(MINUTE, e.EVENT_TIME, e.RECOVER_TIME)) AS 平均恢复时间(分钟)
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_
```

---

## 第 116 题 [hard]

**问题**: 查询客户测试客户名下，所有设备在最近30天内的告警总数，以及这些设备中当前在线的数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT COUNT(DISTINCT n.CI_ID) AS total_devices, SUM(CASE WHEN n.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_devices, COUNT(e.EVENT_ID) AS total_alarms FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID LEFT JOIN event_history e ON n.NE_ID = e.NE_ID AND e
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    COUNT(DISTINCT e.EVENT_ID) AS total_alarm_count,
    SUM(CASE WHEN ci.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_device_count
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
LEFT JOIN 
    event_history e ON ci.NE_ID = e.NE_ID AND e.
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.EVENT_ID) AS alarm_count_last_30_days,
    SUM(CASE WHEN d.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_device_count
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
    INNER JOIN event_history e ON d.NE
```

---

## 第 117 题 [hard]

**问题**: 查询设备型号相同的设备集合，并统计每个型号在最近7天内产生的告警总数，同时列出拥有该型号设备的一个示例客户
**期望表**: `t_bz_config_ci_ne_root, event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT n.NE_MODEL, COUNT(e.EVENT_ID) AS week_alarms, MAX(c.CUSTOMER_NAME) AS example_customer FROM t_bz_config_ci_ne_root n INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID WHERE
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    ci.NE_MODEL AS device_model,
    COUNT(e.EVENT_ID) AS alarm_count,
    c.CUSTOMER_NAME AS example_customer
FROM 
    t_bz_config_ci_ne_root ci
JOIN 
    event_history e ON ci.CI_ID = e.NE_ID
JOIN 
    t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TIME >= DAT
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
SELECT 
    c.NE_MODEL AS device_model,
    COUNT(e.EVENT_ID) AS alarm_count_last_7_days,
    MIN(c.CUSTOMER_ID) AS example_customer_id
FROM 
    t_bz_config_ci_ne_root c
JOIN 
    event_history e ON c.NE_ID = e.NE_ID
WHERE 
    c.IS_ACTIVE = 1 
    AND c.IS_ONLINE = 1 
    AND e.EVENT_TIME >= DATE_
```

---

## 第 118 题 [hard]

**问题**: 统计本月每个客户下，处于活动状态的告警数量与已恢复告警数量的比值
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.EVENT_STATUS = 1 THEN 1 ELSE 0 END) AS active_alarms, SUM(CASE WHEN e.EVENT_STATUS = 2 THEN 1 ELSE 0 END) AS recovered_alarms, CASE WHEN SUM(CASE WHEN e.EVENT_STATUS = 2 THEN 1 ELSE 0 END) = 0 THEN NULL ELSE ROUND(SUM(CASE WHEN e.EVENT_STATUS = 1 THEN 1 ELSE 0
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN eh.EVENT_STATUS = 1 AND YEAR(eh.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(eh.EVENT_TIME) = MONTH(CURDATE()) THEN 1 ELSE 0 END) AS active_alarm_count,
    SUM(CASE WHEN eh.EVENT_STATUS = 2 AND YEAR(eh.RECOVER_TIME) = YEAR(CURDATE()) AND MONTH(eh.RECOVER_TI
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN e.EVENT_STATUS = 1 AND e.RECOVER_TIME IS NULL THEN 1 ELSE 0 END) AS active_alert_count,
    SUM(CASE WHEN e.EVENT_STATUS = 2 AND e.RECOVER_TIME IS NOT NULL THEN 1 ELSE 0 END) AS recovered_alert_count,
    CASE 
        WHEN SUM(CASE WHEN e.EVENT_STATUS 
```

---

## 第 119 题 [hard]

**问题**: 找出上个月告警频率（告警总数/设备数）最高的客户，并列出该客户下所有产生过告警的设备名及告警次数
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, COUNT(e.EVENT_ID) AS device_alarm_count FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND YEAR(e.EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT c.CUSTOMER_NAME, ci.HOST_NAME, COUNT(e.EVENT_ID) AS ALARM_COUNT
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
JOIN t_bz_incident_event_record e ON ci.NE_ID = e.NE_ID
WHERE e.EVENT_TIME >= DATE_FORMAT(CURDATE() - INTERVAL DAYOFMONTH(CURDATE()) DAY
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
WITH alarm_stats AS (
    SELECT 
        c.CUSTOMER_ID,
        c.CUSTOMER_NAME,
        COUNT(e.event_id) AS total_alarms,
        COUNT(DISTINCT n.CI_ID) AS device_count
    FROM event_sdn e
    INNER JOIN t_bz_config_ci_ne_root n ON e.ip_ddress = n.NE_IP
    INNER JOIN t_bz_config_customer c ON 
```

---

## 第 120 题 [hard]

**问题**: 查询最近30天内，每天产生的告警总数，并关联显示当天产生告警最多的那个客户名称
**期望表**: `event_history, t_bz_config_customer`

**DeepSeek参考SQL**:
```sql
SELECT DATE(e.EVENT_TIME) AS alarm_date, COUNT(e.EVENT_ID) AS daily_total, (SELECT c2.CUSTOMER_NAME FROM t_bz_config_customer c2 INNER JOIN event_history e2 ON c2.CUSTOMER_ID = e2.CUSTOMER_ID AND DATE(e2.EVENT_TIME) = DATE(e.EVENT_TIME) GROUP BY c2.CUSTOMER_NAME ORDER BY COUNT(e2.EVENT_ID) DESC LIMI
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT 
    DATE(event_time) AS alert_date,
    COUNT(*) AS total_alerts,
    MAX(customer_alert_count.customer_name) AS customer_with_most_alerts
FROM 
    event_history
JOIN (
    SELECT 
        DATE(event_time) AS alert_date,
        customer_name,
        COUNT(*) AS alert_count
    FROM 
     
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    DATE(e.EVENT_TIME) AS alarm_date,
    COUNT(e.EVENT_ID) AS total_alerts,
    (SELECT c.CUSTOMER_NAME 
     FROM t_bz_config_customer c
     JOIN event_history e2 ON c.CUSTOMER_ID = e2.CUSTOMER_ID
     WHERE DATE(e2.EVENT_TIME) = DATE(e.EVENT_TIME)
     GROUP BY c.CUSTOMER_NAME
     ORDER
```

---

## 第 121 题 [hard]

**问题**: 查询每个客户在过去30天内至少发生过一次严重告警（SEVERITY='CRITICAL'）的在线设备数量，并按设备数量降序排列
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS online_critical_devices FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.SEVERITY = 'CRITICAL' AND e.EV
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT ci.CI_ID) AS ONLINE_DEVICE_COUNT
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
JOIN event_history e ON ci.NE_ID = e.NE_ID
WHERE ci.IS_ONLINE = 1
  AND e.SEVERITY_NAME = 'CRITICAL'
  AND e.EVENT_TIME >= DATE_SUB(CUR
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_ID,
    COUNT(DISTINCT d.CI_ID) AS online_device_count
FROM 
    t_bz_config_ci_ne_root d
    INNER JOIN t_bz_config_customer c ON d.CUSTOMER_ID = c.CUSTOMER_ID
    INNER JOIN event_history e ON d.NE_ID = e.NE_ID AND d.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    d.IS_ONLINE = 1
   
```

---

## 第 122 题 [hard]

**问题**: 找出客户名为'测试客户'或'ngg-319009'的设备中，最近7天内发生'Ping event'告警次数最多的前5台设备（显示设备名、客户名、告警次数）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT r.HOST_NAME, c.CUSTOMER_NAME, COUNT(*) AS ping_event_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE c.CUSTOMER_NAME IN ('测试客户', 'ngg-319009') AND e.EVENT_TYPE_NA
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT ROOT_NE_NAME AS 设备名, CUSTOMER_NAME AS 客户名, COUNT(*) AS 告警次数
FROM event_history
WHERE CUSTOMER_NAME IN ('测试客户', 'ngg-319009')
  AND EVENT_NAME = 'Ping event'
  AND EVENT_TIME >= NOW() - INTERVAL 7 DAY
GROUP BY ROOT_NE_NAME, CUSTOMER_NAME
ORDER BY 告警次数 DESC
LIMIT 5;
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.ROOT_NE_NAME AS 设备名,
    eh.CUSTOMER_NAME AS 客户名,
    COUNT(*) AS 告警次数
FROM 
    event_history eh
WHERE 
    eh.CUSTOMER_NAME IN ('测试客户', 'ngg-319009')
    AND eh.EVENT_TYPE_NAME = 'Ping event'
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    eh.ROOT_NE_NAME, eh.
```

---

## 第 123 题 [hard]

**问题**: 查询每个客户在线设备的'Ping event'和'Trap event'告警总数，并计算两种告警的比例（Ping/Trap），仅显示比例大于2的客户
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_count, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_count, ROUND(SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN e.EVENT_TYPE_NAME =
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT 
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS Ping_Count,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS Trap_Count,
    (SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) / SUM(CASE WHEN eh.EVENT_T
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_count,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_count,
    (SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) / NULL
```

---

## 第 124 题 [hard]

**问题**: 找出设备名为'cx-sx-cc002'或'tdk-shanghai-b'的设备，在最近30天内每小时的平均告警数量，并按小时和客户名分组
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, HOUR(e.EVENT_TIME) AS hour_of_day, COUNT(*) / COUNT(DISTINCT DATE(e.EVENT_TIME)) AS avg_alerts_per_hour FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT 
    DATE_FORMAT(e.EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour,
    c.CUSTOMER_NAME,
    AVG(COUNT(e.EVENT_ID)) OVER (PARTITION BY DATE_FORMAT(e.EVENT_TIME, '%Y-%m-%d %H:00:00'), c.CUSTOMER_NAME) AS avg_alarm_count
FROM 
    t_bz_incident_event_record e
JOIN 
    t_bz_config_ci_ne_root d ON e.NE
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT 
    DATE_FORMAT(e.time_created, '%Y-%m-%d %H:00:00') AS hour,
    c.CUSTOMER_NAME,
    AVG(CASE WHEN ne.HOST_NAME IN ('cx-sx-cc002', 'tdk-shanghai-b') THEN 1 ELSE 0 END) AS avg_alarm_count
FROM 
    event_sdn e
    INNER JOIN t_bz_config_ci_ne_root ne ON e.ip_ddress = ne.NE_IP
    INNER JOIN
```

---

## 第 125 题 [hard]

**问题**: 查询每个客户严重告警（SEVERITY='CRITICAL'）最多的在线设备，显示客户名、设备名、告警次数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH ranked_devices AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(*) AS critical_count, ROW_NUMBER() OVER (PARTITION BY c.CUSTOMER_ID ORDER BY COUNT(*) DESC) AS rn FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AN
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME, 
    e.ROOT_NE_NAME AS DEVICE_NAME, 
    COUNT(e.EVENT_ID) AS CRITICAL_ALARM_COUNT
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
JOIN 
    event_history e ON d.NE_ID = e.NE_ID
WHERE 
    e.SEVERITY_NAME = 'CRITICAL' 
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME AS 客户名,
    ne.HOST_NAME AS 设备名,
    COUNT(e.EVENT_ID) AS 告警次数
FROM 
    event_history e
    INNER JOIN t_bz_config_ci_ne_root ne ON e.NE_ID = ne.NE_ID
    INNER JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.SEVERITY_NAME = 'CRITICAL'
    AND n
```

---

## 第 126 题 [hard]

**问题**: 查询每个客户在线设备中，'Ping event'告警持续时间最长的设备（假设连续告警为持续时间），显示客户名、设备名、最大持续天数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH ping_events AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, e.EVENT_TIME, LAG(e.EVENT_TIME) OVER (PARTITION BY r.NE_ID ORDER BY e.EVENT_TIME) AS prev_time FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.CUSTOMER_NAME AS 客户名,
    eh.ROOT_NE_NAME AS 设备名,
    MAX(TIMESTAMPDIFF(DAY, eh.EVENT_TIME, eh.RECOVER_TIME)) AS 最大持续天数
FROM 
    event_history eh
WHERE 
    eh.EVENT_NAME = 'Ping event'
    AND eh.IS_ONLINE = 1
GROUP BY 
    eh.CUSTOMER_NAME, eh.ROOT_NE_NAME
ORDER BY 
    最大持续天数 DESC
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
WITH ping_events AS (
    SELECT 
        eh.CUSTOMER_ID,
        eh.CUSTOMER_NAME,
        eh.ROOT_NE_NAME AS DEVICE_NAME,
        eh.EVENT_TIME AS START_TIME,
        eh.ACK_TIME AS END_TIME,
        CASE 
            WHEN eh.ACK_TIME IS NOT NULL THEN TIMESTAMPDIFF(DAY, eh.EVENT_TIME, eh.ACK_TIME)
```

---

## 第 127 题 [hard]

**问题**: 找出每个客户在过去24小时内告警频率最高的设备（告警次数/在线时长），假设在线时长从最早告警时间计算
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(*) AS alert_count, TIMESTAMPDIFF(HOUR, MIN(e.EVENT_TIME), MAX(e.EVENT_TIME)) AS hours_span, ROUND(COUNT(*) / NULLIF(TIMESTAMPDIFF(HOUR, MIN(e.EVENT_TIME), MAX(e.EVENT_TIME)), 0), 2) AS alerts_per_hour FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer 
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    e.NE_ID,
    ci.HOST_NAME AS DEVICE_NAME,
    COUNT(e.EVENT_ID) / TIMESTAMPDIFF(SECOND, MIN(e.EVENT_TIME), NOW()) AS ALERT_FREQUENCY
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
JOIN 
    t_
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
WITH alarm_data AS (
    SELECT 
        e.CUSTOMER_ID,
        e.NE_ID,
        e.time_created,
        e.perceived_severity,
        e.native_probable_cause,
        e.ip_ddress,
        e.md_name,
        e.product_type,
        e.alarm_type_qualifier,
        e.is-acked,
        e.repair_action,
```

---

## 第 128 题 [hard]

**问题**: 查询每个客户不同类型告警（EVENT_TYPE_NAME）的分布比例，并找出'Ping event'占比超过30%的客户
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH event_totals AS (SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME, e.EVENT_TYPE_NAME, COUNT(*) AS type_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID GROUP BY c.CUSTOMER_ID, c.CUST
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT eh.CUSTOMER_NAME, 
       eh.EVENT_TYPE_NAME, 
       COUNT(eh.EVENT_ID) AS EVENT_COUNT, 
       (COUNT(eh.EVENT_ID) / SUM(COUNT(eh.EVENT_ID)) OVER (PARTITION BY eh.CUSTOMER_ID)) * 100 AS EVENT_PERCENTAGE
FROM event_history eh
GROUP BY eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh.EVENT_TYPE_NAME
HAVI
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
WITH customer_event_type_counts AS (
    SELECT 
        eh.CUSTOMER_ID,
        eh.CUSTOMER_NAME,
        eh.EVENT_TYPE_NAME,
        COUNT(*) AS event_count
    FROM event_history eh
    WHERE eh.EVENT_TYPE_NAME = 'Ping event'
    GROUP BY eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh.EVENT_TYPE_NAME
),
to
```

---

## 第 129 题 [hard]

**问题**: 找出每个客户中，同时存在'Ping event'和'Trap event'告警的在线设备数量
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS devices_with_both_events FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.EVENT_TYPE_NAME IN ('Ping eve
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT eh.CUSTOMER_ID, eh.CUSTOMER_NAME, COUNT(DISTINCT eh.ROOT_NE_ID) AS online_device_count
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID AND ne.IS_ONLINE = 1
WHERE eh.EVENT_NAME IN ('Ping event', 'Trap event')
GROUP BY eh.CUSTOMER_ID, eh.CUSTOMER_NAME
HAVING COU
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
SELECT 
    e.CUSTOMER_ID,
    COUNT(DISTINCT e.ROOT_NE_ID) AS online_device_count
FROM 
    event_history e
INNER JOIN 
    t_bz_config_ci_ne_root n ON e.ROOT_NE_ID = n.CI_ID
WHERE 
    e.EVENT_TYPE_NAME IN ('Ping event', 'Trap event')
    AND n.IS_ONLINE = 1
    AND e.CUSTOMER_ID IN (
        SELE
```

---

## 第 130 题 [hard]

**问题**: 查询每个客户在过去7天内，每小时告警数量的标准差，找出告警最不稳定的客户（标准差最大）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH hourly_counts AS (SELECT c.CUSTOMER_NAME, HOUR(e.EVENT_TIME) AS hour, COUNT(*) AS alert_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TIME >= DATE_SUB(NOW
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_ID, 
    c.CUSTOMER_NAME, 
    STDDEV(alarm_count) AS std_dev_alarm_count
FROM 
    t_bz_config_customer c
JOIN 
    (SELECT 
         e.CUSTOMER_ID, 
         DATE_FORMAT(e.EVENT_TIME, '%Y-%m-%d %H') AS hour, 
         COUNT(*) AS alarm_count
     FROM 
         event_history
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    STDDEV_POP(hourly_alarm_count) AS std_dev_alarm_count
FROM 
    t_bz_config_customer c
    INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID
    INNER JOIN (
        SELECT 
            CUSTOMER_ID,
            DATE_FORMAT(EVENT_TIME, '%Y-%m-%d %H:00:00') A
```

---

## 第 131 题 [hard]

**问题**: 找出每个客户中，告警严重程度（SEVERITY）从低到高升级的设备（例如从WARNING升级到CRITICAL），显示客户名、设备名、升级次数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH severity_ranks AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, e.EVENT_TIME, e.SEVERITY, CASE e.SEVERITY WHEN 'WARNING' THEN 1 WHEN 'MINOR' THEN 2 WHEN 'MAJOR' THEN 3 WHEN 'CRITICAL' THEN 4 END AS severity_rank, LAG(CASE e.SEVERITY WHEN 'WARNING' THEN 1 WHEN 'MINOR' THEN 2 WHEN 'MAJOR' THEN 3 WHEN 'CR
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    e.ROOT_NE_NAME AS DEVICE_NAME,
    COUNT(*) AS UPGRADE_COUNT
FROM 
    t_bz_config_customer c
JOIN 
    event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    e.SEVERITY_NAME IN ('WARNING', 'CRITICAL')
GROUP BY 
    c.CUSTOMER_NAME, e.ROOT_NE_NAME
HAVING 
    MA
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
WITH alarm_rank AS (
    SELECT 
        e.CUSTOMER_ID,
        e.NE_ID,
        e.NE_NAME,
        e.SEVERITY_NAME,
        e.EVENT_TIME,
        ROW_NUMBER() OVER (PARTITION BY e.CUSTOMER_ID, e.NE_ID ORDER BY e.EVENT_TIME) AS rn
    FROM event_history e
    WHERE e.SEVERITY_NAME IN ('WARNING', 'CR
```

---

## 第 132 题 [hard]

**问题**: 查询每个客户在线设备的平均告警间隔时间（分钟），仅显示间隔时间小于30分钟的客户
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH time_intervals AS (SELECT c.CUSTOMER_NAME, r.NE_ID, TIMESTAMPDIFF(MINUTE, LAG(e.EVENT_TIME) OVER (PARTITION BY r.NE_ID ORDER BY e.EVENT_TIME), e.EVENT_TIME) AS interval_minutes FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.N
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_ID, 
    c.CUSTOMER_NAME, 
    AVG(TIMESTAMPDIFF(MINUTE, e1.EVENT_TIME, e2.EVENT_TIME)) AS avg_alarm_interval
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
JOIN 
    event_history e1 ON d.NE_ID = e1.NE_ID
JOIN 
    event_h
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    AVG(TIMESTAMPDIFF(MINUTE, e1.EVENT_TIME, e2.EVENT_TIME)) AS avg_alarm_interval_minutes
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
    INNER JOIN event_history e1 ON n.NE_ID = e1.NE_ID AND e1.CUSTOMER_ID =
```

---

## 第 133 题 [hard]

**问题**: 找出每个客户中，最近3天内告警数量呈上升趋势的设备（每天告警数递增）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH daily_device_alerts AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, DATE(e.EVENT_TIME) AS alert_date, COUNT(*) AS daily_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.E
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT c.CUSTOMER_NAME, ci.HOST_NAME, d1.alarm_date, d1.alarm_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
JOIN (
    SELECT NE_ID, DATE(time_created) AS alarm_date, COUNT(*) AS alarm_count
    FROM t_bz_incident_event_record
    WHERE time_creat
```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
WITH alarm_counts AS (
    SELECT 
        c.CUSTOMER_ID,
        ci.CI_ID AS DEVICE_ID,
        DATE(e.EVENT_TIME) AS alarm_date,
        COUNT(*) AS alarm_count
    FROM 
        t_bz_config_customer c
        INNER JOIN t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
        INNER JOI
```

---

## 第 134 题 [hard]

**问题**: 查询每个客户在过去30天内，不同严重程度告警的累计数量，并计算CRITICAL告警占比
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.SEVERITY = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_count, SUM(CASE WHEN e.SEVERITY = 'MAJOR' THEN 1 ELSE 0 END) AS major_count, SUM(CASE WHEN e.SEVERITY = 'MINOR' THEN 1 ELSE 0 END) AS minor_count, SUM(CASE WHEN e.SEVERITY = 'WARNING' THEN 1 ELSE 0 END) AS w
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(CASE WHEN e.SEVERITY_NAME = 'CRITICAL' THEN 1 END) AS CRITICAL_COUNT,
    COUNT(CASE WHEN e.SEVERITY_NAME = 'MAJOR' THEN 1 END) AS MAJOR_COUNT,
    COUNT(CASE WHEN e.SEVERITY_NAME = 'MINOR' THEN 1 END) AS MINOR_COUNT,
    COUNT(CASE WHEN e.SEVERITY_NAME = 'WARN
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN e.SEVERITY_NAME = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_count,
    SUM(CASE WHEN e.SEVERITY_NAME = 'MAJOR' THEN 1 ELSE 0 END) AS major_count,
    SUM(CASE WHEN e.SEVERITY_NAME = 'MINOR' THEN 1 ELSE 0 END) AS minor_count,
    SUM(CASE WHEN e.SEVERITY
```

---

## 第 135 题 [hard]

**问题**: 找出每个客户中，'Ping event'告警发生时间最密集的3小时时段（滑动窗口）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH hourly_ping_counts AS (SELECT c.CUSTOMER_NAME, HOUR(e.EVENT_TIME) AS hour, COUNT(*) AS ping_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TYPE_NAME = 'Pin
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    DATE_FORMAT(eh.EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour_start,
    COUNT(*) AS event_count
FROM 
    event_history eh
WHERE 
    eh.EVENT_NAME = 'Ping event'
GROUP BY 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    DATE_FORMAT(eh.EVENT_TIME, '%Y-%
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
WITH ping_events AS (
    SELECT 
        CUSTOMER_ID,
        EVENT_TIME,
        -- 将事件时间转换为小时粒度的起始时间（用于滑动窗口）
        DATE_FORMAT(EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour_start
    FROM event_history
    WHERE EVENT_TYPE_NAME = 'Ping event'
),
hourly_counts AS (
    SELECT 
        CUSTOMER_ID,
  
```

---

## 第 136 题 [hard]

**问题**: 查询每个客户在线设备中，最近一次告警时间与当前时间间隔超过24小时的设备数量
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS idle_devices_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID LEFT JOIN (SELECT NE_ID, CUSTOMER_ID, MAX(EVENT_TIME) AS last_alert FROM event_history GROUP BY NE_ID, CUSTOMER_ID) e ON r.NE_ID = e.NE_ID 
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT c.CUSTOMER_NAME, COUNT(eh.NE_ID) AS DEVICE_COUNT
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN (
    SELECT NE_ID, MAX(EVENT_TIME) AS LAST_ALARM_TIME
    FROM event_history
    GROUP BY NE_ID
) eh ON ci.NE_ID = eh.NE_ID
WHERE ci.IS_ONLI
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_ID,
    COUNT(DISTINCT e.NE_ID) AS device_count
FROM 
    t_bz_config_ci_ne_root e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
JOIN 
    (SELECT 
         NE_ID, 
         MAX(EVENT_TIME) AS last_alarm_time
     FROM 
         event_history
     WHERE 
  
```

---

## 第 137 题 [hard]

**问题**: 找出每个客户中，告警类型数量最多的设备（显示客户名、设备名、告警类型数）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH device_event_types AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(DISTINCT e.EVENT_TYPE_NAME) AS event_type_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID GROUP BY c.CUS
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT c.CUSTOMER_NAME, ci.HOST_NAME, COUNT(DISTINCT e.EVENT_TYPE_NAME) AS ALARM_TYPE_COUNT
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_incident_info e ON ci.CI_ID = e.OBJECT_ID
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
GROUP BY c.CUSTOMER_NAME, ci.HOST_NAME
ORDER BY ALARM_TYPE_COUN
```

**Qwen3 MoE** ✅ 正确
```sql
WITH DeviceAlarmCount AS (
    SELECT 
        c.CUSTOMER_NAME,
        n.NE_NAME AS DEVICE_NAME,
        COUNT(DISTINCT e.EVENT_TYPE_NAME) AS ALARM_TYPE_COUNT
    FROM 
        t_bz_config_ci_ne_root n
    JOIN 
        t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
    JOIN 
        event
```

---

## 第 138 题 [hard]

**问题**: 找出每个客户中，连续两天都有告警的设备数量
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH daily_alerts AS (SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME, r.NE_ID, DATE(e.EVENT_TIME) AS alert_date FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID GROUP BY c.CUSTOMER_ID, c.CUST
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME, COUNT(DISTINCT e.NE_ID) AS DEVICE_COUNT
FROM t_bz_config_customer c
JOIN t_bz_incident_event_record e ON c.CUSTOMER_ID = e.customer_id
WHERE EXISTS (
    SELECT 1
    FROM t_bz_incident_event_record e2
    WHERE e.NE_ID = e2.NE_ID
      AND DATE(e.EVENT_TIME) =
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT 
    c.CUSTOMER_ID,
    COUNT(DISTINCT e.CI_ID) AS continuous_alarm_device_count
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root e ON c.CUSTOMER_ID = e.CUSTOMER_ID
    INNER JOIN (
        SELECT 
            NE_ID,
            DATE(time_created) AS alarm_date
        F
```

---

## 第 139 题 [hard]

**问题**: 查询每个客户在线设备中，告警数量排名前10%的设备（按告警总数）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH device_alert_ranks AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(*) AS total_alerts, PERCENT_RANK() OVER (PARTITION BY c.CUSTOMER_ID ORDER BY COUNT(*) DESC) AS alert_percent_rank FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON 
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT c.CUSTOMER_NAME, ci.HOST_NAME, COUNT(e.EVENT_ID) AS alarm_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root ci ON c.CUSTOMER_ID = ci.CUSTOMER_ID
JOIN t_bz_incident_event_record e ON ci.NE_ID = e.NE_ID
WHERE ci.IS_ONLINE = 1
GROUP BY c.CUSTOMER_NAME, ci.HOST_NAME
HAVING alarm_count
```

**Qwen3 MoE** ❌ 缺表:event_history
```sql
WITH CustomerOnlineDevices AS (
    SELECT 
        c.CUSTOMER_ID,
        c.CUSTOMER_NAME,
        d.CI_ID AS DEVICE_ID,
        d.HOST_NAME AS DEVICE_NAME,
        d.NE_IP AS DEVICE_IP,
        COUNT(e.EVENT_ID) AS ALARM_COUNT
    FROM t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root d
```

---

## 第 140 题 [hard]

**问题**: 找出每个客户中，'Ping event'告警平均响应时间最短的设备（假设响应时间为相邻'Trap event'的时间差）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH ping_trap_pairs AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, e.EVENT_TIME AS ping_time, LEAD(e.EVENT_TIME) OVER (PARTITION BY r.NE_ID ORDER BY e.EVENT_TIME) AS next_trap_time, e.EVENT_TYPE_NAME FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_his
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    AVG(TIMESTAMPDIFF(SECOND, eh.EVENT_TIME, eh.ACK_TIME)) AS AVG_RESPONSE_TIME
FROM 
    event_history eh
WHERE 
    eh.EVENT_NAME = 'Ping event'
    AND eh.IS_ACK = 1
GROUP BY 
    eh.CUSTOMER_ID, eh.CUSTOMER_NAM
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
WITH ping_trap_events AS (
    SELECT 
        eh.CUSTOMER_ID,
        eh.ROOT_NE_NAME AS device_name,
        eh.EVENT_TIME,
        LAG(eh.EVENT_TIME) OVER (PARTITION BY eh.CUSTOMER_ID, eh.ROOT_NE_NAME ORDER BY eh.EVENT_TIME) AS prev_event_time
    FROM event_history eh
    WHERE eh.EVENT_TYPE_NAM
```

---

## 第 141 题 [hard]

**问题**: 查询每个客户在过去30天内，工作日与周末告警数量的比例（工作日/周末）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (2,3,4,5,6) THEN 1 ELSE 0 END) AS weekday_alerts, SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (1,7) THEN 1 ELSE 0 END) AS weekend_alerts, ROUND(SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (2,3,4,5,6) THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    c.CUSTOMER_NAME,
    COALESCE(SUM(CASE WHEN DAYOFWEEK(e.time_created) BETWEEN 2 AND 6 THEN 1 ELSE 0 END), 0) AS weekday_count,
    COALESCE(SUM(CASE WHEN DAYOFWEEK(e.time_created) IN (1, 7) THEN 1 ELSE 0 END), 0) AS weekend_count,
    CASE 
        WHEN COALESCE(SUM(CASE WHEN DAYOFWEEK(e
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    CASE 
        WHEN weekend_count = 0 THEN NULL 
        ELSE ROUND(workday_count / weekend_count, 4) 
    END AS workday_to_weekend_ratio
FROM 
    t_bz_config_customer c
JOIN (
    SELECT 
        e.customer_id,
        SUM(CASE WHEN DAYOFWEEK(e.t
```

---

## 第 142 题 [hard]

**问题**: 找出每个客户中，告警数量月度增长率最高的设备（最近3个月）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH monthly_device_alerts AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, DATE_FORMAT(e.EVENT_TIME, '%Y-%m') AS month, COUNT(*) AS monthly_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOM
```

**Qwen2.5-32B** ❌ 缺表:event_history
```sql
SELECT 
    c.CUSTOMER_NAME,
    ci.HOST_NAME AS DEVICE_NAME,
    MAX(growth_rate) AS MAX_GROWTH_RATE
FROM (
    SELECT 
        ci.CUSTOMER_ID,
        ci.HOST_NAME,
        DATE_FORMAT(e.EVENT_TIME, '%Y-%m') AS MONTH,
        COUNT(e.EVENT_ID) AS ALARM_COUNT,
        LAG(COUNT(e.EVENT_ID)) OVER (P
```

**Qwen3 MoE** ❌ 用错表:event_sdn
```sql
WITH alarm_counts AS (
    SELECT 
        c.CUSTOMER_ID,
        ci.CI_ID,
        ci.HOST_NAME,
        DATE_FORMAT(e.time_created, '%Y-%m') AS alarm_month,
        COUNT(*) AS alarm_count
    FROM 
        event_sdn e
        JOIN t_bz_config_ci_ne_root ci ON e.ip_ddress = ci.NE_IP
        JOIN t
```

---

## 第 143 题 [hard]

**问题**: 查询每个客户在线设备中，不同严重程度告警的熵值（衡量告警分布的均匀程度）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
WITH severity_probabilities AS (SELECT c.CUSTOMER_NAME, e.SEVERITY, COUNT(*) AS severity_count, COUNT(*) * 1.0 / SUM(COUNT(*)) OVER (PARTITION BY c.CUSTOMER_ID) AS probability FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID =
```

**Qwen2.5-32B** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    ci.HOST_NAME AS DEVICE_NAME,
    SUM(CASE WHEN e.SEVERITY_NAME = 'Critical' THEN 1 ELSE 0 END) AS CRITICAL_COUNT,
    SUM(CASE WHEN e.SEVERITY_NAME = 'Major' THEN 1 ELSE 0 END) AS MAJOR_COUNT,
    SUM(CASE WHEN e.SEVERITY_NAME = 'Minor' THEN 1 ELSE 0 END) AS MINOR_CO
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    SUM(-p.log(p.count) * p.count) AS entropy
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
    INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND e.CUSTOMER_ID = c.CUSTOMER_ID
    INNER JOIN
```

---

## 第 144 题 [hard]

**问题**: 查询每个客户在过去30天内至少发生过一次'Ping event'告警的在线设备数量，并按设备数量降序排列，同时显示客户名称和设备总数。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS online_device_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.EVENT_TYPE_NAME = 'Ping event' AND
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT 
    eh.CUSTOMER_NAME,
    COUNT(DISTINCT eh.ROOT_NE_ID) AS online_device_count,
    (SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE CUSTOMER_ID = eh.CUSTOMER_ID AND IS_ONLINE = 1) AS total_online_devices
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root tn ON eh.ROOT_NE_ID = tn.
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(DISTINCT d.CI_ID) AS device_count
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
    INNER JOIN event_history e ON d.NE_ID = e.NE_ID AND c.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    e.EVENT_TYPE_NAME = 'Pin
```

---

## 第 145 题 [hard]

**问题**: 找出客户'测试客户'下所有设备中，'Trap event'告警发生次数最多的前3台设备，显示设备名、告警次数和最近一次告警时间。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT r.HOST_NAME, COUNT(e.EVENT_TYPE_NAME) AS trap_count, MAX(e.EVENT_TIME) AS latest_trap_time FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE c.CUSTOMER_NAME = '测试客户' AND 
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.ROOT_NE_NAME AS 设备名,
    COUNT(eh.EVENT_ID) AS 告警次数,
    MAX(eh.EVENT_TIME) AS 最近一次告警时间
FROM 
    event_history eh
WHERE 
    eh.CUSTOMER_NAME = '测试客户'
    AND eh.EVENT_TYPE_NAME = 'Trap event'
GROUP BY 
    eh.ROOT_NE_NAME
ORDER BY 
    告警次数 DESC
LIMIT 3;
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.ROOT_NE_NAME AS 设备名,
    COUNT(*) AS 告警次数,
    MAX(eh.EVENT_TIME) AS 最近一次告警时间
FROM 
    event_history eh
WHERE 
    eh.CUSTOMER_NAME = '测试客户'
    AND eh.EVENT_TYPE_NAME = 'Trap event'
GROUP BY 
    eh.ROOT_NE_NAME
ORDER BY 
    告警次数 DESC
LIMIT 3;
```

---

## 第 146 题 [hard]

**问题**: 查询每个客户下在线设备与离线设备的'Ping event'告警总数对比，显示客户名、在线设备告警数、离线设备告警数。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN r.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_ping_alerts, SUM(CASE WHEN r.IS_ONLINE = 0 THEN 1 ELSE 0 END) AS offline_ping_alerts FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID
```

**Qwen2.5-32B** ❌ 用错表:customer
```sql
SELECT 
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN tbcinr.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_device_alarm_count,
    SUM(CASE WHEN tbcinr.IS_ONLINE = 0 THEN 1 ELSE 0 END) AS offline_device_alarm_count
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root tbcinr ON eh.ROOT_NE_ID = tbcinr.N
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN d.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_alert_count,
    SUM(CASE WHEN d.IS_ONLINE = 0 THEN 1 ELSE 0 END) AS offline_alert_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root d ON e.NE_ID = d.NE_ID
JOIN 
    t_bz_config_customer c ON d
```

---

## 第 147 题 [hard]

**问题**: 找出过去7天内，'ngg-319009'客户下所有设备中，同时产生过'Ping event'和'Trap event'告警的设备，显示设备名和两种告警各自的数量。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT r.HOST_NAME, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_count, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh1.ROOT_NE_NAME AS device_name,
    COUNT(CASE WHEN eh1.EVENT_TYPE_NAME = 'Ping event' THEN 1 END) AS ping_event_count,
    COUNT(CASE WHEN eh1.EVENT_TYPE_NAME = 'Trap event' THEN 1 END) AS trap_event_count
FROM 
    event_history eh1
JOIN 
    event_history eh2 ON eh1.ROOT_NE_ID = eh2.
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.ROOT_NE_NAME AS 设备名,
    COUNT(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 END) AS ping_event_count,
    COUNT(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 END) AS trap_event_count
FROM 
    event_history eh
WHERE 
    eh.CUSTOMER_ID = (SELECT CUSTOMER_ID FROM t_bz_config
```

---

## 第 148 题 [hard]

**问题**: 查询每个客户下，设备'tdk-shanghai-b'在过去30天内产生的不同严重级别(SEVERITY)的'Trap event'告警分布，显示客户名、严重级别和告警数量。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, e.SEVERITY, COUNT(*) AS alert_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.HOST_NAME = 'tdk-shanghai-b' AND e.EVENT_TYPE_NAME = 'Trap event'
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    CUSTOMER_NAME, 
    SEVERITY_NAME, 
    COUNT(*) AS ALERT_COUNT
FROM 
    event_history
WHERE 
    ROOT_NE_NAME = 'tdk-shanghai-b' 
    AND EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY 
    CUSTOMER_NAME, 
    SEVERITY_NAME;
```

**Qwen3 MoE** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    eh.CUSTOMER_NAME,
    eh.SEVERITY_NAME,
    COUNT(*) AS alarm_count
FROM 
    event_history eh
WHERE 
    eh.ROOT_NE_NAME = 'tdk-shanghai-b'
    AND eh.EVENT_TYPE_NAME = 'Trap event'
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY 
    eh.CUSTOMER_NAME, 
    eh.SEVERIT
```

---

## 第 149 题 [hard]

**问题**: 找出每个客户下，在线设备中'Ping event'告警频率最高的设备（告警总数/设备数），显示客户名、设备名和平均告警数。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(e.EVENT_TYPE_NAME) / COUNT(DISTINCT r.NE_ID) AS avg_ping_alerts FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND 
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT eh.CUSTOMER_NAME, eh.ROOT_NE_NAME AS DEVICE_NAME, AVG(alarm_count) AS AVERAGE_ALARM_COUNT
FROM (
    SELECT CUSTOMER_NAME, ROOT_NE_NAME, COUNT(*) AS alarm_count
    FROM event_history
    WHERE EVENT_TYPE_NAME = 'Ping event' AND IS_ONLINE = 1
    GROUP BY CUSTOMER_NAME, ROOT_NE_NAME
) eh
GROU
```

**Qwen3 MoE** ❌ 用错表:customer
```sql
WITH customer_device_alerts AS (
    SELECT 
        e.CUSTOMER_ID,
        e.CUSTOMER_NAME,
        e.ROOT_NE_NAME AS DEVICE_NAME,
        COUNT(*) AS alert_count,
        COUNT(DISTINCT e.ROOT_NE_NAME) AS device_count
    FROM event_history e
    INNER JOIN t_bz_config_ci_ne_root n ON e.ROOT_NE_ID
```

---

## 第 150 题 [hard]

**问题**: 查询'测试客户'下，设备'cx-sx-cc002'每月产生的'Trap event'告警趋势，显示年份、月份和告警数量。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

**DeepSeek参考SQL**:
```sql
SELECT YEAR(e.EVENT_TIME) AS alert_year, MONTH(e.EVENT_TIME) AS alert_month, COUNT(*) AS trap_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE c.CUSTOMER_NAME = '测试客户' AN
```

**Qwen2.5-32B** ❌ 缺表:t_bz_config_ci_ne_root
```sql
SELECT 
    YEAR(EVENT_TIME) AS 年份,
    MONTH(EVENT_TIME) AS 月份,
    COUNT(*) AS 告警数量
FROM 
    event_history
WHERE 
    CUSTOMER_NAME = '测试客户'
    AND ROOT_NE_NAME = 'cx-sx-cc002'
    AND EVENT_TYPE_NAME = 'Trap event'
GROUP BY 
    YEAR(EVENT_TIME), MONTH(EVENT_TIME)
ORDER BY 
    年份, 月份;
```

**Qwen3 MoE** ✅ 正确
```sql
SELECT 
    YEAR(e.EVENT_TIME) AS 年份,
    MONTH(e.EVENT_TIME) AS 月份,
    COUNT(*) AS 告警数量
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
JOIN 
    t_bz_config_ci_ne_root n ON e.ROOT_NE_ID = n.CI_ID
WHERE 
    c.CUSTOMER_NAME = '测试客户'
    AND n.HOST_NAME =
```

---
