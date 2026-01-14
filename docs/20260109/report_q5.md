# 问题 5

**原始问题**: 上个月上线的新设备有多少

**耗时**: 103.0秒

---

## 上个月上线的新设备数量报告

### 1. 用户问题
用户询问了上个月上线的新设备数量。

### 2. 数据分析
根据提供的 SQL 查询结果，我们已经确定了上个月的具体日期范围，并查询了在该日期范围内上线的新设备数量。

#### 2.1 上个月的日期范围
- 第一天: 2025-12-01
- 最后一天: 2025-12-31

#### 2.2 上个月上线的新设备数量
- 新设备数量: 152

### 3. 关键洞察
在 2025 年 12 月期间，共有 152 台新设备上线。这一数据有助于了解设备部署的趋势和系统扩展情况。

### 4. 限制或注意事项
- 本报告基于 `t_bz_config_ci_ne_root` 表中的数据。
- `ONLINE_CHANGE_TIME` 字段用于判断设备的上线时间。
- 查询结果可能受到数据更新频率的影响。

### 5. 附录
#### 5.1 使用的 SQL 查询
```sql
-- 确定上个月的第一天和最后一天的日期
SELECT 
    DATE_FORMAT(DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH), '%Y-%m-01') AS first_day_of_last_month,
    LAST_DAY(DATE_SUB(NOW(), INTERVAL 1 MONTH)) AS last_day_of_last_month;

-- 查询在上个月上线的新设备数量
SELECT COUNT(*) AS new_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 1
  AND ONLINE_CHANGE_TIME >= DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH)
  AND ONLINE_CHANGE_TIME < DATE_FORMAT(NOW(), '%Y-%m-01');
```

#### 5.2 查询结果
| 日期范围          | 新设备数量 |
|-------------------|------------|
| 2025-12-01 至 2025-12-31 | 152        |

通过以上分析，我们可以清晰地看到上个月新设备上线的数量为 152 台。这为未来的设备管理和资源分配提供了重要的参考信息。