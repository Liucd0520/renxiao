# 图簇分析报告

> 分析候选表通过外键关系形成的连通分量（簇）结构

---

## 1. 研究背景

### 1.1 研究动机

用户提出一个假设：

> "比如说 10-20 张表，里面有外键关系，使用外键相连，能够得到 5-6 个可以通过外键相连形成的路的簇，这里面可以重复。"

**核心问题**：簇结构能否帮助我们更好地选择表？

### 1.2 分析方法

对每个查询的候选表：
1. 构建包含 1-hop 邻居的子图
2. 使用连通分量算法（BFS/DFS）找出所有簇
3. 统计簇的数量、大小、包含的表

---

## 2. 实验数据

### 2.1 全局统计

| 查询 | 候选表数 | 扩展后边数 | 簇数 | 最大簇大小 | 孤立表数 |
|------|----------|------------|------|------------|----------|
| Q1: 告警统计 | 10 | 63 | 8 | 63 | 7 |
| Q2: 设备状态 | 10 | 63 | 8 | 63 | 7 |
| Q3: 客户数量 | 10 | 63 | 8 | 63 | 7 |
| Q4: 设备数量 | 10 | 63 | 8 | 63 | 7 |
| Q5: 新上线设备 | 10 | 63 | 8 | 63 | 7 |
| Q6: 下线设备 | 10 | 63 | 8 | 63 | 7 |
| Q7: 客户告警 | 10 | 63 | 8 | 63 | 7 |

**平均值**：
- 平均候选表数: 10.0
- 平均边数: 63.0
- 平均簇数: 8.0
- 平均孤立表数: 7.0

### 2.2 簇大小分布

| 簇大小 | 出现次数 | 占比 |
|--------|----------|------|
| 1 个表（孤立） | 49 | 87.5% |
| 63 个表（巨型簇） | 7 | 12.5% |

**观察**：所有查询都呈现相同的模式——**1个巨型簇 + 7个孤立表**。

---

## 3. 详细簇结构

### 3.1 Q1: 告警统计

**候选表（BGE 排序）**：
| 排名 | 表名 | BGE 分数 | 所属簇 |
|------|------|----------|--------|
| 1 | t_bz_config_ci_ne_root | 5.07 | 簇1 (巨型) |
| 2 | t_bz_event_month | 2.77 | 孤立 |
| 3 | t_bz_config_customer | 2.53 | 簇1 (巨型) |
| 4 | v_event_first_today | 2.37 | 孤立 |
| 5 | v_event_first_history | 2.35 | 孤立 |
| 6 | t_bz_event_day | 2.16 | 孤立 |
| 7 | t_bz_event_total | 1.88 | 孤立 |
| 8 | t_bz_run_event_current | 1.72 | 孤立 |
| 9 | t_bz_run_ci_ne_cpe | 1.60 | 孤立 |
| 10 | event_history ⭐ | 1.55 | 簇1 (巨型) |

**簇1 详细内容（63个表）**：

核心表（在候选中）：
- `t_bz_config_ci_ne_root` ← 候选表
- `t_bz_config_customer` ← 候选表
- `event_history` ← **关键表**

扩展进来的邻居表（60个）：
```
business, customer, customer_cloud_monitor_key, customer_collector_v2,
customer_model_rl, customer_svr_pkg_limit, event, event_backup,
event_condition, event_history_sdwan, event_type, ne, ne_business_severity,
ne_collect_history, ne_collect_record, ne_protocol_inst, ne_service_collect,
ne_service_item, ne_service_package, ne_syslog_filter_script,
ne_template_access_config, ne_template_collect_config, ne_token, ont_status,
protocol_inst, r_template_customer, report_cust_reachability_ext, report_inst,
route_log, service_package, syslog_filter_script, syslog_server,
t_bz_authority_users, t_bz_authority_users_group, t_bz_config_ci_audit_flow,
t_bz_config_ci_circuit, t_bz_config_ci_ne_root_region_location_relation,
t_bz_config_department, t_bz_config_group, t_bz_config_location,
t_bz_config_region, t_bz_config_work_policy_new, t_bz_customer_poller_config,
t_bz_incident_ci_record, t_bz_incident_event_record, t_bz_incident_transfer,
t_bz_ip_region_manage, t_bz_problem_info, t_bz_release_info,
t_bz_service_ci_record, t_bz_service_evaluation, t_bz_sys_email_record,
t_bz_sys_note, t_bz_sys_operate_audit, t_bz_sys_operator_record,
t_bz_sys_sms_record, t_rl_authority_customer_rolegroup,
t_rl_authority_user_range, t_rl_user_customer, uptime
```

**孤立表（7个）**：
| 表名 | 类型 | 为什么孤立 |
|------|------|------------|
| t_bz_event_month | 统计表 | 无外键定义 |
| v_event_first_today | 视图 | 视图无外键 |
| v_event_first_history | 视图 | 视图无外键 |
| t_bz_event_day | 统计表 | 无外键定义 |
| t_bz_event_total | 统计表 | 无外键定义 |
| t_bz_run_event_current | 运行表 | 无外键定义 |
| t_bz_run_ci_ne_cpe | 运行表 | 无外键定义 |

---

### 3.2 Q2: 设备状态

**候选表（BGE 排序）**：
| 排名 | 表名 | BGE 分数 | 所属簇 |
|------|------|----------|--------|
| 1 | t_bz_config_ci_ne_root | 7.47 | 簇1 (巨型) |
| 2 | v_event_first_today | 2.99 | 孤立 |
| 3 | t_bz_event_month | 2.92 | 孤立 |
| 4 | t_bz_config_customer | 2.82 | 簇1 (巨型) |
| 5 | t_bz_event_day | 2.20 | 孤立 |
| 6 | v_event_first_history | 2.01 | 孤立 |
| 7 | t_bz_run_event_current | 1.75 | 孤立 |
| 8 | t_bz_event_total | 1.64 | 孤立 |
| 9 | event_history ⭐ | 1.27 | 簇1 (巨型) |
| 10 | t_bz_run_ci_ne_cpe | 1.24 | 孤立 |

**簇结构**：与 Q1 完全相同（1 个 63 表的巨型簇 + 7 个孤立表）

---

### 3.3 Q3: 客户数量

**候选表（BGE 排序）**：
| 排名 | 表名 | BGE 分数 | 所属簇 |
|------|------|----------|--------|
| 1 | t_bz_config_customer ⭐ | 11.46 | 簇1 (巨型) |
| 2 | t_bz_order_customer | 3.82 | 孤立 |
| 3 | t_bz_order_detail | 2.62 | 孤立 |
| 4 | t_bz_config_customer_vip | 2.19 | 孤立 |
| 5 | t_bz_run_ci_ne_cpe | 1.41 | 孤立 |
| 6 | t_bz_config_ci_ne_root | 1.33 | 簇1 (巨型) |
| 7 | v_customer_detail | 1.21 | 孤立 |
| 8 | t_bz_event_month | 1.10 | 孤立 |
| 9 | event_history | 0.95 | 簇1 (巨型) |
| 10 | t_bz_event_day | 0.88 | 孤立 |

**特殊观察**：
- 这是单表查询（Q3 只需要 t_bz_config_customer）
- 关键表排名 #1，BGE 分数遥遥领先（11.46 vs 3.82）
- gap_ratio = (11.46 - 3.82) / 11.46 = **66.7%** > 50%
- 门控应正确识别为单表查询 ✅

---

### 3.4 Q7: 客户告警

**候选表（BGE 排序）**：
| 排名 | 表名 | BGE 分数 | 所属簇 |
|------|------|----------|--------|
| 1 | t_bz_config_ci_ne_root | 6.41 | 簇1 (巨型) |
| 2 | t_bz_config_customer ⭐ | 4.94 | 簇1 (巨型) |
| 3 | t_bz_event_month | 2.95 | 孤立 |
| 4 | v_event_first_today | 2.26 | 孤立 |
| 5 | t_bz_event_day | 2.20 | 孤立 |
| 6 | v_event_first_history | 2.02 | 孤立 |
| 7 | event_history ⭐ | 1.88 | 簇1 (巨型) |
| 8 | t_bz_run_event_current | 1.82 | 孤立 |
| 9 | t_bz_event_total | 1.74 | 孤立 |
| 10 | t_bz_run_ci_ne_cpe | 1.57 | 孤立 |

**关键发现**：
- 这是多表查询（需要 event_history + t_bz_config_customer）
- 两个关键表都在簇1（巨型簇）中
- 但簇1 包含 63 个表，无法区分哪些是真正需要的

---

## 4. 问题分析

### 4.1 为什么簇结构无区分度？

**根本原因**：1-hop 扩展 + 外键图的"枢纽效应"

```
候选表 (10个)
    ↓ 1-hop 扩展
扩展后 (70+个表)
    ↓
通过高出度枢纽表（如 customer, ne）连成一片
    ↓
形成 1 个巨型簇 + 若干孤立表
```

**枢纽表示例**：
| 表名 | 出度 | 说明 |
|------|------|------|
| customer | 高 | 几乎与所有业务表关联 |
| ne (网元) | 高 | 设备相关表的核心 |
| t_bz_config_ci_ne_root | 高 | 配置表的核心 |

### 4.2 孤立表的共同特征

| 类型 | 示例 | 特征 |
|------|------|------|
| 视图 (View) | v_event_first_today, v_customer_detail | 无外键定义 |
| 统计表 | t_bz_event_month, t_bz_event_day | 独立聚合，无外键 |
| 运行表 | t_bz_run_event_current | 临时/运行数据，无外键 |

### 4.3 数据结构图示

```
                    ┌─────────────────────────────────────────────────────┐
                    │                  簇 1 (巨型簇)                       │
                    │                    63 个表                          │
                    │                                                     │
                    │   ┌─────────────────────────────────────────────┐   │
                    │   │              核心候选表 (3个)                │   │
                    │   │                                             │   │
                    │   │  t_bz_config_ci_ne_root ←──FK──→ customer   │   │
                    │   │           ↑                         ↑       │   │
                    │   │           │                         │       │   │
                    │   │           FK                        FK      │   │
                    │   │           │                         │       │   │
                    │   │           ↓                         ↓       │   │
                    │   │     event_history ⭐    t_bz_config_customer │   │
                    │   │                                             │   │
                    │   └─────────────────────────────────────────────┘   │
                    │                        ↑                            │
                    │                        │ FK (多条)                  │
                    │                        ↓                            │
                    │   ┌─────────────────────────────────────────────┐   │
                    │   │           扩展进来的邻居 (60个)              │   │
                    │   │                                             │   │
                    │   │   ne, business, event, event_backup, ...    │   │
                    │   │   ne_service_*, t_bz_incident_*, ...        │   │
                    │   │                                             │   │
                    │   └─────────────────────────────────────────────┘   │
                    └─────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────┐
    │                        孤立表 (7个)                                   │
    │                                                                      │
    │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
    │  │ t_bz_event_month│  │v_event_first_today│ │ t_bz_event_day  │      │
    │  │   (统计表)       │  │   (视图)          │ │   (统计表)       │      │
    │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
    │                                                                      │
    │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
    │  │ t_bz_event_total│  │t_bz_run_event_*  │  │ t_bz_run_ci_*   │      │
    │  │   (统计表)       │  │   (运行表)        │  │   (运行表)       │      │
    │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
    └──────────────────────────────────────────────────────────────────────┘
```

---

## 5. Codex 讨论结论

### 5.1 簇想法有价值吗？

**Codex 观点**：
> "簇在你当前的图上确实'没有区分度'，但不是想法错，而是**簇的定义过于依赖 FK 图**。"

### 5.2 替代簇定义

| 簇类型 | 边的定义 | 优点 | 适用场景 |
|--------|----------|------|----------|
| **FK 簇**（当前） | 外键关系 | 精确 | 外键覆盖率高的数据库 |
| **查询共现簇** | 历史查询中常一起出现 | 反映真实使用模式 | 有查询日志 |
| **语义簇** | 表名/列名相似度 | 不依赖外键 | 外键稀疏 |
| **血缘簇** | 视图 → 基表依赖 | 解决视图孤立 | 有视图定义 |

### 5.3 建议的改进方向

1. **不做 1-hop 扩展**：只在候选表之间找簇
2. **用簇做门控/加分**：同簇表加分，孤立表谨慎
3. **加入软边**：表名相似度、列名重合等

---

## 6. 候选表内簇分析（不扩展）

为了验证 Codex 的建议，我们分析**只在 10 个候选表之间**的连通情况。

### 6.1 Q1: 告警统计（候选表内）

**候选表之间的外键边**：
```
t_bz_config_ci_ne_root ←→ t_bz_config_customer (1条)
t_bz_config_ci_ne_root ←→ event_history (1条)
t_bz_config_customer ←→ event_history (1条)
```

**边数**：3 条

**簇结构**：
```
┌─────────────────────────────────────┐
│  簇 A (3个表，通过外键相连)          │
│                                     │
│  t_bz_config_ci_ne_root             │
│           ↕                         │
│  t_bz_config_customer ←→ event_history │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  孤立表 (7个，无外键连接)            │
│                                     │
│  t_bz_event_month                   │
│  v_event_first_today                │
│  v_event_first_history              │
│  t_bz_event_day                     │
│  t_bz_event_total                   │
│  t_bz_run_event_current             │
│  t_bz_run_ci_ne_cpe                 │
└─────────────────────────────────────┘
```

**对比**：

| 方式 | 簇数 | 最大簇 | 区分度 |
|------|------|--------|--------|
| 1-hop 扩展 | 8 | 63 | ❌ 无（巨型簇） |
| 仅候选表内 | 8 | 3 | ⚠️ 略好 |

### 6.2 发现

即使不扩展邻居，候选表之间的连通性仍然很低：
- 10 个候选表，只有 3 条边
- 只有 3 个表相互连通
- 7 个表完全孤立

**结论**：外键覆盖率（17%）本身就是瓶颈，簇分析在这个数据集上难以发挥作用。

---

## 7. 结论与建议

### 7.1 核心发现

1. **当前外键图的簇结构无区分度**
   - 1-hop 扩展后形成 1 个巨型簇 + 7 个孤立表
   - 所有关键表都在巨型簇中，无法区分

2. **孤立表多为视图/统计表**
   - 这些表无外键定义，但可能是答案表
   - 不能简单惩罚孤立表

3. **外键覆盖率是根本瓶颈**
   - 17% 的外键覆盖率导致图结构稀疏
   - 候选表之间只有 3 条边

### 7.2 簇分析对论文的价值

| 用途 | 可行性 | 说明 |
|------|--------|------|
| 主排序信号 | ❌ | 区分度不足 |
| 门控信号 | ⚠️ | 需要与其他信号结合 |
| 可解释性 | ✅ | 展示表之间的连接关系 |
| 诊断工具 | ✅ | 证明 FK 簇在稀疏图上的局限 |

### 7.3 建议的后续方向

1. **短期**：将簇分析作为诊断/可解释性工具，不作为排序信号
2. **中期**：探索语义簇（表名/列名相似度）作为软边
3. **长期**：如果有查询日志，构建查询共现簇

---

## 附录：测试脚本

```python
# analyze_graph_clusters.py
# 用于分析候选表的连通分量结构
# 位置: FusionSQL/analyze_graph_clusters.py
```

运行命令：
```bash
.venv/bin/python3 analyze_graph_clusters.py
```

---

*报告生成时间: 2026-01-26*
*数据来源: 7 道测试题的图优化结果*
