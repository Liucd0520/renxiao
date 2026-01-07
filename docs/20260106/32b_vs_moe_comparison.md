# 32B Coder vs MoE 模型对比报告

**测试日期**: 2026-01-06  
**测试方法**: 7题测试，检测表选择 + 列名幻觉

---

## 1. 总体结果

| 模型 | 正确数 | 准确率 |
|:----|:-----:|:------:|
| Qwen2.5-Coder-32B | 6/7 | 85.7% |
| Qwen3 MoE | 6/7 | 85.7% |

**准确率相同，但失败点不同！**

---

## 2. 逐题对比

| 题号 | 问题 | 32B | MoE | 差异 |
|:---:|:----|:---:|:---:|:----|
| Q1 | ciscoA 告警统计 | ✅ | ✅ | 一致 |
| **Q2** | device state down | ❌ | ✅ | **32B 用错表** |
| Q3 | 客户数量 | ✅ | ✅ | 一致 |
| Q4 | 设备数量 | ✅ | ✅ | 一致 |
| Q5 | 上月上线 | ✅ | ✅ | 一致 |
| Q6 | 上月下线 | ✅ | ✅ | 一致 |
| **Q7** | 一周告警+恢复时间 | ✅ | ❌ | **MoE 列幻觉** |

---

## 3. 失败分析

### 32B 失败 (Q2)

**问题**: 列出平台上设备device state down状态超过3个月的设备清单及客户名称

**32B 生成的 SQL**:
```sql
SELECT bci.CUSTOMER_NAME, td.device_name
FROM t_bz_config_customer bci
JOIN t_gn_topo_device td ON bci.CUSTOMER_ID = td.customer_id  -- ❌ 错误表
WHERE td.device_status = 'down' 
    AND td.UPDATE_TIME <= DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

**正确应该用**:
- `event_history` (查 Device state down 事件)
- `t_bz_config_ci_ne_root` (设备信息)
- `t_bz_config_customer` (客户信息)

**失败原因**: 32B 选择了 `t_gn_topo_device` 而不是 `event_history`，误解了 "device state down" 的含义

---

### MoE 失败 (Q7)

**问题**: 某客户设备近一周内发生过哪些类型的告警？具体告警时间和**恢复时间**分别是什么？

**MoE 生成的 SQL**:
```sql
SELECT e.EVENT_TYPE_NAME, e.EVENT_TIME, 
       e.ALARM_CLEAR_TIME AS recovery_time  -- ❌ 列不存在！
FROM event_history e ...
```

**32B 生成的 SQL**:
```sql
SELECT eh.EVENT_NAME, eh.EVENT_TIME, 
       eh.ACTION_TIME AS 恢复时间  -- ✅ ACTION_TIME 存在
FROM event_history eh ...
```

**差异**: 
- MoE 幻觉了 `ALARM_CLEAR_TIME`（不存在）
- 32B 用了 `ACTION_TIME`（存在）

---

## 4. SQL 质量对比

### Q1: 告警统计

| 模型 | SQL |
|:----|:----|
| 32B | `JOIN ON e.ROOT_NE_ID = n.NE_ID` |
| MoE | `JOIN ON e.NE_ID = c.NE_ID` |

**差异**: 32B 用 `ROOT_NE_ID`，MoE 用 `NE_ID`，两者都可能正确

### Q7: 恢复时间

| 模型 | 列选择 | 是否存在 |
|:----|:------|:-------:|
| 32B | `ACTION_TIME` | ✅ |
| MoE | `ALARM_CLEAR_TIME` | ❌ |

---

## 5. 结论

| 维度 | 32B Coder | MoE | 评价 |
|:----|:--------:|:---:|:----|
| 表选择准确性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | MoE 更准 |
| 列名准确性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 32B 更准 |
| Q2 理解 | ❌ | ✅ | MoE 更好 |
| Q7 理解 | ✅ | ❌ | 32B 更好 |
| 总分 | 6/7 | 6/7 | 平局 |

### 建议

1. **对于需要精确表选择的任务**: 用 MoE
2. **对于需要避免列幻觉的任务**: 用 32B
3. **优化方向**: 两个模型可以互补，考虑 ensemble

---

## 6. 文件清单

```
docs/20260106/
└── 32b_single_test.json  # 32B 测试结果（含完整SQL）
```
