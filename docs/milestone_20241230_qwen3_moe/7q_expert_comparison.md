# Qwen2.5-32B vs Qwen3 MoE 7题人工审核报告

**日期**: 2024-12-30  
**测试方案**: 方案A（检索后直接生成SQL）  
**提示词**: 统一（去掉"使用NOW()函数"要求）  
**温度**: 0.1（两模型一致）

---

## 📊 汇总表格

| # | 问题 | Qwen2.5-32B | Qwen3 MoE | 差异说明 |
|:---:|:-----|:---:|:---:|:-----|
| 1 | ciscoA上个月告警分类统计 | ✅ | ✅ | 两者一致 |
| 2 | down状态超3月的设备清单 | ❌ | ❌ | 都缺少event_history表 |
| 3 | 平台客户数量 | ✅ | ✅ | 两者一致 |
| 4 | 平台设备数量 | ✅ | ✅ | 两者一致 |
| 5 | 上月新上线设备数 | ✅ | ⚠️ | 32B用ONLINE_TIME，MoE用CREATE_TIME |
| 6 | 上月下线设备数 | ✅ | ✅ | 两者一致 |
| 7 | 某客户设备近一周告警 | ✅ | ✅ | 两者一致 |
| | **正确率** | **6/7 (85.7%)** | **5.5/7 (78.6%)** | **32B略优** |

---

## 🔍 逐题详细审核

### 第 1 题
**问题**: 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计

**DeepSeek 参考答案**:
```sql
SELECT `event_type_name`, COUNT(`event_id`) AS `alarm_count`
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.ne_id = t_bz_config_ci_ne_root.ne_id
WHERE t_bz_config_ci_ne_root.host_name LIKE '%ciscoA%' 
    AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY `event_type_name`
```

**Qwen2.5-32B** ✅
```sql
SELECT e.EVENT_TYPE_NAME, COUNT(*) AS alarm_count
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'ciscoA' 
    AND e.EVENT_TIME >= DATE_FORMAT(CURDATE() - INTERVAL DAYOFMONTH(CURDATE()) + 1 DAY, '%Y-%m-01')
GROUP BY e.EVENT_TYPE_NAME;
```

**Qwen3 MoE** ✅
```sql
SELECT e.EVENT_TYPE_NAME AS alarm_type, COUNT(*) AS alarm_count
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.HOST_NAME = 'ciscoA'
    AND e.EVENT_TIME >= DATE_SUB(DATE_TRUNC('month', CURRENT_DATE), INTERVAL 1 MONTH)
GROUP BY e.EVENT_TYPE_NAME;
```

**点评**: 两者结构一致，都正确使用了 event_history + ne_root 表，GROUP BY 正确。

---

### 第 2 题
**问题**: 列出平台上设备device state down状态超过3个月的设备清单及客户名称

**DeepSeek 参考答案**:
```sql
SELECT ne.NE_ID, ne.HOST_NAME, c.CUSTOMER_NAME
FROM t_bz_config_ci_ne_root ne
JOIN t_bz_config_customer c ON ne.CUSTOMER_ID = c.CUSTOMER_ID
JOIN event_history e ON ne.NE_ID = e.NE_ID
WHERE e.EVENT_NAME LIKE 'Device state%' 
    AND e.EVENT_TIME <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY ne.NE_ID, c.CUSTOMER_NAME
```

**Qwen2.5-32B** ❌
```sql
SELECT c.CUSTOMER_NAME, d.HOST_NAME
FROM t_bz_config_customer c
JOIN t_bz_config_ci_ne_root d ON c.CUSTOMER_ID = d.CUSTOMER_ID
WHERE d.NE_STATUS = 'down' AND d.OFFLINE_TIME <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**Qwen3 MoE** ❌
```sql
SELECT c.CUSTOMER_NAME, d.HOST_NAME AS device_name, d.OFFLINE_TIME
FROM t_bz_config_ci_ne_root d
JOIN t_bz_config_customer c ON d.CUSTOMER_ID = c.CUSTOMER_ID
WHERE d.NE_STATUS = 'down' AND d.OFFLINE_TIME <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**点评**: 两者都**缺少 event_history 表**。题目要求查询"device state down"是告警事件名称，需要从event_history获取，但两个模型都误解为直接查设备状态字段。

---

### 第 3 题
**问题**: 现在平台上有多少家客户

**Qwen2.5-32B** ✅
```sql
SELECT COUNT(*) FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```

**Qwen3 MoE** ✅
```sql
SELECT COUNT(*) AS customer_count FROM t_bz_config_customer WHERE IS_ACTIVE = 1;
```

**点评**: 完全一致，都正确。

---

### 第 4 题
**问题**: 现在平台上有多少台设备

**Qwen2.5-32B** ✅
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

**Qwen3 MoE** ✅
```sql
SELECT COUNT(*) AS device_count FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

**点评**: 完全一致，都正确。

---

### 第 5 题
**问题**: 上个月上线的新设备有多少

**DeepSeek 参考答案**:
```sql
SELECT COUNT(`CI_ID`) AS `new_device_count`
FROM t_bz_config_ci_ne_root
WHERE ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
```

**Qwen2.5-32B** ✅
```sql
SELECT COUNT(*) 
FROM t_bz_config_ci_ne_root 
WHERE IS_ONLINE = 1 AND ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
```

**Qwen3 MoE** ⚠️
```sql
SELECT COUNT(*) AS new_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 1
  AND CREATE_TIME >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
  AND CREATE_TIME < DATE_FORMAT(CURDATE(), '%Y-%m-01');
```

**点评**: 
- **32B**: 正确使用 `ONLINE_TIME` 字段
- **MoE**: 使用了 `CREATE_TIME` 而非 `ONLINE_TIME`，语义有偏差（创建时间≠上线时间）

---

### 第 6 题
**问题**: 上个月下线的设备有多少

**Qwen2.5-32B** ✅
```sql
SELECT COUNT(*) 
FROM t_bz_config_ci_ne_root 
WHERE NE_STATUS = '下线' AND OFFLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
```

**Qwen3 MoE** ✅
```sql
SELECT COUNT(*) AS offline_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_DELETED = 0 AND OFFLINE_TIME >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01');
```

**点评**: 两者都正确使用了 `OFFLINE_TIME` 字段。

---

### 第 7 题
**问题**: 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？

**Qwen2.5-32B** ✅
```sql
SELECT eh.EVENT_TYPE_NAME AS 告警类型, eh.EVENT_TIME AS 告警时间, eh.RECOVER_TIME AS 恢复时间
FROM event_history eh
JOIN t_bz_config_ci_ne_root ci ON eh.NE_ID = ci.NE_ID
JOIN t_bz_config_customer c ON ci.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_ID = ? AND eh.EVENT_TIME >= NOW() - INTERVAL 7 DAY;
```

**Qwen3 MoE** ✅
```sql
SELECT DISTINCT eh.EVENT_TYPE_NAME AS alarm_type, eh.EVENT_TIME AS alarm_time, eh.RECOVER_TIME AS recovery_time
FROM event_history eh
JOIN t_bz_config_ci_ne_root ne ON eh.NE_ID = ne.NE_ID
JOIN t_bz_config_customer c ON eh.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_ID = 123 AND eh.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

**点评**: 两者都正确 JOIN 了三张表（event_history + ne_root + customer）。

---

## 📌 结论

| 对比项 | Qwen2.5-32B | Qwen3 MoE |
|:------|:-----------|:----------|
| **7题正确率** | **6/7 (85.7%)** | 5.5/7 (78.6%) |
| **第5题字段选择** | ✅ ONLINE_TIME | ⚠️ CREATE_TIME |
| **稳定性** | 稳定 | 稳定（3轮测试一致） |
| **推荐** | **✅ 生产环境推荐** | 可用，但字段选择稍弱 |

**最终结论**: **Qwen2.5-32B 略优**，在字段选择上更准确。
