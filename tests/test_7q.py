#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7题完整测试

测试流程：
1. 加载 Pipeline
2. 对7个问题进行检索+SQL生成
3. 对比参考答案
4. 生成测试报告

参考答案来源: cc_result.csv
"""

import os
import sys
import json
from datetime import datetime

# FusionSQL 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fusionsql.pipeline import TextToSQL

# 7道测试题（参考答案从 cc_result.csv 提取）
TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root"],
        "reference_sql": """SELECT 
    `event_type_name`, 
    COUNT(`event_id`) AS `alarm_count`
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.ne_id = t_bz_config_ci_ne_root.ne_id
WHERE t_bz_config_ci_ne_root.host_name LIKE '%ciscoA%' 
    AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    AND event_time < CURDATE()
GROUP BY `event_type_name`
ORDER BY `alarm_count` DESC
LIMIT 10;"""
    },
    {
        "id": 2,
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
        "reference_sql": """SELECT 
    `t_bz_config_ci_ne_root`.`NE_ID`,
    `t_bz_config_ci_ne_root`.`HOST_NAME`,
    `t_bz_config_customer`.`CUSTOMER_NAME`
FROM `t_bz_config_ci_ne_root`
JOIN `t_bz_config_customer` ON `t_bz_config_ci_ne_root`.`CUSTOMER_ID` = `t_bz_config_customer`.`CUSTOMER_ID`
JOIN `event_history` ON `t_bz_config_ci_ne_root`.`NE_ID` = `event_history`.`NE_ID`
WHERE `event_history`.`EVENT_NAME` LIKE 'Device state%' 
    AND `event_history`.`EVENT_TIME` <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY `t_bz_config_ci_ne_root`.`NE_ID`, `t_bz_config_customer`.`CUSTOMER_NAME`
HAVING COUNT(DISTINCT `event_history`.`EVENT_ID`) > 0
LIMIT 10;"""
    },
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "expected_tables": ["t_bz_config_customer"],
        "reference_sql": """SELECT COUNT(`CUSTOMER_ID`) AS `customer_count`
FROM t_bz_config_customer
WHERE `IS_ACTIVE` = 1
LIMIT 10;"""
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "reference_sql": """SELECT COUNT(`CI_ID`) AS `device_count`
FROM t_bz_config_ci_ne_root
WHERE `IS_DELETED` = 0
LIMIT 10;"""
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "reference_sql": """SELECT COUNT(`CI_ID`) AS `new_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `ONLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
LIMIT 10;"""
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "reference_sql": """SELECT COUNT(`CI_ID`) AS `offline_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `OFFLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND `OFFLINE_TIME` < CURDATE()
LIMIT 10;"""
    },
    {
        "id": 7,
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
        "reference_sql": """SELECT
  `t_bz_config_customer`.`CUSTOMER_NAME`,
  `t_bz_config_ci_ne_root`.`HOST_NAME`,
  `event_history`.`EVENT_NAME`,
  `event_history`.`EVENT_TIME`
FROM `event_history`
JOIN `t_bz_config_ci_ne_root` ON `event_history`.`NE_ID` = `t_bz_config_ci_ne_root`.`NE_ID`
JOIN `t_bz_config_customer` ON `event_history`.`CUSTOMER_ID` = `t_bz_config_customer`.`CUSTOMER_ID`
WHERE `event_history`.`EVENT_TIME` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
  AND `event_history`.`EVENT_STATUS_NAME` = 'alarm'
LIMIT 10;"""
    },
]


def check_table_usage(sql, expected_tables):
    """检查SQL是否使用了所有期望的表"""
    sql_upper = sql.upper()
    missing = []
    for table in expected_tables:
        if table.upper() not in sql_upper:
            missing.append(table)
    return len(missing) == 0, missing


def run_test():
    """运行完整测试"""
    print("=" * 60)
    print("7题完整测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 初始化 Pipeline
    print("\n初始化 Pipeline...")
    pipeline = TextToSQL()
    
    results = []
    correct_count = 0
    
    print("\n" + "-" * 60)
    print("开始测试")
    print("-" * 60)
    
    for q in TEST_QUESTIONS:
        print(f"\n[{q['id']}] {q['question'][:40]}...")
        
        # 运行 Pipeline
        result = pipeline.run_with_details(q['question'])
        
        # 检查表使用
        tables_ok, missing = check_table_usage(result['sql'], q['expected_tables'])
        
        # 判断结果
        if tables_ok:
            status = "✅"
            correct_count += 1
        else:
            status = "❌"
        
        print(f"    {status} 期望表: {q['expected_tables']}")
        print(f"    检索到: {result['retrieved_tables'][:5]}")
        if missing:
            print(f"    缺失: {missing}")
        
        results.append({
            "id": q['id'],
            "question": q['question'],
            "expected_tables": q['expected_tables'],
            "retrieved_tables": result['retrieved_tables'],
            "generated_sql": result['sql'],
            "reference_sql": q['reference_sql'],
            "tables_correct": tables_ok,
            "missing_tables": missing,
        })
    
    # 汇总
    print("\n" + "=" * 60)
    print(f"测试结果: {correct_count}/7 ({correct_count/7*100:.1f}%)")
    print("=" * 60)
    
    # 保存结果
    output = {
        "test_time": datetime.now().isoformat(),
        "model": "qwen3_30b_a3b_2507",
        "summary": {
            "total": 7,
            "correct": correct_count,
            "accuracy": f"{correct_count/7*100:.1f}%"
        },
        "results": results
    }
    
    output_file = os.path.join(os.path.dirname(__file__), "7q_full_test_result.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存: {output_file}")
    
    return correct_count, results


if __name__ == "__main__":
    run_test()
