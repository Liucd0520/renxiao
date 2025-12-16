# LinkAlign SQL 生成分析报告

> 测试时间: 2025-12-12 | 测试用例数: 7

## 📊 总体结果

### 核心统计

| 指标 | 结果 |
|------|------|
| **表召回率** | 4/7 (57%) 完全召回 |
| **平均表召回率** | 67% |
| **SQL 正确率** | **0/7 (0%)** ❌ |
| **平均单次测试时间** | **~700秒 (约12分钟)** |
| **平均 LLM 过滤轮次** | 4轮 |
| **每测试 LLM API 调用** | ~800-1000次 |

---

## 🔍 SQL 正确性详细分析

### 测试 1: ciscoA 告警统计

| 项目 | 内容 |
|------|------|
| **问题** | 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计 |
| **表召回** | ✅ 100% |
| **SQL正确** | ❌ **错误** |

**LinkAlign 生成的 SQL (核心部分)**:
```sql
SELECT `event_type`.`EVENT_TYPE_NAME` AS alarm_type, COUNT(`t_bz_sdn_alarm`.`ALARM_ID`) AS count
FROM `t_bz_sdn_alarm`
JOIN `event_type` ON `t_bz_sdn_alarm`.`ALARM_TYPE` = `event_type`.`EVENT_TYPE_ID`
WHERE `t_bz_sdn_alarm`.`DEVICE_NAME` = 'ciscoA'
  AND `t_bz_sdn_alarm`.`OCCUR_TIME` >= '2023-09-01'
  AND `t_bz_sdn_alarm`.`OCCUR_TIME` < '2023-10-01'
GROUP BY `event_type`.`EVENT_TYPE_NAME`;
```

**正确 SQL**:
```sql
SELECT `event_type_name`, COUNT(`event_id`) AS `alarm_count`
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.ne_id = t_bz_config_ci_ne_root.ne_id
WHERE t_bz_config_ci_ne_root.host_name LIKE '%ciscoA%' 
  AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY `event_type_name`;
```

**❌ 错误分析**:
1. **表选择错误**: 使用了 `t_bz_sdn_alarm` 而非正确的 `event_history`
2. **关联方式错误**: 应通过设备表 `t_bz_config_ci_ne_root` 的 `host_name` 模糊匹配
3. **时间函数错误**: 使用硬编码日期而非动态函数 `DATE_SUB(CURDATE(), INTERVAL 1 MONTH)`

---

### 测试 2: 设备 down 状态超3个月

| 项目 | 内容 |
|------|------|
| **问题** | 列出平台上设备device state down状态超过3个月的设备清单及客户名称 |
| **表召回** | ✅ 100% |
| **SQL正确** | ❌ **错误** |

**LinkAlign 生成的 SQL (核心部分)**:
```sql
SELECT `sdw_dp_device`.`dev_name`, `customer`.`CUSTOMER_NAME` 
FROM `sdw_dp_device` 
JOIN `customer` ON `sdw_dp_device`.`customer_id` = `customer`.`CUSTOMER_ID` 
JOIN `sdw_dp_device_performance` ON `sdw_dp_device`.`dev_id` = `sdw_dp_device_performance`.`dev_id` 
WHERE `sdw_dp_device_performance`.`device_status` = 'down' 
  AND `sdw_dp_device_performance`.`gather_time` <= 'xxx'
```

**正确 SQL**:
```sql
SELECT `t_bz_config_ci_ne_root`.`NE_ID`, `t_bz_config_ci_ne_root`.`HOST_NAME`, `t_bz_config_customer`.`CUSTOMER_NAME`
FROM `t_bz_config_ci_ne_root`
JOIN `t_bz_config_customer` ON `t_bz_config_ci_ne_root`.`CUSTOMER_ID` = `t_bz_config_customer`.`CUSTOMER_ID`
JOIN `event_history` ON `t_bz_config_ci_ne_root`.`NE_ID` = `event_history`.`NE_ID`
WHERE `event_history`.`EVENT_NAME` LIKE 'Device state%' 
  AND `event_history`.`EVENT_TIME` <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH);
```

**❌ 错误分析**:
1. **核心表完全错误**: 使用 `sdw_dp_device` 系列表而非 `t_bz_config_ci_ne_root`
2. **事件状态查询方式错误**: 应通过 `event_history.EVENT_NAME` 匹配 'Device state%'
3. **客户表名错误**: `customer` vs `t_bz_config_customer`

---

### 测试 3: 客户数量

| 项目 | 内容 |
|------|------|
| **问题** | 现在平台上有多少家客户 |
| **表召回** | ✅ 100% |
| **SQL正确** | ❌ **错误** (逻辑相近但实现不同) |

**LinkAlign 生成**: 未完整输出（思考过程过长）

**正确 SQL**:
```sql
SELECT COUNT(`CUSTOMER_ID`) AS `customer_count`
FROM t_bz_config_customer
WHERE `IS_ACTIVE` = 1;
```

**❌ 错误分析**:
1. **表名不准确**: 应使用 `t_bz_config_customer` 而非 `customer`
2. **缺少状态过滤**: 应添加 `IS_ACTIVE = 1` 条件
3. **强制 JOIN 导致过度复杂化**

---

### 测试 4: 设备数量

| 项目 | 内容 |
|------|------|
| **问题** | 现在平台上有多少台设备 |
| **表召回** | ✅ 100% |
| **SQL正确** | ❌ **错误** |

**LinkAlign 生成**:
```sql
SELECT COUNT(*) AS total_devices 
FROM `sdw_dp_device` 
JOIN `sdw_dp_site` ON `sdw_dp_device`.`platform` = `sdw_dp_site`.`platform` 
WHERE `sdw_dp_site`.`platform` = 'xxx';
```

**正确 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `device_count`
FROM t_bz_config_ci_ne_root
WHERE `IS_DELETED` = 0;
```

**❌ 错误分析**:
1. **核心表完全错误**: 设备主表应为 `t_bz_config_ci_ne_root`
2. **无意义的 JOIN**: 强制加入不相关的 `sdw_dp_site`
3. **缺少删除状态过滤**: `IS_DELETED = 0`

---

### 测试 5: 上月新设备

| 项目 | 内容 |
|------|------|
| **问题** | 上个月上线的新设备有多少 |
| **表召回** | ❌ **0%** (丢失在 LLM过滤轮次2) |
| **SQL正确** | ❌ **错误** |

**LinkAlign 生成** (使用了错误的表):
```sql
SELECT SUM(`NUM`) AS new_devices 
FROM `report_new_dev` r 
JOIN `t_gn_all_net_device` d ON r.`REP_MONTH` = d.`region_name` 
WHERE r.`REP_MONTH` = '2023-03' AND r.`STATUS` = '新设备';
```

**正确 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `new_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `ONLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
```

**❌ 错误分析**:
1. **核心表被过滤掉**: `t_bz_config_ci_ne_root` 在 LLM 过滤阶段丢失
2. **使用报表表而非设备主表**: `report_new_dev` 是汇总表，不是设备明细表
3. **JOIN 条件完全无意义**: `REP_MONTH = region_name` 毫无关联

---

### 测试 6: 上月下线设备

| 项目 | 内容 |
|------|------|
| **问题** | 上个月下线的设备有多少 |
| **表召回** | ❌ **0%** (丢失在 LLM过滤轮次2) |
| **SQL正确** | ❌ **错误** |

**正确 SQL**:
```sql
SELECT COUNT(`CI_ID`) AS `offline_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `OFFLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
```

**❌ 错误分析**: 同测试5，核心表被错误过滤

---

### 测试 7: 客户设备近一周告警

| 项目 | 内容 |
|------|------|
| **问题** | 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？ |
| **表召回** | ❌ **67%** (丢失 `t_bz_config_ci_ne_root`) |
| **SQL正确** | ❌ **错误** |

**❌ 错误分析**: 使用了 `event_backup` + `event_history_sdwan` 而非正确的 `event_history` + `t_bz_config_ci_ne_root`

---

## ⏱ 性能分析

### 单次测试耗时详情

| 测试 | 向量检索 | LLM过滤 | 总时间 | LLM调用次数(估) |
|------|---------|---------|--------|-----------------|
| 1 | 174.5s | 502.3s | **702.8s** | ~900 |
| 2 | 105.6s | 605.7s | **739.1s** | ~1000 |
| 3 | 114.1s | 532.0s | **702.5s** | ~800 |
| 4 | 156.4s | 518.9s | **713.5s** | ~800 |
| 5 | 122.9s | 459.4s | ~620s | ~700 |
| 6 | ~100s | ~500s | **654.5s** | ~750 |
| 7 | ~100s | ~500s | ~650s | ~800 |

**⚠️ 问题汇总**:
- **平均单次测试耗时**: 约 **12分钟**
- **平均 LLM 过滤耗时**: 约 **8-10分钟** (占总时间 70-75%)
- **LLM 过滤轮次**: 固定 4 轮
- **每轮过滤 LLM 调用**: 约 150-200 次

---

## 🔧 根因分析与改进建议

### 1. SQL 生成 0% 正确率的根本原因

#### A. Schema 理解偏差
| 问题 | 描述 |
|------|------|
| **核心表不明确** | LLM 无法识别 `t_bz_config_ci_ne_root` 是设备主表 |
| **表名相似混淆** | `customer` vs `t_bz_config_customer`，`event_history` vs `event_history_sdwan` |
| **关联字段不清** | 不知道应该通过 `NE_ID` 关联设备和事件 |

#### B. Prompt 模板问题
| 问题 | 描述 |
|------|------|
| **强制 JOIN 要求** | 导致在简单查询中强制加入无关表 |
| **思考过程冗长** | 输出包含大量 `<think>` 标签，增加 token 消耗 |
| **缺乏业务知识** | 不知道 'Device state down' 是特定的事件名称模式 |

#### C. LLM 过滤问题
| 问题 | 描述 |
|------|------|
| **过滤过于激进** | `t_bz_config_ci_ne_root` 在 LLM 过滤轮次2 被错误移除 |
| **时间相关查询弱** | 涉及 ONLINE_TIME / OFFLINE_TIME 的查询表召回率极低 |
| **reserve_df 未生效** | 核心表未被保护 |

### 2. 性能问题根因

| 问题 | 原因 | 影响 |
|------|------|------|
| **LLM 调用过多** | 多轮过滤 × 多次判断 | 12分钟/测试 |
| **固定 4 轮过滤** | 无论表数多少都执行 4 轮 | 简单查询同样慢 |
| **向量检索范围大** | 每次检索 120-160 张表 | 过滤负担重 |

---

## 💡 改进建议

### 立即可做 (Quick Wins)

1. **优化 SQL 生成 Prompt**
   - 移除强制 JOIN 要求
   - 添加输出格式约束，禁止 `<think>` 标签
   - 明确指定主表优先级

2. **增强 Schema 元数据**
   ```
   t_bz_config_ci_ne_root: 设备主表，存储所有设备基础信息
   - CI_ID: 设备唯一标识
   - ONLINE_TIME: 设备上线时间
   - OFFLINE_TIME: 设备下线时间
   - IS_DELETED: 删除标记 (0=未删除)
   ```

3. **调整 LLM 过滤参数**
   - 降低 `post_retrieval_turn` 从 4 → 2
   - 增加 `reserve_rate` 保护更多核心表
   - 添加业务核心表白名单

### 中期优化

1. **建立表优先级索引**
   - 核心表: `t_bz_config_ci_ne_root`, `t_bz_config_customer`, `event_history`
   - 过滤时永不移除核心表

2. **添加 SQL 验证层**
   - 检查生成的 SQL 是否使用了召回的表
   - 表名自动校正

3. **减少 LLM 调用**
   - 基于表数量动态调整过滤轮次
   - 列数 < 100 时跳过后续轮次

---

## 📈 结论

### 当前状态评估

| 维度 | 评分 | 说明 |
|------|------|------|
| **表召回能力** | ⭐⭐⭐ (57%) | 简单查询良好，复杂查询有丢失 |
| **SQL 正确性** | ⭐ (0%) | 所有生成 SQL 均无法直接使用 |
| **执行效率** | ⭐ | 12分钟/查询过慢 |
| **生产可用性** | ❌ | 当前不可用于生产环境 |

### 适用场景

✅ **适合**:
- 探索性表发现
- Schema 范围缩小
- 辅助理解数据库结构

❌ **不适合**:
- 生产环境 SQL 自动生成
- 需要准确 SQL 的应用
- 实时/低延迟场景

### 下一步行动

1. 优化 Schema 元数据质量
2. 调整 LLM 过滤参数
3. 改进 SQL 生成 Prompt
4. 建立核心表保护机制
5. 添加 SQL 后处理校验

---

*报告生成时间: 2025-12-12 13:45*
