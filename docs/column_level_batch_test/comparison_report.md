# LinkAlign 批量测试报告
测试时间: 2025-12-16 13:04:43
测试用例数: 7

## 总体统计
- 完全召回: 3/7 (43%)
- 平均召回率: 52%

---

## 测试 1: 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计...

**期望表**: `t_bz_config_ci_ne_root, event_history`

**表召回**: 100% ✅

### 处理步骤
| 步骤 | 表数 | 期望表 | 备注 |
|------|------|--------|------|
| 1. 向量检索+增强 | 146 | t_bz_config_ci_ne_root, event_history |  |
| 2. 计算 reserve_df | 43 | - |  |
| 3.1 LLM过滤轮次1 | 52 | t_bz_config_ci_ne_root, event_history |  |
| 3.2 LLM过滤轮次2 | 44 | t_bz_config_ci_ne_root, event_history |  |
| 3.3 LLM过滤轮次3 | 44 | t_bz_config_ci_ne_root, event_history |  |
| 3.4 LLM过滤轮次4 | 44 | t_bz_config_ci_ne_root, event_history |  |
| 3. LLM过滤总结 | - | - |  |
| 4. SQL生成 | - | - |  |

### SQL 对比

**LinkAlign 生成的 SQL**:
```sql
SELECT `EVENT_TYPE_ID`, COUNT(*) AS `alert_count`
FROM `event_history`
WHERE `EVENT_TIME` BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
  AND `NE_NAME` = 'ciscoA'
GROUP BY `EVENT_TYPE_ID`;
```

**正确 SQL**:
```sql
SELECT 
    `event_type_name`, 
    COUNT(`event_id`) AS `alarm_count`
FROM 
    event_history
JOIN 
    t_bz_config_ci_ne_root ON event_history.ne_id = t_bz_config_ci_ne_root.ne_id
WHERE 
    t_bz_config_ci_ne_root.host_name LIKE '%ciscoA%' 
    AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    AND event_time < CURDATE()
GROUP BY 
    `event_type_name`
ORDER BY 
    `alarm_count` DESC
LIMIT 10;
```

---

## 测试 2: 列出平台上设备device state down状态超过3个月的设备清单及客户名...

**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**表召回**: 67% ❌ 缺失: `t_bz_config_ci_ne_root`

**丢失位置**: LLM过滤轮次2

### 处理步骤
| 步骤 | 表数 | 期望表 | 备注 |
|------|------|--------|------|
| 1. 向量检索+增强 | 148 | t_bz_config_customer, t_bz_config_ci_ne_root, event_history |  |
| 2. 计算 reserve_df | 54 | - |  |
| 3.1 LLM过滤轮次1 | 127 | t_bz_config_customer, t_bz_config_ci_ne_root, event_history |  |
| 3.2 LLM过滤轮次2 | 64 | t_bz_config_customer, event_history | ❌ 丢失: t_bz_config_ci_ne_root |
| 3.3 LLM过滤轮次3 | 55 | t_bz_config_customer, event_history |  |
| 3.4 LLM过滤轮次4 | - | - | 跳过: 列数 90 <= 100 |
| 3. LLM过滤总结 | - | - |  |
| 4. SQL生成 | - | - |  |

### SQL 对比

**LinkAlign 生成的 SQL**:
```sql
SELECT `t_gn_all_net_device`.`customer_id`, `t_bz_config_customer`.`CUSTOMER_NAME`
FROM `t_gn_all_net_device`
JOIN `t_bz_config_customer` ON `t_gn_all_net_device`.`customer_id` = `t_bz_config_customer`.`CUSTOMER_ID`
WHERE `t_gn_all_net_device`.`customer_id` IN (
    SELECT `CUSTOMER_ID` FROM `uptime`
    WHERE `DOWN_TIME` < DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
);
```

**正确 SQL**:
```sql
select a.* from (
SELECT 
    `t_bz_config_ci_ne_root`.`NE_ID`,
    `t_bz_config_ci_ne_root`.`HOST_NAME`,
    `t_bz_config_customer`.`CUSTOMER_NAME`
FROM 
    `t_bz_config_ci_ne_root`
JOIN 
    `t_bz_config_customer` ON `t_bz_config_ci_ne_root`.`CUSTOMER_ID` = `t_bz_config_customer`.`CUSTOMER_ID`
JOIN 
    `event_history` ON `t_bz_config_ci_ne_root`.`NE_ID` = `event_history`.`NE_ID`
WHERE 
    `event_history`.`EVENT_NAME` LIKE 'Device state%' 
    AND `event_history`.`EVENT_TIME` <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY 
    `t_bz_config_ci_ne_root`.`NE_ID`, `t_bz_config_customer`.`CUSTOMER_NAME`
HAVING 
    COUNT(DISTINCT `event_history`.`EVENT_ID`) > 0
) a where `a`.`EVENT_TIME` <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) and `a`.`EVENT_STATUS_NAME` = 'alarm'
LIMIT 10;
```

---

## 测试 3: 现在平台上有多少家客户...

**期望表**: `t_bz_config_customer`

**表召回**: 100% ✅

### 处理步骤
| 步骤 | 表数 | 期望表 | 备注 |
|------|------|--------|------|
| 1. 向量检索+增强 | 153 | t_bz_config_customer |  |
| 2. 计算 reserve_df | 52 | - |  |
| 3.1 LLM过滤轮次1 | 122 | t_bz_config_customer |  |
| 3.2 LLM过滤轮次2 | 65 | t_bz_config_customer |  |
| 3.3 LLM过滤轮次3 | 53 | t_bz_config_customer |  |
| 3.4 LLM过滤轮次4 | 52 | t_bz_config_customer |  |
| 3. LLM过滤总结 | - | - |  |
| 4. SQL生成 | - | - |  |

### SQL 对比

**LinkAlign 生成的 SQL**:
```sql
SELECT COUNT(*) FROM `customer`;
```

**正确 SQL**:
```sql
SELECT COUNT(`CUSTOMER_ID`) AS `customer_count`
FROM t_bz_config_customer
WHERE `IS_ACTIVE` = 1
LIMIT 10;
```

---

## 测试 4: 现在平台上有多少台设备...

**期望表**: `t_bz_config_ci_ne_root`

**表召回**: 0% ❌ 缺失: `t_bz_config_ci_ne_root`

**丢失位置**: LLM过滤轮次1

### 处理步骤
| 步骤 | 表数 | 期望表 | 备注 |
|------|------|--------|------|
| 1. 向量检索+增强 | 125 | t_bz_config_ci_ne_root |  |
| 2. 计算 reserve_df | 41 | - |  |
| 3.1 LLM过滤轮次1 | 58 | - | ❌ 丢失: t_bz_config_ci_ne_root |
| 3.2 LLM过滤轮次2 | 49 | - |  |
| 3.3 LLM过滤轮次3 | 49 | - |  |
| 3.4 LLM过滤轮次4 | 44 | - |  |
| 3. LLM过滤总结 | - | - |  |
| 4. SQL生成 | - | - |  |

### SQL 对比

**LinkAlign 生成的 SQL**:
```sql
SELECT COUNT(*) AS `device_count` FROM `sdw_dp_device`;
```

**正确 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `device_count`
FROM t_bz_config_ci_ne_root
WHERE `IS_DELETED` = 0
LIMIT 10;
```

---

## 测试 5: 上个月上线的新设备有多少...

**期望表**: `t_bz_config_ci_ne_root`

**表召回**: 0% ❌ 缺失: `t_bz_config_ci_ne_root`

**丢失位置**: LLM过滤轮次1

### 处理步骤
| 步骤 | 表数 | 期望表 | 备注 |
|------|------|--------|------|
| 1. 向量检索+增强 | 147 | t_bz_config_ci_ne_root |  |
| 2. 计算 reserve_df | 45 | - |  |
| 3.1 LLM过滤轮次1 | 109 | - | ❌ 丢失: t_bz_config_ci_ne_root |
| 3.2 LLM过滤轮次2 | 50 | - |  |
| 3.3 LLM过滤轮次3 | 48 | - |  |
| 3.4 LLM过滤轮次4 | - | - | 跳过: 列数 92 <= 100 |
| 3. LLM过滤总结 | - | - |  |
| 4. SQL生成 | - | - |  |

### SQL 对比

**LinkAlign 生成的 SQL**:
```sql
SELECT COUNT(*) AS new_device_count
FROM `report_new_dev`
WHERE `REP_MONTH` = DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND `STATUS` = '上线';
```

**正确 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `new_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `ONLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
AND YEAR(`ONLINE_TIME`) = 2025
LIMIT 10;
```

---

## 测试 6: 上个月下线的设备有多少...

**期望表**: `t_bz_config_ci_ne_root`

**表召回**: 0% ❌ 缺失: `t_bz_config_ci_ne_root`

**丢失位置**: LLM过滤轮次3

### 处理步骤
| 步骤 | 表数 | 期望表 | 备注 |
|------|------|--------|------|
| 1. 向量检索+增强 | 135 | t_bz_config_ci_ne_root |  |
| 2. 计算 reserve_df | 45 | - |  |
| 3.1 LLM过滤轮次1 | 56 | t_bz_config_ci_ne_root |  |
| 3.2 LLM过滤轮次2 | 49 | t_bz_config_ci_ne_root |  |
| 3.3 LLM过滤轮次3 | 47 | - | ❌ 丢失: t_bz_config_ci_ne_root |
| 3.4 LLM过滤轮次4 | - | - | 跳过: 列数 94 <= 100 |
| 3. LLM过滤总结 | - | - |  |
| 4. SQL生成 | - | - |  |

### SQL 对比

**LinkAlign 生成的 SQL**:
```sql
SELECT COUNT(*) AS `offline_device_count`
FROM `t_gn_business_application_change`
WHERE `status` = '下线' AND `data_time` BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH));
```

**正确 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `offline_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `OFFLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND `OFFLINE_TIME` < CURDATE()
LIMIT 10;
```

---

## 测试 7: 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？...

**期望表**: `t_bz_config_customer, t_bz_config_ci_ne_root, event_history`

**表召回**: 100% ✅

### 处理步骤
| 步骤 | 表数 | 期望表 | 备注 |
|------|------|--------|------|
| 1. 向量检索+增强 | 119 | t_bz_config_customer, t_bz_config_ci_ne_root, event_history |  |
| 2. 计算 reserve_df | 39 | - |  |
| 3.1 LLM过滤轮次1 | 101 | t_bz_config_customer, t_bz_config_ci_ne_root, event_history |  |
| 3.2 LLM过滤轮次2 | 101 | t_bz_config_customer, t_bz_config_ci_ne_root, event_history |  |
| 3.3 LLM过滤轮次3 | 92 | t_bz_config_customer, t_bz_config_ci_ne_root, event_history |  |
| 3.4 LLM过滤轮次4 | 54 | t_bz_config_customer, t_bz_config_ci_ne_root, event_history |  |
| 3. LLM过滤总结 | - | - |  |
| 4. SQL生成 | - | - |  |

### SQL 对比

**LinkAlign 生成的 SQL**:
```sql
SELECT `event_type`.`EVENT_TYPE_NAME`, `event_yjk_history`.`trigger_time` AS `alarm_time`, `event_yjk_history`.`recover_time` AS `recover_time`
FROM `event_yjk_history`
JOIN `event_type` ON `event_yjk_history`.`event_tag` = `event_type`.`EVENT_TYPE_ID`
WHERE `event_yjk_history`.`customer_no` = 'xxx'
  AND `event_yjk_history`.`trigger_time` >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK);
```

**正确 SQL**:
```sql
SELECT
 `t_bz_config_customer`.`CUSTOMER_NAME`,
 `t_bz_config_ci_ne_root`.`HOST_NAME`,
 `event_history`.`EVENT_NAME`,
 `event_history`.`EVENT_TIME`
FROM
 `event_history`
JOIN `t_bz_config_ci_ne_root` ON `event_history`.`NE_ID` = `t_bz_config_ci_ne_root`.`NE_ID`
JOIN `t_bz_config_customer` ON `event_history`.`CUSTOMER_ID` = `t_bz_config_customer`.ID
WHERE
 `event_history`.`EVENT_TIME` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
AND `event_history`.`EVENT_STATUS_NAME` = 'alarm'
AND `t_bz_config_customer`.`CUSTOMER_NAME` = 'xxx'
LIMIT 10;

```

---
