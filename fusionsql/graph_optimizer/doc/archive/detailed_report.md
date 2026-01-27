# FusionSQL 图算法技术分析报告

> 生成时间：2025-02-14

## 0. 环境与数据准备

### 0.1 “7 题测试”确认
来源：`tests/test_7q.py`（与 `tests/7q_full_test_result.json` 一致）

1. 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计
2. 列出平台上设备device state down状态超过3个月的设备清单及客户名称
3. 现在平台上有多少家客户
4. 现在平台上有多少台设备
5. 上个月上线的新设备有多少
6. 上个月下线的设备有多少
7. 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？

### 0.2 目录准备
已创建：`fusionsql/graph_optimizer/doc/`

### 0.3 本次运行限制与可用数据
- **缺失依赖**：`FlagEmbedding` 与 `neo4j` Python 包未安装，无法本地重跑 BGE 检索与 Neo4j 图优化。
- **网络受限**：LLM 端点为内网地址（`http://172.31.24.112:8502/v1`），当前环境无法访问，无法重跑 SQL 生成。
- **替代数据源**：
  - `tests/7q_full_test_result.json`（最近一次完整 pipeline 运行结果，含检索表与 SQL）
  - `tests/graph_compare_result.json`（图优化前后表名单对比）
  - `fusionsql/graph_optimizer/docs/REPORT.md`（V1/V2 算法与 Neo4j 诊断）

> 结论：本报告以**现有运行日志与代码分析**为主；无法在当前环境重新跑完整 pipeline（Retrieve → Graph Pruning → SQL Generation）。

---

## 1. 图算法代码与核心逻辑概览

- `fusionsql/graph_optimizer/algorithms.py`
  - `personalized_pagerank()`：以候选表为种子做 PPR。
  - `find_steiner_subgraph()`：Steiner 近似。
  - `compute_connectivity_score()`：候选表间 1-hop 连通性。
- `fusionsql/graph_optimizer/optimizer.py`
  - `hybrid`：**Boost-Only**，图分只加不减；**不截断**候选表。
  - `steiner_tree` / `connectivity`：仍有截断逻辑（`MIN_TABLES/ MAX_TABLES`）。
- `fusionsql/graph_optimizer/config.py`
  - `RELATION_WEIGHTS`：`IS=1.0`，`MOSTLYIS=0.2`。
  - `WEIGHTS`：V1 时代的加权公式仍保留，但 **当前 hybrid 已不使用**。
- `fusionsql/graph_optimizer/graph_cache.py`
  - 全局度中心性缓存；未命中则度分为 0。

---

## 2. 关键点检查 1：单表问题的“惩罚”是否会过滤正确答案？

**结论：在当前 `hybrid` 策略下，单表正确答案不会被“惩罚性过滤”，但排序可能被拉开。**

证据与原因：
- `hybrid` 使用 **Boost-Only**（`optimizer.py`），图分只加不减；即使孤立表连通性为 0，也不会被扣分。
- `hybrid` **不截断**候选表（直接返回全部排序结果），不会因“排名下降”而被过滤。
- 单表查询的正确表多数是 BGE Top1（`REPORT.md`），即使没有图提升也能保留。

风险点：
- 若调用方在图优化后**再次截断**（例如只取 TOP-N），孤立表可能被别的表“加分超车”。
- 使用 `steiner_tree` 或 `connectivity` 策略时，仍可能裁掉孤立表（存在 `MIN/MAX/TARGET_TABLES` 截断）。

改进建议：
- 单表问题直接跳过图优化，或开启“强保留 Top1”。
- 对 `connectivity/steiner` 增加“保留原始 TopK”保护策略。

---

## 3. 关键点检查 2：算法演变（初期 vs 当前）

### 初期（V1）逻辑（来自 `docs/REPORT.md`）
- **线性加权**：`final = 0.70×BGE_norm + 0.15×PPR + 0.10×Conn + 0.05×Degree`。
- **BGE 归一化**：压缩差异，容易被图分“翻盘”。
- **PPR 均匀播种**：忽略 BGE 排名差异。
- **硬截断到 8 表**：`TARGET_TABLES=8`，导致 BGE 第 9-10 名被切掉。

### 当前（V2）逻辑（`optimizer.py`）
- **Boost-Only**：图分只能加分，不能倒扣。
- **保留原始 BGE 分数**：不再归一化 BGE。
- **连通性参考集扩大至 top10**：减少连通性过度为 0 的问题。
- **不截断**：`hybrid` 直接返回全部候选。

### 变化总结
| 维度 | V1 | V2（当前） |
|---|---|---|
| BGE 分数处理 | 归一化 | 保留原分 | 
| 图特征影响 | 可加可减 | 只加不减 | 
| 返回数量 | 截断到 8 | 不截断 | 
| 连通性参考集 | top5 | top10 | 

---

## 4. Pipeline 运行与日志记录（受限条件下的可复用结果）

### 4.1 可复用结果来源
- **完整 pipeline（含 SQL）**：`tests/7q_full_test_result.json`
- **图优化前后表名单对比**：`tests/graph_compare_result.json`
- **Neo4j 关系诊断**：`fusionsql/graph_optimizer/docs/REPORT.md`

### 4.2 Neo4j 边与权重（导师关注点）
- 当前环境无法连接 Neo4j（缺失 `neo4j` 包）。
- 参考 `REPORT.md` 结论：**7 题的 BGE 候选表之间均未发现 IS/MOSTLYIS 关系**。
- 结论：**边数 = 0，权重 = N/A**（无法计算）。

---

## 5. 第 7 题深度复盘（检索 → 图优化 → SQL）

### 5.1 BGE 检索 Top 表（来自 `tests/7q_full_test_result.json`）
`t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_bz_config_customer`, `t_bz_incident_info`, `event_yjk_history`, `ne_syslog_filter_script`, `syslog_filter_script`, **`event_history`**, `event_sdn`, `t_gn_botnet`, ...

**结论**：BGE Top N 中已包含全部正确表：
- `event_history` ✅（第 8）
- `t_bz_config_ci_ne_root` ✅（第 1）
- `t_bz_config_customer` ✅（第 3）

### 5.2 图优化后是否保留正确表？
- `tests/graph_compare_result.json` 显示图优化后 TOP10 仍包含上述三表。
- 图优化未剔除正确表。

### 5.3 SQL 错误链路定位
- 生成 SQL（摘自 `tests/7q_full_test_result.json`）：
  - 未使用 `t_bz_config_customer`
  - 使用了占位 `CUSTOMER_ID = 12345`
  - 使用列 `ALARM_CLEAR_TIME`（**schema 中不存在**，`event_history.json` 未定义）

**结论**：错误来自 **SQL 生成环节**，非检索或图剪枝问题。
- Schema 信息虽已提供，但 LLM 没有选择 customer 表。
- `event_history` 表中并无明确的“恢复时间”字段，导致列幻觉。

改进建议（Q7）：
- 在 prompt 中增加 **“恢复时间字段不存在时使用替代字段或返回 NULL”** 的约束。
- 对 “某客户” 语义要求，明确提示 **必须 JOIN customer**，并允许参数化条件。

---

## 6. 单表惩罚机制分析与改进建议

### 代码层面证据
- `optimizer.py` 的 `hybrid`：Boost-Only，不会减少 BGE 分数。
- `hybrid` 不截断，避免被 TopN 过滤。
- `steiner_tree` / `connectivity` 仍截断（`MIN/MAX/TARGET_TABLES`）。

### 改进建议
- **策略选择**：单表查询直接跳过图优化。
- **保留兜底**：图优化后强保留 BGE Top1 或期望表。
- **特征权重**：若子图无边（全 0），直接跳过图分计算（避免无意义加分）。

---

## 7. 运行数据透视（7 题总览）

> 说明：BGE Top List 来自 `tests/7q_full_test_result.json`（最近一次 pipeline 运行）。
> 图算法分数分布在当前环境无法重新计算（缺失 Neo4j & FlagEmbedding）。
> 结合 `REPORT.md`，这 7 题候选表间外键为 0，图优化仅对分数做等幅提升，**排序不变**。

### Q1
- **BGE Top List**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_bz_incident_info`, `t_bz_config_ci_entity`, `ne_syslog_filter_script`, `t_bz_config_customer`, `t_gn_botnet`, `event_yjk_history`, `t_bz_problem_info`, `event_history`, `sdw_dp_port_basic`, `t_bz_config_ci_rfc`, `t_gn_vulnerability_weak_password`, `t_gn_weaknesses_attack`, `report_new_dev`, `t_dc_incident_accident_type`, `t_dc_release_type`, `t_dc_service_source_type`, `event_type`
- **图算法 Score 分布**：无法重算；参考 `REPORT.md`，无边 → Boost-Only 等幅提升。
- **被保留的 Schema（图优化后 Top10）**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_bz_incident_info`, `t_bz_config_ci_entity`, `ne_syslog_filter_script`, `t_bz_config_customer`, `t_gn_botnet`, `event_yjk_history`, `t_bz_problem_info`, `event_history`
- **边/权重**：0 条（参考 `REPORT.md`）

### Q2
- **BGE Top List**：
  `t_bz_config_customer`, `t_gn_topo_link`, `t_gn_topo_device`, `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `sdw_dp_device`, `t_dc_config_device_type`, `sdw_dp_device_performance`, `event_history`, `customer`, `sdw_dp_port_performance`, `sdwan_device`, `t_gn_all_net_device`, `topology_point_port`, `atomic_cutover_order`
- **图算法 Score 分布**：无法重算；无边 → Boost-Only 等幅提升。
- **被保留的 Schema（图优化后 Top10）**：
  `t_bz_config_customer`, `t_gn_topo_link`, `t_gn_topo_device`, `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `sdw_dp_device`, `t_dc_config_device_type`, `sdw_dp_device_performance`, `event_history`, `customer`
- **边/权重**：0 条（参考 `REPORT.md`）

### Q3
- **BGE Top List**：
  `t_bz_config_customer`, `customer`, `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_bz_authority_users`, `event_yjk_history`, `t_bz_incident_info`, `t_bz_config_work_policy_new`, `temp`, `customer_collector_v2`, `event_history`, `t_bz_config_ci_entity`, `t_bz_config_ci_circuit`, `t_bz_config_location`, `t_bz_config_group`, `customer_global_config`, `customer_model_rl`
- **图算法 Score 分布**：无法重算；无边 → Boost-Only 等幅提升。
- **被保留的 Schema（图优化后 Top10）**：
  `t_bz_config_customer`, `customer`, `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_bz_authority_users`, `event_yjk_history`, `t_bz_incident_info`, `t_bz_config_work_policy_new`, `temp`, `customer_collector_v2`
- **边/权重**：0 条（参考 `REPORT.md`）

### Q4
- **BGE Top List**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_gn_traffic_abnormality`, `t_gn_scanning_probe`, `t_gn_botnet`, `t_gn_topo_link`, `t_gn_weaknesses_attack`, `t_gn_vulnerability_clear_transmission`, `sdw_dp_device`, `ont_status`, `ne`, `hardware`, `t_bz_sys_dev_additional`, `ne_business_severity`, `collector`, `ne_collect_record`, `t_gn_all_net_device`, `uptime`
- **图算法 Score 分布**：无法重算；无边 → Boost-Only 等幅提升。
- **被保留的 Schema（图优化后 Top10）**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_gn_traffic_abnormality`, `t_gn_scanning_probe`, `t_gn_botnet`, `t_gn_topo_link`, `t_gn_weaknesses_attack`, `t_gn_vulnerability_clear_transmission`, `sdw_dp_device`, `ont_status`
- **边/权重**：0 条（参考 `REPORT.md`）

### Q5
- **BGE Top List**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_gn_traffic_abnormality`, `t_gn_scanning_probe`, `t_gn_botnet`, `t_gn_weaknesses_attack`, `t_gn_topo_link`, `t_gn_vulnerability_clear_transmission`, `sdw_dp_device`, `ont_status`, `t_gn_vulnerability_hole`, `ne`, `hardware`, `t_bz_sys_dev_additional`, `ne_business_severity`, `collector`, `ne_collect_record`, `uptime`, `t_gn_all_net_device`
- **图算法 Score 分布**：无法重算；无边 → Boost-Only 等幅提升。
- **被保留的 Schema（图优化后 Top10）**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_gn_traffic_abnormality`, `t_gn_scanning_probe`, `t_gn_botnet`, `t_gn_weaknesses_attack`, `t_gn_topo_link`, `t_gn_vulnerability_clear_transmission`, `sdw_dp_device`, `ont_status`
- **边/权重**：0 条（参考 `REPORT.md`）

### Q6
- **BGE Top List**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_gn_traffic_abnormality`, `ont_status`, `t_gn_scanning_probe`, `t_gn_botnet`, `t_gn_topo_link`, `t_gn_weaknesses_attack`, `t_gn_vulnerability_clear_transmission`, `sdw_dp_device`, `uptime`, `trap`, `hardware`, `t_bz_sys_dev_additional`, `ne_business_severity`, `collector`, `ne_collect_record`, `t_gn_all_net_device`
- **图算法 Score 分布**：无法重算；无边 → Boost-Only 等幅提升。
- **被保留的 Schema（图优化后 Top10）**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_gn_traffic_abnormality`, `ont_status`, `t_gn_scanning_probe`, `t_gn_botnet`, `t_gn_topo_link`, `t_gn_weaknesses_attack`, `t_gn_vulnerability_clear_transmission`, `sdw_dp_device`
- **边/权重**：0 条（参考 `REPORT.md`）

### Q7
- **BGE Top List**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_bz_config_customer`, `t_bz_incident_info`, `event_yjk_history`, `ne_syslog_filter_script`, `syslog_filter_script`, `event_history`, `event_sdn`, `t_gn_botnet`, `event_backup`, `event_history_sdwan`, `ne_business_severity`, `report_new_dev`, `event_knowledge`, `t_dc_release_type`, `t_dc_incident_finish`
- **图算法 Score 分布**：无法重算；无边 → Boost-Only 等幅提升。
- **被保留的 Schema（图优化后 Top10）**：
  `t_bz_config_ci_ne_root`, `t_gn_business_application_change`, `t_bz_config_customer`, `t_bz_incident_info`, `event_yjk_history`, `ne_syslog_filter_script`, `syslog_filter_script`, `event_history`, `event_sdn`, `t_gn_botnet`
- **边/权重**：0 条（参考 `REPORT.md`）

---

## 8. 结论（优缺点总结）

**优点**
- BGE 召回稳定，7 题检索均覆盖期望表。
- V2 Boost-Only 策略避免“图优化反杀”问题。
- 单表查询几乎不受图优化影响，稳定性好。

**缺点 / 风险**
- 依赖 Neo4j 的外键图质量；若候选表间无边，图优化无法发挥作用。
- SQL 生成环节仍是主要瓶颈（Q7 的错误来自 SQL 生成与 schema 误用）。
- `steiner_tree` / `connectivity` 仍有截断风险，可能影响单表或低连接表。

**建议方向**
- 缺边场景直接降级到纯 BGE（或跳过图优化）。
- 为 SQL 生成增加“字段不存在时回退策略”。
- 对“某客户”类问题增加参数化提示，强制 JOIN customer。
