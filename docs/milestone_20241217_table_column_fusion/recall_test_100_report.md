# 100 个测试问题表召回率测试报告

**测试时间**: 2025-12-19 11:26:50

**测试问题**: 100 个

---

## 汇总

| 指标 | 数量 | 占比 |
|-----|------|------|
| ✅ 完全召回 | 65 | 65.0% |
| ⚠️ 部分召回 | 28 | 28.0% |
| ❌ 未召回 | 7 | 7.0% |
| **总计** | **100** | **100%** |

**平均召回率**: 78.8%

---

## 失败案例（未召回）

| ID | 问题 | 期望表 |
|----|----- |-------|
| 5 | 列出上个月新增设备数量最多的前5个客户... | t_bz_config_ci_ne_root, t_bz_config_customer |
| 6 | 查询当前处于'挂起'状态的告警工单数量... | t_bz_incident_info |
| 7 | 统计每个客户配置的服务包（service package）数量，并列出数量大于3... | t_bz_config_customer, ne_service_package |
| 18 | 列出最近30天内，处理时长超过24小时的告警工单（从创建到关闭）... | t_bz_incident_info |
| 20 | 统计当前系统中，各严重等级（severity）的未确认告警数量... | event_history |
| 32 | 统计每个客户拥有的设备数量，并按设备数量从高到低排序，显示前10名... | t_bz_config_customer, t_bz_config_ci_ne_root |
| 75 | 列出最近24小时内CPU使用率持续超过90%的设备，并关联其所属客户... | sdw_dp_device_performance, t_bz_config_ci_ne_root, t_bz_config_customer |

---

## 部分召回案例

| ID | 问题 | 召回率 | 匹配表 | 缺失表 |
|----|----- |--------|-------|-------|
| 10 | 统计各设备类型（ne_type）下的设备数量，并按数量降序排... | 50% | ne_type | t_bz_config_ci_ne_root |
| 11 | 查询最近一周内，端口流量使用率（95峰值）最高的前10个设备... | 50% | report_port_info | t_bz_config_ci_ne_root |
| 12 | 列出所有未配置任何联系人的客户... | 50% | t_rl_config_ci_contact | t_bz_config_customer |
| 13 | 统计上个月每个客户产生的告警事件总数... | 33% | event_history | t_bz_config_ci_ne_root, t_bz_config_customer |
| 14 | 查询当前系统中所有'管理员'角色的用户数量... | 67% | framework_role, framework_user_role | framework_user |
| 19 | 查询客户'XYZ科技'使用的所有云监控密钥（cloud mo... | 50% | customer_cloud_monitor_key | t_bz_config_customer |
| 24 | 统计每个区域（region）下的设备数量... | 67% | t_bz_config_ci_ne_root_region_location_relation, t_bz_config_region | t_bz_config_ci_ne_root |
| 31 | 查询所有未确认（ACK_STATUS=0）且严重程度为'严重... | 50% | event_history | t_bz_config_ci_ne_root |
| 35 | 查询设备'Router-01'（假设HOST_NAME='R... | 50% | sdw_dp_port_performance | sdw_dp_device |
| 42 | 查询设备'Switch-01'（假设HOST_NAME='S... | 67% | ne_service_package, service_package | t_bz_config_ci_ne_root |
| 44 | 统计每个区域（REGION）下有多少个客户... | 50% | t_bz_config_region | t_bz_config_customer |
| 46 | 查询所有'高'优先级（PRIORITY_NAME='高'）的... | 50% | t_bz_change_info | t_dc_change_priority |
| 50 | 查询用户'admin'（假设USER_NAME='admin... | 67% | framework_role, framework_user_role | framework_user |
| 54 | 列出客户'ABC公司'名下所有设备的ID、名称和IP地址... | 50% | t_bz_config_ci_ne_root | t_bz_config_customer |
| 55 | 统计上个月每个客户产生的告警事件数量，并按数量降序排列... | 33% | event_history | t_bz_config_ci_ne_root, t_bz_config_customer |
| 57 | 找出当前处于'挂起'状态的工单，并列出其工单ID、客户名称和... | 50% | t_bz_work_info | t_bz_config_customer |
| 58 | 统计每个设备类型（如路由器、交换机）在当前平台上的数量... | 50% | t_bz_config_ci_ne_root | ne_type |
| 60 | 列出所有采集机状态为'异常'的设备，并关联其负责的客户名称... | 67% | collector_v2, customer_collector_v2 | t_bz_config_customer |
| 65 | 查询所有'严重'级别的未确认告警，并关联设备名称和客户联系人... | 25% | event_history | t_bz_config_ci_ne_root, t_bz_config_contact |
| 68 | 查询用户'admin'所拥有的所有角色及权限... | 40% | framework_role, framework_role_authority | framework_user, framework_authority |

---

*报告生成时间: 2025-12-19 11:26:50*
