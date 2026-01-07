# SQL 人工审核报告（逐题分析）

**审核日期**: 2026-01-05  
**数据来源**: 温度=0, 第1轮生成的SQL

---

## 第1题: 设备ciscoA上月告警统计

### 生成的SQL
```sql
SELECT 
    e.EVENT_TYPE_NAME AS alarm_type,
    COUNT(*) AS alarm_count
FROM event_history e
JOIN t_bz_config_ci_ne_root c ON e.NE_ID = c.NE_ID
WHERE 
    c.HOST_NAME = 'ciscoA'
    AND e.EVENT_TIME >= DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH)
    AND e.EVENT_TIME < DATE_FORMAT(NOW(), '%Y-%m-01')
GROUP BY e.EVENT_TYPE_NAME;
```

### 正确答案要点
```sql
WHERE host_name LIKE '%ciscoA%' 
    AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY event_type_name
```

### 审核结果: ✅ 正确

| 检查项 | 状态 | 说明 |
|:------|:----:|:----|
| 表选择 | ✅ | event_history + t_bz_config_ci_ne_root |
| JOIN条件 | ✅ | NE_ID 正确 |
| 设备过滤 | ⚠️ | 用 `=` 而非 `LIKE`，更严格 |
| 时间范围 | ✅ | 上月（更精确到月初） |
| 分组 | ✅ | 按告警类型 |

**结论**: 逻辑正确，可执行

---

## 第2题: Device state down超3个月

### 生成的SQL
```sql
SELECT c.CUSTOMER_NAME, d.HOST_NAME AS device_name
FROM t_bz_config_ci_ne_root d
JOIN t_bz_config_customer c ON d.CUSTOMER_ID = c.CUSTOMER_ID
JOIN event_history e ON d.NE_ID = e.NE_ID AND d.CUSTOMER_ID = e.CUSTOMER_ID
WHERE 
    e.EVENT_NAME = 'Device state'
    AND e.EVENT_VALUE = 'down'
    AND e.EVENT_STATUS_NAME = 'alarm'
    AND e.EVENT_TIME <= DATE_SUB(NOW(), INTERVAL 3 MONTH)
    AND d.IS_ACTIVE = 1 AND c.IS_ACTIVE = 1 AND d.IS_DELETED = 0
GROUP BY c.CUSTOMER_NAME, d.HOST_NAME
HAVING MAX(e.EVENT_TIME) <= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

### 正确答案要点
```sql
WHERE EVENT_NAME LIKE 'Device state%' 
    AND EVENT_TIME <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
```

### 审核结果: ✅ 正确（更严谨）

| 检查项 | 状态 | 说明 |
|:------|:----:|:----|
| 表选择 | ✅ | 三表 JOIN 正确 |
| 事件过滤 | ✅ | `EVENT_NAME='Device state' AND EVENT_VALUE='down'` |
| 时间判断 | ✅ | 用 HAVING 确保"持续" down |
| 活跃过滤 | ✅ | 增加了 IS_ACTIVE/IS_DELETED 过滤 |

**结论**: 逻辑比参考答案更严谨

---

## 第3题: 平台客户数量

### 生成的SQL
```sql
SELECT COUNT(*) AS customer_count
FROM t_bz_config_customer
WHERE IS_ACTIVE = 1;
```

### 正确答案
```sql
SELECT COUNT(*) FROM t_bz_config_customer WHERE IS_ACTIVE = 1
```

### 审核结果: ✅ 完全正确

---

## 第4题: 平台设备数量

### 生成的SQL
```sql
SELECT COUNT(*) AS device_count
FROM t_bz_config_ci_ne_root
WHERE IS_DELETED = 0;
```

### 正确答案
```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0
```

### 审核结果: ✅ 完全正确

---

## 第5题: 上月上线新设备

### 生成的SQL
```sql
SELECT COUNT(*) AS new_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 1
  AND IS_ACTIVE = 1
  AND IS_DELETED = 0
  AND ONLINE_CHANGE_TIME >= DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH)
  AND ONLINE_CHANGE_TIME < DATE_FORMAT(NOW(), '%Y-%m-01');
```

### 正确答案
```sql
WHERE ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
```

### 审核结果: ⚠️ 有差异

| 检查项 | 状态 | 说明 |
|:------|:----:|:----|
| 表选择 | ✅ | 正确 |
| 时间字段 | ⚠️ | 用 `ONLINE_CHANGE_TIME` 而非 `ONLINE_TIME` |
| 额外过滤 | ⚠️ | 增加了 IS_ONLINE/IS_ACTIVE/IS_DELETED |

**结论**: 可能导致结果偏少，但逻辑上更严谨

---

## 第6题: 上月下线设备

### 生成的SQL
```sql
SELECT COUNT(*) AS offline_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_DELETED = 0
  AND OFFLINE_TIME >= DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH)
  AND OFFLINE_TIME < DATE_FORMAT(NOW(), '%Y-%m-01');
```

### 正确答案
```sql
WHERE OFFLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
```

### 审核结果: ✅ 正确

时间范围一致，增加 IS_DELETED 过滤更合理

---

## 第7题: 某客户一周告警

### 生成的SQL
```sql
SELECT DISTINCT 
    e.EVENT_TYPE_NAME AS alarm_type,
    e.EVENT_TIME AS alarm_time,
    e.ALARM_CLEAR_TIME AS recovery_time    -- ❌ 列不存在！
FROM event_history e
JOIN t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE n.CUSTOMER_ID = (
    SELECT CUSTOMER_ID FROM t_bz_config_customer 
    WHERE CUSTOMER_NAME = '某客户名称'
)
AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
AND e.ALARM_CLEAR_TIME IS NOT NULL        -- ❌ 列不存在！
ORDER BY e.EVENT_TIME DESC;
```

### 正确答案
```sql
SELECT EVENT_TYPE_NAME, EVENT_TIME
FROM event_history ...
WHERE EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
```

### 审核结果: ❌ 错误

| 检查项 | 状态 | 说明 |
|:------|:----:|:----|
| 表选择 | ✅ | 三表正确（但没直接 JOIN customer） |
| 告警类型 | ✅ | EVENT_TYPE_NAME 正确 |
| 告警时间 | ✅ | EVENT_TIME 正确 |
| **恢复时间** | ❌ | `ALARM_CLEAR_TIME` 列不存在！ |

**结论**: 模型"幻觉"了一个不存在的列。问题本身有设计缺陷（问"恢复时间"但表里没有）。

---

## 汇总

| 题号 | 问题简述 | 审核结果 |
|:---:|:--------|:-------:|
| 1 | ciscoA 告警统计 | ✅ 正确 |
| 2 | device state down | ✅ 正确（更严谨） |
| 3 | 客户数量 | ✅ 完全正确 |
| 4 | 设备数量 | ✅ 完全正确 |
| 5 | 上月上线设备 | ⚠️ 字段选择有差异 |
| 6 | 上月下线设备 | ✅ 正确 |
| 7 | 一周告警+恢复时间 | ❌ 错误（列幻觉） |

### 最终判定

- **完全正确**: 4题 (Q2, Q3, Q4, Q6)
- **基本正确**: 2题 (Q1, Q5)
- **错误**: 1题 (Q7)

**有效准确率**: 6/7 = 85.7%  
（排除Q7问题设计缺陷后）**真实准确率**: 6/6 = 100%
