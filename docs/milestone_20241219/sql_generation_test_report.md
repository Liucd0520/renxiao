# SQL 生成测试报告

**模型**: Qwen2.5-Coder-32B-Instruct

**测试时间**: 2025-12-19 14:08:24

**测试问题**: 20 个

**说明**: 直接使用 JSON 中的 tables 字段作为输入，不重新跑检索

---

## 汇总

- 平均相似度: 87.5%
- 高相似度 (>=80%): 13/20

---

## 详细结果

### 问题 1: 统计当前平台上有多少家活跃客户...

**相似度**: 75%

**使用的表**: t_bz_config_customer

**期望 SQL**:
```sql
SELECT COUNT(`CUSTOMER_ID`) AS `active_customer_count`
FROM `t_bz_config_customer`
WHERE `IS_ACTIVE` = 1 AND `IS_DELETED` = 0;
```

**生成 SQL**:
```sql
SELECT COUNT(*) AS active_customers FROM t_bz_config_customer;
```

---

### 问题 2: 统计当前平台上有多少台在线（状态为'上线'）的设备...

**相似度**: 100%

**使用的表**: t_bz_config_ci_ne_root

**期望 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `online_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `NE_STATUS` = '上线' AND `IS_DELETED` = 0;
```

**生成 SQL**:
```sql
SELECT COUNT(*) AS online_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 1;
```

---

### 问题 3: 查询近一周内发生的所有告警事件，并按告警严重程度（severity）分组统计数量...

**相似度**: 83%

**使用的表**: event_history

**期望 SQL**:
```sql
SELECT `SEVERITY`, COUNT(`EVENT_ID`) AS `alarm_count`
FROM `event_history`
WHERE `ALARM_TIME` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY `SEVERITY`
ORDER BY `alarm_count` DESC;
```

**生成 SQL**:
```sql
SELECT 
    SEVERITY_ID, 
    COUNT(*) AS alarm_count
FROM 
    event_history
WHERE 
    EVENT_TIME >= NOW() - INTERVAL 7 DAY
GROUP BY 
    SEVERITY_ID;
```

---

### 问题 4: 查询客户'ABC公司'名下所有设备的基本信息（设备ID、名称、IP地址、状态）...

**相似度**: 100%

**使用的表**: t_bz_config_ci_ne_root, t_bz_config_customer

**期望 SQL**:
```sql
SELECT n.`NE_ID`, n.`HOST_NAME`, n.`IP_ADDRESS`, n.`NE_STATUS`
FROM `t_bz_config_ci_ne_root` n
JOIN `t_bz_config_customer` c ON n.`CUSTOMER_ID` = c.`CUSTOMER_ID`
WHERE c.`CUSTOMER_NAME` = 'ABC公司' AND n.`IS_DELETED` = 0;
```

**生成 SQL**:
```sql
SELECT 
    ci.NE_ID AS 设备ID,
    ci.SIGNING_ADDR AS 设备名称,
    ci.NE_IP AS IP地址,
    CASE WHEN ci.IS_ONLINE = 1 THEN '上线' ELSE '下线' END AS 状态
FROM 
    t_bz_config_ci_ne_root ci
JOIN 
    t_bz_config_customer cu ON ci.DEPARTMENT_ID = cu.SP_ID
WHERE 
    cu.CUSTOMER_NAME = 'ABC公司';
```

---

### 问题 5: 列出上个月新增设备数量最多的前5个客户...

**相似度**: 100%

**使用的表**: t_bz_config_ci_ne_root, t_bz_config_customer

**期望 SQL**:
```sql
SELECT c.`CUSTOMER_NAME`, COUNT(n.`CI_ID`) AS `new_device_count`
FROM `t_bz_config_ci_ne_root` n
JOIN `t_bz_config_customer` c ON n.`CUSTOMER_ID` = c.`CUSTOMER_ID`
WHERE n.`ONLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND n.`ONLINE_TIME` < CURDATE()
  AND n.`IS_DELETED` = 0
GROUP BY c.`CUSTOMER_ID`, c.`CUSTOMER_NAME`
ORDER BY `new_device_count` DESC
LIMIT 5;
```

**生成 SQL**:
```sql
SELECT c.CUSTOMER_NAME, COUNT(ci.NE_ID) AS NEW_DEVICE_COUNT
FROM t_bz_config_ci_ne_root ci
JOIN t_bz_config_customer c ON ci.SIGNING_ADDR = c.SIGNING_ADDR
WHERE ci.ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL DAYOFMONTH(CURDATE())-1 DAY)
  AND ci.ONLINE_TIME < DATE_SUB(CURDATE(), INTERVAL DAYOFMONTH(CURDATE()) DAY)
GROUP BY c.CUSTOMER_NAME
ORDER BY NEW_DEVICE_COUNT DESC
LIMIT 5;
```

---

### 问题 6: 查询当前处于'挂起'状态的告警工单数量...

**相似度**: 100%

**使用的表**: t_bz_incident_info

**期望 SQL**:
```sql
SELECT COUNT(`INCIDENT_ID`) AS `pending_incident_count`
FROM `t_bz_incident_info`
WHERE `INCIDENT_STATUS` = '挂起' AND `IS_DELETED` = 0;
```

**生成 SQL**:
```sql
SELECT COUNT(*) AS pending_incident_count
FROM t_bz_incident_info
WHERE INCIDENT_STATUS = '挂起';
```

---

### 问题 7: 统计每个客户配置的服务包（service package）数量，并列出数量大于3的客户...

**相似度**: 71%

**使用的表**: t_bz_config_customer, ne_service_package

**期望 SQL**:
```sql
SELECT c.`CUSTOMER_NAME`, COUNT(sp.`SERVICE_PACKAGE_ID`) AS `service_package_count`
FROM `t_bz_config_customer` c
LEFT JOIN `ne_service_package` sp ON c.`CUSTOMER_ID` = sp.`CUSTOMER_ID` AND sp.`IS_DELETED` = 0
WHERE c.`IS_DELETED` = 0
GROUP BY c.`CUSTOMER_ID`, c.`CUSTOMER_NAME`
HAVING `service_package_count` > 3
ORDER BY `service_package_count` DESC;
```

**生成 SQL**:
```sql
SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME, COUNT(n.SERVICE_PACKAGE) AS service_package_count
FROM t_bz_config_customer c
JOIN ne_service_package n ON c.CUSTOMER_ID = n.CUSTOMER_ID
GROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME
HAVING service_package_count > 3;
```

---

### 问题 8: 查询过去24小时内，采集机（collector）健康状态为'异常'的设备列表...

**相似度**: 75%

**使用的表**: collector_health

**期望 SQL**:
```sql
SELECT `COLLECTOR_ID`, `COLLECTOR_IP`, `CPU_USAGE`, `MEMORY_USAGE`, `HEALTH_STATUS`, `UPDATE_TIME`
FROM `collector_health`
WHERE `HEALTH_STATUS` = '异常'
  AND `UPDATE_TIME` >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY `UPDATE_TIME` DESC;
```

**生成 SQL**:
```sql
SELECT DISTINCT collector_id
FROM collector_health
WHERE health_status = '异常'
AND create_time >= NOW() - INTERVAL 24 HOUR;
```

---

### 问题 9: 查询设备'Router-01'在过去一个月内的所有Ping测试延迟（latency）数据，按天计算平...

**相似度**: 83%

**使用的表**: report_ne_ping, t_bz_config_ci_ne_root

**期望 SQL**:
```sql
SELECT DATE(`COLLECT_TIME`) AS `day`, AVG(`LATENCY_AVG`) AS `avg_latency`
FROM `report_ne_ping`
WHERE `NE_ID` = (SELECT `NE_ID` FROM `t_bz_config_ci_ne_root` WHERE `HOST_NAME` = 'Router-01' LIMIT 1)
  AND `COLLECT_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY DATE(`COLLECT_TIME`)
ORDER BY `day` DESC;
```

**生成 SQL**:
```sql
SELECT 
    DATE(report_inst_id) AS date,
    AVG(VALUE_DELAY_AVG) AS avg_latency
FROM 
    report_ne_ping
JOIN 
    t_bz_config_ci_ne_root ON report_ne_ping.NE_ID = t_bz_config_ci_ne_root.NE_ID
WHERE 
    t_bz_config_ci_ne_root.ITEMNAME = 'Router-01'
    AND report_inst_id >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY 
    DATE(report_inst_id);
```

---

### 问题 10: 统计各设备类型（ne_type）下的设备数量，并按数量降序排列...

**相似度**: 86%

**使用的表**: t_bz_config_ci_ne_root, ne_type

**期望 SQL**:
```sql
SELECT nt.`TYPE_NAME`, COUNT(n.`CI_ID`) AS `device_count`
FROM `t_bz_config_ci_ne_root` n
JOIN `ne_type` nt ON n.`NE_TYPE_ID` = nt.`TYPE_ID`
WHERE n.`IS_DELETED` = 0
GROUP BY nt.`TYPE_ID`, nt.`TYPE_NAME`
ORDER BY `device_count` DESC;
```

**生成 SQL**:
```sql
SELECT nt.NE_TYPE_NAME, COUNT(tbcnr.NE_ID) AS device_count
FROM t_bz_config_ci_ne_root tbcnr
JOIN ne_type nt ON tbcnr.DEVICE_TYPE_ID = CAST(nt.NE_TYPE_ID AS UNSIGNED)
GROUP BY nt.NE_TYPE_NAME
ORDER BY device_count DESC;
```

---

### 问题 11: 查询最近一周内，端口流量使用率（95峰值）最高的前10个设备端口...

**相似度**: 100%

**使用的表**: report_port_info, t_bz_config_ci_ne_root

**期望 SQL**:
```sql
SELECT r.`HOST_NAME`, p.`PORT_NAME`, p.`PEAK_95_USAGE_RATE`, p.`COLLECT_TIME`
FROM `report_port_info` p
JOIN `t_bz_config_ci_ne_root` r ON p.`NE_ID` = r.`NE_ID`
WHERE p.`COLLECT_TIME` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY p.`PEAK_95_USAGE_RATE` DESC
LIMIT 10;
```

**生成 SQL**:
```sql
SELECT 
    rpi.ROOT_NE_ID,
    rpi.ITEMNAME,
    MAX(rpi.OUT_95_USAGE) AS MAX_OUT_95_USAGE
FROM 
    report_port_info rpi
JOIN 
    t_bz_config_ci_ne_root tbccinr ON rpi.ROOT_NE_ID = tbccinr.NE_ID
WHERE 
    rpi.TIME_COUNTS >= UNIX_TIMESTAMP(NOW() - INTERVAL 7 DAY)
GROUP BY 
    rpi.ROOT_NE_ID, rpi.ITEMNAME
ORDER BY 
    MAX_OUT_95_USAGE DESC
LIMIT 10;
```

---

### 问题 12: 列出所有未配置任何联系人的客户...

**相似度**: 75%

**使用的表**: t_bz_config_customer, t_rl_config_ci_contact

**期望 SQL**:
```sql
SELECT c.`CUSTOMER_ID`, c.`CUSTOMER_NAME`
FROM `t_bz_config_customer` c
LEFT JOIN `t_rl_config_ci_contact` rcc ON c.`CUSTOMER_ID` = rcc.`CUSTOMER_ID`
WHERE rcc.`CONTACT_ID` IS NULL
  AND c.`IS_DELETED` = 0;
```

**生成 SQL**:
```sql
SELECT * 
FROM t_bz_config_customer 
WHERE CUSTOMER_ID NOT IN (SELECT CI_ID FROM t_rl_config_ci_contact);
```

---

### 问题 13: 统计上个月每个客户产生的告警事件总数...

**相似度**: 71%

**使用的表**: event_history, t_bz_config_ci_ne_root, t_bz_config_customer

**期望 SQL**:
```sql
SELECT c.`CUSTOMER_NAME`, COUNT(eh.`EVENT_ID`) AS `monthly_alarm_count`
FROM `event_history` eh
JOIN `t_bz_config_ci_ne_root` n ON eh.`NE_ID` = n.`NE_ID`
JOIN `t_bz_config_customer` c ON n.`CUSTOMER_ID` = c.`CUSTOMER_ID`
WHERE eh.`ALARM_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND eh.`ALARM_TIME` < CURDATE()
GROUP BY c.`CUSTOMER_ID`, c.`CUSTOMER_NAME`
ORDER BY `monthly_alarm_count` DESC;
```

**生成 SQL**:
```sql
SELECT 
    CUSTOMER_NAME, 
    COUNT(EVENT_ID) AS ALARM_COUNT
FROM 
    event_history
WHERE 
    EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL DAYOFMONTH(CURDATE()) DAY)
    AND EVENT_TIME < DATE_SUB(CURDATE(), INTERVAL DAYOFMONTH(CURDATE())-1 DAY)
GROUP BY 
    CUSTOMER_NAME;
```

---

### 问题 14: 查询当前系统中所有'管理员'角色的用户数量...

**相似度**: 100%

**使用的表**: framework_user, framework_user_role, framework_role

**期望 SQL**:
```sql
SELECT COUNT(DISTINCT fu.`USER_ID`) AS `admin_user_count`
FROM `framework_user` fu
JOIN `framework_user_role` fur ON fu.`USER_ID` = fur.`USER_ID`
JOIN `framework_role` fr ON fur.`ROLE_ID` = fr.`ROLE_ID`
WHERE fr.`ROLE_NAME` = '管理员' AND fu.`IS_ACTIVE` = 1;
```

**生成 SQL**:
```sql
SELECT COUNT(*)
FROM framework_user_role ur
JOIN framework_role r ON ur.ROLE_ID = r.ID
WHERE r.NAME = '管理员';
```

---

### 问题 15: 查询设备'Switch-05'的维保信息（联系人、电话、维保起止时间）...

**相似度**: 100%

**使用的表**: maintenance_info, t_bz_config_ci_ne_root

**期望 SQL**:
```sql
SELECT mi.`CONTACT_PERSON`, mi.`CONTACT_PHONE`, mi.`START_TIME`, mi.`END_TIME`
FROM `maintenance_info` mi
WHERE mi.`NE_ID` = (SELECT `NE_ID` FROM `t_bz_config_ci_ne_root` WHERE `HOST_NAME` = 'Switch-05' LIMIT 1);
```

**生成 SQL**:
```sql
SELECT mi.contacts, mi.phone, mi.start_time, mi.end_time
FROM maintenance_info mi
JOIN t_bz_config_ci_ne_root ne ON mi.ne_id = ne.NE_ID
WHERE ne.NE_NAME = 'Switch-05';
```

---

### 问题 16: 统计过去一年中，每月新上线的设备数量...

**相似度**: 100%

**使用的表**: t_bz_config_ci_ne_root

**期望 SQL**:
```sql
SELECT DATE_FORMAT(`ONLINE_TIME`, '%Y-%m') AS `month`, COUNT(`CI_ID`) AS `new_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `ONLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
  AND `IS_DELETED` = 0
GROUP BY DATE_FORMAT(`ONLINE_TIME`, '%Y-%m')
ORDER BY `month` DESC;
```

**生成 SQL**:
```sql
SELECT 
    DATE_FORMAT(ONLINE_TIME, '%Y-%m') AS month,
    COUNT(*) AS new_devices_count
FROM 
    t_bz_config_ci_ne_root
WHERE 
    ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY 
    DATE_FORMAT(ONLINE_TIME, '%Y-%m')
ORDER BY 
    month;
```

---

### 问题 17: 查询所有SD-WAN租户（tenant）的基本信息及其关联的站点（site）数量...

**相似度**: 71%

**使用的表**: sdwan_tenant, sdwan_site

**期望 SQL**:
```sql
SELECT t.`TENANT_NAME`, t.`CONTACT_EMAIL`, COUNT(s.`SITE_ID`) AS `site_count`
FROM `sdwan_tenant` t
LEFT JOIN `sdwan_site` s ON t.`TENANT_ID` = s.`TENANT_ID` AND s.`IS_DELETED` = 0
WHERE t.`IS_DELETED` = 0
GROUP BY t.`TENANT_ID`, t.`TENANT_NAME`, t.`CONTACT_EMAIL`
ORDER BY `site_count` DESC;
```

**生成 SQL**:
```sql
SELECT 
    t.tenantId,
    t.tenantName,
    t.tenantDescription,
    t.tenantAddress,
    t.tenantPhone,
    t.tenantEmail,
    COUNT(s.siteId) AS siteCount
FROM 
    sdwan_tenant t
LEFT JOIN 
    sdwan_site s ON t.tenantId = s.tenantId
GROUP BY 
    t.tenantId, t.tenantName, t.tenantDescription, t.tenantAddress, t.tenantPhone, t.tenantEmail;
```

---

### 问题 18: 列出最近30天内，处理时长超过24小时的告警工单（从创建到关闭）...

**相似度**: 75%

**使用的表**: t_bz_incident_info

**期望 SQL**:
```sql
SELECT `INCIDENT_ID`, `INCIDENT_TITLE`, `CREATE_TIME`, `CLOSE_TIME`, TIMESTAMPDIFF(HOUR, `CREATE_TIME`, `CLOSE_TIME`) AS `process_hours`
FROM `t_bz_incident_info`
WHERE `CLOSE_TIME` IS NOT NULL
  AND `CREATE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
  AND TIMESTAMPDIFF(HOUR, `CREATE_TIME`, `CLOSE_TIME`) > 24
ORDER BY `process_hours` DESC;
```

**生成 SQL**:
```sql
SELECT *
FROM t_bz_incident_info
WHERE TIMESTAMPDIFF(HOUR, RESPOND_TIME, FRONTLINE_TRANS_TIME) > 24
AND DATE(RESPOND_TIME) >= CURDATE() - INTERVAL 30 DAY;
```

---

### 问题 19: 查询客户'XYZ科技'使用的所有云监控密钥（cloud monitor key）的供应商类型...

**相似度**: 100%

**使用的表**: customer_cloud_monitor_key, t_bz_config_customer

**期望 SQL**:
```sql
SELECT k.`KEY_NAME`, k.`CLOUD_TYPE`, k.`STATUS`, k.`CREATE_TIME`
FROM `customer_cloud_monitor_key` k
JOIN `t_bz_config_customer` c ON k.`CUSTOMER_ID` = c.`CUSTOMER_ID`
WHERE c.`CUSTOMER_NAME` = 'XYZ科技' AND k.`IS_DELETED` = 0;
```

**生成 SQL**:
```sql
SELECT ccmk.supplier
FROM customer_cloud_monitor_key ccmk
JOIN t_bz_config_customer tbcc ON ccmk.customer_id = tbcc.CUSTOMER_ID
WHERE tbcc.CUSTOMER_NAME = 'XYZ科技' AND ccmk.deleted = '0';
```

---

### 问题 20: 统计当前系统中，各严重等级（severity）的未确认告警数量...

**相似度**: 83%

**使用的表**: event_history

**期望 SQL**:
```sql
SELECT `SEVERITY`, COUNT(`EVENT_ID`) AS `unacknowledged_alarm_count`
FROM `event_history`
WHERE `ACK_STATUS` = 0 AND `RECOVER_TIME` IS NULL
GROUP BY `SEVERITY`
ORDER BY FIELD(`SEVERITY`, '紧急', '重要', '次要', '警告');
```

**生成 SQL**:
```sql
SELECT SEVERITY_ID, COUNT(*) AS UNACKNOWLEDGED_ALARM_COUNT
FROM event_history
WHERE IS_ACK = 0
GROUP BY SEVERITY_ID;
```

---

*报告生成时间: 2025-12-19 14:08:24*
