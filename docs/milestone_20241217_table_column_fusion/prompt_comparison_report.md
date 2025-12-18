# Prompt 模式对比测试报告

**测试时间**: 2025-12-18 09:51:02

**模型**: Qwen3-14B-awq

---

## 测试说明

### 禁止思考模式
```
要求：直接输出 SQL 语句，不要思考过程，不要解释
```

### 深度思考模式
```
任务：请仔细分析用户问题和数据库 Schema
1. 深度思考：这个问题需要查询哪些表？表之间如何关联？
2. 反复推敲：选择最准确的字段，确保条件逻辑正确
3. 验证检查：SQL 语法是否正确？能否得到用户想要的结果？
```

---

## 测试 3: 现在平台上有多少家客户

**正确答案关键字段**: ['COUNT', 'CUSTOMER_ID', 'IS_ACTIVE']

### 禁止思考 ❌ 错误

**关键字段匹配**: 33%

**问题**: 缺少 IS_ACTIVE 条件

```sql
SELECT COUNT(*) FROM t_bz_config_customer;
```

### 深度思考 ❌ 错误

**关键字段匹配**: 33%

**问题**: 缺少 IS_ACTIVE 条件

```sql
SELECT COUNT(*) AS 客户数量 FROM t_bz_config_customer;
```

---

## 测试 4: 现在平台上有多少台设备

**正确答案关键字段**: ['COUNT', 'CI_ID', 'IS_DELETED']

### 禁止思考 ⚠️ 部分正确

**关键字段匹配**: 67%

```sql
SELECT COUNT(*) FROM t_bz_config_ci_ne_root WHERE IS_DELETED = 0;
```

### 深度思考 ⚠️ 部分正确

**关键字段匹配**: 67%

```sql
SELECT COUNT(*) AS device_count 
FROM t_bz_config_ci_ne_root 
WHERE IS_DELETED = 0;
```

---

## 测试 5: 上个月上线的新设备有多少

**正确答案关键字段**: ['COUNT', 'ONLINE_TIME', 'DATE_SUB', 'INTERVAL 1 MONTH']

### 禁止思考 ✅ 正确

**关键字段匹配**: 100%

```sql
SELECT COUNT(*) AS new_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 1
AND ONLINE_TIME BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE();
```

### 深度思考 ✅ 正确

**关键字段匹配**: 100%

```sql
SELECT COUNT(*) AS new_devices_count
FROM t_bz_config_ci_ne_root
WHERE IS_DELETED = 0
  AND ONLINE_TIME >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND ONLINE_TIME <= LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH));
```

---

## 测试 6: 上个月下线的设备有多少

**正确答案关键字段**: ['COUNT', 'OFFLINE_TIME', 'DATE_SUB', 'INTERVAL 1 MONTH']

### 禁止思考 ✅ 正确

**关键字段匹配**: 100%

```sql
SELECT COUNT(*) AS offline_device_count
FROM t_bz_config_ci_ne_root
WHERE IS_ONLINE = 0
  AND OFFLINE_TIME BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE();
```

### 深度思考 ✅ 正确

**关键字段匹配**: 100%

```sql
SELECT COUNT(*) AS offline_device_count
FROM t_bz_config_ci_ne_root
WHERE NE_STATUS IN ('下线', 'down')
AND OFFLINE_TIME BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH));
```

---

## 汇总对比

| 指标 | 禁止思考 | 深度思考 |
|-----|---------|--------|
| ✅ 正确 | 2/4 | 2/4 |
| ⚠️ 部分正确 | 1/4 | 1/4 |
| ❌ 错误 | 1/4 | 1/4 |
| **正确率** | **50%** | **50%** |

## 结论

**两种模式效果相当**：正确率都是 50%


---

*报告生成时间: 2025-12-18 09:52:18*
