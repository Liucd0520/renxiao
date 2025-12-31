# 表级别方案端到端测试报告

测试时间: 2025-12-16 14:19:16
**检索模式**: Dense-only（未启用混合检索）

## 总体统计

| 指标 | 结果 |
|------|------|
| 测试用例数 | 7 |
| 表完全召回 | 4/7 (57%) |
| 平均表召回率 | 74% |
| **平均 SQL 评分** | **54/100** |
| 优秀(≥80分) | 0/7 (0%) |

---

## 测试 1: 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计...

**期望表**: `event_history, t_bz_config_ci_ne_root`

**表召回率**: 50%
 ❌ 缺失: `t_bz_config_ci_ne_root`


### 处理步骤

| 步骤 | 耗时 | 详情 |
|------|------|------|
| A. 表级别向量检索 | 2.9s | 检索 10 表 |
| B. 加载完整 Schema | 0.0s | 加载 10 表 (3908 字符) |
| C. LLM 生成 SQL | 1.5s | 生成 269 字符 SQL |
| D. LLM 评判 SQL 正确性 | 15.1s | - |

### SQL 正确性评判: 60/100 ⚠️

| 评判项 | 结果 |
|--------|------|
| 表选择 | 错误 - 生成的SQL仅使用了t_bz_sdn_alarm表，而正确的SQL需要通过JOIN操作关联event_history和t_bz_config_ci_ne_root表来获取告警类型信息 |
| 列选择 | 错误 - 生成的SQL使用了ALARM_TYPE列，而正确的SQL使用了event_type_name列，且正确的SQL使用COUNT(event_id)更精确地统计具体事件数量 |
| 连接条件 | 不适用 - 生成的SQL没有使用JOIN操作，而正确的SQL需要通过ne_id字段连接两个表 |
| 过滤条件 | 部分正确 - 生成的SQL使用了BETWEEN...AND CURDATE()，但正确的SQL使用更精确的event_time >= ... AND event_time < CURDATE()，避免包含当前日期 |
| 聚合逻辑 | 部分正确 - 生成的SQL使用了GROUP BY ALARM_TYPE，但若ALARM_TYPE字段与正确的SQL中的event_type_name不对应，会导致分类统计错误 |

**总结**: 表结构和字段映射存在关键差异，导致无法正确获取告警类型分类数据


### SQL 对比

**生成的 SQL**:
```sql
SELECT `t_bz_sdn_alarm`.`ALARM_TYPE`, COUNT(*) AS `alarm_count`
FROM `t_bz_sdn_alarm`
WHERE `t_bz_sdn_alarm`.`DEVICE_NAME` = 'ciscoA'
  AND `t_bz_sdn_alarm`.`OCCUR_TIME` BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE()
GROUP BY `t_bz_sdn_alarm`.`ALARM_TYPE`;
```

**正确的 SQL**:
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

## 测试 2: 列出平台上设备device state down状态超过3个月的设备清单及客户名称...

**期望表**: `event_history, t_bz_config_customer, t_bz_config_ci_ne_root`

**表召回率**: 33%
 ❌ 缺失: `event_history, t_bz_config_customer`


### 处理步骤

| 步骤 | 耗时 | 详情 |
|------|------|------|
| A. 表级别向量检索 | 0.1s | 检索 10 表 |
| B. 加载完整 Schema | 0.0s | 加载 10 表 (3986 字符) |
| C. LLM 生成 SQL | 2.0s | 生成 480 字符 SQL |
| D. LLM 评判 SQL 正确性 | 18.3s | - |

### SQL 正确性评判: 40/100 ❌

| 评判项 | 结果 |
|--------|------|
| 表选择 | 错误 - 生成SQL使用了t_dc_config_ci_ne_root和t_dc_change_status表，而正确SQL使用了t_bz_config_ci_ne_root、t_bz_config_customer和event_history表，表名不一致且缺少关键事件表 |
| 列选择 | 错误 - 生成SQL错误地将t_bz_config_ci_ne_root的STATUS_NAME字段作为客户名称，且选择了NE_IP、GROUP_NAME等非用户要求的字段，正确SQL选择了NE_ID、HOST_NAME和CUSTOMER_NAME |
| 连接条件 | 错误 - 生成SQL错误地通过STATUS_ID连接状态表，而正确SQL通过NE_ID连接设备表和事件表，且缺少客户表连接 |
| 过滤条件 | 错误 - 生成SQL仅使用了状态名称和DOWN_TIME字段，而正确SQL需要同时满足事件名称、事件时间、事件状态等多个条件 |
| 聚合逻辑 | 不适用 - 生成SQL未使用GROUP BY或COUNT等聚合操作，而正确SQL使用了GROUP BY和HAVING来确保事件记录有效性 |

**总结**: 生成SQL存在表结构、字段选择和过滤条件的重大错误，无法正确获取所需数据


### SQL 对比

**生成的 SQL**:
```sql
SELECT `t_dc_config_ci_ne_root`.`NE_IP` AS device_ip, `t_dc_config_ci_ne_root`.`GROUP_NAME` AS group_name, `t_dc_config_ci_ne_root`.`CUSTOMER_ID` AS customer_id, `t_bz_config_ci_ne_root`.`STATUS_NAME` AS customer_name
FROM `t_dc_config_ci_ne_root`
JOIN `t_dc_change_status` ON `t_dc_config_ci_ne_root`.`STATUS_ID` = `t_dc_change_status`.`STATUS_ID`
WHERE `t_dc_change_status`.`STATUS_NAME` = 'down'
AND `t_dc_config_ci_ne_root`.`DOWN_TIME` < DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**正确的 SQL**:
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

**表召回率**: 100%
 ✅


### 处理步骤

| 步骤 | 耗时 | 详情 |
|------|------|------|
| A. 表级别向量检索 | 0.1s | 检索 10 表 |
| B. 加载完整 Schema | 0.0s | 加载 10 表 (3642 字符) |
| C. LLM 生成 SQL | 0.3s | 生成 62 字符 SQL |
| D. LLM 评判 SQL 正确性 | 12.9s | - |

### SQL 正确性评判: 60/100 ⚠️

| 评判项 | 结果 |
|--------|------|
| 表选择 | 正确 - 两者都使用了正确的客户配置表t_bz_config_customer |
| 列选择 | 部分正确 - COUNT(*)虽然语法正确，但不如COUNT(CUSTOMER_ID)精确，可能包含无效记录 |
| 连接条件 | 不适用 - 查询中没有JOIN操作 |
| 过滤条件 | 错误 - 缺少IS_ACTIVE=1的过滤条件，会统计所有客户包括非活跃客户 |
| 聚合逻辑 | 正确 - 使用COUNT函数进行聚合统计，但未配合过滤条件导致结果不准确 |

**总结**: 生成的SQL缺少关键过滤条件，可能导致统计结果包含非活跃客户。


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(*) AS customer_count FROM `t_bz_config_customer`;
```

**正确的 SQL**:
```sql
SELECT COUNT(`CUSTOMER_ID`) AS `customer_count`
FROM t_bz_config_customer
WHERE `IS_ACTIVE` = 1
LIMIT 10;
```

---

## 测试 4: 现在平台上有多少台设备...

**期望表**: `t_bz_config_ci_ne_root`

**表召回率**: 100%
 ✅


### 处理步骤

| 步骤 | 耗时 | 详情 |
|------|------|------|
| A. 表级别向量检索 | 0.1s | 检索 10 表 |
| B. 加载完整 Schema | 0.0s | 加载 10 表 (4297 字符) |
| C. LLM 生成 SQL | 0.4s | 生成 62 字符 SQL |
| D. LLM 评判 SQL 正确性 | 8.5s | - |

### SQL 正确性评判: 50/100 ❌

| 评判项 | 结果 |
|--------|------|
| 表选择 | 正确 - 两者都使用了正确的表t_bz_config_ci_ne_root |
| 列选择 | 部分正确 - 生成SQL使用COUNT(*)可能包含无效记录，正确SQL使用COUNT(CI_ID)更准确 |
| 连接条件 | 不适用 - 两个SQL都没有使用JOIN操作 |
| 过滤条件 | 错误 - 生成SQL缺少IS_DELETED=0的过滤条件，会导致统计包含已删除设备 |
| 聚合逻辑 | 正确 - 两者都使用了正确的COUNT聚合函数 |

**总结**: 生成SQL缺少关键过滤条件，会导致统计结果包含已删除设备，与用户需求不符。


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(*) AS device_count FROM `t_bz_config_ci_ne_root`;
```

**正确的 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `device_count`
FROM t_bz_config_ci_ne_root
WHERE `IS_DELETED` = 0
LIMIT 10;
```

---

## 测试 5: 上个月上线的新设备有多少...

**期望表**: `t_bz_config_ci_ne_root`

**表召回率**: 100%
 ✅


### 处理步骤

| 步骤 | 耗时 | 详情 |
|------|------|------|
| A. 表级别向量检索 | 0.1s | 检索 10 表 |
| B. 加载完整 Schema | 0.0s | 加载 10 表 (5028 字符) |
| C. LLM 生成 SQL | 1.7s | 生成 372 字符 SQL |
| D. LLM 评判 SQL 正确性 | 15.7s | - |

### SQL 正确性评判: 40/100 ❌

| 评判项 | 结果 |
|--------|------|
| 表选择 | 错误 - 生成的SQL错误地引入了sub_change_num表，而正确的SQL仅使用了t_bz_config_ci_ne_root表。用户问题关注的是设备上线时间，无需关联其他表。 |
| 列选择 | 部分正确 - 生成的SQL使用了CI_ID进行计数（与正确SQL一致），但错误地依赖了sub_change_num表的字段（如discovery_type）作为过滤条件。 |
| 连接条件 | 错误 - 生成的SQL使用了NE_ID与ne_id的JOIN，但用户问题未要求关联其他表，且正确的SQL未包含任何JOIN操作。 |
| 过滤条件 | 错误 - 生成的SQL使用了discovery_type='xxx'（无依据）和sub_change_num.data_time（可能非上线时间字段），而正确的SQL使用ONLINE_TIME字段并限制年份为2025。 |
| 聚合逻辑 | 正确 - 两者均使用COUNT函数统计记录数，且无GROUP BY错误。 |

**总结**: 


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(`t_bz_config_ci_ne_root`.`CI_ID`) AS new_device_count
FROM `t_bz_config_ci_ne_root`
JOIN `sub_change_num` ON `t_bz_config_ci_ne_root`.`NE_ID` = `sub_change_num`.`ne_id`
WHERE `sub_change_num`.`discovery_type` = 'xxx'
  AND `sub_change_num`.`data_time` BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE()
  AND `t_bz_config_ci_ne_root`.`IS_ONLINE` = 1;
```

**正确的 SQL**:
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

**表召回率**: 100%
 ✅


### 处理步骤

| 步骤 | 耗时 | 详情 |
|------|------|------|
| A. 表级别向量检索 | 0.1s | 检索 10 表 |
| B. 加载完整 Schema | 0.0s | 加载 10 表 (4670 字符) |
| C. LLM 生成 SQL | 1.0s | 生成 192 字符 SQL |
| D. LLM 评判 SQL 正确性 | 13.1s | - |

### SQL 正确性评判: 60/100 ⚠️

| 评判项 | 结果 |
|--------|------|
| 表选择 | 正确 - 两个SQL都使用了正确的表t_bz_config_ci_ne_root |
| 列选择 | 错误 - 生成SQL使用了ne_id而正确SQL使用了CI_ID，字段名存在差异且未明确说明是否等价 |
| 连接条件 | 不适用 - 两个SQL都没有使用JOIN操作，符合单表查询需求 |
| 过滤条件 | 错误 - 生成SQL使用IS_ONLINE=0和CALCTIME的BETWEEN条件，而正确SQL使用OFFLINE_TIME字段并精确限定上个月时间范围 |
| 聚合逻辑 | 正确 - 两个SQL都使用COUNT函数进行统计，但生成SQL缺少AS别名 |

**总结**: 生成SQL使用了错误的字段和不精确的时间范围过滤条件，导致统计结果可能不准确。


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(`ne_id`) 
FROM `t_bz_config_ci_ne_root` 
WHERE `IS_ONLINE` = 0 
  AND `CALCTIME` BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH));
```

**正确的 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `offline_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `OFFLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND `OFFLINE_TIME` < CURDATE()
LIMIT 10;
```

---

## 测试 7: 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？...

**期望表**: `event_history, t_bz_config_customer, t_bz_config_ci_ne_root`

**表召回率**: 33%
 ❌ 缺失: `t_bz_config_customer, t_bz_config_ci_ne_root`


### 处理步骤

| 步骤 | 耗时 | 详情 |
|------|------|------|
| A. 表级别向量检索 | 0.1s | 检索 10 表 |
| B. 加载完整 Schema | 0.0s | 加载 10 表 (4731 字符) |
| C. LLM 生成 SQL | 1.5s | 生成 372 字符 SQL |
| D. LLM 评判 SQL 正确性 | 19.8s | - |

### SQL 正确性评判: 65/100 ⚠️

| 评判项 | 结果 |
|--------|------|
| 表选择 | 部分正确 - 生成SQL使用了event_history和event_yjk_history表，但未连接设备表（如t_bz_config_ci_ne_root），可能无法获取具体设备信息 |
| 列选择 | 部分正确 - 包含EVENT_TYPE_NAME（告警类型）、EVENT_TIME（告警时间）和RECOVER_TIME（恢复时间）三个关键字段，但缺少设备标识字段 |
| 连接条件 | 部分正确 - 使用EVENT_ID=id连接两个表，但未连接设备表，可能无法定位具体设备 |
| 过滤条件 | 错误 - 使用event_yjk_history的trigger_time和customer_no字段，而正确的SQL应使用event_history的EVENT_TIME和EVENT_STATUS_NAME字段 |
| 聚合逻辑 | 不适用 - 两个SQL均未使用GROUP BY/聚合函数，符合查询需求 |

**总结**: 表连接不完整且过滤条件字段错误，导致可能无法准确获取设备告警信息


### SQL 对比

**生成的 SQL**:
```sql
SELECT `event_history`.EVENT_TYPE_NAME, `event_history`.EVENT_TIME, `event_history`.RECOVER_TIME
FROM `event_history`
JOIN `event_yjk_history` ON `event_history`.EVENT_ID = `event_yjk_history`.id
WHERE `event_yjk_history`.customer_no = 'xxx'
  AND `event_yjk_history`.trigger_time >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK)
  AND `event_yjk_history`.recover_time IS NOT NULL;
```

**正确的 SQL**:
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
