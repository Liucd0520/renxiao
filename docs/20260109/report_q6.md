# 问题 6

**原始问题**: 上个月下线的设备有多少

**耗时**: 111.5秒

---

## 上个月下线设备数量报告

### 1. 用户问题
用户询问上个月下线的设备数量。

### 2. 具体数据
根据查询结果，在2025年12月1日至2025年12月31日期间，共有45个设备的状态变为下线。

### 3. 数据展示

| 日期范围       | 下线设备数量 |
|----------------|--------------|
| 2025-12-01 至 2025-12-31 | 45           |

### 4. 关键洞察
- 在2025年12月，有45个设备的状态变更为下线。这可能表明该月份存在一些影响设备正常运行的因素，如维护、故障或其他技术问题。

### 5. 限制与注意事项
- 该查询仅计算了`t_bz_config_ci_ne_root`表中`IS_ONLINE`字段为0且`OFFLINE_TIME`在指定日期范围内的记录。
- 如果需要进一步分析，可以考虑结合`t_gn_business_application_change`和`t_gn_traffic_abnormality`表中的信息。

### 6. 附录：使用的 SQL 查询
#### 6.1 确定上个月的第一天和最后一天的日期范围
```sql
SELECT 
    DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01') AS start_date,
    LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AS end_date;
```

#### 6.2 查询在上个月日期范围内状态变为下线的设备数量
```sql
SELECT COUNT(*) AS offline_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 0
  AND OFFLINE_TIME >= DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH)
  AND OFFLINE_TIME < DATE_FORMAT(NOW(), '%Y-%m-01');
```

### 7. 总结
根据上述查询结果，我们可以得出结论：在2025年12月，共有45个设备的状态变为下线。建议进一步调查这些设备下线的原因，以确保系统的稳定性和可靠性。