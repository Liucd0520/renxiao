# Schema增强后 150题完整人工审核报告

**日期**: 2024-12-30
**数据来源**: 150q_enhanced_schema_test.json

---

## 📊 汇总统计

| 难度 | Qwen2.5-32B | Qwen3 MoE |
|:-----|:-----------:|:---------:|
| simple | 50/50 (100%) | 49/50 (98%) |
| medium | 29/50 (58%) | 35/50 (70%) |
| hard | 16/50 (32%) | 11/50 (22%) |
| **总计** | **95/150 (63.3%)** | **95/150 (63.3%)** |

---

## �� 逐题详细审核（150题完整）


## 第 1 题 [simple]

**问题**: 查询所有设备的基础信息
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root;
```

**MoE生成**:
```sql
SELECT 
    c.CI_ID AS device_id,
    c.NE_ID,
    c.HOST_NAME AS device_name,
    c.NE_MODEL AS device_model,
    c.NE_IP AS ip_address,
    c.IS_ACTIVE AS is_active,
    c.IS_ONLINE AS is_online,
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    c.DEVICE_TYPE_ID,
    c.VENDOR_ID,
    c.SERIAL_NUMBER,
    c.VERSION,
    c.STATUS,
    c.AUDIT_STATUS_ID,
    c.MONITOR_STATUS_ID,
    c.ONLINE_CHANGE_TIME,
```

---

## 第 2 题 [simple]

**问题**: 查询所有在线设备的ID和主机名
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1
```

**32B生成**:
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1;
```

**MoE生成**:
```sql
SELECT ci.CI_ID, ci.HOST_NAME
FROM t_bz_config_ci_ne_root ci
WHERE ci.IS_ONLINE = 1 AND ci.IS_DELETED = 0;
```

---

## 第 3 题 [simple]

**问题**: 查询所有已激活的设备数量
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 1
```

**32B生成**:
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 1;
```

**MoE生成**:
```sql
SELECT COUNT(*) AS active_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ACTIVE = 1;
```

---

## 第 4 题 [simple]

**问题**: 查询设备型号为ciscoA的所有设备
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL = 'ciscoA'
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL = 'ciscoA';
```

**MoE生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL = 'ciscoA';
```

---

## 第 5 题 [simple]

**问题**: 查询主机名包含shanghai的设备
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%'
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%';
```

**MoE生成**:
```sql
SELECT DISTINCT t.*
FROM t_bz_config_ci_ne_root t
WHERE t.HOST_NAME LIKE '%shanghai%' OR t.NE_NAME LIKE '%shanghai%' OR t.ALIAS LIKE '%shanghai%';
```

---

## 第 6 题 [simple]

**问题**: 查询主机名为tdk-shanghai-b的设备的IP地址
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT NE_IP FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'tdk-shanghai-b'
```

**32B生成**:
```sql
SELECT NE_IP FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'tdk-shanghai-b';
```

**MoE生成**:
```sql
SELECT NE_IP 
FROM t_bz_config_ci_ne_root 
WHERE HOST_NAME = 'tdk-shanghai-b';
```

---

## 第 7 题 [simple]

**问题**: 查询所有离线设备的ID和名称
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 0
```

**32B生成**:
```sql
SELECT CI_ID, HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 0;
```

**MoE生成**:
```sql
SELECT CI_ID AS device_id, HOST_NAME AS device_name
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 0 AND IS_DELETED = 0;
```

---

## 第 8 题 [simple]

**问题**: 查询所有客户的信息
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_customer
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_customer;
```

**MoE生成**:
```sql
SELECT * FROM t_bz_config_customer;
```

---

## 第 9 题 [simple]

**问题**: 查询客户名称为测试客户的所有信息
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户'
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE CUSTOMER_NAME = '测试客户';
```

---

## 第 10 题 [simple]

**问题**: 查询所有已激活的客户数量
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_customer WHERE IS_ACTIVE = 1
```

**32B生成**:
```sql
SELECT COUNT(DISTINCT CUSTOMER_ID) AS active_customer_count FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```

**MoE生成**:
```sql
SELECT COUNT(*) AS total_active_customers
FROM t_bz_config_customer
WHERE IS_ACTIVE = 1;
```

---

## 第 11 题 [simple]

**问题**: 查询客户简称是上海理想公司的客户ID和联系电话
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_ID, CUSTOMER_PHONE FROM t_bz_config_customer WHERE CUSTOMER_ABB = '上海理想公司'
```

**32B生成**:
```sql
SELECT CUSTOMER_ID, CUSTOMER_PHONE FROM t_bz_config_customer WHERE CUSTOMER_ABB = '上海理想公司';
```

**MoE生成**:
```sql
SELECT c.CUSTOMER_ID, c.CUSTOMER_PHONE
FROM t_bz_config_customer c
WHERE c.CUSTOMER_ABB = '上海理想';
```

---

## 第 12 题 [simple]

**问题**: 查询客户名称为中国电信上海理想的客户邮箱
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_EMAIL FROM t_bz_config_customer WHERE CUSTOMER_NAME = '中国电信上海理想'
```

**32B生成**:
```sql
SELECT t_bz_config_customer.CUSTOMER_EMAIL 
FROM t_bz_config_customer 
WHERE t_bz_config_customer.CUSTOMER_NAME = '中国电信上海理想';
```

**MoE生成**:
```sql
SELECT c.CUSTOMER_EMAIL
FROM t_bz_config_customer c
WHERE c.CUSTOMER_NAME = '中国电信上海理想';
```

---

## 第 13 题 [simple]

**问题**: 查询今天发生的所有告警记录
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE()
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE();
```

**MoE生成**:
```sql
SELECT * 
FROM event_history 
WHERE DATE(EVENT_TIME) = CURDATE() 
  AND EVENT_STATUS_NAME = 'alarm';
```

---

## 第 14 题 [simple]

**问题**: 查询昨天发生的所有告警数量
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE DATE(EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
```

**32B生成**:
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_TIME >= CURDATE() - INTERVAL 1 DAY AND EVENT_TIME < CURDATE();
```

**MoE生成**:
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE DATE(EVENT_TIME) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY))
  AND EVENT_STATUS_NAME = 'alarm';
```

---

## 第 15 题 [simple]

**问题**: 查询最近7天发生的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= NOW() - INTERVAL 7 DAY AND EVENT_STATUS_NAME = 'alarm';
```

**MoE生成**:
```sql
SELECT *
FROM event_history
WHERE EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND EVENT_STATUS_NAME = 'alarm';
```

---

## 第 16 题 [simple]

**问题**: 查询最近30天发生的告警数量
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
```

**32B生成**:
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_STATUS_NAME = 'alarm' AND EVENT_TIME >= NOW() - INTERVAL 30 DAY;
```

**MoE生成**:
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
  AND EVENT_STATUS_NAME = 'alarm';
```

---

## 第 17 题 [simple]

**问题**: 查询本月发生的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE YEAR(EVENT_TIME) = YEAR(CURDATE()) AND MONTH(EVENT_TIME) = MONTH(CURDATE())
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01') AND EVENT_TIME < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01');
```

**MoE生成**:
```sql
SELECT *
FROM event_history
WHERE EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
  AND EVENT_STATUS_NAME = 'alarm';
```

---

## 第 18 题 [simple]

**问题**: 查询上个月发生的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE YEAR(EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(EVENT_TIME) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND EVENT_TIME < CURDATE() AND EVENT_STATUS_NAME = 'alarm';
```

**MoE生成**:
```sql
SELECT *
FROM event_history
WHERE EVENT_TIME >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01 00:00:00')
  AND EVENT_TIME < DATE_FORMAT(CURDATE(), '%Y-%m-01 00:00:00');
```

---

## 第 19 题 [simple]

**问题**: 查询过去三个月发生的告警数量
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
```

**32B生成**:
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_STATUS_NAME = 'alarm'
  AND EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**MoE生成**:
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_STATUS_NAME = 'alarm'
  AND EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

---

## 第 20 题 [simple]

**问题**: 查询告警级别为严重的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE SEVERITY = 1
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE SEVERITY_NAME = 'Critical';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE SEVERITY_NAME = 'Critical';
```

---

## 第 21 题 [simple]

**问题**: 查询告警类型为Ping event的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event'
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

---

## 第 22 题 [simple]

**问题**: 查询告警状态为已恢复的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 2
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = 'normal';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = 'normal';
```

---

## 第 23 题 [simple]

**问题**: 查询告警级别为警告的所有告警数量
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM event_history WHERE SEVERITY = 4
```

**32B生成**:
```sql
SELECT COUNT(*) FROM event_history WHERE SEVERITY_NAME = 'Warning';
```

**MoE生成**:
```sql
SELECT COUNT(*) AS alarm_count
FROM event_history
WHERE SEVERITY_NAME = 'Warning';
```

---

## 第 24 题 [simple]

**问题**: 查询告警类型为Trap event的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event'
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event';
```

---

## 第 25 题 [simple]

**问题**: 查询告警状态为活动的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 1
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = 'alarm';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = 'alarm';
```

---

## 第 26 题 [simple]

**问题**: 查询所有在线的设备数量
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1
```

**32B生成**:
```sql
SELECT COUNT(*) AS online_device_count FROM t_bz_config_ci_ne_root WHERE IS_ONLINE = 1;
```

**MoE生成**:
```sql
SELECT COUNT(*) AS online_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 1 AND IS_DELETED = 0;
```

---

## 第 27 题 [simple]

**问题**: 查询所有已激活的客户列表
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_NAME FROM t_bz_config_customer WHERE IS_ACTIVE = 1
```

**32B生成**:
```sql
SELECT DISTINCT c.CUSTOMER_ID, c.CUSTOMER_NAME
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE c.IS_ACTIVE = 1;
```

**MoE生成**:
```sql
SELECT DISTINCT c.CUSTOMER_ID, c.CUSTOMER_NAME
FROM t_bz_config_customer c
WHERE c.IS_ACTIVE = 1;
```

---

## 第 28 题 [simple]

**问题**: 查询今天发生的所有告警记录
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE()
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE();
```

**MoE生成**:
```sql
SELECT * 
FROM event_history 
WHERE DATE(EVENT_TIME) = CURDATE() 
  AND EVENT_STATUS_NAME = 'alarm';
```

---

## 第 29 题 [simple]

**问题**: 查询主机名为 ciscoA 的设备信息
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'ciscoA'
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'ciscoA';
```

**MoE生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'ciscoA';
```

---

## 第 30 题 [simple]

**问题**: 查询客户名称为 测试客户 的详细信息
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户'
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户';
```

**MoE生成**:
```sql
SELECT * FROM t_bz_config_customer WHERE CUSTOMER_NAME = '测试客户';
```

---

## 第 31 题 [simple]

**问题**: 查询昨天发生的所有严重级别的告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE DATE(EVENT_TIME) = CURDATE() - INTERVAL 1 DAY AND SEVERITY = 1
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= CURDATE() - INTERVAL 1 DAY AND EVENT_TIME < CURDATE() AND SEVERITY_NAME = 'Critical';
```

**MoE生成**:
```sql
SELECT *
FROM event_history
WHERE SEVERITY_NAME = 'Critical'
  AND EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
  AND EVENT_TIME < CURDATE();
```

---

## 第 32 题 [simple]

**问题**: 查询所有设备型号
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT NE_MODEL FROM t_bz_config_ci_ne_root
```

**32B生成**:
```sql
SELECT DISTINCT NE_MODEL FROM t_bz_config_ci_ne_root;
```

**MoE生成**:
```sql
SELECT DISTINCT NE_MODEL 
FROM t_bz_config_ci_ne_root 
WHERE IS_DELETED = 0 AND IS_ACTIVE = 1;
```

---

## 第 33 题 [simple]

**问题**: 查询所有告警类型名称
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT EVENT_TYPE_NAME FROM event_history
```

**32B生成**:
```sql
SELECT DISTINCT EVENT_TYPE_NAME FROM event_history;
```

**MoE生成**:
```sql
SELECT DISTINCT EVENT_TYPE_NAME 
FROM event_history 
WHERE EVENT_TYPE_NAME IS NOT NULL;
```

---

## 第 34 题 [simple]

**问题**: 查询主机名为 poller1 的设备是否在线
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME, IS_ONLINE FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'poller1'
```

**32B生成**:
```sql
SELECT IS_ONLINE FROM t_bz_config_ci_ne_root WHERE HOST_NAME = 'poller1';
```

**MoE生成**:
```sql
SELECT IS_ONLINE 
FROM t_bz_config_ci_ne_root 
WHERE HOST_NAME = 'poller1';
```

---

## 第 35 题 [simple]

**问题**: 查询客户简称是 ngg-319009 的客户ID
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_ABB = 'ngg-319009'
```

**32B生成**:
```sql
SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_ABB = 'ngg-319009';
```

**MoE生成**:
```sql
SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_ABB = 'ngg-319009';
```

---

## 第 36 题 [simple]

**问题**: 查询最近7天内发生的所有告警事件ID和名称
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT EVENT_ID, EVENT_NAME FROM event_history WHERE EVENT_TIME >= CURDATE() - INTERVAL 7 DAY
```

**32B生成**:
```sql
SELECT DISTINCT eh.EVENT_ID, eh.EVENT_NAME
FROM event_history eh
WHERE eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY;
```

**MoE生成**:
```sql
SELECT EVENT_ID, EVENT_NAME
FROM event_history
WHERE EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND EVENT_STATUS_NAME = 'alarm';
```

---

## 第 37 题 [simple]

**问题**: 查询所有设备类型ID
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT NE_TYPE_ID FROM t_bz_config_ci_ne_root
```

**32B生成**:
```sql
SELECT DISTINCT DEVICE_TYPE_ID FROM t_bz_config_ci_ne_root;
```

**MoE生成**:
```sql
SELECT DISTINCT DEVICE_TYPE_ID FROM t_bz_config_ci_ne_root;
```

---

## 第 38 题 [simple]

**问题**: 查询所有状态为已恢复的告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS = 2
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = 'normal';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE EVENT_STATUS_NAME = 'normal' AND EVENT_TIME IS NOT NULL AND EVENT_STATUS = 1;
```

---

## 第 39 题 [simple]

**问题**: 查询本月创建的所有客户
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_NAME FROM t_bz_config_customer WHERE MONTH(CREATE_TIME) = MONTH(CURDATE()) AND YEAR(CREATE_TIME) = YEAR(CURDATE())
```

**32B生成**:
```sql
SELECT DISTINCT c.CUSTOMER_ID, c.CUSTOMER_NAME, c.CREATE_TIME
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE MONTH(c.CREATE_TIME) = MONTH(CURDATE()) AND YEAR(c.CREATE_TIME) = YEAR(CURDATE());
```

**MoE生成**:
```sql
SELECT DISTINCT c.*
FROM t_bz_config_customer c
WHERE c.CREATE_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND c.CREATE_TIME < DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
  AND c.IS_ACTIVE = 1;
```

---

## 第 40 题 [simple]

**问题**: 查询设备型号为空的设备有哪些
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE NE_MODEL IS NULL OR NE_MODEL = ''
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE NE_MODEL IS NULL OR NE_MODEL = '';
```

**MoE生成**:
```sql
SELECT *
FROM t_bz_config_ci_ne_root
WHERE NE_MODEL IS NULL OR NE_MODEL = '';
```

---

## 第 41 题 [simple]

**问题**: 查询告警类型为 Ping event 的所有告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event'
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

**MoE生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Ping event';
```

---

## 第 42 题 [simple]

**问题**: 查询客户 南京研发中心 的联系电话和邮箱
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CUSTOMER_PHONE, CUSTOMER_EMAIL FROM t_bz_config_customer WHERE CUSTOMER_NAME = '南京研发中心'
```

**32B生成**:
```sql
SELECT CUSTOMER_PHONE, CUSTOMER_EMAIL FROM t_bz_config_customer WHERE CUSTOMER_NAME = '南京研发中心';
```

**MoE生成**:
```sql
SELECT CUSTOMER_PHONE, CUSTOMER_EMAIL
FROM t_bz_config_customer
WHERE CUSTOMER_NAME = '南京研发中心';
```

---

## 第 43 题 [simple]

**问题**: 查询所有未激活的设备
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 0
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 0;
```

**MoE生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE IS_ACTIVE = 0;
```

---

## 第 44 题 [simple]

**问题**: 查询过去三个月内发生的所有主要级别告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= CURDATE() - INTERVAL 3 MONTH AND SEVERITY = 2
```

**32B生成**:
```sql
SELECT eh.*
FROM event_history eh
JOIN event_sdn es ON eh.EVENT_ID = es.event_id
WHERE eh.SEVERITY_NAME IN ('Critical', 'Major')
AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**MoE生成**:
```sql
SELECT e.*
FROM event_history e
WHERE e.EVENT_STATUS_NAME = 'alarm'
  AND e.SEVERITY_NAME IN ('Critical', 'Major', 'Warning')
  AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

---

## 第 45 题 [simple]

**问题**: 查询主机名包含 shanghai 的设备
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%'
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE HOST_NAME LIKE '%shanghai%';
```

**MoE生成**:
```sql
SELECT DISTINCT t.*
FROM t_bz_config_ci_ne_root t
WHERE t.HOST_NAME LIKE '%shanghai%' OR t.NE_NAME LIKE '%shanghai%' OR t.ALIAS LIKE '%shanghai%';
```

---

## 第 46 题 [simple]

**问题**: 查询上个月创建的所有设备
**期望表**: `t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT HOST_NAME FROM t_bz_config_ci_ne_root WHERE MONTH(CREATE_TIME) = MONTH(CURDATE() - INTERVAL 1 MONTH) AND YEAR(CREATE_TIME) = YEAR(CURDATE() - INTERVAL 1 MONTH)
```

**32B生成**:
```sql
SELECT * FROM t_bz_config_ci_ne_root WHERE DATE_FORMAT(CREATE_TIME, '%Y-%m') = DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m');
```

**MoE生成**:
```sql
SELECT *
FROM t_bz_config_ci_ne_root
WHERE CREATE_TIME >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01 00:00:00')
  AND CREATE_TIME < DATE_FORMAT(CURDATE(), '%Y-%m-01 00:00:00');
```

---

## 第 47 题 [simple]

**问题**: 查询告警级别为警告的所有告警名称
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT EVENT_NAME FROM event_history WHERE SEVERITY = 4
```

**32B生成**:
```sql
SELECT DISTINCT EVENT_NAME FROM event_history WHERE SEVERITY_NAME = 'Warning';
```

**MoE生成**:
```sql
SELECT DISTINCT EVENT_NAME 
FROM event_history 
WHERE SEVERITY_NAME = 'Warning';
```

---

## 第 48 题 [simple]

**问题**: 查询客户 上海理想公司 的创建时间
**期望表**: `t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT CREATE_TIME FROM t_bz_config_customer WHERE CUSTOMER_NAME = '上海理想公司'
```

**32B生成**:
```sql
SELECT CREATE_TIME FROM t_bz_config_customer WHERE CUSTOMER_NAME = '上海理想公司';
```

**MoE生成**:
```sql
SELECT tc.CREATE_TIME 
FROM t_bz_config_customer tc 
WHERE tc.CUSTOMER_NAME = '上海理想公司';
```

---

## 第 49 题 [simple]

**问题**: 查询最近30天内发生的所有 Trap event 类型告警
**期望表**: `event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT * FROM event_history WHERE EVENT_TIME >= CURDATE() - INTERVAL 30 DAY AND EVENT_TYPE_NAME = 'Trap event'
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE EVENT_TYPE_NAME = 'Trap event' AND EVENT_TIME >= NOW() - INTERVAL 30 DAY;
```

**MoE生成**:
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

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(DISTINCT REGION_ID) FROM t_bz_config_ci_ne_root
```

**32B生成**:
```sql
SELECT COUNT(DISTINCT REGION_ID) FROM t_bz_config_ci_ne_root;
```

**MoE生成**:
```sql
SELECT COUNT(DISTINCT REGION_ID) AS distinct_region_count
FROM t_bz_config_ci_ne_root;
```

---

## 第 51 题 [medium]

**问题**: 查询客户南京研发中心名下所有设备的名称和IP地址
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_IP FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '南京研发中心'
```

**32B生成**:
```sql
SELECT t.HOST_NAME, t.NE_IP 
FROM t_bz_config_ci_ne_root t 
JOIN t_bz_config_customer c ON t.CUSTOMER_ID = c.CUSTOMER_ID 
WHERE c.CUSTOMER_NAME = '南京研发中心';
```

**MoE生成**:
```sql
SELECT DISTINCT t.NE_NAME AS 设备名称, t.NE_IP AS IP地址
FROM t_bz_config_ci_ne_root t
JOIN t_bz_config_customer c ON t.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '南京研发中心' AND t.IS_ACTIVE = 1 AND t.IS_DELETED = 0;
```

---

## 第 52 题 [medium]

**问题**: 统计每个客户拥有的在线设备数量，并按数量降序排列
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS online_count FROM t_bz_config_customer cus LEFT JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID AND ne.IS_ONLINE = 1 GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME ORDER BY online_count DESC
```

**32B生成**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(ne.NE_ID) AS online_device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root ne ON c.CUSTOMER_ID = ne.CUSTOMER_ID
WHERE ne.IS_ONLINE = 1
GROUP BY c.CUSTOMER_NAME
ORDER BY online_device_count DESC;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(e.CI_ID) AS online_device_count
FROM 
    t_bz_config_ci_ne_root e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.IS_ONLINE = 1 
    AND e.IS_ACTIVE = 1 
    AND e.IS_DELETED = 0
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME
ORDER BY 
    online_device_count DESC;
```

---

## 第 53 题 [medium]

**问题**: 查询设备名为tdk-shanghai-b的所有历史告警记录，并显示告警名称和发生时间
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'tdk-shanghai-b'
```

**32B生成**:
```sql
SELECT eh.EVENT_NAME, eh.EVENT_TIME
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE ne.HOST_NAME = 'tdk-shanghai-b' AND eh.EVENT_STATUS_NAME = 'alarm';
```

**MoE生成**:
```sql
SELECT eh.EVENT_NAME, eh.EVENT_TIME
FROM event_history eh
WHERE eh.ROOT_NE_NAME = 'tdk-shanghai-b';
```

---

## 第 54 题 [medium]

**问题**: 统计最近7天内，每个客户产生的严重告警数量
**期望表**: `t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS severe_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.SEVERITY = 1 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID, 
    eh.CUSTOMER_NAME, 
    COUNT(*) AS critical_alarm_count
FROM 
    event_history eh
WHERE 
    eh.SEVERITY_NAME = 'Critical' 
    AND eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
GROUP BY 
    eh.CUSTOMER_ID, 
    eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(*) AS severe_alert_count
FROM 
    event_history eh
JOIN 
    t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    eh.EVENT_STATUS_NAME = 'alarm'
    AND eh.SEVERITY_NAME IN ('Critical', 'Major', 'Warning')
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    eh.CUSTOMER_ID, c.CUSTOMER_NAME
ORDER BY 
    se
```

---

## 第 55 题 [medium]

**问题**: 查询客户ngg-319009名下所有设备的型号和激活状态
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_MODEL, ne.IS_ACTIVE FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = 'ngg-319009'
```

**32B生成**:
```sql
SELECT t.NE_MODEL, t.IS_ACTIVE
FROM t_bz_config_ci_ne_root t
JOIN t_bz_config_customer c ON t.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = 'ngg-319009';
```

**MoE生成**:
```sql
SELECT n.NE_MODEL, n.IS_ACTIVE
FROM t_bz_config_ci_ne_root n
WHERE n.CUSTOMER_ID = (SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_NAME = 'ngg-319009')
```

---

## 第 56 题 [medium]

**问题**: 统计本月发生的所有Trap event告警，并关联显示对应的设备名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TYPE_NAME = 'Trap event' AND YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE())
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_TIME, eh.EVENT_NAME, eh.EVENT_DESC, eh.SEVERITY_NAME, eh.ROOT_NE_NAME, tbci.HOST_NAME AS DEVICE_NAME
FROM event_history eh
JOIN t_bz_config_ci_ne_root tbci ON eh.ROOT_NE_ID = tbci.NE_ID
WHERE eh.EVENT_TYPE_NAME = 'Trap event' AND YEAR(eh.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(eh.EVENT_TIME) = MONTH(CURDATE());
```

**MoE生成**:
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_TYPE_NAME,
    eh.EVENT_NAME,
    eh.EVENT_STATUS_NAME,
    eh.EVENT_TIME,
    eh.SEVERITY_NAME,
    eh.NE_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    eh.ADDRESS AS DEVICE_IP
FROM 
    event_history eh
WHERE 
    eh.EVENT_TYPE_NAME = 'Trap event'
    AND eh.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND eh.EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(
```

---

## 第 57 题 [medium]

**问题**: 查询客户中国电信上海理想名下所有离线设备的名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '中国电信上海理想' AND ne.IS_ONLINE = 0
```

**32B生成**:
```sql
SELECT DISTINCT tbc.HOST_NAME 
FROM t_bz_config_ci_ne_root tbc 
JOIN t_bz_config_customer tcc ON tbc.CUSTOMER_ID = tcc.CUSTOMER_ID 
WHERE tcc.CUSTOMER_NAME = '中国电信上海理想' AND tbc.IS_ONLINE = 0;
```

**MoE生成**:
```sql
SELECT DISTINCT t1.HOST_NAME
FROM t_bz_config_ci_ne_root t1
JOIN t_bz_config_customer t2 ON t1.CUSTOMER_ID = t2.CUSTOMER_ID
WHERE t2.CUSTOMER_NAME = '中国电信上海理想'
  AND t1.IS_ONLINE = 0;
```

---

## 第 58 题 [medium]

**问题**: 统计昨天发生的所有告警，并按告警级别分组统计数量
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ev.SEVERITY, COUNT(*) AS count FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE DATE(ev.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY) GROUP BY ev.SEVERITY
```

**32B生成**:
```sql
SELECT SEVERITY_NAME, COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_TIME >= CURDATE() - INTERVAL 1 DAY AND EVENT_TIME < CURDATE()
GROUP BY SEVERITY_NAME;
```

**MoE生成**:
```sql
SELECT SEVERITY_NAME, COUNT(*) AS alarm_count
FROM event_history
WHERE DATE(EVENT_TIME) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY))
  AND EVENT_STATUS_NAME = 'alarm'
GROUP BY SEVERITY_NAME;
```

---

## 第 59 题 [medium]

**问题**: 查询设备名为ciscoA和ngg-rt-01的所有告警记录，包括告警类型和状态
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_TYPE_NAME, ev.EVENT_STATUS_NAME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME IN ('ciscoA', 'ngg-rt-01')
```

**32B生成**:
```sql
SELECT eh.EVENT_NAME, eh.EVENT_STATUS_NAME
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE ne.HOST_NAME IN ('ciscoA', 'ngg-rt-01');
```

**MoE生成**:
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_TYPE_NAME,
    eh.EVENT_STATUS_NAME,
    eh.EVENT_TIME,
    eh.EVENT_DESC,
    eh.ROOT_NE_NAME,
    eh.ADDRESS
FROM 
    event_history eh
WHERE 
    eh.ROOT_NE_NAME IN ('ciscoA', 'ngg-rt-01');
```

---

## 第 60 题 [medium]

**问题**: 统计每个客户名下设备型号为空的设备数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS null_model_count FROM t_bz_config_customer cus LEFT JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID AND (ne.NE_MODEL IS NULL OR ne.NE_MODEL = '') GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(ne.NE_ID) AS device_count
FROM t_bz_config_customer c
LEFT JOIN t_bz_config_ci_ne_root ne ON c.CUSTOMER_ID = ne.CUSTOMER_ID
WHERE ne.NE_MODEL IS NULL OR ne.NE_MODEL = ''
GROUP BY c.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(*) AS device_count
FROM 
    t_bz_config_ci_ne_root n
JOIN 
    t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    n.NE_MODEL IS NULL OR n.NE_MODEL = ''
GROUP BY 
    c.CUSTOMER_NAME;
```

---

## 第 61 题 [medium]

**问题**: 查询过去三个月内，客户测试客户产生的所有主要告警的详细信息
**期望表**: `event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME, ev.EVENT_DESC FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '测试客户' AND ev.SEVERITY = 2 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
```

**32B生成**:
```sql
SELECT eh.*
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '测试客户'
  AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
  AND eh.SEVERITY_NAME IN ('Critical', 'Major');
```

**MoE生成**:
```sql
SELECT eh.*
FROM event_history eh
WHERE eh.CUSTOMER_NAME = '客户测试客户'
  AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
  AND eh.EVENT_STATUS_NAME = 'alarm'
  AND eh.SEVERITY_NAME IN ('Critical', 'Major', 'Warning');
```

---

## 第 62 题 [medium]

**问题**: 统计每个客户名下，处于活动状态的告警数量
**期望表**: `t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS active_alarm_count FROM t_bz_config_customer cus LEFT JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID AND ev.EVENT_STATUS = 1 GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_NAME, COUNT(eh.EVENT_ID) AS active_alarm_count
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.NE_ID = ne.NE_ID
WHERE eh.EVENT_STATUS_NAME = 'alarm' AND ne.IS_ACTIVE = 1
GROUP BY eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    COUNT(*) AS active_alarm_count
FROM 
    event_history eh
WHERE 
    eh.EVENT_STATUS_NAME = 'alarm'
    AND eh.CUSTOMER_ID IS NOT NULL
GROUP BY 
    eh.CUSTOMER_NAME;
```

---

## 第 63 题 [medium]

**问题**: 查询设备名为v6-dcs21和poller1的创建时间和客户名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.CREATE_TIME, cus.CUSTOMER_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ne.HOST_NAME IN ('v6-dcs21', 'poller1')
```

**32B生成**:
```sql
SELECT ne.HOST_NAME, ne.CREATE_TIME, c.CUSTOMER_NAME
FROM t_bz_config_ci_ne_root ne
JOIN t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
WHERE ne.HOST_NAME IN ('v6-dcs21', 'poller1');
```

**MoE生成**:
```sql
SELECT 
    e.EVENT_TIME AS 创建时间,
    c.CUSTOMER_NAME AS 客户名称
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root r ON e.ROOT_NE_NAME = r.HOST_NAME
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    r.HOST_NAME IN ('v6-dcs21', 'poller1');
```

---

## 第 64 题 [medium]

**问题**: 统计最近30天内，每种告警类型发生的次数
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_TYPE_NAME, COUNT(*) AS count FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) GROUP BY ev.EVENT_TYPE_NAME
```

**32B生成**:
```sql
SELECT EVENT_TYPE_NAME, COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_TIME >= NOW() - INTERVAL 30 DAY AND EVENT_STATUS_NAME = 'alarm'
GROUP BY EVENT_TYPE_NAME;
```

**MoE生成**:
```sql
SELECT 
    EVENT_TYPE_NAME,
    COUNT(*) AS alarm_count
FROM 
    event_history
WHERE 
    EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND EVENT_STATUS_NAME = 'alarm'
GROUP BY 
    EVENT_TYPE_NAME;
```

---

## 第 65 题 [medium]

**问题**: 查询客户上海理想公司名下，所有已恢复的告警记录及恢复时间
**期望表**: `event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME, ev.RECOVER_TIME FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '上海理想公司' AND ev.EVENT_STATUS = 2
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, eh.EVENT_DESC, eh.RECOVER_TIME
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '上海理想公司' AND eh.EVENT_STATUS_NAME = 'normal';
```

**MoE生成**:
```sql
SELECT eh.*
FROM event_history eh
JOIN t_bz_config_customer tc ON eh.CUSTOMER_ID = tc.CUSTOMER_ID
WHERE tc.CUSTOMER_NAME = '上海理想'
  AND eh.EVENT_STATUS_NAME = 'normal'
  AND eh.EVENT_TIME IS NOT NULL
  AND eh.EVENT_STATUS = 1;
```

---

## 第 66 题 [medium]

**问题**: 查询设备名为demo-switch-01和test-router-02的客户联系邮箱
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, cus.CUSTOMER_EMAIL FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ne.HOST_NAME IN ('demo-switch-01', 'test-router-02')
```

**32B生成**:
```sql
SELECT DISTINCT c.CUSTOMER_EMAIL
FROM t_bz_config_ci_ne_root ne
JOIN t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
WHERE ne.HOST_NAME IN ('demo-switch-01', 'test-router-02');
```

**MoE生成**:
```sql
SELECT DISTINCT c.CUSTOMER_EMAIL
FROM event_history e
JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE e.ROOT_NE_NAME IN ('demo-switch-01', 'test-router-02')
  AND c.CUSTOMER_EMAIL IS NOT NULL;
```

---

## 第 67 题 [medium]

**问题**: 统计今天发生的所有Threshold event告警，并显示对应的设备IP地址
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_IP, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TYPE_NAME = 'Threshold event' AND DATE(ev.EVENT_TIME) = CURDATE()
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_TIME, eh.ADDRESS AS DEVICE_IP
FROM event_history eh
WHERE eh.EVENT_TYPE_NAME = 'Threshold event' AND DATE(eh.EVENT_TIME) = CURDATE();
```

**MoE生成**:
```sql
SELECT DISTINCT eh.ADDRESS AS device_ip
FROM event_history eh
WHERE eh.EVENT_TYPE_NAME = 'Threshold event'
  AND DATE(eh.EVENT_TIME) = CURDATE();
```

---

## 第 68 题 [medium]

**问题**: 查询客户南京研发中心名下，所有未激活的设备名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '南京研发中心' AND ne.IS_ACTIVE = 0
```

**32B生成**:
```sql
SELECT DISTINCT tbc.HOST_NAME
FROM t_bz_config_ci_ne_root tbc
JOIN t_bz_config_customer tcc ON tbc.CUSTOMER_ID = tcc.CUSTOMER_ID
WHERE tcc.CUSTOMER_NAME = '南京研发中心' AND tbc.IS_ACTIVE = 0;
```

**MoE生成**:
```sql
SELECT DISTINCT t1.HOST_NAME
FROM t_bz_config_ci_ne_root t1
JOIN t_bz_config_customer t2 ON t1.CUSTOMER_ID = t2.CUSTOMER_ID
WHERE t2.CUSTOMER_NAME = '南京研发中心'
  AND t1.IS_ACTIVE = 0;
```

---

## 第 69 题 [medium]

**问题**: 统计每个客户名下，设备数量最多的前三个客户
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS device_count FROM t_bz_config_customer cus LEFT JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME ORDER BY device_count DESC LIMIT 3
```

**32B生成**:
```sql
SELECT CUSTOMER_NAME, COUNT(DISTINCT NE_ID) AS DEVICE_COUNT
FROM t_bz_config_ci_ne_root
GROUP BY CUSTOMER_NAME
ORDER BY DEVICE_COUNT DESC
LIMIT 3;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(DISTINCT n.CI_ID) AS device_count
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
WHERE 
    n.IS_ACTIVE = 1 
    AND n.IS_DELETED = 0
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME
ORDER BY 
    device_count DESC
LIMIT 3;
```

---

## 第 70 题 [medium]

**问题**: 查询设备名为cx-sx-cc002的所有Syslog event告警的描述信息
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_DESC, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'cx-sx-cc002' AND ev.EVENT_TYPE_NAME = 'Syslog event'
```

**32B生成**:
```sql
SELECT EVENT_DESC FROM event_history WHERE ROOT_NE_NAME = 'cx-sx-cc002' AND EVENT_TYPE_NAME = 'Syslog event';
```

**MoE生成**:
```sql
SELECT eh.EVENT_DESC
FROM event_history eh
JOIN t_bz_config_ci_ne_root nc ON eh.ROOT_NE_NAME = nc.HOST_NAME OR eh.ADDRESS = nc.NE_IP
WHERE nc.HOST_NAME = 'cx-sx-cc002' OR nc.NE_IP = 'cx-sx-cc002'
  AND eh.EVENT_TYPE_NAME = 'Syslog event'
  AND eh.EVENT_STATUS_NAME = 'alarm';
```

---

## 第 71 题 [medium]

**问题**: 统计最近7天内，告警级别为警告且状态为已确认的告警数量，按客户分组
**期望表**: `t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS confirmed_warning_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.SEVERITY = 4 AND ev.EVENT_STATUS = 3 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME, 
    COUNT(eh.EVENT_ID) AS warning_alarm_count
FROM 
    event_history eh
JOIN 
    event_sdn es ON eh.EVENT_ID = es.event_id
WHERE 
    eh.SEVERITY_NAME = 'Warning' 
    AND es.is_acked = 'true'
    AND eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
GROUP BY 
    eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    COUNT(*) AS alarm_count
FROM 
    event_history eh
WHERE 
    eh.SEVERITY_NAME = 'Warning'
    AND eh.EVENT_STATUS_NAME = 'alarm'
    AND eh.IS_ACK = 1
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    eh.CUSTOMER_ID;
```

---

## 第 72 题 [medium]

**问题**: 查询所有发生过Ping event告警的设备名称和客户简称
**期望表**: `t_bz_config_ci_ne_root, event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT ne.HOST_NAME, cus.CUSTOMER_ABB FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ev.EVENT_TYPE_NAME = 'Ping event'
```

**32B生成**:
```sql
SELECT DISTINCT eh.ROOT_NE_NAME AS 设备名称, tc.CUSTOMER_ABB AS 客户简称
FROM event_history eh
JOIN t_bz_config_customer tc ON eh.CUSTOMER_ID = tc.CUSTOMER_ID
WHERE eh.EVENT_TYPE_NAME = 'Ping event' AND eh.EVENT_STATUS_NAME = 'alarm';
```

**MoE生成**:
```sql
SELECT DISTINCT eh.ROOT_NE_NAME, tc.CUSTOMER_ABB
FROM event_history eh
JOIN t_bz_config_customer tc ON eh.CUSTOMER_ID = tc.CUSTOMER_ID
WHERE eh.EVENT_TYPE_NAME = 'Ping event';
```

---

## 第 73 题 [medium]

**问题**: 查询客户ngg-319009名下，所有设备的最后更新时间
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.UPDATE_TIME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = 'ngg-319009' ORDER BY ne.UPDATE_TIME DESC
```

**32B生成**:
```sql
SELECT ne.HOST_NAME, MAX(eh.EVENT_TIME) AS last_update_time
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.NE_ID = ne.NE_ID
WHERE eh.CUSTOMER_NAME = 'ngg-319009'
GROUP BY ne.HOST_NAME;
```

**MoE生成**:
```sql
SELECT MAX(e.EVENT_TIME) AS last_update_time
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = 'ngg-319009';
```

---

## 第 74 题 [medium]

**问题**: 查询客户ngg-319009名下所有设备的主机名和IP地址
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_IP FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = 'ngg-319009'
```

**32B生成**:
```sql
SELECT HOST_NAME, NE_IP FROM t_bz_config_ci_ne_root WHERE CUSTOMER_ID = (SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_NAME = 'ngg-319009');
```

**MoE生成**:
```sql
SELECT t.HOST_NAME, t.NE_IP
FROM t_bz_config_ci_ne_root t
WHERE t.CUSTOMER_ID = (SELECT CUSTOMER_ID FROM t_bz_config_customer WHERE CUSTOMER_NAME = 'ngg-319009') AND t.IS_DELETED = 0;
```

---

## 第 75 题 [medium]

**问题**: 统计每个客户拥有的在线设备数量，并列出客户名称和数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS online_device_count FROM t_bz_config_customer cus JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID WHERE ne.IS_ONLINE = 1 GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(d.NE_ID) AS online_device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE d.IS_ONLINE = 1
GROUP BY c.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.CI_ID) AS online_device_count
FROM 
    t_bz_config_ci_ne_root e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.IS_ONLINE = 1
    AND e.IS_DELETED = 0
    AND c.IS_ACTIVE = 1
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME;
```

---

## 第 76 题 [medium]

**问题**: 查询设备名为ciscoA的所有历史告警记录，包括告警名称和发生时间
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'ciscoA'
```

**32B生成**:
```sql
SELECT eh.EVENT_NAME, eh.EVENT_TIME
FROM event_history eh
JOIN event_sdn es ON eh.EVENT_ID = es.event_id
WHERE eh.ROOT_NE_NAME = 'ciscoA';
```

**MoE生成**:
```sql
SELECT eh.EVENT_NAME, eh.EVENT_TIME
FROM event_history eh
JOIN t_bz_config_ci_ne_root nc ON eh.ROOT_NE_NAME = nc.HOST_NAME
WHERE nc.HOST_NAME = 'ciscoA';
```

---

## 第 77 题 [medium]

**问题**: 统计最近7天内，每个客户产生的严重级别告警数量
**期望表**: `t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS critical_alarm_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.SEVERITY = 1 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID, 
    eh.CUSTOMER_NAME, 
    COUNT(eh.EVENT_ID) AS CRITICAL_ALARM_COUNT
FROM 
    event_history eh
WHERE 
    eh.SEVERITY_NAME = 'Critical' 
    AND eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
GROUP BY 
    eh.CUSTOMER_ID, 
    eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(*) AS severe_alert_count
FROM 
    event_history eh
JOIN 
    t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    eh.EVENT_STATUS_NAME = 'alarm'
    AND eh.SEVERITY_NAME IN ('Critical', 'Major', 'Warning')
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY 
    eh.CUSTOMER_ID, c.CUSTOMER_NAME
ORDER BY 
    se
```

---

## 第 78 题 [medium]

**问题**: 查询客户中国电信上海理想名下，所有处于离线状态的设备名称
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '中国电信上海理想' AND ne.IS_ONLINE = 0
```

**32B生成**:
```sql
SELECT DISTINCT t.HOST_NAME 
FROM t_bz_config_ci_ne_root t 
JOIN t_bz_config_customer c ON t.CUSTOMER_ID = c.CUSTOMER_ID 
WHERE c.CUSTOMER_NAME = '中国电信上海理想' AND t.IS_ONLINE = 0;
```

**MoE生成**:
```sql
SELECT DISTINCT t1.HOST_NAME
FROM t_bz_config_ci_ne_root t1
JOIN t_bz_config_customer t2 ON t1.CUSTOMER_ID = t2.CUSTOMER_ID
WHERE t2.CUSTOMER_NAME = '中国电信上海理想'
  AND t1.IS_ONLINE = 0;
```

---

## 第 79 题 [medium]

**问题**: 查询昨天发生的所有Trap event告警，并关联显示对应的设备名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_TYPE_NAME = 'Trap event' AND DATE(ev.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_TIME, eh.EVENT_TYPE_NAME, eh.EVENT_NAME, eh.EVENT_VALUE, eh.SEVERITY_NAME, eh.ROOT_NE_NAME AS DEVICE_NAME
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE eh.EVENT_TYPE_NAME = 'Trap event' AND DATE(eh.EVENT_TIME) = CURDATE() - INTERVAL 1 DAY;
```

**MoE生成**:
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_TYPE_NAME,
    eh.EVENT_NAME,
    eh.EVENT_STATUS_NAME,
    eh.EVENT_TIME,
    eh.EVENT_DESC,
    eh.NE_NAME,
    eh.ROOT_NE_NAME,
    eh.ADDRESS,
    eh.SEVERITY_NAME
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root t ON eh.NE_ID = t.NE_ID
WHERE 
    eh.EVENT_TYPE_NAME = 'Trap event'
    AND DATE(eh.EVENT_TIME) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY
```

---

## 第 80 题 [medium]

**问题**: 统计本月每个设备型号产生的告警总数，按数量降序排列
**期望表**: `t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_MODEL, COUNT(ev.EVENT_ID) AS alarm_count FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID WHERE YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE()) GROUP BY ne.NE_MODEL ORDER BY alarm_count DESC
```

**32B生成**:
```sql
SELECT ne_model, COUNT(*) AS alarm_count
FROM event_history eh
JOIN t_bz_config_ci_ne_root tbcn ON eh.NE_ID = tbcn.NE_ID
WHERE eh.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND eh.EVENT_TIME < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
  AND eh.EVENT_STATUS_NAME = 'alarm'
GROUP BY ne_model
ORDER BY alarm_count DESC;
```

**MoE生成**:
```sql
SELECT 
    t.NE_MODEL AS device_model,
    COUNT(e.EVENT_ID) AS alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root t ON e.NE_ID = t.NE_ID
WHERE 
    e.EVENT_STATUS_NAME = 'alarm'
    AND e.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND e.EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY 
    t.NE_MODEL
ORDER BY 
    alarm_count DESC
```

---

## 第 81 题 [medium]

**问题**: 查询客户上海理想公司名下，所有发生过严重告警的设备名称
**期望表**: `t_bz_config_ci_ne_root, event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT ne.HOST_NAME FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '上海理想公司' AND ev.SEVERITY = 1
```

**32B生成**:
```sql
SELECT DISTINCT eh.ROOT_NE_NAME 
FROM event_history eh 
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID 
WHERE c.CUSTOMER_NAME = '上海理想公司' AND eh.SEVERITY_NAME = 'Critical';
```

**MoE生成**:
```sql
SELECT DISTINCT eh.ROOT_NE_NAME
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
JOIN t_bz_config_ci_ne_root n ON eh.NE_ID = n.NE_ID
WHERE c.CUSTOMER_NAME = '上海理想'
  AND eh.SEVERITY_NAME IN ('Critical', 'Major', 'Warning')
  AND eh.EVENT_STATUS_NAME = 'alarm';
```

---

## 第 82 题 [medium]

**问题**: 查询设备tdk-shanghai-b在过去三个月内的所有告警，按发生时间倒序排列
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TYPE_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'tdk-shanghai-b' AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) ORDER BY ev.EVENT_TIME DESC
```

**32B生成**:
```sql
SELECT eh.*
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.NE_ID = ne.NE_ID
WHERE ne.HOST_NAME = 'tdk-shanghai-b' AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
ORDER BY eh.EVENT_TIME DESC;
```

**MoE生成**:
```sql
SELECT e.*
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.ROOT_NE_NAME = n.HOST_NAME OR e.ADDRESS = n.NE_IP
WHERE n.HOST_NAME = 'tdk-shanghai-b'
  AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
ORDER BY e.EVENT_TIME DESC;
```

---

## 第 83 题 [medium]

**问题**: 查询今天所有状态为已恢复的告警，并显示对应的客户简称
**期望表**: `event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, cus.CUSTOMER_ABB, ev.RECOVER_TIME FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ev.EVENT_STATUS = 2 AND DATE(ev.RECOVER_TIME) = CURDATE()
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, eh.CUSTOMER_NAME, tc.CUSTOMER_ABB
FROM event_history eh
JOIN t_bz_config_customer tc ON eh.CUSTOMER_ID = tc.CUSTOMER_ID
WHERE eh.EVENT_STATUS_NAME = 'normal' AND DATE(eh.EVENT_TIME) = CURDATE();
```

**MoE生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, eh.RECOVERY_TIME, c.CUSTOMER_ABB
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE eh.EVENT_STATUS_NAME = 'normal'
  AND DATE(eh.RECOVERY_TIME) = CURDATE();
```

---

## 第 84 题 [medium]

**问题**: 查询设备v6-dcs21产生的所有Threshold event告警的详细描述
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_DESC, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'v6-dcs21' AND ev.EVENT_TYPE_NAME = 'Threshold event'
```

**32B生成**:
```sql
SELECT EVENT_DESC FROM event_history WHERE ROOT_NE_NAME = 'v6-dcs21' AND EVENT_TYPE_NAME = 'Threshold event';
```

**MoE生成**:
```sql
SELECT eh.EVENT_DESC
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_NAME = ne.HOST_NAME OR eh.ADDRESS = ne.NE_IP
WHERE eh.EVENT_TYPE_NAME = 'Threshold event'
  AND (ne.HOST_NAME = 'v6-dcs21' OR ne.NE_IP = 'v6-dcs21');
```

---

## 第 85 题 [medium]

**问题**: 统计每个客户名下，设备型号为空的设备数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS null_model_count FROM t_bz_config_customer cus JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID WHERE ne.NE_MODEL IS NULL OR ne.NE_MODEL = '' GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT CUSTOMER_NAME, COUNT(*) AS device_count
FROM t_bz_config_ci_ne_root
WHERE NE_MODEL IS NULL OR NE_MODEL = ''
GROUP BY CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(*) AS device_count
FROM 
    t_bz_config_ci_ne_root n
JOIN 
    t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    n.NE_MODEL IS NULL OR n.NE_MODEL = ''
GROUP BY 
    c.CUSTOMER_NAME;
```

---

## 第 86 题 [medium]

**问题**: 查询最近30天内，告警级别为主要的告警，并关联显示设备IP地址
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_IP, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.SEVERITY = 2 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_TIME, eh.SEVERITY_NAME, eh.ADDRESS AS DEVICE_IP
FROM event_history eh
JOIN event_sdn es ON eh.EVENT_ID = es.event_id
WHERE eh.SEVERITY_NAME = 'Major'
  AND eh.EVENT_TIME >= NOW() - INTERVAL 30 DAY;
```

**MoE生成**:
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_NAME,
    eh.EVENT_TIME,
    eh.SEVERITY_NAME,
    eh.ADDRESS AS DEVICE_IP
FROM 
    event_history eh
WHERE 
    eh.EVENT_STATUS_NAME = 'alarm'
    AND eh.SEVERITY_NAME IN ('Critical', 'Major', 'Warning')
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY 
    eh.EVENT_TIME DESC;
```

---

## 第 87 题 [medium]

**问题**: 查询客户测试客户名下，所有已激活设备的最近更新时间
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.UPDATE_TIME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '测试客户' AND ne.IS_ACTIVE = 1 ORDER BY ne.UPDATE_TIME DESC
```

**32B生成**:
```sql
SELECT eh.ROOT_NE_NAME, MAX(eh.EVENT_TIME) AS LAST_UPDATE_TIME
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
JOIN t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '测试客户名' AND ne.IS_ACTIVE = 1
GROUP BY eh.ROOT_NE_NAME;
```

**MoE生成**:
```sql
SELECT MAX(e.EVENT_TIME) AS last_update_time
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '测试客户'
  AND n.IS_ACTIVE = 1;
```

---

## 第 88 题 [medium]

**问题**: 统计本月每种告警类型发生的次数
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_TYPE_NAME, COUNT(ev.EVENT_ID) AS count FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE()) GROUP BY ev.EVENT_TYPE_NAME
```

**32B生成**:
```sql
SELECT EVENT_TYPE_NAME, COUNT(*) AS alarm_count
FROM event_history
WHERE EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01') AND EVENT_TIME < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
GROUP BY EVENT_TYPE_NAME;
```

**MoE生成**:
```sql
SELECT 
    EVENT_TYPE_NAME AS alarm_type,
    COUNT(*) AS occurrence_count
FROM 
    event_history
WHERE 
    EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY 
    EVENT_TYPE_NAME;
```

---

## 第 89 题 [medium]

**问题**: 查询设备poller1和demo-switch-01的所有告警记录，包括告警状态名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ev.EVENT_NAME, ev.EVENT_STATUS_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME IN ('poller1', 'demo-switch-01')
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_TYPE_NAME, eh.EVENT_NAME, eh.EVENT_VALUE, eh.EVENT_STATUS_NAME, eh.EVENT_TIME, eh.EVENT_DESC, eh.SEVERITY_NAME, eh.NE_NAME, eh.ROOT_NE_NAME, es.time_created, es.is_acked, es.perceived_severity, es.repair_action, es.location_info, es.native_probable_cause, es.md_name, es.product_type, es.alarm_type_qualifier, es.ip_ddress
FROM event_history eh
JOIN event_sdn es ON eh.EV
```

**MoE生成**:
```sql
SELECT eh.*
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_NAME = ne.HOST_NAME OR eh.ADDRESS = ne.NE_IP
WHERE ne.HOST_NAME IN ('poller1', 'demo-switch-01') OR ne.NE_IP IN ('poller1', 'demo-switch-01')
ORDER BY eh.EVENT_TIME DESC;
```

---

## 第 90 题 [medium]

**问题**: 查询客户南京研发中心名下，设备创建时间在最近一年的所有设备
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, ne.NE_MODEL, ne.CREATE_TIME FROM t_bz_config_ci_ne_root ne JOIN t_bz_config_customer cus ON ne.CUSTOMER_ID = cus.CUSTOMER_ID WHERE cus.CUSTOMER_NAME = '南京研发中心' AND ne.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
```

**32B生成**:
```sql
SELECT DISTINCT ci.*
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '南京研发中心'
AND ci.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
```

**MoE生成**:
```sql
SELECT DISTINCT e.*
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '南京研发中心'
  AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
```

---

## 第 91 题 [medium]

**问题**: 统计过去三个月内，每个设备产生的警告级别告警数量，只显示数量大于5的设备
**期望表**: `t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT ne.HOST_NAME, COUNT(ev.EVENT_ID) AS warning_count FROM t_bz_config_ci_ne_root ne JOIN event_history ev ON ne.NE_ID = ev.NE_ID WHERE ev.SEVERITY = 4 AND ev.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) GROUP BY ne.NE_ID, ne.HOST_NAME HAVING warning_count > 5
```

**32B生成**:
```sql
SELECT ROOT_NE_NAME, COUNT(*) AS warning_count
FROM event_history
WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
  AND SEVERITY_NAME = 'Warning'
GROUP BY ROOT_NE_NAME
HAVING warning_count > 5;
```

**MoE生成**:
```sql
SELECT 
    eh.ROOT_NE_NAME AS device_name,
    COUNT(*) AS warning_alarm_count
FROM 
    event_history eh
WHERE 
    eh.SEVERITY_NAME = 'Warning'
    AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY 
    eh.ROOT_NE_NAME
HAVING 
    COUNT(*) > 5;
```

---

## 第 92 题 [medium]

**问题**: 查询所有Syslog event告警，并关联显示对应的客户名称和告警发生时间
**期望表**: `event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_customer cus ON ev.CUSTOMER_ID = cus.CUSTOMER_ID WHERE ev.EVENT_TYPE_NAME = 'Syslog event' ORDER BY ev.EVENT_TIME DESC
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, c.CUSTOMER_NAME
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE eh.EVENT_TYPE_NAME = 'System event' AND eh.EVENT_STATUS_NAME = 'alarm';
```

**MoE生成**:
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_NAME,
    eh.EVENT_STATUS_NAME,
    eh.EVENT_TIME,
    eh.CUSTOMER_NAME
FROM 
    event_history eh
WHERE 
    eh.EVENT_TYPE_NAME = 'Syslog event'
    AND eh.EVENT_STATUS_NAME = 'alarm';
```

---

## 第 93 题 [medium]

**问题**: 查询设备test-router-02的最后一次告警记录详情
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_TYPE_NAME, ev.SEVERITY, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'test-router-02' ORDER BY ev.EVENT_TIME DESC LIMIT 1
```

**32B生成**:
```sql
SELECT eh.* 
FROM event_history eh 
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID 
WHERE ne.HOST_NAME = 'test-router-02' AND eh.EVENT_STATUS_NAME = 'alarm' 
ORDER BY eh.EVENT_TIME DESC 
LIMIT 1;
```

**MoE生成**:
```sql
SELECT eh.*
FROM event_history eh
JOIN t_bz_config_ci_ne_root t ON eh.ROOT_NE_NAME = t.HOST_NAME OR eh.ADDRESS = t.NE_IP
WHERE t.HOST_NAME = 'test-router-02' OR t.NE_IP = 'test-router-02'
ORDER BY eh.EVENT_TIME DESC
LIMIT 1;
```

---

## 第 94 题 [medium]

**问题**: 统计每个客户名下，当前在线的设备数量与总设备数量的比例
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ne.CI_ID) AS total, SUM(CASE WHEN ne.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online FROM t_bz_config_customer cus JOIN t_bz_config_ci_ne_root ne ON cus.CUSTOMER_ID = ne.CUSTOMER_ID GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN ne.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS ONLINE_DEVICE_COUNT,
    COUNT(ne.NE_ID) AS TOTAL_DEVICE_COUNT,
    (SUM(CASE WHEN ne.IS_ONLINE = 1 THEN 1 ELSE 0 END) / COUNT(ne.NE_ID)) AS ONLINE_RATIO
FROM 
    t_bz_config_customer c
JOIN 
    t_bz_config_ci_ne_root ne ON c.CUSTOMER_ID = ne.CUSTOMER_ID
GROUP BY 
    c.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN d.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_device_count,
    COUNT(*) AS total_device_count,
    ROUND(SUM(CASE WHEN d.IS_ONLINE = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS online_ratio
FROM 
    t_bz_config_ci_ne_root d
JOIN 
    t_bz_config_customer c ON d.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    d.IS_DELETED = 0
    AND c.IS_ACTIVE = 1
GROUP BY 
    c
```

---

## 第 95 题 [medium]

**问题**: 查询昨天所有状态为活动的告警，并显示对应的设备型号
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ne.NE_MODEL, ev.EVENT_NAME, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ev.EVENT_STATUS = 1 AND DATE(ev.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.EVENT_TIME, eh.ROOT_NE_NAME, tbcc.NE_MODEL
FROM event_history eh
JOIN t_bz_config_ci_ne_root tbcc ON eh.ROOT_NE_ID = tbcc.NE_ID
WHERE eh.EVENT_STATUS_NAME = 'alarm' AND DATE(eh.EVENT_TIME) = CURDATE() - INTERVAL 1 DAY AND tbcc.IS_ACTIVE = 1;
```

**MoE生成**:
```sql
SELECT eh.EVENT_NAME, eh.EVENT_TIME, tbcn.NE_MODEL
FROM event_history eh
JOIN t_bz_config_ci_ne_root tbcn ON eh.NE_ID = tbcn.NE_ID
WHERE eh.EVENT_STATUS_NAME = 'alarm'
  AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
  AND eh.EVENT_TIME < CURDATE()
  AND tbcn.IS_ACTIVE = 1;
```

---

## 第 96 题 [medium]

**问题**: 查询设备ngg-rt-01产生的所有次要告警，按发生时间正序排列
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.EVENT_DESC, ev.EVENT_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'ngg-rt-01' AND ev.SEVERITY = 3 ORDER BY ev.EVENT_TIME ASC
```

**32B生成**:
```sql
SELECT * FROM event_history WHERE ROOT_NE_NAME = 'ngg-rt-01' AND SEVERITY_NAME = 'Minor' ORDER BY EVENT_TIME ASC;
```

**MoE生成**:
```sql
SELECT e.*
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.ROOT_NE_NAME = n.HOST_NAME OR e.ADDRESS = n.NE_IP
WHERE n.HOST_NAME = 'ngg-rt-01' OR n.NE_IP = 'ngg-rt-01'
  AND e.SEVERITY_NAME IN ('Minor', 'Warning', 'Informational')
ORDER BY e.EVENT_TIME ASC;
```

---

## 第 97 题 [medium]

**问题**: 统计本月每个客户产生的Ping event告警数量
**期望表**: `t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT cus.CUSTOMER_NAME, COUNT(ev.EVENT_ID) AS ping_event_count FROM t_bz_config_customer cus JOIN event_history ev ON cus.CUSTOMER_ID = ev.CUSTOMER_ID WHERE ev.EVENT_TYPE_NAME = 'Ping event' AND YEAR(ev.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(ev.EVENT_TIME) = MONTH(CURDATE()) GROUP BY cus.CUSTOMER_ID, cus.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT 
    CUSTOMER_ID, 
    CUSTOMER_NAME, 
    COUNT(*) AS ping_event_count
FROM 
    event_history
WHERE 
    EVENT_TYPE_NAME = 'Ping event' 
    AND YEAR(EVENT_TIME) = YEAR(CURDATE()) 
    AND MONTH(EVENT_TIME) = MONTH(CURDATE())
GROUP BY 
    CUSTOMER_ID, 
    CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(*) AS ping_event_count
FROM 
    event_history eh
JOIN 
    t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    eh.EVENT_TYPE_NAME = 'Ping event'
    AND eh.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND eh.EVENT_TIME < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY 
    eh.CUSTOMER_ID, c.
```

---

## 第 98 题 [medium]

**问题**: 查询设备cx-sx-cc002的所有告警恢复记录，包括恢复时间和告警名称
**期望表**: `event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT ev.EVENT_NAME, ev.RECOVER_TIME FROM event_history ev JOIN t_bz_config_ci_ne_root ne ON ev.NE_ID = ne.NE_ID WHERE ne.HOST_NAME = 'cx-sx-cc002' AND ev.RECOVER_TIME IS NOT NULL ORDER BY ev.RECOVER_TIME DESC
```

**32B生成**:
```sql
SELECT eh.EVENT_TIME AS 恢复时间, es.native_probable_cause AS 告警名称
FROM event_history eh
JOIN event_sdn es ON eh.EVENT_ID = es.event_id
WHERE eh.ROOT_NE_NAME = 'cx-sx-cc002' AND eh.EVENT_STATUS_NAME = 'normal';
```

**MoE生成**:
```sql
SELECT eh.EVENT_TIME AS recovery_time, eh.EVENT_NAME AS alarm_name
FROM event_history eh
JOIN t_bz_config_ci_ne_root cn ON eh.ROOT_NE_NAME = cn.HOST_NAME OR eh.ADDRESS = cn.NE_IP
WHERE cn.HOST_NAME = 'cx-sx-cc002' OR cn.NE_IP = 'cx-sx-cc002'
  AND eh.EVENT_STATUS_NAME = 'normal'
  AND eh.EVENT_TIME IS NOT NULL
ORDER BY eh.EVENT_TIME DESC;
```

---

## 第 99 题 [medium]

**问题**: 查询客户中国电信上海理想名下所有设备的名称和IP地址
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT n.HOST_NAME, n.NE_IP FROM t_bz_config_ci_ne_root n JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID WHERE c.CUSTOMER_NAME = '中国电信上海理想'
```

**32B生成**:
```sql
SELECT DISTINCT t.HOST_NAME AS 设备名称, t.NE_IP AS IP地址
FROM t_bz_config_ci_ne_root t
JOIN t_bz_config_customer c ON t.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '中国电信上海理想';
```

**MoE生成**:
```sql
SELECT DISTINCT t.NE_NAME AS 设备名称, t.NE_IP AS IP地址
FROM t_bz_config_ci_ne_root t
JOIN t_bz_config_customer c ON t.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '中国电信上海理想' AND t.IS_ACTIVE = 1 AND t.IS_DELETED = 0;
```

---

## 第 100 题 [medium]

**问题**: 统计每个客户拥有的在线设备数量，并列出客户名称和数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(n.CI_ID) AS online_device_count FROM t_bz_config_customer c LEFT JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID AND n.IS_ONLINE = 1 GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME
```

**32B生成**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(d.NE_ID) AS online_device_count
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE d.IS_ONLINE = 1
GROUP BY c.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.CI_ID) AS online_device_count
FROM 
    t_bz_config_ci_ne_root e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.IS_ONLINE = 1
    AND e.IS_DELETED = 0
    AND c.IS_ACTIVE = 1
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME;
```

---

## 第 101 题 [hard]

**问题**: 找出最近30天内发生过严重告警，并且设备型号为特定型号的所有设备，同时显示其所属客户名称和告警发生次数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.NE_MODEL, COUNT(e.EVENT_ID) AS alarm_count FROM t_bz_config_ci_ne_root n INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.SEVERITY = 1 AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND n.NE_MODEL IS NOT NULL GROUP BY c.CUSTOMER_NAME, n.HOST_NAME, n.NE_MODEL HAVING alarm_count
```

**32B生成**:
```sql
SELECT 
    eh.ROOT_NE_NAME AS device_name,
    eh.CUSTOMER_NAME AS customer_name,
    COUNT(eh.EVENT_ID) AS alarm_count
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE 
    eh.SEVERITY_NAME = 'Critical'
    AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    AND ne.NE_MODEL = '特定型号'
GROUP BY 
    eh.ROOT_NE_NAME, eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    e.ROOT_NE_NAME AS device_name,
    c.CUSTOMER_NAME,
    COUNT(e.EVENT_ID) AS alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root r ON e.NE_ID = r.NE_ID
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND e.SEVERITY_NAME IN ('Critical', 'Major', 'Warning')
    AND r.NE_MODEL = '特定型号'
   
```

---

## 第 102 题 [hard]

**问题**: 统计本月每个客户产生的每种告警类型的数量，即使某些客户本月没有告警也要显示出来
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, e.EVENT_TYPE_NAME, COUNT(e.EVENT_ID) AS type_count FROM t_bz_config_customer c LEFT JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND YEAR(e.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(e.EVENT_TIME) = MONTH(CURDATE()) LEFT JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID WHERE c.CUSTOMER_NAME IN ('中国电信上海理想', '测试客户', '南京研发中心', 'ngg-319009', '上海理想公司') GROUP BY c.CUSTOME
```

**32B生成**:
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    eh.EVENT_TYPE_NAME,
    COUNT(eh.EVENT_ID) AS ALARM_COUNT
FROM 
    t_bz_config_customer c
LEFT JOIN 
    event_history eh ON c.CUSTOMER_ID = eh.CUSTOMER_ID AND MONTH(eh.EVENT_TIME) = MONTH(CURDATE()) AND YEAR(eh.EVENT_TIME) = YEAR(CURDATE())
GROUP BY 
    c.CUSTOMER_ID, c.CUSTOMER_NAME, eh.EVENT_TYPE_NAME;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    et.EVENT_TYPE_NAME,
    COALESCE(COUNT(e.EVENT_ID), 0) AS alarm_count
FROM 
    t_bz_config_customer c
CROSS JOIN 
    (SELECT DISTINCT EVENT_TYPE_NAME FROM event_history) et
LEFT JOIN 
    event_history e 
    ON c.CUSTOMER_ID = e.CUSTOMER_ID 
    AND e.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01') 
    AND e.EVENT_TIME < DATE_ADD(DATE_FORMAT
```

---

## 第 103 题 [hard]

**问题**: 查询上个月告警总数最多的前3个客户，并列出这些客户下所有在线设备的名称和IP地址
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.NE_IP, COUNT(e.EVENT_ID) AS total_alarms FROM t_bz_config_customer c INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND YEAR(e.EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(e.EVENT_TIME) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) INNER JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID AND n.IS_ONLINE = 1 WHERE c.CUSTOME
```

**32B生成**:
```sql
SELECT c.CUSTOMER_NAME, d.HOST_NAME, d.NE_IP
FROM (
    SELECT CUSTOMER_ID, COUNT(*) AS alarm_count
    FROM event_history
    WHERE EVENT_TIME >= DATE_SUB(LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)), INTERVAL 1 MONTH) + INTERVAL 1 DAY
      AND EVENT_TIME < LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) + INTERVAL 1 DAY
      AND EVENT_STATUS_NAME = 'alarm'
    GROUP BY CUSTOMER_ID
    ORDER
```

**MoE生成**:
```sql
WITH alarm_counts AS (
    SELECT 
        e.CUSTOMER_ID,
        c.CUSTOMER_NAME,
        COUNT(*) AS alarm_count
    FROM event_history e
    INNER JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
    WHERE e.EVENT_STATUS_NAME = 'alarm'
      AND e.EVENT_TIME >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01 00:00:00')
      AND e.EVENT_TIME < DATE_FORMAT(CURDATE(), '%Y
```

---

## 第 104 题 [hard]

**问题**: 查询昨天发生告警且告警状态为已恢复的设备，需要显示设备名、客户名、告警类型和告警恢复时间
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT n.HOST_NAME, c.CUSTOMER_NAME, e.EVENT_TYPE_NAME, e.RECOVER_TIME FROM t_bz_config_ci_ne_root n INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.EVENT_STATUS = 2 AND DATE(e.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND n.HOST_NAME IN ('cx-sx-cc002', 'tdk-shanghai-b') ORDER BY e.RECOVER_TIME DESC;
```

**32B生成**:
```sql
SELECT 
    eh.ROOT_NE_NAME AS 设备名,
    eh.CUSTOMER_NAME AS 客户名,
    eh.EVENT_NAME AS 告警类型,
    eh.ACTION_TIME AS 告警恢复时间
FROM 
    event_history eh
JOIN 
    t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    DATE(eh.EVENT_TIME) = CURDATE() - INTERVAL 1 DAY
    AND eh.EVENT_STATUS_NAME = 'normal'
    AND eh.ACTION_TIME IS NOT NULL;
```

**MoE生成**:
```sql
SELECT 
    eh.ROOT_NE_NAME AS 设备名,
    c.CUSTOMER_NAME AS 客户名,
    eh.EVENT_TYPE_NAME AS 告警类型,
    eh.EVENT_TIME AS 告警恢复时间
FROM 
    event_history eh
JOIN 
    t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    eh.EVENT_STATUS_NAME = 'normal'
    AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
    AND eh.EVENT_TIME < CURDATE()
    AND eh.EVENT_TYPE_NAME IN ('Threshold ev
```

---

## 第 105 题 [hard]

**问题**: 统计每个客户在最近7天内，每种告警级别的发生次数，并只显示告警总次数大于5次的客户
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, e.SEVERITY, COUNT(e.EVENT_ID) AS severity_count FROM t_bz_config_customer c INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) INNER JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID GROUP BY c.CUSTOMER_NAME, e.SEVERITY HAVING SUM(COUNT(e.EVENT_ID)) OVER (PARTITION BY c.CUSTOMER_NAME) > 5 ORDER BY c.CUSTOMER_
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID, 
    eh.CUSTOMER_NAME, 
    eh.SEVERITY_NAME, 
    COUNT(eh.EVENT_ID) AS alarm_count
FROM 
    event_history eh
WHERE 
    eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
GROUP BY 
    eh.CUSTOMER_ID, 
    eh.CUSTOMER_NAME, 
    eh.SEVERITY_NAME
HAVING 
    alarm_count > 5;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    eh.SEVERITY_NAME,
    COUNT(*) AS alarm_count
FROM 
    event_history eh
WHERE 
    eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND eh.EVENT_STATUS_NAME = 'alarm'
GROUP BY 
    eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh.SEVERITY_NAME
HAVING 
    SUM(COUNT(*)) > 5;
```

---

## 第 106 题 [hard]

**问题**: 找出客户名为中国电信上海理想或南京研发中心，且设备名为cx-sx-cc002或v6-dcs21的所有历史告警记录，按告警发生时间倒序排列
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, e.EVENT_NAME, e.EVENT_TYPE_NAME, e.EVENT_TIME, e.SEVERITY FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE c.CUSTOMER_NAME IN ('中国电信上海理想', '南京研发中心') AND n.HOST_NAME IN ('cx-sx-cc002', 'v6-dcs21') ORDER BY e.EVENT_TIME DESC;
```

**32B生成**:
```sql
SELECT * 
FROM event_history 
WHERE CUSTOMER_NAME IN ('中国电信上海理想', '南京研发中心') 
  AND ROOT_NE_NAME IN ('cx-sx-cc002', 'v6-dcs21') 
ORDER BY EVENT_TIME DESC;
```

**MoE生成**:
```sql
SELECT eh.*
FROM event_history eh
WHERE (eh.CUSTOMER_NAME = '中国电信上海理想' OR eh.CUSTOMER_NAME = '南京研发中心')
  AND (eh.ROOT_NE_NAME = 'cx-sx-cc002' OR eh.ROOT_NE_NAME = 'v6-dcs21')
ORDER BY eh.EVENT_TIME DESC;
```

---

## 第 107 题 [hard]

**问题**: 查询本月告警数量最多的设备，并显示该设备所属的客户信息以及设备的具体型号
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.NE_MODEL, COUNT(e.EVENT_ID) AS month_alarm_count FROM t_bz_config_ci_ne_root n INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND YEAR(e.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(e.EVENT_TIME) = MONTH(CURDATE()) GROUP BY c.CUSTOMER_NAME, n.HOST_NAME, n.NE_MODEL ORDER BY month_alarm_count DESC L
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_ID, c.CUSTOMER_NAME, ci.NE_MODEL, COUNT(eh.EVENT_ID) AS alarm_count
FROM event_history eh
JOIN t_bz_config_ci_ne_root ci ON eh.ROOT_NE_ID = ci.NE_ID
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE eh.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01') AND eh.EVENT_TIME < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
GROUP BY eh.CUSTOMER_ID, c.CUSTOMER_NA
```

**MoE生成**:
```sql
SELECT 
    e.ROOT_NE_NAME AS device_name,
    c.CUSTOMER_NAME AS customer_name,
    t.NE_MODEL AS device_model,
    COUNT(e.EVENT_ID) AS alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
JOIN 
    t_bz_config_ci_ne_root t ON e.NE_ID = t.NE_ID
WHERE 
    e.EVENT_STATUS_NAME = 'alarm'
    AND e.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  
```

---

## 第 108 题 [hard]

**问题**: 统计过去三个月每个客户下，产生过告警的设备数量与总设备数量的比例
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT n.CI_ID) AS total_devices, COUNT(DISTINCT CASE WHEN e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) THEN n.NE_ID END) AS alarmed_devices, ROUND(COUNT(DISTINCT CASE WHEN e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) THEN n.NE_ID END) / COUNT(DISTINCT n.CI_ID) * 100, 2) AS alarm_ratio FROM t_bz_config_customer c LEFT JOIN t_bz_config_ci_ne_root n 
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    COUNT(DISTINCT CASE WHEN eh.EVENT_STATUS_NAME = 'alarm' THEN eh.ROOT_NE_ID END) AS ALARM_DEVICE_COUNT,
    COUNT(DISTINCT eh.ROOT_NE_ID) AS TOTAL_DEVICE_COUNT,
    (COUNT(DISTINCT CASE WHEN eh.EVENT_STATUS_NAME = 'alarm' THEN eh.ROOT_NE_ID END) / COUNT(DISTINCT eh.ROOT_NE_ID)) AS ALARM_DEVICE_RATIO
FROM 
    event_history eh
JOIN 
    t_bz_conf
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    COUNT(DISTINCT CASE WHEN e.EVENT_STATUS_NAME = 'alarm' THEN e.NE_ID END) AS alarm_device_count,
    COUNT(DISTINCT e.NE_ID) AS total_device_count,
    ROUND(
        COUNT(DISTINCT CASE WHEN e.EVENT_STATUS_NAME = 'alarm' THEN e.NE_ID END) / COUNT(DISTINCT e.NE_ID), 4
    ) AS alarm_ratio
FROM 
    event_history e
JOIN 
    t_bz_config_customer c 
```

---

## 第 109 题 [hard]

**问题**: 查询最近30天内，告警级别为次要或警告，且尚未恢复（状态为活动）的告警，关联显示设备及其客户信息
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, e.EVENT_NAME, e.EVENT_TYPE_NAME, e.EVENT_TIME, e.EVENT_DESC FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.SEVERITY IN (3, 4) AND e.EVENT_STATUS = 1 AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) ORDER BY e.EVENT_TIME;
```

**32B生成**:
```sql
SELECT eh.EVENT_ID, eh.EVENT_NAME, eh.SEVERITY_NAME, eh.EVENT_TIME, eh.NE_NAME, eh.CUSTOMER_NAME, ci.HOST_NAME, cu.CUSTOMER_DESC
FROM event_history eh
JOIN t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
JOIN t_bz_config_customer cu ON eh.CUSTOMER_ID = cu.CUSTOMER_ID
WHERE eh.EVENT_TIME >= NOW() - INTERVAL 30 DAY
AND eh.SEVERITY_NAME IN ('Minor', 'Warning')
AND eh.EVENT_STATUS_NAME = 'alarm';
```

**MoE生成**:
```sql
SELECT 
    eh.EVENT_ID,
    eh.EVENT_NAME,
    eh.EVENT_TIME,
    eh.SEVERITY_NAME,
    eh.EVENT_STATUS_NAME,
    eh.NE_NAME,
    eh.ROOT_NE_NAME,
    eh.ADDRESS,
    eh.CUSTOMER_NAME,
    tbc.CUSTOMER_NO,
    tbc.CUSTOMER_TYPE,
    tbc.INDUSTRY,
    tbc.SERVICE_ENGINER,
    tbc.PROPETY,
    tbc.LEVEL,
    tbc.CUSTOMER_PHONE,
    tbc.CUSTOMER_EMAIL,
    tbc.CUSTOMER_ADD,
    tbc.CUSTOMER_FAX,
   
```

---

## 第 110 题 [hard]

**问题**: 找出上个月平均每天告警次数超过3次的客户，并列出这些客户下所有设备的名称
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, COUNT(e.EVENT_ID)/DAY(LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))) AS avg_daily_alarms FROM t_bz_config_customer c INNER JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND YEAR(e.EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(e.EVENT_TIME) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) INNER JOIN t_bz_config_ci_ne_root n ON e.NE_
```

**32B生成**:
```sql
SELECT DISTINCT c.CUSTOMER_NAME, d.HOST_NAME
FROM (
    SELECT CUSTOMER_ID
    FROM event_history
    WHERE EVENT_TIME >= DATE_SUB(DATE_FORMAT(NOW() ,'%Y-%m-01'), INTERVAL 1 MONTH)
      AND EVENT_TIME < DATE_FORMAT(NOW() ,'%Y-%m-01')
      AND EVENT_STATUS_NAME = 'alarm'
    GROUP BY CUSTOMER_ID
    HAVING AVG(COUNT(EVENT_ID)) OVER (PARTITION BY CUSTOMER_ID) > 3
) AS high_alert_customers
JOIN t_b
```

**MoE生成**:
```sql
SELECT DISTINCT c.CUSTOMER_NAME, t.NE_NAME
FROM event_history e
JOIN t_bz_config_ci_ne_root t ON e.NE_ID = t.NE_ID
JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE e.EVENT_TIME >= DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
  AND e.EVENT_TIME < DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND e.EVENT_STATUS_NAME = 'alarm'
GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME, t.NE_N
```

---

## 第 111 题 [hard]

**问题**: 查询设备名为ciscoA或ngg-rt-01的所有历史告警，并按客户分组统计每个客户的告警总数和最近一次告警时间
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(e.EVENT_ID) AS total_alarms, MAX(e.EVENT_TIME) AS last_alarm_time FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE n.HOST_NAME IN ('ciscoA', 'ngg-rt-01') GROUP BY c.CUSTOMER_NAME ORDER BY total_alarms DESC;
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    COUNT(eh.EVENT_ID) AS ALARM_TOTAL_COUNT,
    MAX(eh.EVENT_TIME) AS LAST_ALARM_TIME
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE 
    ne.HOST_NAME IN ('ciscoA', 'ngg-rt-01')
GROUP BY 
    eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    COUNT(*) AS alarm_count,
    MAX(eh.EVENT_TIME) AS last_alarm_time
FROM 
    event_history eh
WHERE 
    eh.ROOT_NE_NAME IN ('ciscoA', 'ngg-rt-01')
    AND eh.EVENT_STATUS_NAME = 'alarm'
GROUP BY 
    eh.CUSTOMER_NAME
ORDER BY 
    last_alarm_time DESC;
```

---

## 第 112 题 [hard]

**问题**: 找出最近7天内，同时产生过Ping event和Threshold event两种告警类型的设备，并显示其客户信息
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT DISTINCT c.CUSTOMER_NAME, n.HOST_NAME FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND e.EVENT_TYPE_NAME = 'Ping event' AND n.NE_ID IN (SELECT NE_ID FROM event_history WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND EVENT_T
```

**32B生成**:
```sql
SELECT DISTINCT c.CUSTOMER_ID, c.CUSTOMER_NAME
FROM event_history eh
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
AND eh.EVENT_TYPE_NAME IN ('Ping event', 'Threshold event')
GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME
HAVING COUNT(DISTINCT eh.EVENT_TYPE_NAME) = 2;
```

**MoE生成**:
```sql
SELECT DISTINCT e.CUSTOMER_ID, e.CUSTOMER_NAME
FROM event_history e
WHERE e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND e.EVENT_TYPE_NAME IN ('Ping event', 'Threshold event')
  AND e.CUSTOMER_ID IN (
    SELECT CUSTOMER_ID
    FROM event_history
    WHERE EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
      AND EVENT_TYPE_NAME = 'Ping event'
    INTERSECT
    SELECT CUSTOMER_ID
    FROM eve
```

---

## 第 113 题 [hard]

**问题**: 统计每个客户在昨天发生的不同告警级别的数量，并以客户名称和告警级别作为行，数量作为列进行展示
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.SEVERITY = 1 THEN 1 ELSE 0 END) AS '严重', SUM(CASE WHEN e.SEVERITY = 2 THEN 1 ELSE 0 END) AS '主要', SUM(CASE WHEN e.SEVERITY = 3 THEN 1 ELSE 0 END) AS '次要', SUM(CASE WHEN e.SEVERITY = 4 THEN 1 ELSE 0 END) AS '警告' FROM t_bz_config_customer c LEFT JOIN event_history e ON c.CUSTOMER_ID = e.CUSTOMER_ID AND DATE(e.EVENT_TIME) = DATE_SUB(CURDATE(), INTERVAL 1 DAY) L
```

**32B生成**:
```sql
SELECT 
    CUSTOMER_NAME,
    SUM(CASE WHEN SEVERITY_NAME = 'Normal' THEN 1 ELSE 0 END) AS Normal,
    SUM(CASE WHEN SEVERITY_NAME = 'Warning' THEN 1 ELSE 0 END) AS Warning,
    SUM(CASE WHEN SEVERITY_NAME = 'Critical' THEN 1 ELSE 0 END) AS Critical,
    SUM(CASE WHEN SEVERITY_NAME = 'Informational' THEN 1 ELSE 0 END) AS Informational,
    SUM(CASE WHEN SEVERITY_NAME = 'Minor' THEN 1 ELSE 0 END) 
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    eh.SEVERITY_NAME,
    COUNT(*) AS count
FROM 
    event_history eh
WHERE 
    DATE(eh.EVENT_TIME) = DATE(DATE_SUB(NOW(), INTERVAL 1 DAY))
GROUP BY 
    eh.CUSTOMER_NAME, 
    eh.SEVERITY_NAME
ORDER BY 
    eh.CUSTOMER_NAME, 
    eh.SEVERITY_NAME;
```

---

## 第 114 题 [hard]

**问题**: 查询所有设备创建时间在一年以内，且在过去三个月内产生过严重或主要告警的设备清单，包含客户名
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, n.CREATE_TIME, COUNT(e.EVENT_ID) AS recent_alarms FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID AND n.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND e.SEVERITY IN (1, 2) GROUP BY c.CUSTOMER_NAME, n
```

**32B生成**:
```sql
SELECT DISTINCT c.CUSTOMER_NAME, e.ROOT_NE_NAME
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.ROOT_NE_ID = n.NE_ID
JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE n.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
AND e.SEVERITY_NAME IN ('Critical', 'Major');
```

**MoE生成**:
```sql
SELECT DISTINCT tbc.CUSTOMER_NAME, tbcn.HOST_NAME AS device_name, tbcn.CREATE_TIME AS device_create_time
FROM t_bz_config_ci_ne_root tbcn
JOIN t_bz_config_customer tbc ON tbcn.CUSTOMER_ID = tbc.CUSTOMER_ID
JOIN event_history eh ON tbcn.NE_ID = eh.NE_ID
WHERE tbcn.CREATE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
  AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
  AND eh.SEVERITY_NAME 
```

---

## 第 115 题 [hard]

**问题**: 找出本月告警恢复平均时间最长的前5个设备，并显示其所属客户和平均恢复时间（分钟）
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, AVG(TIMESTAMPDIFF(MINUTE, e.EVENT_TIME, e.RECOVER_TIME)) AS avg_recover_minutes FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID WHERE YEAR(e.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(e.EVENT_TIME) = MONTH(CURDATE()) AND e.EVENT_STATUS = 2 AND e.RECOVER_TIME IS NOT NUL
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME AS 客户名称,
    eh.ROOT_NE_NAME AS 设备名称,
    AVG(TIMESTAMPDIFF(MINUTE, eh.EVENT_TIME, eh.ACK_TIME)) AS 平均恢复时间_分钟
FROM 
    event_history eh
WHERE 
    eh.EVENT_STATUS_NAME = 'alarm' 
    AND eh.ACK_TIME IS NOT NULL
    AND YEAR(eh.EVENT_TIME) = YEAR(CURDATE())
    AND MONTH(eh.EVENT_TIME) = MONTH(CURDATE())
GROUP BY 
    eh.CUSTOMER_NAME, eh.ROOT_NE_NAME
ORDER BY 
    平均恢
```

**MoE生成**:
```sql
SELECT 
    eh.ROOT_NE_NAME AS device_name,
    tc.CUSTOMER_NAME AS customer_name,
    AVG(TIMESTAMPDIFF(MINUTE, eh.EVENT_TIME, eh.EVENT_END_TIME)) AS avg_recovery_time_minutes
FROM 
    event_history eh
JOIN 
    t_bz_config_customer tc ON eh.CUSTOMER_ID = tc.CUSTOMER_ID
WHERE 
    eh.EVENT_STATUS_NAME = 'alarm'
    AND eh.EVENT_TIME >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND eh.EVENT_TIME < D
```

---

## 第 116 题 [hard]

**问题**: 查询客户测试客户名下，所有设备在最近30天内的告警总数，以及这些设备中当前在线的数量
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT COUNT(DISTINCT n.CI_ID) AS total_devices, SUM(CASE WHEN n.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_devices, COUNT(e.EVENT_ID) AS total_alarms FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID LEFT JOIN event_history e ON n.NE_ID = e.NE_ID AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) WHERE c.CUSTOMER_NAME = '测试客户';
```

**32B生成**:
```sql
SELECT 
    COUNT(DISTINCT eh.NE_ID) AS total_devices,
    SUM(CASE WHEN tbci.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_devices,
    COUNT(eh.EVENT_ID) AS total_alarms
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root tbci ON eh.NE_ID = tbci.NE_ID
JOIN 
    t_bz_config_customer tbcu ON eh.CUSTOMER_ID = tbcu.CUSTOMER_ID
WHERE 
    tbcu.CUSTOMER_NAME = '测试客户名'
    AND eh.EVENT_TIME >= DAT
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(e.EVENT_ID) AS alarm_count_last_30_days,
    SUM(CASE WHEN d.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_device_count
FROM 
    t_bz_config_customer c
    INNER JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
    INNER JOIN event_history e ON d.NE_IP = e.ADDRESS AND d.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    c.CUSTOMER_NAME = '测试客户'
    AND e.EVEN
```

---

## 第 117 题 [hard]

**问题**: 查询设备型号相同的设备集合，并统计每个型号在最近7天内产生的告警总数，同时列出拥有该型号设备的一个示例客户
**期望表**: `t_bz_config_ci_ne_root, event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT n.NE_MODEL, COUNT(e.EVENT_ID) AS week_alarms, MAX(c.CUSTOMER_NAME) AS example_customer FROM t_bz_config_ci_ne_root n INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) INNER JOIN t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID WHERE n.NE_MODEL IS NOT NULL GROUP BY n.NE_MODEL HAVING week_alarms > 0 ORDER BY week_alarms DESC;
```

**32B生成**:
```sql
SELECT 
    ne.NE_MODEL,
    COUNT(eh.EVENT_ID) AS alarm_count,
    c.CUSTOMER_NAME AS example_customer
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
JOIN 
    t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
    AND eh.EVENT_STATUS_NAME = 'alarm'
GROUP BY 
    ne.NE_MODEL, c.CUSTOMER_NAME
ORDER
```

**MoE生成**:
```sql
SELECT 
    t.NE_MODEL AS device_model,
    COUNT(e.EVENT_ID) AS alarm_count_last_7_days,
    MAX(t.CUSTOMER_NAME) AS example_customer_name
FROM 
    event_history e
    INNER JOIN t_bz_config_ci_ne_root t ON e.NE_ID = t.NE_ID
WHERE 
    e.EVENT_STATUS_NAME = 'alarm'
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND t.IS_ACTIVE = 1
    AND t.IS_ONLINE = 1
GROUP BY 
    t.NE_MODEL
ORD
```

---

## 第 118 题 [hard]

**问题**: 统计本月每个客户下，处于活动状态的告警数量与已恢复告警数量的比值
**期望表**: `t_bz_config_customer, event_history, t_bz_config_ci_ne_root`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.EVENT_STATUS = 1 THEN 1 ELSE 0 END) AS active_alarms, SUM(CASE WHEN e.EVENT_STATUS = 2 THEN 1 ELSE 0 END) AS recovered_alarms, CASE WHEN SUM(CASE WHEN e.EVENT_STATUS = 2 THEN 1 ELSE 0 END) = 0 THEN NULL ELSE ROUND(SUM(CASE WHEN e.EVENT_STATUS = 1 THEN 1 ELSE 0 END) / SUM(CASE WHEN e.EVENT_STATUS = 2 THEN 1 ELSE 0 END), 2) END AS active_to_recovered_ratio FRO
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN eh.EVENT_STATUS_NAME = 'alarm' AND YEAR(eh.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(eh.EVENT_TIME) = MONTH(CURDATE()) THEN 1 ELSE 0 END) AS active_alarm_count,
    SUM(CASE WHEN eh.EVENT_STATUS_NAME = 'normal' AND YEAR(eh.EVENT_TIME) = YEAR(CURDATE()) AND MONTH(eh.EVENT_TIME) = MONTH(CURDATE()) THEN 1 ELSE 0 END) AS recovered_alarm
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    SUM(CASE WHEN e.EVENT_STATUS_NAME = 'alarm' THEN 1 ELSE 0 END) AS active_alarm_count,
    SUM(CASE WHEN e.EVENT_STATUS_NAME = 'normal' THEN 1 ELSE 0 END) AS recovered_alarm_count,
    CASE 
        WHEN SUM(CASE WHEN e.EVENT_STATUS_NAME = 'alarm' THEN 1 ELSE 0 END) = 0 THEN 0
        ELSE CAST(SUM(CASE WHEN e.EVENT_STATUS_NAME = 'normal' THEN 1 E
```

---

## 第 119 题 [hard]

**问题**: 找出上个月告警频率（告警总数/设备数）最高的客户，并列出该客户下所有产生过告警的设备名及告警次数
**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, n.HOST_NAME, COUNT(e.EVENT_ID) AS device_alarm_count FROM t_bz_config_customer c INNER JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID INNER JOIN event_history e ON n.NE_ID = e.NE_ID AND YEAR(e.EVENT_TIME) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(e.EVENT_TIME) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) WHERE c.CUSTOMER_ID = (SELECT c2.CUSTO
```

**32B生成**:
```sql
SELECT c.CUSTOMER_NAME, ne.HOST_NAME AS DEVICE_NAME, COUNT(e.EVENT_ID) AS ALARM_COUNT
FROM event_history e
JOIN t_bz_config_ci_ne_root ne ON e.NE_ID = ne.NE_ID
JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE e.EVENT_STATUS_NAME = 'alarm' AND e.EVENT_TIME >= DATE_SUB(LAST_DAY(CURDATE()), INTERVAL DAY(CURDATE())+1 DAY) AND e.EVENT_TIME < LAST_DAY(CURDATE())
GROUP BY c.CUSTOMER_NAM
```

**MoE生成**:
```sql
WITH customer_alert_stats AS (
    SELECT 
        e.CUSTOMER_ID,
        c.CUSTOMER_NAME,
        COUNT(e.EVENT_ID) AS total_alerts,
        COUNT(DISTINCT e.NE_ID) AS device_count,
        COUNT(e.EVENT_ID) / COUNT(DISTINCT e.NE_ID) AS alert_frequency
    FROM event_history e
    INNER JOIN t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
    WHERE e.EVENT_TIME >= DATE_FORMAT(DATE_SUB(CUR
```

---

## 第 120 题 [hard]

**问题**: 查询最近30天内，每天产生的告警总数，并关联显示当天产生告警最多的那个客户名称
**期望表**: `event_history, t_bz_config_customer`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT DATE(e.EVENT_TIME) AS alarm_date, COUNT(e.EVENT_ID) AS daily_total, (SELECT c2.CUSTOMER_NAME FROM t_bz_config_customer c2 INNER JOIN event_history e2 ON c2.CUSTOMER_ID = e2.CUSTOMER_ID AND DATE(e2.EVENT_TIME) = DATE(e.EVENT_TIME) GROUP BY c2.CUSTOMER_NAME ORDER BY COUNT(e2.EVENT_ID) DESC LIMIT 1) AS top_customer FROM event_history e WHERE e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
```

**32B生成**:
```sql
SELECT 
    DATE(e.EVENT_TIME) AS alert_date,
    COUNT(e.EVENT_ID) AS total_alerts,
    c.CUSTOMER_NAME AS customer_with_most_alerts
FROM 
    event_history e
JOIN 
    (SELECT 
         DATE(EVENT_TIME) AS alert_date,
         CUSTOMER_ID,
         COUNT(EVENT_ID) AS alert_count
     FROM 
         event_history
     WHERE 
         EVENT_TIME >= CURDATE() - INTERVAL 30 DAY
     GROUP BY 
      
```

**MoE生成**:
```sql
SELECT 
    DATE(e.EVENT_TIME) AS alarm_date,
    COUNT(*) AS total_alerts,
    (SELECT c.CUSTOMER_NAME 
     FROM event_history e2 
     WHERE DATE(e2.EVENT_TIME) = DATE(e.EVENT_TIME) 
       AND e2.EVENT_STATUS_NAME = 'alarm'
     GROUP BY c.CUSTOMER_NAME 
     ORDER BY COUNT(*) DESC 
     LIMIT 1) AS max_customer_name
FROM event_history e
WHERE e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
 
```

---

## 第 121 题 [hard]

**问题**: 查询每个客户在过去30天内至少发生过一次严重告警（SEVERITY='CRITICAL'）的在线设备数量，并按设备数量降序排列
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS online_critical_devices FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.SEVERITY = 'CRITICAL' AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME ORDER BY online
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_ID, eh.CUSTOMER_NAME, COUNT(DISTINCT eh.NE_ID) AS online_device_count
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.NE_ID = ne.NE_ID
WHERE eh.SEVERITY_NAME = 'Critical'
  AND eh.EVENT_TIME >= NOW() - INTERVAL 30 DAY
  AND ne.IS_ONLINE = 1
GROUP BY eh.CUSTOMER_ID, eh.CUSTOMER_NAME
HAVING online_device_count > 0
ORDER BY online_device_count DESC;
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    COUNT(DISTINCT d.CI_ID) AS online_device_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root d ON e.NE_ID = d.NE_ID
WHERE 
    e.SEVERITY_NAME = 'CRITICAL'
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND d.IS_ONLINE = 1
    AND d.IS_ACTIVE = 1
    AND d.IS_DELETED = 0
GROUP BY 
    e.CUSTOMER_ID
ORDER BY 
    online_device_count DESC;
```

---

## 第 122 题 [hard]

**问题**: 找出客户名为'测试客户'或'ngg-319009'的设备中，最近7天内发生'Ping event'告警次数最多的前5台设备（显示设备名、客户名、告警次数）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT r.HOST_NAME, c.CUSTOMER_NAME, COUNT(*) AS ping_event_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE c.CUSTOMER_NAME IN ('测试客户', 'ngg-319009') AND e.EVENT_TYPE_NAME = 'Ping event' AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY r.NE_ID, r.HOST_NAME,
```

**32B生成**:
```sql
SELECT eh.ROOT_NE_NAME AS 设备名, eh.CUSTOMER_NAME AS 客户名, COUNT(eh.EVENT_ID) AS 告警次数
FROM event_history eh
WHERE eh.CUSTOMER_NAME IN ('测试客户', 'ngg-319009')
  AND eh.EVENT_TYPE_NAME = 'Ping event'
  AND eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY
GROUP BY eh.ROOT_NE_NAME, eh.CUSTOMER_NAME
ORDER BY 告警次数 DESC
LIMIT 5;
```

**MoE生成**:
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
    eh.ROOT_NE_NAME, eh.CUSTOMER_NAME
ORDER BY 
    告警次数 DESC
LIMIT 5;
```

---

## 第 123 题 [hard]

**问题**: 查询每个客户在线设备的'Ping event'和'Trap event'告警总数，并计算两种告警的比例（Ping/Trap），仅显示比例大于2的客户
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_count, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_count, ROUND(SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END), 0), 2) AS ping_trap_ratio FROM t_bz_config_ci_ne_root r JOIN t_bz_
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_count,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_count,
    (SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) / SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END)) AS ping_to_trap_ratio
FROM 
    event_history eh
JOIN 
 
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_count,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_count,
    (SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END), 0)) AS ping_trap_ratio
FROM 

```

---

## 第 124 题 [hard]

**问题**: 找出设备名为'cx-sx-cc002'或'tdk-shanghai-b'的设备，在最近30天内每小时的平均告警数量，并按小时和客户名分组
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, HOUR(e.EVENT_TIME) AS hour_of_day, COUNT(*) / COUNT(DISTINCT DATE(e.EVENT_TIME)) AS avg_alerts_per_hour FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.HOST_NAME IN ('cx-sx-cc002', 'tdk-shanghai-b') AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DA
```

**32B生成**:
```sql
SELECT 
    DATE_FORMAT(e.EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour,
    e.CUSTOMER_NAME,
    AVG(CASE WHEN e.ROOT_NE_NAME IN ('cx-sx-cc002', 'tdk-shanghai-b') THEN 1 ELSE 0 END) AS avg_alarm_count
FROM 
    event_history e
WHERE 
    e.EVENT_TIME >= NOW() - INTERVAL 30 DAY
GROUP BY 
    hour, e.CUSTOMER_NAME
ORDER BY 
    hour, e.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    DATE_FORMAT(e.EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour,
    e.CUSTOMER_NAME,
    AVG(CASE WHEN e.EVENT_STATUS_NAME = 'alarm' THEN 1 ELSE 0 END) AS avg_alarm_count
FROM 
    event_history e
WHERE 
    e.ROOT_NE_NAME IN ('cx-sx-cc002', 'tdk-shanghai-b')
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY 
    DATE_FORMAT(e.EVENT_TIME, '%Y-%m-%d %H:00:00'),
    e.CUSTOMER_NA
```

---

## 第 125 题 [hard]

**问题**: 查询每个客户严重告警（SEVERITY='CRITICAL'）最多的在线设备，显示客户名、设备名、告警次数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
WITH ranked_devices AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(*) AS critical_count, ROW_NUMBER() OVER (PARTITION BY c.CUSTOMER_ID ORDER BY COUNT(*) DESC) AS rn FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.SEVERITY = 'CRITICAL' GROUP BY c.CUSTOME
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_NAME, eh.ROOT_NE_NAME AS DEVICE_NAME, COUNT(eh.EVENT_ID) AS CRITICAL_ALERT_COUNT
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE eh.SEVERITY_NAME = 'Critical' AND ne.IS_ONLINE = 1
GROUP BY eh.CUSTOMER_NAME, eh.ROOT_NE_NAME
ORDER BY eh.CUSTOMER_NAME, CRITICAL_ALERT_COUNT DESC;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    e.NE_NAME AS DEVICE_NAME,
    COUNT(e.EVENT_ID) AS ALARM_COUNT
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root r ON e.NE_ID = r.NE_ID
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.SEVERITY_NAME = 'CRITICAL'
    AND r.IS_ONLINE = 1
GROUP BY 
    c.CUSTOMER_NAME, e.NE_NAME
HAVING 
    ALARM_COUNT = (
        SELECT MAX(alar
```

---

## 第 126 题 [hard]

**问题**: 查询每个客户在线设备中，'Ping event'告警持续时间最长的设备（假设连续告警为持续时间），显示客户名、设备名、最大持续天数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
WITH ping_events AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, e.EVENT_TIME, LAG(e.EVENT_TIME) OVER (PARTITION BY r.NE_ID ORDER BY e.EVENT_TIME) AS prev_time FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.EVENT_TYPE_NAME = 'Ping event'), durations AS (SELEC
```

**32B生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    MAX(TIMESTAMPDIFF(DAY, eh.EVENT_TIME, COALESCE(eh_next.EVENT_TIME, NOW()))) AS MAX_CONTINUOUS_DAYS
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
JOIN 
    t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN 
    event_history eh_next ON eh.ROOT_NE_ID = eh_next.ROOT_NE_ID
```

**MoE生成**:
```sql
WITH ping_events AS (
    SELECT 
        eh.CUSTOMER_ID,
        eh.CUSTOMER_NAME,
        eh.ROOT_NE_NAME AS DEVICE_NAME,
        eh.EVENT_TIME AS ALARM_TIME,
        eh.EVENT_STATUS_NAME,
        LAG(eh.EVENT_TIME) OVER (PARTITION BY eh.CUSTOMER_ID, eh.ROOT_NE_NAME ORDER BY eh.EVENT_TIME) AS PREV_ALARM_TIME
    FROM event_history eh
    WHERE eh.EVENT_TYPE_NAME = 'Ping event'
      AND eh.EVENT
```

---

## 第 127 题 [hard]

**问题**: 找出每个客户在过去24小时内告警频率最高的设备（告警次数/在线时长），假设在线时长从最早告警时间计算
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(*) AS alert_count, TIMESTAMPDIFF(HOUR, MIN(e.EVENT_TIME), MAX(e.EVENT_TIME)) AS hours_span, ROUND(COUNT(*) / NULLIF(TIMESTAMPDIFF(HOUR, MIN(e.EVENT_TIME), MAX(e.EVENT_TIME)), 0), 2) AS alerts_per_hour FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.C
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    eh.ROOT_NE_ID,
    eh.ROOT_NE_NAME,
    COUNT(eh.EVENT_ID) / TIMESTAMPDIFF(HOUR, MIN(eh.EVENT_TIME), NOW()) AS alarm_frequency
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE 
    eh.EVENT_TIME >= NOW() - INTERVAL 24 HOUR
    AND ne.IS_ONLINE = 1
GROUP BY 
    eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh
```

**MoE生成**:
```sql
WITH alarm_events AS (
    SELECT 
        eh.CUSTOMER_ID,
        eh.ROOT_NE_NAME AS device_name,
        eh.ADDRESS AS device_ip,
        eh.EVENT_TIME,
        ROW_NUMBER() OVER (PARTITION BY eh.CUSTOMER_ID, eh.ROOT_NE_NAME ORDER BY eh.EVENT_TIME) AS rn
    FROM event_history eh
    WHERE eh.EVENT_STATUS_NAME = 'alarm'
      AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
),
device_onlin
```

---

## 第 128 题 [hard]

**问题**: 查询每个客户不同类型告警（EVENT_TYPE_NAME）的分布比例，并找出'Ping event'占比超过30%的客户
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH event_totals AS (SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME, e.EVENT_TYPE_NAME, COUNT(*) AS type_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME, e.EVENT_TYPE_NAME), customer_totals AS (SELECT CUSTOMER_ID, SUM(type_count) AS total_aler
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    et.EVENT_TYPE_NAME,
    COUNT(et.EVENT_TYPE_NAME) AS event_count,
    (COUNT(et.EVENT_TYPE_NAME) / SUM(COUNT(et.EVENT_TYPE_NAME)) OVER (PARTITION BY eh.CUSTOMER_ID)) * 100 AS distribution_percentage
FROM 
    event_history eh
JOIN 
    (SELECT DISTINCT EVENT_TYPE_NAME FROM event_history) et
ON 
    eh.EVENT_TYPE_NAME = et.EVENT_TYPE_NAME
GROUP 
```

**MoE生成**:
```sql
WITH customer_event_type_counts AS (
    SELECT 
        e.CUSTOMER_ID,
        e.CUSTOMER_NAME,
        e.EVENT_TYPE_NAME,
        COUNT(*) AS event_count
    FROM event_history e
    GROUP BY e.CUSTOMER_ID, e.CUSTOMER_NAME, e.EVENT_TYPE_NAME
),
customer_total_counts AS (
    SELECT 
        CUSTOMER_ID,
        CUSTOMER_NAME,
        SUM(event_count) AS total_events
    FROM customer_event_type_
```

---

## 第 129 题 [hard]

**问题**: 找出每个客户中，同时存在'Ping event'和'Trap event'告警的在线设备数量
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS devices_with_both_events FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.EVENT_TYPE_NAME IN ('Ping event', 'Trap event') GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME HAVING COUNT(DISTINCT CASE WHEN e.EVENT_T
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_ID, COUNT(DISTINCT eh.NE_ID) AS online_device_count
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.NE_ID = ne.NE_ID
WHERE eh.EVENT_TYPE_NAME IN ('Ping event', 'Trap event')
  AND ne.IS_ONLINE = 1
GROUP BY eh.CUSTOMER_ID
HAVING COUNT(DISTINCT CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN eh.NE_ID END) > 0
   AND COUNT(DISTINCT CASE WHEN eh.EVENT_TYPE_NAME = 'Trap e
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    COUNT(DISTINCT e.NE_ID) AS online_device_count
FROM 
    event_history e
INNER JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE 
    e.EVENT_TYPE_NAME IN ('Ping event', 'Trap event')
    AND n.IS_ONLINE = 1
    AND e.CUSTOMER_ID IS NOT NULL
GROUP BY 
    e.CUSTOMER_ID
HAVING 
    COUNT(DISTINCT CASE WHEN e.EVENT_TYPE_NAME = 'Ping event' THEN e.NE_ID END)
```

---

## 第 130 题 [hard]

**问题**: 查询每个客户在过去7天内，每小时告警数量的标准差，找出告警最不稳定的客户（标准差最大）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH hourly_counts AS (SELECT c.CUSTOMER_NAME, HOUR(e.EVENT_TIME) AS hour, COUNT(*) AS alert_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY c.CUSTOMER_NAME, HOUR(e.EVENT_TIME)) SELECT CUSTOMER_NAME, ROUND(STDDEV
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID, 
    eh.CUSTOMER_NAME, 
    STDDEV(alarm_count) AS std_dev_alarm_count
FROM (
    SELECT 
        CUSTOMER_ID, 
        CUSTOMER_NAME, 
        HOUR(EVENT_TIME) AS hour_of_day, 
        COUNT(*) AS alarm_count
    FROM 
        event_history
    WHERE 
        EVENT_TIME >= NOW() - INTERVAL 7 DAY
        AND EVENT_STATUS_NAME = 'alarm'
    GROUP BY 
        CUSTOMER_ID,
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    e.CUSTOMER_NAME,
    STDDEV_POP(hourly_alarm_count) AS std_dev_alarm_count
FROM (
    SELECT 
        CUSTOMER_ID,
        CUSTOMER_NAME,
        DATE_FORMAT(EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour_start,
        COUNT(*) AS hourly_alarm_count
    FROM event_history
    WHERE EVENT_STATUS_NAME = 'alarm'
      AND EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    GRO
```

---

## 第 131 题 [hard]

**问题**: 找出每个客户中，告警严重程度（SEVERITY）从低到高升级的设备（例如从WARNING升级到CRITICAL），显示客户名、设备名、升级次数
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH severity_ranks AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, e.EVENT_TIME, e.SEVERITY, CASE e.SEVERITY WHEN 'WARNING' THEN 1 WHEN 'MINOR' THEN 2 WHEN 'MAJOR' THEN 3 WHEN 'CRITICAL' THEN 4 END AS severity_rank, LAG(CASE e.SEVERITY WHEN 'WARNING' THEN 1 WHEN 'MINOR' THEN 2 WHEN 'MAJOR' THEN 3 WHEN 'CRITICAL' THEN 4 END) OVER (PARTITION BY r.NE_ID ORDER BY e.EVENT_TIME) AS prev_rank FROM t_bz_config_
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    COUNT(*) AS UPGRADE_COUNT
FROM 
    event_history eh
JOIN (
    SELECT 
        CUSTOMER_ID,
        ROOT_NE_ID,
        LAG(SEVERITY_NAME) OVER (PARTITION BY CUSTOMER_ID, ROOT_NE_ID ORDER BY EVENT_TIME) AS PREV_SEVERITY,
        SEVERITY_NAME
    FROM 
        event_history
    WHERE 
        SEVERITY_NAME IN ('Warning', 'Criti
```

**MoE生成**:
```sql
WITH severity_rank AS (
    SELECT 
        CUSTOMER_NAME,
        ROOT_NE_NAME AS DEVICE_NAME,
        EVENT_TIME,
        SEVERITY_NAME,
        ROW_NUMBER() OVER (PARTITION BY CUSTOMER_NAME, ROOT_NE_NAME ORDER BY EVENT_TIME) AS rn
    FROM event_history
    WHERE SEVERITY_NAME IN ('Normal', 'Warning', 'Critical', 'Minor', 'Major', 'Informational', 'Unknown', 'Symptom')
),
severity_upgrade AS (

```

---

## 第 132 题 [hard]

**问题**: 查询每个客户在线设备的平均告警间隔时间（分钟），仅显示间隔时间小于30分钟的客户
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
WITH time_intervals AS (SELECT c.CUSTOMER_NAME, r.NE_ID, TIMESTAMPDIFF(MINUTE, LAG(e.EVENT_TIME) OVER (PARTITION BY r.NE_ID ORDER BY e.EVENT_TIME), e.EVENT_TIME) AS interval_minutes FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1) SELECT CUSTOMER_NAME, ROUND(
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_NAME, AVG(TIMESTAMPDIFF(MINUTE, eh.EVENT_TIME, LEAD(eh.EVENT_TIME) OVER (PARTITION BY eh.CUSTOMER_ID, eh.NE_ID ORDER BY eh.EVENT_TIME))) AS avg_interval_minutes
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.NE_ID = ne.NE_ID
WHERE ne.IS_ONLINE = 1 AND eh.EVENT_STATUS_NAME = 'alarm'
GROUP BY eh.CUSTOMER_NAME
HAVING avg_interval_minutes < 30;
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    e.CUSTOMER_NAME,
    AVG(TIMESTAMPDIFF(MINUTE, e.EVENT_TIME, LEAD(e.EVENT_TIME) OVER (PARTITION BY e.CUSTOMER_ID ORDER BY e.EVENT_TIME))) AS avg_alarm_interval_minutes
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE 
    n.IS_ONLINE = 1
    AND e.EVENT_STATUS_NAME = 'alarm'
    AND e.EVENT_TYPE_NAME IN ('Threshold event', 'Indi
```

---

## 第 133 题 [hard]

**问题**: 找出每个客户中，最近3天内告警数量呈上升趋势的设备（每天告警数递增）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH daily_device_alerts AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, DATE(e.EVENT_TIME) AS alert_date, COUNT(*) AS daily_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 3 DAY) GROUP BY c.CUSTOMER_NAME, r.HOST_NAME, DATE(e.EVENT_TIM
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh.ROOT_NE_ID, eh.ROOT_NE_NAME, COUNT(eh.EVENT_ID) AS alarm_count, DATE(eh.EVENT_TIME) AS event_date
FROM event_history eh
WHERE eh.EVENT_STATUS_NAME = 'alarm'
AND eh.EVENT_TIME >= CURDATE() - INTERVAL 3 DAY
GROUP BY eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh.ROOT_NE_ID, eh.ROOT_NE_NAME, DATE(eh.EVENT_TIME)
HAVING alarm_count > 0
ORDER BY eh.CUSTOMER_ID, eh.ROOT_
```

**MoE生成**:
```sql
WITH daily_alarm_counts AS (
    SELECT 
        e.CUSTOMER_ID,
        e.ROOT_NE_NAME AS device_name,
        DATE(e.EVENT_TIME) AS event_date,
        COUNT(*) AS alarm_count
    FROM event_history e
    WHERE e.EVENT_STATUS_NAME = 'alarm'
      AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 DAY)
    GROUP BY e.CUSTOMER_ID, e.ROOT_NE_NAME, DATE(e.EVENT_TIME)
),
trend_analysis AS (
    SELECT
```

---

## 第 134 题 [hard]

**问题**: 查询每个客户在过去30天内，不同严重程度告警的累计数量，并计算CRITICAL告警占比
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN e.SEVERITY = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_count, SUM(CASE WHEN e.SEVERITY = 'MAJOR' THEN 1 ELSE 0 END) AS major_count, SUM(CASE WHEN e.SEVERITY = 'MINOR' THEN 1 ELSE 0 END) AS minor_count, SUM(CASE WHEN e.SEVERITY = 'WARNING' THEN 1 ELSE 0 END) AS warning_count, ROUND(SUM(CASE WHEN e.SEVERITY = 'CRITICAL' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) 
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    COUNT(CASE WHEN eh.SEVERITY_NAME = 'Critical' THEN 1 END) AS CRITICAL_COUNT,
    COUNT(*) AS TOTAL_COUNT,
    (COUNT(CASE WHEN eh.SEVERITY_NAME = 'Critical' THEN 1 END) / COUNT(*)) * 100 AS CRITICAL_PERCENTAGE
FROM 
    event_history eh
WHERE 
    eh.EVENT_TIME >= NOW() - INTERVAL 30 DAY
GROUP BY 
    eh.CUSTOMER_ID, eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Critical' THEN 1 ELSE 0 END) AS critical_count,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Warning' THEN 1 ELSE 0 END) AS warning_count,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Major' THEN 1 ELSE 0 END) AS major_count,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Minor' THEN 1 ELSE 0 END) AS minor_count,
    SUM(CASE WHEN eh
```

---

## 第 135 题 [hard]

**问题**: 找出每个客户中，'Ping event'告警发生时间最密集的3小时时段（滑动窗口）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH hourly_ping_counts AS (SELECT c.CUSTOMER_NAME, HOUR(e.EVENT_TIME) AS hour, COUNT(*) AS ping_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TYPE_NAME = 'Ping event' GROUP BY c.CUSTOMER_NAME, HOUR(e.EVENT_TIME)), window_sums AS (SELECT CUSTOMER_NAME, hour, 
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    DATE_FORMAT(eh.EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour_start,
    COUNT(*) AS event_count
FROM 
    event_history eh
WHERE 
    eh.EVENT_TYPE_NAME = 'Ping event'
GROUP BY 
    eh.CUSTOMER_ID, eh.CUSTOMER_NAME, DATE_FORMAT(eh.EVENT_TIME, '%Y-%m-%d %H:00:00')
ORDER BY 
    eh.CUSTOMER_ID, event_count DESC
LIMIT 3;
```

**MoE生成**:
```sql
WITH ping_events AS (
    SELECT 
        CUSTOMER_ID,
        EVENT_TIME,
        -- 将事件时间转换为小时粒度，用于滑动窗口
        DATE_FORMAT(EVENT_TIME, '%Y-%m-%d %H:00:00') AS hour_start
    FROM event_history
    WHERE EVENT_TYPE_NAME = 'Ping event'
      AND EVENT_STATUS_NAME = 'alarm'
),
hourly_counts AS (
    SELECT 
        CUSTOMER_ID,
        hour_start,
        COUNT(*) AS event_count
    FROM ping_even
```

---

## 第 136 题 [hard]

**问题**: 查询每个客户在线设备中，最近一次告警时间与当前时间间隔超过24小时的设备数量
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS idle_devices_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID LEFT JOIN (SELECT NE_ID, CUSTOMER_ID, MAX(EVENT_TIME) AS last_alert FROM event_history GROUP BY NE_ID, CUSTOMER_ID) e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND (e.last_alert IS NULL OR TIMESTAMPDIFF(H
```

**32B生成**:
```sql
SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME, COUNT(DISTINCT eh.NE_ID) AS DEVICE_COUNT
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root n ON c.CUSTOMER_ID = n.CUSTOMER_ID
JOIN (
    SELECT NE_ID, MAX(EVENT_TIME) AS LAST_ALARM_TIME
    FROM event_history
    WHERE EVENT_STATUS_NAME = 'alarm'
    GROUP BY NE_ID
) eh ON n.NE_ID = eh.NE_ID
WHERE n.IS_ONLINE = 1 AND TIMESTAMPDIFF(HOUR, eh.LAST_ALARM_TI
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    COUNT(DISTINCT e.NE_ID) AS device_count
FROM 
    event_history e
INNER JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE 
    n.IS_ONLINE = 1 
    AND e.EVENT_STATUS_NAME = 'alarm'
    AND e.EVENT_TIME < NOW() - INTERVAL 24 HOUR
    AND e.CUSTOMER_ID = n.CUSTOMER_ID
GROUP BY 
    e.CUSTOMER_ID;
```

---

## 第 137 题 [hard]

**问题**: 找出每个客户中，告警类型数量最多的设备（显示客户名、设备名、告警类型数）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH device_event_types AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(DISTINCT e.EVENT_TYPE_NAME) AS event_type_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME, r.NE_ID, r.HOST_NAME) SELECT CUSTOMER_NAME, HOST_NAME, event_type_count F
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_NAME, eh.ROOT_NE_NAME AS DEVICE_NAME, COUNT(DISTINCT eh.EVENT_TYPE_NAME) AS ALARM_TYPE_COUNT
FROM event_history eh
JOIN (
    SELECT CUSTOMER_ID, ROOT_NE_ID, COUNT(DISTINCT EVENT_TYPE_NAME) AS type_count
    FROM event_history
    WHERE EVENT_STATUS_NAME = 'alarm'
    GROUP BY CUSTOMER_ID, ROOT_NE_ID
) sub ON eh.CUSTOMER_ID = sub.CUSTOMER_ID AND eh.ROOT_NE_ID = sub.ROOT_NE_ID
WH
```

**MoE生成**:
```sql
WITH customer_device_alarm_counts AS (
    SELECT 
        eh.CUSTOMER_NAME,
        eh.ROOT_NE_NAME AS DEVICE_NAME,
        COUNT(DISTINCT eh.EVENT_TYPE_ID) AS alarm_type_count
    FROM event_history eh
    WHERE eh.EVENT_STATUS_NAME = 'alarm'
    GROUP BY eh.CUSTOMER_NAME, eh.ROOT_NE_NAME
),
ranked_devices AS (
    SELECT 
        CUSTOMER_NAME,
        DEVICE_NAME,
        alarm_type_count,
   
```

---

## 第 138 题 [hard]

**问题**: 找出每个客户中，连续两天都有告警的设备数量
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH daily_alerts AS (SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME, r.NE_ID, DATE(e.EVENT_TIME) AS alert_date FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME, r.NE_ID, DATE(e.EVENT_TIME)), consecutive_days AS (SELECT CUSTOMER_NAME, NE_ID, alert_dat
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_ID, eh.CUSTOMER_NAME, COUNT(DISTINCT eh.ROOT_NE_ID) AS DEVICE_COUNT
FROM event_history eh
JOIN (
    SELECT CUSTOMER_ID, ROOT_NE_ID, DATE(EVENT_TIME) AS event_date
    FROM event_history
    WHERE EVENT_STATUS_NAME = 'alarm'
    GROUP BY CUSTOMER_ID, ROOT_NE_ID, DATE(EVENT_TIME)
) AS subquery
ON eh.CUSTOMER_ID = subquery.CUSTOMER_ID AND eh.ROOT_NE_ID = subquery.ROOT_NE_ID
WHERE 
```

**MoE生成**:
```sql
WITH alarm_dates AS (
    SELECT 
        e.CUSTOMER_ID,
        e.ROOT_NE_NAME AS device_name,
        DATE(e.EVENT_TIME) AS alarm_date
    FROM event_history e
    WHERE e.EVENT_STATUS_NAME = 'alarm'
),
daily_alarm_counts AS (
    SELECT 
        CUSTOMER_ID,
        device_name,
        alarm_date,
        LAG(alarm_date) OVER (PARTITION BY CUSTOMER_ID, device_name ORDER BY alarm_date) AS prev_
```

---

## 第 139 题 [hard]

**问题**: 查询每个客户在线设备中，告警数量排名前10%的设备（按告警总数）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
WITH device_alert_ranks AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(*) AS total_alerts, PERCENT_RANK() OVER (PARTITION BY c.CUSTOMER_ID ORDER BY COUNT(*) DESC) AS alert_percent_rank FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 GROUP BY c.CUSTOMER_ID, c.
```

**32B生成**:
```sql
SELECT eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh.ROOT_NE_ID, eh.ROOT_NE_NAME, COUNT(eh.EVENT_ID) AS alarm_count
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE ne.IS_ONLINE = 1 AND eh.EVENT_STATUS_NAME = 'alarm'
GROUP BY eh.CUSTOMER_ID, eh.CUSTOMER_NAME, eh.ROOT_NE_ID, eh.ROOT_NE_NAME
HAVING alarm_count >= (
    SELECT CEIL(COUNT(*) * 0.1)
    FROM (
        SELEC
```

**MoE生成**:
```sql
WITH CustomerOnlineDevices AS (
    SELECT 
        e.CUSTOMER_ID,
        e.CUSTOMER_NAME,
        e.NE_ID,
        e.NE_NAME,
        e.ADDRESS,
        COUNT(e.EVENT_ID) AS alarm_count
    FROM event_history e
    INNER JOIN t_bz_config_ci_ne_root r ON e.NE_ID = r.NE_ID
    WHERE r.IS_ONLINE = 1
      AND e.EVENT_STATUS_NAME = 'alarm'
    GROUP BY e.CUSTOMER_ID, e.CUSTOMER_NAME, e.NE_ID, e.NE_N
```

---

## 第 140 题 [hard]

**问题**: 找出每个客户中，'Ping event'告警平均响应时间最短的设备（假设响应时间为相邻'Trap event'的时间差）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH ping_trap_pairs AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, e.EVENT_TIME AS ping_time, LEAD(e.EVENT_TIME) OVER (PARTITION BY r.NE_ID ORDER BY e.EVENT_TIME) AS next_trap_time, e.EVENT_TYPE_NAME FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TYPE_NAME IN ('Ping even
```

**32B生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    ne.ROOT_NE_NAME AS DEVICE_NAME,
    AVG(TIMESTAMPDIFF(SECOND, p.EVENT_TIME, t.EVENT_TIME)) AS AVG_RESPONSE_TIME
FROM 
    event_history p
JOIN 
    event_history t ON p.NE_ID = t.NE_ID AND p.EVENT_TIME < t.EVENT_TIME
JOIN 
    t_bz_config_ci_ne_root ne ON p.NE_ID = ne.NE_ID
JOIN 
    t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    p.EVENT_TYPE_N
```

**MoE生成**:
```sql
WITH ping_trap_events AS (
    SELECT 
        eh.CUSTOMER_ID,
        eh.ROOT_NE_NAME AS device_name,
        eh.EVENT_TIME,
        LAG(eh.EVENT_TIME) OVER (PARTITION BY eh.CUSTOMER_ID, eh.ROOT_NE_NAME ORDER BY eh.EVENT_TIME) AS prev_event_time
    FROM event_history eh
    WHERE eh.EVENT_TYPE_NAME IN ('Ping event', 'Trap event')
      AND eh.EVENT_STATUS_NAME = 'alarm'
),
response_times AS (
  
```

---

## 第 141 题 [hard]

**问题**: 查询每个客户在过去30天内，工作日与周末告警数量的比例（工作日/周末）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (2,3,4,5,6) THEN 1 ELSE 0 END) AS weekday_alerts, SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (1,7) THEN 1 ELSE 0 END) AS weekend_alerts, ROUND(SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (2,3,4,5,6) THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (1,7) THEN 1 ELSE 0 END), 0), 2) AS weekday_weekend_ratio FROM t_bz_conf
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    SUM(CASE WHEN DAYOFWEEK(eh.EVENT_TIME) BETWEEN 2 AND 6 THEN 1 ELSE 0 END) / 
    SUM(CASE WHEN DAYOFWEEK(eh.EVENT_TIME) IN (1, 7) THEN 1 ELSE 0 END) AS weekday_weekend_ratio
FROM 
    event_history eh
WHERE 
    eh.EVENT_TIME >= CURDATE() - INTERVAL 30 DAY
GROUP BY 
    eh.CUSTOMER_ID, eh.CUSTOMER_NAME;
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    c.CUSTOMER_NAME,
    SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (1, 7) THEN 1 ELSE 0 END) AS weekend_count,
    SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) NOT IN (1, 7) THEN 1 ELSE 0 END) AS weekday_count,
    CASE 
        WHEN SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) IN (1, 7) THEN 1 ELSE 0 END) = 0 THEN NULL
        ELSE CAST(SUM(CASE WHEN DAYOFWEEK(e.EVENT_TIME) NOT IN (1,
```

---

## 第 142 题 [hard]

**问题**: 找出每个客户中，告警数量月度增长率最高的设备（最近3个月）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
WITH monthly_device_alerts AS (SELECT c.CUSTOMER_NAME, r.HOST_NAME, DATE_FORMAT(e.EVENT_TIME, '%Y-%m') AS month, COUNT(*) AS monthly_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 3 MONTH) GROUP BY c.CUSTOMER_NAME, r.HOST_NAME,
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_ID,
    eh.CUSTOMER_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    MAX(growth_rate) AS MAX_GROWTH_RATE
FROM (
    SELECT 
        eh.CUSTOMER_ID,
        eh.CUSTOMER_NAME,
        eh.ROOT_NE_NAME,
        DATE_FORMAT(eh.EVENT_TIME, '%Y-%m') AS MONTH,
        COUNT(eh.EVENT_ID) AS ALERT_COUNT,
        LAG(COUNT(eh.EVENT_ID)) OVER (PARTITION BY eh.CUSTOMER_ID, eh.ROOT_NE_NAME 
```

**MoE生成**:
```sql
WITH monthly_alarm_counts AS (
    SELECT 
        e.CUSTOMER_ID,
        e.ROOT_NE_NAME AS device_name,
        DATE_FORMAT(e.EVENT_TIME, '%Y-%m') AS month,
        COUNT(e.EVENT_ID) AS alarm_count
    FROM event_history e
    WHERE e.EVENT_STATUS_NAME = 'alarm'
      AND e.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    GROUP BY e.CUSTOMER_ID, e.ROOT_NE_NAME, DATE_FORMAT(e.EVENT_TIME, '%
```

---

## 第 143 题 [hard]

**问题**: 查询每个客户在线设备中，不同严重程度告警的熵值（衡量告警分布的均匀程度）
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
WITH severity_probabilities AS (SELECT c.CUSTOMER_NAME, e.SEVERITY, COUNT(*) AS severity_count, COUNT(*) * 1.0 / SUM(COUNT(*)) OVER (PARTITION BY c.CUSTOMER_ID) AS probability FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 GROUP BY c.CUSTOMER_ID, c.CUSTOMER_
```

**32B生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    ne.HOST_NAME AS DEVICE_NAME,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Normal' THEN 1 ELSE 0 END) AS Normal_COUNT,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Warning' THEN 1 ELSE 0 END) AS Warning_COUNT,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Critical' THEN 1 ELSE 0 END) AS Critical_COUNT,
    SUM(CASE WHEN eh.SEVERITY_NAME = 'Informational' THEN 1 ELSE 0 END) AS Information
```

**MoE生成**:
```sql
SELECT 
    e.CUSTOMER_ID,
    e.CUSTOMER_NAME,
    SUM(-p.severity_prob * LOG2(p.severity_prob)) AS entropy
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
CROSS JOIN (
    SELECT 
        SEVERITY_NAME,
        COUNT(*) AS severity_count,
        SUM(COUNT(*)) OVER (PARTITION BY e.CUSTOMER_ID) AS total_count,
        COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY e
```

---

## 第 144 题 [hard]

**问题**: 查询每个客户在过去30天内至少发生过一次'Ping event'告警的在线设备数量，并按设备数量降序排列，同时显示客户名称和设备总数。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(DISTINCT r.NE_ID) AS online_device_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.EVENT_TYPE_NAME = 'Ping event' AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME ORDER BY o
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    COUNT(DISTINCT eh.ROOT_NE_ID) AS online_device_count,
    SUM(CASE WHEN tbcr.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS total_online_devices
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root tbcr ON eh.ROOT_NE_ID = tbcr.NE_ID
WHERE 
    eh.EVENT_TYPE_NAME = 'Ping event'
    AND eh.EVENT_TIME >= NOW() - INTERVAL 30 DAY
    AND tbcr.IS_ONLINE = 1
GROUP BY 
    eh
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    COUNT(DISTINCT d.CI_ID) AS device_count
FROM 
    event_history e
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
JOIN 
    t_bz_config_ci_ne_root d ON e.NE_ID = d.NE_ID
WHERE 
    e.EVENT_TYPE_NAME = 'Ping event'
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND d.IS_ONLINE = 1
    AND d.IS_ACTIVE = 1
    AND d.IS_DELETED = 0
GROUP
```

---

## 第 145 题 [hard]

**问题**: 找出客户'测试客户'下所有设备中，'Trap event'告警发生次数最多的前3台设备，显示设备名、告警次数和最近一次告警时间。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT r.HOST_NAME, COUNT(e.EVENT_TYPE_NAME) AS trap_count, MAX(e.EVENT_TIME) AS latest_trap_time FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE c.CUSTOMER_NAME = '测试客户' AND e.EVENT_TYPE_NAME = 'Trap event' GROUP BY r.NE_ID, r.HOST_NAME ORDER BY trap_count DESC, latest_trap
```

**32B生成**:
```sql
SELECT eh.ROOT_NE_NAME AS 设备名, COUNT(eh.EVENT_ID) AS 告警次数, MAX(eh.EVENT_TIME) AS 最近一次告警时间
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
JOIN t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_NAME = '测试客户' AND eh.EVENT_TYPE_NAME = 'Trap event'
GROUP BY eh.ROOT_NE_NAME
ORDER BY 告警次数 DESC
LIMIT 3;
```

**MoE生成**:
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
    AND eh.EVENT_STATUS_NAME = 'alarm'
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

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, SUM(CASE WHEN r.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_ping_alerts, SUM(CASE WHEN r.IS_ONLINE = 0 THEN 1 ELSE 0 END) AS offline_ping_alerts FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE e.EVENT_TYPE_NAME = 'Ping event' GROUP BY c.CUSTOMER_ID, c.
```

**32B生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN d.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_device_alarm_count,
    SUM(CASE WHEN d.IS_ONLINE = 0 THEN 1 ELSE 0 END) AS offline_device_alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root d ON e.NE_ID = d.NE_ID
JOIN 
    t_bz_config_customer c ON d.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TYPE_NAME = 'Ping event'
GROUP BY 
   
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    SUM(CASE WHEN d.IS_ONLINE = 1 THEN 1 ELSE 0 END) AS online_alarm_count,
    SUM(CASE WHEN d.IS_ONLINE = 0 THEN 1 ELSE 0 END) AS offline_alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root d ON e.NE_ID = d.NE_ID
JOIN 
    t_bz_config_customer c ON d.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TYPE_NAME = 'Ping event'
    AND e.EVENT_STATUS_NAME
```

---

## 第 147 题 [hard]

**问题**: 找出过去7天内，'ngg-319009'客户下所有设备中，同时产生过'Ping event'和'Trap event'告警的设备，显示设备名和两种告警各自的数量。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_ci_ne_root |
| MoE | ❌ | 缺表:t_bz_config_ci_ne_root |

**DeepSeek参考SQL**:
```sql
SELECT r.HOST_NAME, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_count, SUM(CASE WHEN e.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE c.CUSTOMER_NAME = 'ngg-319009' AND e.EVENT_TIM
```

**32B生成**:
```sql
SELECT 
    eh1.ROOT_NE_NAME AS device_name,
    COUNT(CASE WHEN eh1.EVENT_TYPE_NAME = 'Ping event' THEN 1 END) AS ping_event_count,
    COUNT(CASE WHEN eh1.EVENT_TYPE_NAME = 'Trap event' THEN 1 END) AS trap_event_count
FROM 
    event_history eh1
JOIN 
    event_history eh2 ON eh1.ROOT_NE_ID = eh2.ROOT_NE_ID AND eh1.CUSTOMER_NAME = eh2.CUSTOMER_NAME
WHERE 
    eh1.CUSTOMER_NAME = 'ngg-319009'
   
```

**MoE生成**:
```sql
SELECT 
    eh.ROOT_NE_NAME AS device_name,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Ping event' THEN 1 ELSE 0 END) AS ping_event_count,
    SUM(CASE WHEN eh.EVENT_TYPE_NAME = 'Trap event' THEN 1 ELSE 0 END) AS trap_event_count
FROM 
    event_history eh
WHERE 
    eh.CUSTOMER_NAME = 'ngg-319009'
    AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND eh.EVENT_TYPE_NAME IN ('Ping event', '
```

---

## 第 148 题 [hard]

**问题**: 查询每个客户下，设备'tdk-shanghai-b'在过去30天内产生的不同严重级别(SEVERITY)的'Trap event'告警分布，显示客户名、严重级别和告警数量。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ❌ | 缺表:t_bz_config_customer |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, e.SEVERITY, COUNT(*) AS alert_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.HOST_NAME = 'tdk-shanghai-b' AND e.EVENT_TYPE_NAME = 'Trap event' AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME, e.SEV
```

**32B生成**:
```sql
SELECT 
    eh.CUSTOMER_NAME,
    eh.SEVERITY_NAME,
    COUNT(eh.EVENT_ID) AS AlarmCount
FROM 
    event_history eh
JOIN 
    t_bz_config_ci_ne_root ne ON eh.ROOT_NE_ID = ne.NE_ID
WHERE 
    eh.EVENT_TYPE_NAME = 'Trap event'
    AND eh.ROOT_NE_NAME = 'tdk-shanghai-b'
    AND eh.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY 
    eh.CUSTOMER_NAME, eh.SEVERITY_NAME;
```

**MoE生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    e.SEVERITY_NAME,
    COUNT(*) AS alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.ROOT_NE_NAME = n.HOST_NAME
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    e.EVENT_TYPE_NAME = 'Trap event'
    AND n.HOST_NAME = 'tdk-shanghai-b'
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY 
    c.CUSTOME
```

---

## 第 149 题 [hard]

**问题**: 找出每个客户下，在线设备中'Ping event'告警频率最高的设备（告警总数/设备数），显示客户名、设备名和平均告警数。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ❌ | 缺表:t_bz_config_customer |

**DeepSeek参考SQL**:
```sql
SELECT c.CUSTOMER_NAME, r.HOST_NAME, COUNT(e.EVENT_TYPE_NAME) / COUNT(DISTINCT r.NE_ID) AS avg_ping_alerts FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE r.IS_ONLINE = 1 AND e.EVENT_TYPE_NAME = 'Ping event' GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME, r.NE_ID, r.HOST_NAME ORDER
```

**32B生成**:
```sql
SELECT 
    c.CUSTOMER_NAME,
    eh.ROOT_NE_NAME AS DEVICE_NAME,
    AVG(eh.EVENT_COUNT) AS AVERAGE_ALARM_COUNT
FROM (
    SELECT 
        CUSTOMER_ID,
        ROOT_NE_NAME,
        COUNT(*) AS EVENT_COUNT
    FROM 
        event_history
    WHERE 
        EVENT_TYPE_NAME = 'Ping event'
        AND EVENT_STATUS_NAME = 'alarm'
        AND NE_ID IN (
            SELECT 
                NE_ID
       
```

**MoE生成**:
```sql
WITH customer_device_alerts AS (
    SELECT 
        e.CUSTOMER_ID,
        e.CUSTOMER_NAME,
        e.ROOT_NE_NAME AS DEVICE_NAME,
        COUNT(e.EVENT_ID) AS ALERT_COUNT,
        COUNT(DISTINCT e.ROOT_NE_NAME) AS DEVICE_COUNT
    FROM event_history e
    INNER JOIN t_bz_config_ci_ne_root n ON e.ROOT_NE_ID = n.NE_ID
    WHERE e.EVENT_TYPE_NAME = 'Ping event'
      AND n.IS_ONLINE = 1
    GROUP B
```

---

## 第 150 题 [hard]

**问题**: 查询'测试客户'下，设备'cx-sx-cc002'每月产生的'Trap event'告警趋势，显示年份、月份和告警数量。
**期望表**: `t_bz_config_ci_ne_root, t_bz_config_customer, event_history`

| 模型 | 结果 | 说明 |
|:-----|:---:|:-----|
| 32B | ✅ | 正确 |
| MoE | ✅ | 正确 |

**DeepSeek参考SQL**:
```sql
SELECT YEAR(e.EVENT_TIME) AS alert_year, MONTH(e.EVENT_TIME) AS alert_month, COUNT(*) AS trap_count FROM t_bz_config_ci_ne_root r JOIN t_bz_config_customer c ON r.CUSTOMER_ID = c.CUSTOMER_ID JOIN event_history e ON r.NE_ID = e.NE_ID AND r.CUSTOMER_ID = e.CUSTOMER_ID WHERE c.CUSTOMER_NAME = '测试客户' AND r.HOST_NAME = 'cx-sx-cc002' AND e.EVENT_TYPE_NAME = 'Trap event' GROUP BY YEAR(e.EVENT_TIME), MONT
```

**32B生成**:
```sql
SELECT 
    YEAR(e.EVENT_TIME) AS 年份,
    MONTH(e.EVENT_TIME) AS 月份,
    COUNT(e.EVENT_ID) AS 告警数量
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.ROOT_NE_ID = n.NE_ID
JOIN 
    t_bz_config_customer c ON n.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    c.CUSTOMER_NAME = '测试客户'
    AND n.HOST_NAME = 'cx-sx-cc002'
    AND e.EVENT_TYPE_NAME = 'Trap event'
GROUP BY 
    YEAR(e.EVENT_TIME), M
```

**MoE生成**:
```sql
SELECT 
    YEAR(e.EVENT_TIME) AS 年份,
    MONTH(e.EVENT_TIME) AS 月份,
    COUNT(*) AS 告警数量
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.ROOT_NE_NAME = n.HOST_NAME OR e.ADDRESS = n.NE_IP
JOIN 
    t_bz_config_customer c ON e.CUSTOMER_ID = c.CUSTOMER_ID
WHERE 
    c.CUSTOMER_NAME = '测试客户'
    AND (n.HOST_NAME = 'cx-sx-cc002' OR n.NE_IP = 'cx-sx-cc002')
    AND e.EVENT_TYPE_NAME =
```

---
