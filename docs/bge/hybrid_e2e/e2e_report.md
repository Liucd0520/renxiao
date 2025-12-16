# BGE-M3 混合检索端到端测试报告

测试时间: 2025-12-16 16:31:25

**检索模式**: Dense + Sparse 混合检索

**权重配置**: Dense=0.7, Sparse=0.3

## 总体统计

| 指标 | 结果 |
|------|------|
| 测试用例数 | 7 |
| 表完全召回 | 4/7 (57%) |
| 平均表召回率 | 74% |
| **平均 SQL 评分** | **51/100** |
| 优秀(≥80分) | 0/7 (0%) |

---

## 测试 1: 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计...

**期望表**: `event_history, t_bz_config_ci_ne_root`

**表召回率**: 50%
 ❌ 缺失: `event_history`


### 检索结果 (Top 5)

| 排名 | 表名 | Hybrid | Dense | Sparse |
|------|------|--------|-------|--------|
| 1 | t_bz_sdn_alarm  | 0.5021 | 0.6509 | 0.1550 |
| 2 | event_sdn  | 0.4835 | 0.6343 | 0.1316 |
| 3 | t_bz_incident_event_record  | 0.4757 | 0.6255 | 0.1261 |
| 4 | event_yjk_history  | 0.4693 | 0.6162 | 0.1265 |
| 5 | ne_syslog_filter_script  | 0.4486 | 0.5889 | 0.1212 |

### SQL 正确性评判: 60/100 ⚠️

**总结**: 生成的SQL未正确匹配表名和字段名，且连接条件可能错误，但聚合逻辑正确。


### SQL 对比

**生成的 SQL**:
```sql
SELECT `t_bz_sdn_alarm`.`ALARM_TYPE`, COUNT(*) AS `alarm_count`
FROM `t_bz_sdn_alarm`
JOIN `t_bz_config_ci_ne_root` ON `t_bz_sdn_alarm`.`DEVICE_IP` = `t_bz_config_ci_ne_root`.`NE_IP`
WHERE `t_bz_config_ci_ne_root`.`NE_NAME` = 'ciscoA'
  AND `t_bz_sdn_alarm`.`OCCUR_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
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

**期望表**: `event_history, t_bz_config_ci_ne_root, t_bz_config_customer`

**表召回率**: 33%
 ❌ 缺失: `event_history, t_bz_config_customer`


### 检索结果 (Top 5)

| 排名 | 表名 | Hybrid | Dense | Sparse |
|------|------|--------|-------|--------|
| 1 | uptime  | 0.4540 | 0.5991 | 0.1152 |
| 2 | t_gn_all_net_device  | 0.4474 | 0.5674 | 0.1675 |
| 3 | sdw_dp_device  | 0.4399 | 0.5630 | 0.1527 |
| 4 | ont_status  | 0.4372 | 0.5713 | 0.1243 |
| 5 | ne_business_severity  | 0.4301 | 0.5811 | 0.0777 |

### SQL 正确性评判: 50/100 ❌

**总结**: 生成的SQL未正确关联事件表和状态逻辑，且缺少聚合处理，无法准确筛选出"device state down"超过3个月的设备。


### SQL 对比

**生成的 SQL**:
```sql
SELECT `sdw_dp_device`.`dev_id`, `sdw_dp_device`.`dev_name`, `sdw_dp_device`.`customer_id`, `t_gn_all_net_device`.`region_name` AS `customer_name`
FROM `sdw_dp_device`
JOIN `t_gn_all_net_device` ON `sdw_dp_device`.`customer_id` = `t_gn_all_net_device`.`customer_id`
WHERE `sdw_dp_device`.`dev_id` IN (
    SELECT `ne_id` FROM `uptime` 
    WHERE `DOWN_TIME` < DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
)
AND `sdw_dp_device`.`dev_id` IN (
    SELECT `root_ne_id` FROM `ont_status` 
    WHERE `status` = 2
);
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


### 检索结果 (Top 5)

| 排名 | 表名 | Hybrid | Dense | Sparse |
|------|------|--------|-------|--------|
| 1 | customer  | 0.4129 | 0.5371 | 0.1229 |
| 2 | t_bz_config_customer ✅ | 0.4063 | 0.5288 | 0.1204 |
| 3 | customer_cloud_monitor_key  | 0.3926 | 0.5205 | 0.0942 |
| 4 | t_gn_all_net_device  | 0.3921 | 0.5273 | 0.0765 |
| 5 | t_bz_customer_poller_config  | 0.3918 | 0.5186 | 0.0959 |

### SQL 正确性评判: 50/100 ❌

**总结**: 生成的SQL表名和过滤条件与正确答案不一致，可能导致统计结果不准确或遗漏关键业务逻辑。


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(DISTINCT `customer`.`CUSTOMER_ID`) AS `customer_count`
FROM `customer`;
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


### 检索结果 (Top 5)

| 排名 | 表名 | Hybrid | Dense | Sparse |
|------|------|--------|-------|--------|
| 1 | t_gn_all_net_device  | 0.4316 | 0.5811 | 0.0828 |
| 2 | ne_business_severity  | 0.4128 | 0.5513 | 0.0896 |
| 3 | sdw_dp_device  | 0.4107 | 0.5425 | 0.1032 |
| 4 | t_gn_topo_device  | 0.4001 | 0.5278 | 0.1020 |
| 5 | t_bz_config_ci_ne_root ✅ | 0.3982 | 0.5347 | 0.0799 |

### SQL 正确性评判: 50/100 ❌

**总结**: 生成的SQL未正确选择表和过滤条件，可能导致统计结果包含无效数据。


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(`dev_id`) AS device_count 
FROM `sdw_dp_device`;
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


### 检索结果 (Top 5)

| 排名 | 表名 | Hybrid | Dense | Sparse |
|------|------|--------|-------|--------|
| 1 | t_gn_all_net_device  | 0.3788 | 0.5098 | 0.0731 |
| 2 | report_new_dev  | 0.3782 | 0.5190 | 0.0497 |
| 3 | t_bz_config_ci_ne_root ✅ | 0.3653 | 0.4819 | 0.0931 |
| 4 | sdw_dp_device  | 0.3649 | 0.4819 | 0.0918 |
| 5 | ne_template_access_config  | 0.3634 | 0.4907 | 0.0664 |

### SQL 正确性评判: 50/100 ❌

**总结**: 生成的SQL表名和过滤条件与正确答案不一致，可能导致统计结果错误。


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(*) AS new_device_count
FROM `report_new_dev`
WHERE `REPORT_TIME` BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE()
  AND `TYPE` = 'xxx';
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


### 检索结果 (Top 5)

| 排名 | 表名 | Hybrid | Dense | Sparse |
|------|------|--------|-------|--------|
| 1 | t_gn_all_net_device  | 0.3777 | 0.5083 | 0.0729 |
| 2 | uptime  | 0.3739 | 0.4932 | 0.0955 |
| 3 | t_bz_config_ci_ne_root ✅ | 0.3681 | 0.4919 | 0.0791 |
| 4 | ne_business_severity  | 0.3583 | 0.4788 | 0.0772 |
| 5 | sdw_dp_device  | 0.3569 | 0.4719 | 0.0885 |

### SQL 正确性评判: 50/100 ❌

**总结**: 生成的SQL表结构、过滤条件和聚合逻辑均存在偏差，无法准确统计上个月下线的设备数量。


### SQL 对比

**生成的 SQL**:
```sql
SELECT COUNT(*) 
FROM `uptime` u
JOIN `t_gn_all_net_device` d ON u.`CUSTOMER_ID` = d.`customer_id` AND u.`NE_ID` = d.`id`
WHERE u.`DOWN_TIME` BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE();
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

**期望表**: `event_history, t_bz_config_ci_ne_root, t_bz_config_customer`

**表召回率**: 33%
 ❌ 缺失: `event_history, t_bz_config_customer`


### 检索结果 (Top 5)

| 排名 | 表名 | Hybrid | Dense | Sparse |
|------|------|--------|-------|--------|
| 1 | event_yjk_history  | 0.5064 | 0.6470 | 0.1785 |
| 2 | t_bz_sdn_alarm  | 0.4865 | 0.6284 | 0.1553 |
| 3 | event_sdn  | 0.4827 | 0.6338 | 0.1301 |
| 4 | event_history_sdwan  | 0.4721 | 0.6143 | 0.1405 |
| 5 | t_bz_incident_event_record  | 0.4604 | 0.6045 | 0.1243 |

### SQL 正确性评判: 50/100 ❌

**总结**: 生成的SQL未正确关联客户表且缺少告警状态过滤条件，导致无法准确回答用户问题。


### SQL 对比

**生成的 SQL**:
```sql
SELECT `event_yjk_history`.`event_status`, `event_yjk_history`.`trigger_time`, `event_yjk_history`.`recover_time`, `event_yjk_history`.`event_tag` 
FROM `event_yjk_history` 
JOIN `t_bz_config_ci_ne_root` ON `event_yjk_history`.`device` = `t_bz_config_ci_ne_root`.`NE_IP` 
WHERE `event_yjk_history`.`customer_no` = 'xxx' 
  AND `event_yjk_history`.`trigger_time` >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK) 
  AND `event_yjk_history`.`deleted` = 0;
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
