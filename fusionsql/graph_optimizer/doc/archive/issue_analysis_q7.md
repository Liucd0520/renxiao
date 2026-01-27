# Question 7 问题分析报告

## 问题描述

**测试问题**: 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？

**期望表**:
- `event_history` (告警历史)
- `t_bz_config_ci_ne_root` (设备信息)
- `t_bz_config_customer` (客户信息)

**测试结果**: FAIL

**标记的缺失表**: `t_bz_config_customer`

---

## 死因分析

### 检查点 1: BGE 召回 - PASS

**关键发现**: `t_bz_config_customer` **在 BGE 检索结果的第 3 位**

```
retrieved_tables: [
  "t_bz_config_ci_ne_root",      # Rank 1 - 期望表
  "t_gn_business_application_change",
  "t_bz_config_customer",         # Rank 3 - 期望表 (在这里!)
  "t_bz_incident_info",
  "event_yjk_history",
  "ne_syslog_filter_script",
  "syslog_filter_script",
  "event_history",                # Rank 8 - 期望表
  ...
]
```

**结论**: BGE 召回正常，所有三张期望表都在 Top 20 内

---

### 检查点 2: Graph 剪枝 - PASS

根据当前 Boost-Only 算法设计：

```python
# 最终分数 = BGE原分 + boost（只加不减）
final_scores[table] = bge_scores[table] + boost_factor * graph_boost
```

**分析**:
- `t_bz_config_customer` 作为核心业务表，在 Neo4j 中有大量外键连接
- 与 `t_bz_config_ci_ne_root` 有 IS 关系（CUSTOMER_ID 外键）
- PPR 和连通性分数应该较高

**结论**: 图剪枝不会移除该表，它在最终返回列表中

---

### 检查点 3: SQL 生成 - FAIL (根本原因)

**生成的 SQL**:
```sql
SELECT DISTINCT
    e.EVENT_TYPE_NAME AS alarm_type,
    e.EVENT_TIME AS alarm_time,
    e.ALARM_CLEAR_TIME AS recovery_time
FROM
    event_history e
JOIN
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE
    n.CUSTOMER_ID = 12345  -- 硬编码客户ID!
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND e.ALARM_CLEAR_TIME IS NOT NULL
    AND e.EVENT_STATUS_NAME = 'alarm'
ORDER BY
    e.EVENT_TIME DESC;
```

**问题**:
1. LLM 硬编码了 `CUSTOMER_ID = 12345`
2. 没有 JOIN `t_bz_config_customer` 表
3. 没有返回 `CUSTOMER_NAME`

**参考 SQL**:
```sql
SELECT
  t_bz_config_customer.CUSTOMER_NAME,
  t_bz_config_ci_ne_root.HOST_NAME,
  event_history.EVENT_NAME,
  event_history.EVENT_TIME
FROM event_history
JOIN t_bz_config_ci_ne_root
  ON event_history.NE_ID = t_bz_config_ci_ne_root.NE_ID
JOIN t_bz_config_customer
  ON event_history.CUSTOMER_ID = t_bz_config_customer.CUSTOMER_ID
WHERE event_history.EVENT_TIME >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
  AND event_history.EVENT_STATUS_NAME = 'alarm'
LIMIT 10;
```

---

## 根本原因

### 问题不在 Graph Optimizer，而在 SQL Generator

| 阶段 | 状态 | 说明 |
|-----|------|------|
| BGE 检索 | PASS | 3/3 期望表全部召回 |
| 图优化 | PASS | 表未被剪枝 |
| SQL 生成 | **FAIL** | LLM 未使用 customer 表 |

**LLM 决策问题**:
1. 问题说"某客户设备"，LLM 理解为已知客户ID
2. 于是硬编码 `CUSTOMER_ID = 12345` 而非 JOIN
3. 这是 LLM 对"某"字的语义理解问题

---

## 验证用户猜想: 孤岛表问题

**用户猜想**: 如果一张表是孤岛（没有外键连接其他 top nodes），它的最终得分会不会被严重压低？

### 代码验证

查看 `optimizer.py` 第 194-209 行:

```python
# 6. Boost-Only 计算：图分数只能加分，不能减分
max_bge = max(bge_scores.values()) if bge_scores else 1.0
boost_factor = max_bge * 0.3  # 最多加 30% 的 BGE 最高分

final_scores = {}
for table in table_names:
    # 计算图特征加成（全部为正）
    graph_boost = (
        0.50 * ppr_normalized.get(table, 0)  # PPR 权重
        + 0.35 * conn_normalized.get(table, 0)  # 连通性
        + 0.15 * degree_normalized.get(table, 0)  # 度中心性
    )

    # 最终分数 = BGE原分 + boost（只加不减）
    final_scores[table] = bge_scores[table] + boost_factor * graph_boost
```

### 结论

**当前版本 (Boost-Only) 不会严重压低孤岛表分数**:

- 孤岛表: `graph_boost = 0`
- 最终分数 = `BGE_score + 0 = BGE_score` (保持原分)

**但在旧版本 (Weighted Average) 中确实会被压低**:

- 孤岛表: 图特征全为 0
- 最终分数 = `BGE_score * 0.70 + 0 = 0.70 * BGE_score`
- **损失 30% 分数!**

---

## 修复建议

### 短期: 改进 SQL Generator Prompt

问题在于 LLM 对"某客户"的理解。建议在 prompt 中添加:

```
当问题中出现"某客户"、"某设备"等模糊表述时:
- 不要硬编码具体ID值
- 应该 JOIN 相关维度表
- 返回实体名称（如 CUSTOMER_NAME）供用户筛选
```

### 中期: 表使用验证

在 SQL 生成后添加验证:
- 检查生成的 SQL 是否使用了所有高分检索表
- 如果期望的表未被使用，提示 LLM 重新考虑

### 长期: 多表 JOIN 意图识别

在检索阶段识别查询是否需要多表 JOIN:
- 如果需要，确保所有维度表都被传递给 LLM
- 并在 prompt 中强调这些表的 JOIN 关系

---

## 总结

| 项目 | 结论 |
|-----|------|
| 故障点 | SQL 生成阶段（非图优化） |
| 孤岛表问题 | 当前 Boost-Only 策略已解决 |
| 图优化器状态 | 工作正常 |
| 建议优先级 | 改进 SQL Generator Prompt |

---

## 附录: 测试数据原文

```json
{
  "id": 7,
  "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
  "expected_tables": [
    "event_history",
    "t_bz_config_ci_ne_root",
    "t_bz_config_customer"
  ],
  "retrieved_tables": [
    "t_bz_config_ci_ne_root",
    "t_gn_business_application_change",
    "t_bz_config_customer",  // <-- 在这里，排名第3
    "t_bz_incident_info",
    "event_yjk_history",
    "ne_syslog_filter_script",
    "syslog_filter_script",
    "event_history",          // <-- 排名第8
    "event_sdn",
    "t_gn_botnet",
    "event_backup",
    "event_history_sdwan",
    "ne_business_severity",
    "report_new_dev",
    "event_knowledge",
    "t_dc_release_type",
    "t_dc_incident_finish"
  ],
  "tables_correct": false,
  "missing_tables": ["t_bz_config_customer"]  // <-- 误报! 表在列表中
}
```

**注意**: `missing_tables` 标记为 `t_bz_config_customer`，但该表实际在 `retrieved_tables` 的第 3 位。这可能是测试脚本的判断逻辑问题——它可能是检查 SQL 中是否使用了该表，而非检索列表中是否存在。
