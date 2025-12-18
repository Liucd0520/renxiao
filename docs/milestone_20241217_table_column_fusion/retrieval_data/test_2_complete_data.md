# 测试 2 完整检索数据

**问题**: 列出平台上设备device state down状态超过3个月的设备清单及客户名称

**期望表**: ['t_bz_config_ci_ne_root', 't_bz_config_customer', 'event_history']

---

## 一、表级别 Sparse Top 10

| 排名 | 表名 | 分数 | 命中 |
|-----|------|------|-----|
| 1 | t_bz_config_ci_ne_root | 0.1742 | ✅ |
| 2 | sdw_dp_device | 0.1720 |  |
| 3 | t_gn_all_net_device | 0.1658 |  |
| 4 | atomic_cutover_order | 0.1526 |  |
| 5 | topology_point_port | 0.1488 |  |
| 6 | t_gn_topo_device | 0.1478 |  |
| 7 | sdwan_device | 0.1475 |  |
| 8 | sdw_dp_port_performance | 0.1338 |  |
| 9 | sdw_dp_device_performance | 0.1298 |  |
| 10 | customer | 0.1259 |  |

**表级别召回**: 1/3

---

## 二、列级别 Sparse Top 200

| 排名 | 表名 | 列名 | 分数 |
|-----|------|------|-----|
| 1 | t_gn_topo_device | device_status | 0.1946 |
| 2 | sdw_dp_device_performance | device_status | 0.1455 |
| 3 | sdw_dp_port_performance | port_state | 0.1404 |
| 4 | topology_point_port | state | 0.1338 |
| 5 | sdw_dp_device | dev_name | 0.1327 |
| 6 | t_gn_topo_link | flow_device_id | 0.1256 |
| 7 | sdw_dp_device | customer_id | 0.1245 |
| 8 | sdw_dp_device | dev_id | 0.1219 |
| 9 | t_gn_topo_link | src_device_id | 0.1157 |
| 10 | t_gn_topo_link | des_device_id | 0.1150 |
| 11 | t_gn_topo_link | topo_device_id | 0.1111 |
| 12 | t_gn_topo_device | device_id | 0.1105 |
| 13 | t_gn_topo_device | device_desc | 0.1103 |
| 14 | t_gn_weaknesses_attack | device_info | 0.1097 |
| 15 | t_gn_website_host_vulnerabilities | device_info | 0.1096 |
| 16 | sdw_dp_device | dev_ip | 0.1094 |
| 17 | sdw_dp_device | dev_type | 0.1076 |
| 18 | sdw_dp_device | dev_model | 0.1063 |
| 19 | t_gn_topo_device | device_ip | 0.1062 |
| 20 | t_gn_vulnerability_weak_password | device_info | 0.1059 |
| 21 | t_gn_vulnerability_clear_transmission | device_info | 0.1058 |
| 22 | sdw_dp_device_performance | dev_id | 0.1052 |
| 23 | t_gn_vulnerability_hole | device_info | 0.1036 |
| 24 | t_gn_botnet | device_info | 0.1033 |
| 25 | t_gn_traffic_abnormality | device_info | 0.0990 |
| 26 | t_dc_config_device_type | device_head_portrait | 0.0989 |
| 27 | t_gn_scanning_probe | device_info | 0.0958 |
| 28 | customer | CUSTOMER_ABB | 0.0938 |
| 29 | t_bz_sys_operate_audit | CUSTOMER_NAME | 0.0928 |
| 30 | t_bz_config_customer | CUSTOMER_ABB | 0.0897 |
| 31 | ont_status | status | 0.0889 |
| 32 | t_gn_topo_link | src_device_name | 0.0865 |
| 33 | sdwan_device | siteId | 0.0853 |
| 34 | t_gn_topo_device | id | 0.0851 |
| 35 | customer | CUSTOMER_NAME | 0.0836 |
| 36 | sdw_dp_device_performance | id | 0.0820 |
| 37 | t_gn_topo_link | flow_device_name | 0.0813 |
| 38 | event | EVENT_VALUE | 0.0792 |
| 39 | event_ping | EVENT_VALUE | 0.0781 |
| 40 | t_bz_config_customer | CUSTOMER_DESC | 0.0778 |
| 41 | event_yjk_history | customer_name | 0.0775 |
| 42 | event_history | CUSTOMER_NAME | 0.0770 |
| 43 | sdwan_device | deviceId | 0.0757 |
| 44 | sdwan_device | data | 0.0754 |
| 45 | t_gn_topo_link | des_device_name | 0.0752 |
| 46 | sdwan_device | tenantId | 0.0746 |
| 47 | t_gn_topo_device | device_name | 0.0739 |
| 48 | t_gn_topo_device | device_alias | 0.0735 |
| 49 | t_gn_topo_device | position_x | 0.0721 |
| 50 | t_gn_traffic_abnormality | dev_id | 0.0718 |
| 51 | t_gn_topo_device | position_y | 0.0712 |
| 52 | t_gn_business_application_change | replace_link_name | 0.0710 |
| 53 | customer_collector_v2 | customer_name | 0.0703 |
| 54 | ne_template_access_config | customer_id | 0.0698 |
| 55 | customer_collector_v2 | customer_id | 0.0684 |
| 56 | t_bz_config_work_policy | IN_WORKING_POLICY | 0.0684 |
| 57 | t_bz_incorporate_config | SHARING_TYPE | 0.0681 |
| 58 | sdw_dp_port_basic | dev_name | 0.0681 |
| 59 | t_bz_authority_users_group | CUSTOMER_ID | 0.0680 |
| 60 | t_bz_incident_event_record | EVENT_VALUE | 0.0680 |
| 61 | cc_cmdb_sync_history | tenant_num | 0.0679 |
| 62 | t_gn_business_application_change | equipment_name | 0.0677 |
| 63 | customer_global_config | CUSTOMER_ID | 0.0676 |
| 64 | t_bz_config_group | CUSTOMER_ID | 0.0675 |
| 65 | t_bz_config_customer | SP_PARENT_ID | 0.0674 |
| 66 | t_gn_all_net_device | region_name | 0.0673 |
| 67 | t_gn_topo_device | customer_id | 0.0669 |
| 68 | t_bz_config_ci_ne_root | NE_DESC | 0.0668 |
| 69 | ne_token | CUSTOMER_ID | 0.0667 |
| 70 | t_bz_authority_users | CUSTOMER_ID | 0.0666 |
| 71 | t_bz_customer_poller_config | NE_ID | 0.0666 |
| 72 | t_gn_vulnerability_hole | device_version | 0.0664 |
| 73 | ne_service_item | CUSTOMER_ID | 0.0663 |
| 74 | t_gn_scanning_probe | dev_id | 0.0663 |
| 75 | ne_service_collect | customer_id | 0.0662 |
| 76 | t_gn_topo_device | des_topo_id | 0.0661 |
| 77 | t_bz_config_customer | CUSTOMER_LOGO | 0.0660 |
| 78 | t_gn_vulnerability_clear_transmission | device_version | 0.0658 |
| 79 | t_gn_topo_device | topo_id | 0.0657 |
| 80 | t_gn_all_net_device | id | 0.0655 |
| 81 | event_history | CUSTOMER_ID | 0.0654 |
| 82 | customer | CUSTOMER_ID | 0.0653 |
| 83 | ne_template_collect_config | customer_id | 0.0652 |
| 84 | sdw_dp_tunnel_basic | a_dev_name | 0.0651 |
| 85 | ne_service_package | CUSTOMER_ID | 0.0649 |
| 86 | t_bz_config_customer | CUSTOMER_NO | 0.0648 |
| 87 | event_history | ROOT_NE_NAME | 0.0647 |
| 88 | ne_template_collect_config | name | 0.0647 |
| 89 | t_bz_config_customer | WHETHER_COUNTRY | 0.0646 |
| 90 | customer | CUSTOMER_TYPE | 0.0645 |
| 91 | t_bz_config_work_policy | CUSTOMER_ID | 0.0644 |
| 92 | t_bz_config_customer | CUSTOMER_FAX | 0.0643 |
| 93 | t_bz_config_work_policy_new | customer_id | 0.0642 |
| 94 | sdw_dp_device | tenant_id | 0.0641 |
| 95 | ne_collect_record | customer_id | 0.0640 |
| 96 | trap_snmp | down_counts | 0.0638 |
| 97 | t_gn_business_application_change | equipment_unit | 0.0637 |
| 98 | t_gn_weaknesses_attack | device_version | 0.0637 |
| 99 | event_yjk_history | customer_no | 0.0637 |
| 100 | ne_protocol_inst | CUSTOMER_ID | 0.0637 |
| 101 | t_bz_customer_poller_config | CUSTOMER_ID | 0.0635 |
| 102 | customer | CRM_NO | 0.0634 |
| 103 | ne_collect_history | customer_id | 0.0634 |
| 104 | t_bz_config_ci_ne_root | CUSTOMER_ID | 0.0634 |
| 105 | t_bz_config_region | CUSTOMER_ID | 0.0633 |
| 106 | protocol_inst | CUSTOMER_ID | 0.0632 |
| 107 | customer_cloud_monitor_key | customer_id | 0.0631 |
| 108 | syslog_server | customer_id | 0.0631 |
| 109 | t_bz_config_ci_circuit | CUSTOMER_ID | 0.0631 |
| 110 | t_rl_user_customer | CUSTOMER_ID | 0.0631 |
| 111 | cc_cmdb_sync_history | resource_num | 0.0630 |
| 112 | t_bz_config_customer | CHANNEL_ID | 0.0629 |
| 113 | t_bz_sys_note | CUSTOMER_ID | 0.0629 |
| 114 | t_gn_all_net_device | device_num | 0.0629 |
| 115 | t_gn_business_application_change | serve_clients_id | 0.0629 |
| 116 | t_gn_security_access | device_name | 0.0629 |
| 117 | t_gn_traffic_abnormality | device_version | 0.0629 |
| 118 | t_bz_config_customer | CHINESE_OR_ENGLISH | 0.0629 |
| 119 | t_bz_config_work_policy_new | active | 0.0627 |
| 120 | t_gn_business_application_change | equipment_num | 0.0626 |
| 121 | t_bz_config_location | customer_id | 0.0625 |
| 122 | t_gn_business_application_change | customer_phone | 0.0625 |
| 123 | t_gn_all_net_device | customer_id | 0.0624 |
| 124 | t_gn_weaknesses_attack | device_id | 0.0622 |
| 125 | ont_status | description | 0.0621 |
| 126 | t_gn_vulnerability_weak_password | device_version | 0.0620 |
| 127 | origin_availability | CUSTOMER_ID | 0.0620 |
| 128 | t_gn_topo_link | des_device_type | 0.0620 |
| 129 | t_bz_config_customer | CUSTOMER_ADD | 0.0619 |
| 130 | t_gn_botnet | device_version | 0.0617 |
| 131 | t_bz_config_customer | CUSTOMER_PHONE | 0.0616 |
| 132 | t_bz_config_policy | customer_id | 0.0615 |
| 133 | temp | CUSTOMER_ID | 0.0615 |
| 134 | t_bz_config_customer | LEVEL | 0.0614 |
| 135 | t_gn_topo_link | src_device_type | 0.0614 |
| 136 | sdw_dp_device_performance | gather_time | 0.0613 |
| 137 | t_bz_config_customer | CUSTOMER_TYPE | 0.0613 |
| 138 | t_gn_botnet | device_id | 0.0612 |
| 139 | t_bz_yun_circuit | CUSTOMER_ID | 0.0611 |
| 140 | syslog_filter_script | customer_id | 0.0610 |
| 141 | t_dc_config_device_type | TYPE_NAME | 0.0610 |
| 142 | t_bz_config_ci_ne_root_region_location_relation | customer_id | 0.0610 |
| 143 | t_gn_vulnerability_hole | device_id | 0.0609 |
| 144 | t_gn_topo_link | des_device_ip | 0.0609 |
| 145 | event_yjk_history | device | 0.0607 |
| 146 | cc_cmdb_sync_service_catalog | resource_id | 0.0606 |
| 147 | t_bz_config_ci_ne_root | HOST_NAME | 0.0605 |
| 148 | t_gn_topo_link | src_device_ip | 0.0605 |
| 149 | t_bz_config_customer | CUSTOMER_ID | 0.0605 |
| 150 | t_gn_topo_device | device_location_name | 0.0602 |
| 151 | t_bz_config_contact | customer_id | 0.0602 |
| 152 | t_gn_website_host_vulnerabilities | device_version | 0.0602 |
| 153 | t_bz_ip_segment_manage | CUSTOMER_ID | 0.0601 |
| 154 | sdw_dp_device | platform | 0.0601 |
| 155 | t_gn_traffic_abnormality | device_id | 0.0600 |
| 156 | t_gn_scanning_probe | device_version | 0.0599 |
| 157 | t_bz_config_ci_ne_root | SIGNING_ADDR | 0.0598 |
| 158 | t_gn_vulnerability_clear_transmission | device_id | 0.0598 |
| 159 | t_bz_sys_operate_audit | CUSTOMER_ID | 0.0597 |
| 160 | t_gn_notice | content | 0.0597 |
| 161 | trap_ne | ne_id | 0.0597 |
| 162 | ont_status | customer_id | 0.0595 |
| 163 | t_gn_vulnerability_weak_password | device_id | 0.0595 |
| 164 | t_gn_website_host_vulnerabilities | device_id | 0.0593 |
| 165 | month_availability | CUSTOMER_ID | 0.0593 |
| 166 | t_bz_clouds_auth | customer_id | 0.0592 |
| 167 | sdw_dp_tunnel_basic | z_dev_name | 0.0590 |
| 168 | ne_syslog_filter_script | customer_id | 0.0589 |
| 169 | t_bz_config_ci_rfc | CI_ID | 0.0587 |
| 170 | t_gn_scanning_probe | device_id | 0.0586 |
| 171 | t_gn_topo_link | des_device_port | 0.0585 |
| 172 | t_bz_config_customer | IS_TRIAL | 0.0584 |
| 173 | sdw_dp_device_performance | remark | 0.0581 |
| 174 | t_bz_ip_subnet_manage | CUSTOMER_ID | 0.0580 |
| 175 | t_bz_config_work_policy_new_link | ne_id | 0.0580 |
| 176 | day_availability | CUSTOMER_ID | 0.0579 |
| 177 | t_gn_business_application_change | customer_address | 0.0577 |
| 178 | trap_ne_policy | ne_id | 0.0577 |
| 179 | t_bz_authority_users | CUSTOMER_NO | 0.0577 |
| 180 | maintenance_info | ne_id | 0.0575 |
| 181 | t_bz_ip_region_manage | CUSTOMER_ID | 0.0575 |
| 182 | t_bz_config_customer | INDUSTRY | 0.0574 |
| 183 | t_bz_service_evaluation | customer_id | 0.0573 |
| 184 | ne_template_access_config | name | 0.0573 |
| 185 | maintenance_info | ne_time | 0.0573 |
| 186 | syslog_server | ne_id | 0.0572 |
| 187 | t_dc_config_device_type | VERSION | 0.0571 |
| 188 | t_dc_config_device_type | TYPE_ID | 0.0570 |
| 189 | t_gn_business_application_change | equipment_arg | 0.0570 |
| 190 | t_gn_business_application_change | equipment_ip | 0.0569 |
| 191 | t_bz_config_ci_ne_root | CI_ID | 0.0567 |
| 192 | t_dc_config_device_type | CREATE_USER_ID | 0.0566 |
| 193 | cc_cmdb_sync_history | tenant_success_num | 0.0565 |
| 194 | t_gn_topo_link | src_device_port | 0.0565 |
| 195 | t_dc_config_device_type | UPDATE_TIME | 0.0563 |
| 196 | t_gn_business_application_change | equipment_type | 0.0563 |
| 197 | ont_status | root_ne_id | 0.0563 |
| 198 | t_gn_botnet | classify_id | 0.0559 |
| 199 | collector_v2 | switch_type | 0.0558 |
| 200 | t_gn_business_application_change | equipment_brand | 0.0558 |

---

## 三、列级别累加分 Top 10 表

| 排名 | 表名 | 累加分 | 命中 |
|-----|------|-------|-----|
| 1 | t_gn_topo_device | 1.1563 |  |
| 2 | t_gn_topo_link | 1.0702 |  |
| 3 | t_bz_config_customer | 1.0427 | ✅ |
| 4 | sdw_dp_device | 0.8267 |  |
| 5 | t_gn_business_application_change | 0.6742 |  |
| 6 | sdw_dp_device_performance | 0.4521 |  |
| 7 | t_dc_config_device_type | 0.3868 |  |
| 8 | customer | 0.3705 |  |
| 9 | sdwan_device | 0.3110 |  |
| 10 | t_bz_config_ci_ne_root | 0.3073 | ✅ |

**列级别召回**: 2/3

---

## 四、融合结果

- 表级别贡献: 10 个表
- 列级别贡献: 10 个表
- 融合并集: 14 个表
- **融合召回**: 2/3
- **缺失**: {'event_history'}
