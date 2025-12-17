# 测试 1 完整检索数据

**问题**: 设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计

**期望表**: ['event_history', 't_bz_config_ci_ne_root']

---

## 一、表级别 Sparse Top 10

| 排名 | 表名 | 分数 | 命中 |
|-----|------|------|-----|
| 1 | t_dc_release_type | 0.1940 |  |
| 2 | t_dc_incident_accident_type | 0.1917 |  |
| 3 | event_history | 0.1870 | ✅ |
| 4 | t_bz_config_ci_rfc | 0.1681 |  |
| 5 | t_gn_weaknesses_attack | 0.1617 |  |
| 6 | report_new_dev | 0.1615 |  |
| 7 | t_dc_service_source_type | 0.1556 |  |
| 8 | t_gn_vulnerability_weak_password | 0.1556 |  |
| 9 | t_gn_botnet | 0.1550 |  |
| 10 | event_type | 0.1544 |  |

**表级别召回**: 1/2

---

## 二、列级别 Sparse Top 200

| 排名 | 表名 | 列名 | 分数 |
|-----|------|------|-----|
| 1 | t_bz_config_ci_ne_root | ALARM_TYPE | 0.1589 |
| 2 | t_gn_weaknesses_attack | classify1_id | 0.1501 |
| 3 | t_gn_botnet | classify1_id | 0.1477 |
| 4 | t_bz_config_ci_rfc | MODIFY_CLASSIFY | 0.1467 |
| 5 | t_gn_vulnerability_hole | classify1_id | 0.1422 |
| 6 | t_gn_traffic_abnormality | classify1_id | 0.1420 |
| 7 | t_gn_vulnerability_clear_transmission | classify1_id | 0.1407 |
| 8 | t_gn_scanning_probe | classify1_id | 0.1377 |
| 9 | t_gn_vulnerability_weak_password | classify1_id | 0.1377 |
| 10 | t_bz_incident_event_record | EVENT_TYPE_ID | 0.1233 |
| 11 | t_bz_config_ci_ne_root | DEVICE_TYPE_ID | 0.1171 |
| 12 | t_bz_config_ci_ne_root | ACCOUNT | 0.1103 |
| 13 | event_history_sdwan | ALARM_MESSAGE | 0.1058 |
| 14 | t_bz_incident_event_record | EVENT_ID | 0.1041 |
| 15 | t_bz_config_ci_ne_root | CONFIRM_ALARM | 0.1039 |
| 16 | t_gn_notice | notice_type | 0.1018 |
| 17 | event_yjk_history | content | 0.0997 |
| 18 | t_bz_yun_notice | notice_type | 0.0994 |
| 19 | event_sdn | time_created | 0.0991 |
| 20 | event_sdn | is-acked | 0.0988 |
| 21 | syslog_filter_script | association_type_a | 0.0984 |
| 22 | ne_syslog_filter_script | association_type_a | 0.0983 |
| 23 | event_yjk_history | name | 0.0973 |
| 24 | t_bz_incident_event_record | EVENT_STATUS | 0.0970 |
| 25 | t_bz_sdn_alarm | ALARM_NAME | 0.0967 |
| 26 | t_gn_all_net_event | num | 0.0962 |
| 27 | event_sdn | perceived_severity | 0.0961 |
| 28 | t_bz_config_ci_ne_root | ALARM_THRESHOLD | 0.0961 |
| 29 | ne_service_item | SEVERITY | 0.0959 |
| 30 | t_gn_business_application_change | equipment_type | 0.0950 |
| 31 | t_bz_incident_event_record | EVENT_TIME | 0.0948 |
| 32 | t_gn_weaknesses_attack | classify_id | 0.0919 |
| 33 | event_yjk_history | priority | 0.0918 |
| 34 | event_sdn | location_info | 0.0914 |
| 35 | event_sdn | md_name | 0.0909 |
| 36 | t_gn_botnet | classify_id | 0.0902 |
| 37 | t_gn_vulnerability_clear_transmission | classify_id | 0.0897 |
| 38 | event_sdn | native_probable_cause | 0.0885 |
| 39 | t_gn_traffic_abnormality | classify_id | 0.0885 |
| 40 | ne_syslog_filter_script | alarm_level_a | 0.0873 |
| 41 | ne_template_collect_config | alert_level | 0.0871 |
| 42 | event_sdn | repair_action | 0.0870 |
| 43 | t_gn_scanning_probe | classify_id | 0.0868 |
| 44 | sdw_dp_device | dev_type | 0.0865 |
| 45 | syslog_filter_script | alarm_level_a | 0.0853 |
| 46 | trap_ne_policy | max_severity | 0.0846 |
| 47 | ne_template_collect_config | name | 0.0842 |
| 48 | event_sdn | alarm_type_qualifier | 0.0828 |
| 49 | event_yjk_history | hash | 0.0812 |
| 50 | t_bz_config_ci_rfc | CI_ID | 0.0811 |
| 51 | syslog_filter_script | end_time_a | 0.0807 |
| 52 | event_sdn | ip_ddress | 0.0806 |
| 53 | ne_syslog_filter_script | end_time_a | 0.0804 |
| 54 | t_bz_incident_event_record | EVENT_NAME | 0.0795 |
| 55 | t_bz_incident_event_record | EVENT_VALUE | 0.0790 |
| 56 | t_bz_config_ci_ne_root | CI_ID | 0.0790 |
| 57 | ne_syslog_filter_script | start_time_a | 0.0789 |
| 58 | ne_syslog_filter_script | facility_a | 0.0787 |
| 59 | ne_template_collect_config | description | 0.0785 |
| 60 | ne_syslog_filter_script | message_one_a | 0.0783 |
| 61 | syslog_filter_script | facility_a | 0.0783 |
| 62 | ne_syslog_filter_script | severity_a | 0.0765 |
| 63 | syslog_filter_script | start_time_a | 0.0765 |
| 64 | ne_template_access_config | username | 0.0756 |
| 65 | t_bz_sys_email_record | EMAIL_CONTENT | 0.0753 |
| 66 | t_bz_config_ci_ne_root | NE_SN | 0.0746 |
| 67 | syslog_filter_script | message_one_a | 0.0739 |
| 68 | syslog_filter_script | severity_a | 0.0739 |
| 69 | ne_template_access_config | password | 0.0734 |
| 70 | t_bz_config_ci_ne_root | NE_CONFIG | 0.0727 |
| 71 | t_bz_config_ci_ne_root | NE_GROUP | 0.0721 |
| 72 | t_bz_config_ci_ne_root_region_location_relation | ne_id | 0.0720 |
| 73 | ne_syslog_filter_script | message_two_a | 0.0705 |
| 74 | t_bz_config_ci_ne_root | NE_IMPORTANCE | 0.0704 |
| 75 | t_bz_config_ci_ne_root | NE_DESC | 0.0695 |
| 76 | syslog_filter_script | message_two_a | 0.0691 |
| 77 | t_bz_config_ci_rfc | MODIFY_TYPE | 0.0688 |
| 78 | t_gn_vulnerability_hole | branch_type | 0.0682 |
| 79 | business | BUSINESS_ABB | 0.0674 |
| 80 | trap_ne_policy | disable_alert | 0.0674 |
| 81 | t_bz_config_ci_ne_root | HOST_NAME | 0.0659 |
| 82 | sdw_dp_device | dev_model | 0.0630 |
| 83 | t_bz_sys_operate_audit | DATA_TYPE | 0.0629 |
| 84 | t_dc_report_monitor_menu | SORT_ID | 0.0624 |
| 85 | t_bz_config_ci_ne_root | SERIAL_NO_PACKETEER | 0.0619 |
| 86 | sdw_dp_device | dev_name | 0.0600 |
| 87 | t_bz_config_ci_rfc | VERSION | 0.0592 |
| 88 | event_history_sdwan | ALARM_NAME | 0.0590 |
| 89 | t_gn_business_application_change | equipment_unit | 0.0583 |
| 90 | sdw_dp_port_basic | dev_name | 0.0577 |
| 91 | t_gn_business_application_change | equipment_num | 0.0569 |
| 92 | event_condition | EVENT_VALUE | 0.0569 |
| 93 | cc_cmdb_sync_history | resource_num | 0.0568 |
| 94 | customer_cloud_monitor_count_config | title | 0.0564 |
| 95 | ont_status | description | 0.0555 |
| 96 | cc_cmdb_sync_service_catalog | resource_id | 0.0547 |
| 97 | trap_ne | ne_id | 0.0542 |
| 98 | t_bz_config_ci_ne_root_region_location_relation | type | 0.0536 |
| 99 | event_yjk_history | device | 0.0533 |
| 100 | trap_ne_policy | ne_id | 0.0530 |
| 101 | t_bz_config_ci_ne_root | PASSWORD | 0.0529 |
| 102 | t_bz_sdn_alarm | NATIVE_PROBABLE_CAUSE | 0.0529 |
| 103 | t_bz_config_work_policy_new_link | ne_id | 0.0527 |
| 104 | maintenance_info | ne_id | 0.0522 |
| 105 | maintenance_info | ne_time | 0.0520 |
| 106 | sdw_dp_tunnel_basic | a_dev_name | 0.0519 |
| 107 | syslog_server | ne_id | 0.0519 |
| 108 | ont_status | status | 0.0518 |
| 109 | sdw_dp_device_performance | device_status | 0.0516 |
| 110 | trap_ne_discard | ne_id | 0.0515 |
| 111 | t_gn_topo_link | flow_device_id | 0.0515 |
| 112 | ne_syslog_filter_script | ne_id | 0.0513 |
| 113 | t_gn_business_application_change | equipment_arg | 0.0512 |
| 114 | t_gn_business_application_change | replace_link_name | 0.0512 |
| 115 | t_gn_business_application_change | equipment_ip | 0.0510 |
| 116 | ont_status | root_ne_id | 0.0507 |
| 117 | t_gn_topo_link | src_device_id | 0.0506 |
| 118 | t_gn_business_application_change | equipment_brand | 0.0506 |
| 119 | t_gn_topo_link | flow_port_id | 0.0503 |
| 120 | t_gn_business_application_change | equipment_name | 0.0502 |
| 121 | customer | CUSTOMER_TYPE | 0.0498 |
| 122 | t_gn_topo_device | device_id | 0.0497 |
| 123 | t_gn_topo_device | device_status | 0.0494 |
| 124 | customer_global_config | DISCOVER_TIME | 0.0493 |
| 125 | sdw_dp_port_performance | port_state | 0.0492 |
| 126 | t_gn_business_application_change | serve_type | 0.0492 |
| 127 | t_bz_customer_poller_config | NE_ID | 0.0489 |
| 128 | t_gn_business_application_change | business_type | 0.0488 |
| 129 | t_gn_topo_device | device_ip | 0.0488 |
| 130 | sdw_dp_device | dev_id | 0.0485 |
| 131 | t_gn_scanning_probe | dev_id | 0.0485 |
| 132 | t_gn_traffic_abnormality | dev_id | 0.0485 |
| 133 | sdw_dp_port_performance | dev_esn | 0.0484 |
| 134 | sdw_dp_device | dev_ip | 0.0484 |
| 135 | t_gn_business_application_change | user_type | 0.0481 |
| 136 | cc_cmdb_sync_history | resource_success_num | 0.0481 |
| 137 | event_history | ADDRESS | 0.0480 |
| 138 | t_dc_config_circuit_type | TYPE_ID | 0.0480 |
| 139 | t_bz_authority_role | ROLE_TYPE | 0.0478 |
| 140 | snmp_walk_result | root_ne_id | 0.0478 |
| 141 | t_gn_topo_device | device_desc | 0.0478 |
| 142 | t_gn_topo_link | topo_device_id | 0.0476 |
| 143 | sdw_dp_device_performance | dev_id | 0.0472 |
| 144 | sp_netype_driver | DATA_TYPE | 0.0471 |
| 145 | t_gn_vulnerability_weak_password | device_info | 0.0471 |
| 146 | t_dc_config_device_type | device_head_portrait | 0.0471 |
| 147 | t_gn_weaknesses_attack | device_info | 0.0470 |
| 148 | sdw_dp_port_basic | dev_id | 0.0469 |
| 149 | t_gn_botnet | device_info | 0.0467 |
| 150 | t_gn_topo_link | des_device_id | 0.0466 |
| 151 | t_bz_config_customer | CUSTOMER_TYPE | 0.0466 |
| 152 | t_gn_business_application_change | equipment_model | 0.0464 |
| 153 | t_gn_website_host_vulnerabilities | device_info | 0.0464 |
| 154 | t_gn_security_access | device_name | 0.0463 |
| 155 | t_gn_vulnerability_clear_transmission | device_info | 0.0460 |
| 156 | customer_cloud_monitor_region | product_type | 0.0459 |
| 157 | t_bz_service_type_level | TYPE_NAME | 0.0458 |
| 158 | t_gn_business_application_change | link_reqtype | 0.0457 |
| 159 | sdw_dp_tunnel_basic | z_dev_name | 0.0455 |
| 160 | ne_template_access_config | type | 0.0454 |
| 161 | framework_authority | AUTHORITY_TYPE | 0.0453 |
| 162 | syslog_filter_script | is_contains_one_a | 0.0452 |
| 163 | t_bz_incorporate_config | SHARING_TYPE | 0.0450 |
| 164 | t_gn_vulnerability_hole | device_info | 0.0450 |
| 165 | t_gn_account | cost_type | 0.0447 |
| 166 | t_gn_business_application_change | replace_link_ip | 0.0447 |
| 167 | syslog_filter_script | is_contains_two_a | 0.0446 |
| 168 | sdw_dp_tunnel_performance | dev_no | 0.0446 |
| 169 | t_gn_weaknesses_attack | device_id | 0.0445 |
| 170 | event_history | EVENT_TYPE_NAME | 0.0444 |
| 171 | t_gn_traffic_abnormality | device_info | 0.0443 |
| 172 | event_history | ROOT_NE_NAME | 0.0443 |
| 173 | ne_service_item | BUSINESS_ID | 0.0443 |
| 174 | business | BUSINESS_NAME | 0.0443 |
| 175 | t_bz_config_work_policy_new_link | type | 0.0443 |
| 176 | t_gn_business_application_change | access_type | 0.0442 |
| 177 | t_gn_botnet | device_id | 0.0440 |
| 178 | t_dc_config_circuit_type | TYPE_NAME | 0.0440 |
| 179 | customer_cloud_monitor_count_config | time_type | 0.0439 |
| 180 | sdw_dp_tunnel_basic | z_dev_id | 0.0439 |
| 181 | ne_syslog_filter_script | is_contains_one_a | 0.0438 |
| 182 | t_gn_vulnerability_hole | device_id | 0.0437 |
| 183 | business | BUSINESS_ID | 0.0436 |
| 184 | t_bz_service_evaluation | evaluation_type | 0.0436 |
| 185 | ne_service_item | ITEM_TYPE | 0.0435 |
| 186 | t_gn_vulnerability_clear_transmission | device_id | 0.0435 |
| 187 | t_gn_vulnerability_weak_password | device_id | 0.0431 |
| 188 | ne_collect_record | document | 0.0430 |
| 189 | service_item | ITEM_TYPE | 0.0430 |
| 190 | t_gn_traffic_abnormality | device_id | 0.0428 |
| 191 | ont_status | mac | 0.0427 |
| 192 | t_gn_vulnerability_clear_transmission | device_version | 0.0426 |
| 193 | t_gn_weaknesses_attack | data_type | 0.0425 |
| 194 | ne_syslog_filter_script | is_contains_two_a | 0.0424 |
| 195 | event_history | EVENT_TYPE_ID | 0.0424 |
| 196 | t_gn_scanning_probe | device_info | 0.0424 |
| 197 | t_gn_vulnerability_hole | device_version | 0.0424 |
| 198 | t_gn_scanning_probe | device_id | 0.0423 |
| 199 | sdw_dp_tunnel_basic | a_dev_id | 0.0423 |
| 200 | ont_status | ont_id | 0.0422 |

---

## 三、列级别累加分 Top 10 表

| 排名 | 表名 | 累加分 | 命中 |
|-----|------|-------|-----|
| 1 | t_bz_config_ci_ne_root | 1.2052 | ✅ |
| 2 | event_sdn | 0.8150 |  |
| 3 | t_gn_business_application_change | 0.7916 |  |
| 4 | ne_syslog_filter_script | 0.7863 |  |
| 5 | syslog_filter_script | 0.7260 |  |
| 6 | t_bz_incident_event_record | 0.5777 |  |
| 7 | event_yjk_history | 0.4232 |  |
| 8 | t_gn_weaknesses_attack | 0.3760 |  |
| 9 | t_gn_traffic_abnormality | 0.3661 |  |
| 10 | t_gn_vulnerability_clear_transmission | 0.3625 |  |

**列级别召回**: 1/2

---

## 四、融合结果

- 表级别贡献: 10 个表
- 列级别贡献: 10 个表
- 融合并集: 19 个表
- **融合召回**: 2/2
