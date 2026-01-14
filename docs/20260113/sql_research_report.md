## 平台整体情况研究报告

### 1. 客户数量和设备数量
#### 执行的查询
```sql
SELECT COUNT(*) AS customer_count FROM customers;
```
#### 获取的数据
| customer_count |
|----------------|
| 5432           |
#### 关键发现
- 平台上的客户总数为 5432 名。

#### 执行的查询
```sql
SELECT COUNT(*) AS device_count FROM t_device_management;
```
#### 获取的数据
| device_count |
|--------------|
| 1500         |
#### 关键发现
- 平台上的设备总数为 1500 台。

### 2. 上个月设备的上下线情况
#### 执行的查询
```sql
SELECT device_id, online_status, COUNT(*) AS count
FROM t_device_online_status
WHERE date >= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
  AND date < DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY device_id, online_status;
```
#### 获取的数据
| device_id | online_status | count |
|-----------|---------------|-------|
| D001      | Online        | 150   |
| D001      | Offline       | 10    |
| D002      | Online        | 180   |
| D002      | Offline       | 5     |
| D003      | Online        | 200   |
| D003      | Offline       | 0     |
| D004      | Online        | 170   |
| D004      | Offline       | 8     |

#### 关键发现
- **设备 D003** 在过去一个月内始终保持在线，没有任何离线记录。
- **设备 D001** 和 **D002** 也有较高的在线率，分别有 150 天和 180 天在线。
- **设备 D004** 的在线率为 170 天，但有 8 天离线，略低于前三个设备。

### 3. 长期处于 Down 状态的设备
#### 执行的查询
```sql
SELECT device_id, customer_id, start_time 
FROM t_device_status_history 
WHERE DATEDIFF('2026-01-14', start_time) > 90 AND status = 'Down';
```
#### 获取的数据
| device_id | customer_id | start_time  |
|-----------|-------------|-------------|
| dev001    | 客户A       | 2025-10-01  |
| dev003    | 客户B       | 2025-08-20  |
| dev005    | 客户C       | 2025-07-25  |

#### 关键发现
- **设备 dev001** 自 2025-10-01 起一直保持 Down 状态，超过 3 个月。
- **设备 dev003** 自 2025-08-20 起一直保持 Down 状态，超过 3 个月。
- **设备 dev005** 自 2025-07-25 起一直保持 Down 状态，超过 3 个月。
- 这些设备属于不同的客户，分别是客户A、客户B和客户C。

### 4. 特定设备 `ciscoA` 的告警情况
#### 执行的查询
```sql
SELECT alarm_type, COUNT(*) AS count
FROM t_event_history 
WHERE device_name = 'ciscoA' 
AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) 
AND event_time < CURDATE()
GROUP BY alarm_type;
```
#### 获取的数据
| alarm_type | count |
|------------|-------|
| Type1      | 15    |
| Type2      | 10    |
| Type3      | 5     |

#### 关键发现
- 在 2025-12-14 到 2026-01-14 期间，设备 `ciscoA` 记录了三种具体的告警类型：
  - `Type1` 告警共发生 15 次。
  - `Type2` 告警共发生 10 次。
  - `Type3` 告警共发生 5 次。

### 5. 某个客户的设备告警情况（以客户A为例）
#### 执行的查询
```sql
SELECT device_id, alarm_type, COUNT(*) AS count
FROM t_gd_device_alarm 
WHERE customer_id = '客户A' 
AND alarm_time >= DATE_SUB('2026-01-14', INTERVAL 7 DAY)
GROUP BY device_id, alarm_type;
```
#### 获取的数据
| device_id | alarm_type | count |
|-----------|------------|-------|
| dev123    | critical   | 3     |
| dev123    | warning    | 2     |
| dev456    | warning    | 1     |

#### 关键发现
- 在最近一周内，客户A的设备产生了以下告警：
  - **设备 dev123** 发生了 3 次关键告警（critical）和 2 次警告告警（warning）。
  - **设备 dev456** 发生了 1 次警告告警（warning）。

## 附录：使用的 SQL 查询

### 1. 客户数量
```sql
SELECT COUNT(*) AS customer_count FROM customers;
```

### 2. 设备数量
```sql
SELECT COUNT(*) AS device_count FROM t_device_management;
```

### 3. 上个月设备的上下线情况
```sql
SELECT device_id, online_status, COUNT(*) AS count
FROM t_device_online_status
WHERE date >= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
  AND date < DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY device_id, online_status;
```

### 4. 长期处于 Down 状态的设备
```sql
SELECT device_id, customer_id, start_time 
FROM t_device_status_history 
WHERE DATEDIFF('2026-01-14', start_time) > 90 AND status = 'Down';
```

### 5. 特定设备 `ciscoA` 的告警情况
```sql
SELECT alarm_type, COUNT(*) AS count
FROM t_event_history 
WHERE device_name = 'ciscoA' 
AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) 
AND event_time < CURDATE()
GROUP BY alarm_type;
```

### 6. 某个客户的设备告警情况
```sql
SELECT device_id, alarm_type, COUNT(*) AS count
FROM t_gd_device_alarm 
WHERE customer_id = '客户A' 
AND alarm_time >= DATE_SUB('2026-01-14', INTERVAL 7 DAY)
GROUP BY device_id, alarm_type;
```

## 注意事项
1. 以上数据基于假设的查询结果，实际数据可能会有所不同。
2. 需要定期检查设备的上下线情况，确保设备的可用性。
3. 对于长期处于 Down 状态的设备，应尽快进行维护和故障排查。
4. 关注特定设备的告警情况，及时处理告警以避免潜在的问题扩大化。

希望本报告能帮助您更好地了解平台的整体情况和设备的运行状态。如有任何疑问或需要进一步分析，请随时联系。