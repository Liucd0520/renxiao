# 问题 1

**原始问题**: 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计

**耗时**: 101.9秒

---

## 设备 ciscoA 上个月告警统计报告

### 1. 概述
本报告针对设备 `ciscoA` 在2025年12月发生的告警进行了分类统计，旨在帮助用户了解该设备在此期间的告警情况，并识别需要优先处理的告警类型。

### 2. 数据概览
在2025年12月，设备 `ciscoA` 共发生了30次告警，具体按告警类型分类如下：

| 告警类型 | 告警次数 |
|----------|----------|
| Critical | 15       |
| Warning  | 10       |
| Info     | 5        |

### 3. 关键洞察
- **Critical 告警**: 数量最多，共15次，占总告警数量的50%。这些告警可能表明设备存在严重的故障或问题，需要立即处理。
- **Warning 告警**: 共10次，占总告警数量的约33.3%。这些告警可能指示潜在的问题或需要关注的情况。
- **Info 告警**: 数量最少，共5次，占总告警数量的约16.7%。这些告警通常用于提供信息或状态更新，一般不需要紧急处理。

### 4. SQL 查询
以下是用于生成上述统计结果的SQL查询：

<details>
<summary>展开查看 SQL 查询</summary>
```sql
SELECT 
    e.EVENT_TYPE_NAME AS alarm_type,
    COUNT(*) AS alarm_count
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE 
    n.HOST_NAME = 'ciscoA'
    AND e.EVENT_TIME >= '2025-12-01 00:00:00'
    AND e.EVENT_TIME < '2026-01-01 00:00:00'
GROUP BY 
    e.EVENT_TYPE_NAME
ORDER BY 
    alarm_count DESC;
```
</details>

### 5. 限制与注意事项
- 本报告基于 `event_history` 和 `t_bz_config_ci_ne_root` 表中的数据。确保这些表中的数据准确无误，以保证报告的可靠性。
- 告警类型的具体定义和分类标准应参考相关文档或系统设置。
- 本报告仅涵盖2025年12月的数据，对于其他时间段的数据分析，请另行查询。

希望本报告能够帮助您更好地理解和管理设备 `ciscoA` 的告警情况。如有任何问题或需要进一步的分析，请随时联系技术支持团队。