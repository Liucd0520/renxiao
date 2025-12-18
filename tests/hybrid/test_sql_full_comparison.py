#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整 SQL 对比测试（含基线对比）

对比：
1. 原始3表SQL（cc_result.csv 中的，直接给 3 张正确表）
2. 正确答案（人工手写）
3. 完整格式（10+表）→ LLM 生成
4. 精简格式（10+表）→ LLM 生成
5. 最精简格式（10+表）→ LLM 生成

重点测试 2 和 7（原来错误的）
"""

import os
import sys
import json
from pathlib import Path
from openai import OpenAI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from config import QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL

TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
COLUMN_SCHEMA_DIR = "./spider2_dev/schemas/netcaredb_ai"
OUTPUT_FILE = "./docs/milestone_20241217_table_column_fusion/sql_comparison_full_report.md"

# 全部 7 个测试用例
TEST_CASES = [
    {
        "id": 1,
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "fusion_tables": ["event_history", "t_bz_config_ci_ne_root", "t_dc_release_type", "t_dc_incident_accident_type", 
                         "t_bz_config_ci_rfc", "t_gn_weaknesses_attack", "report_new_dev", "t_dc_service_source_type",
                         "t_gn_vulnerability_weak_password", "t_gn_botnet"],  # 融合后的 10 表
        "original_correct": True,
        "original_sql": """SELECT 
    `event_type_name`, 
    COUNT(`event_id`) AS `alarm_count`
FROM event_history
JOIN t_bz_config_ci_ne_root ON event_history.ne_id = t_bz_config_ci_ne_root.ne_id
WHERE t_bz_config_ci_ne_root.host_name LIKE '%ciscoA%' 
    AND event_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    AND event_time < CURDATE()
GROUP BY `event_type_name`
ORDER BY `alarm_count` DESC
LIMIT 10;""",
        "correct_sql": None  # 原来就是正确的
    },
    {
        "id": 2,
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "fusion_tables": ["t_bz_config_ci_ne_root", "t_bz_config_customer", "sdw_dp_device", "t_gn_all_net_device",
                         "atomic_cutover_order", "topology_point_port", "t_gn_topo_device", "sdwan_device",
                         "sdw_dp_port_performance", "sdw_dp_device_performance", "customer", "t_gn_topo_link"],  # 融合后的表（没有 event_history）
        "original_correct": False,
        "original_sql": """SELECT 
    `t_bz_config_ci_ne_root`.`NE_ID`,
    `t_bz_config_ci_ne_root`.`HOST_NAME`,
    `t_bz_config_customer`.`CUSTOMER_NAME`
FROM `t_bz_config_ci_ne_root`
JOIN `t_bz_config_customer` ON `t_bz_config_ci_ne_root`.`CUSTOMER_ID` = `t_bz_config_customer`.`CUSTOMER_ID`
JOIN `event_history` ON `t_bz_config_ci_ne_root`.`NE_ID` = `event_history`.`NE_ID`
WHERE `event_history`.`EVENT_TYPE_NAME` LIKE '%down%' 
    AND `event_history`.`EVENT_TIME` <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY `t_bz_config_ci_ne_root`.`NE_ID`, `t_bz_config_customer`.`CUSTOMER_NAME`
HAVING COUNT(DISTINCT `event_history`.`EVENT_ID`) > 0
LIMIT 10;""",
        "correct_sql": """select a.* from (
SELECT 
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
) a where `a`.`EVENT_TIME` <= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) and `a`.`EVENT_STATUS_NAME` = 'alarm'
LIMIT 10;"""
    },
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "fusion_tables": ["t_bz_config_customer"],
        "original_correct": True,
        "original_sql": """SELECT COUNT(`CUSTOMER_ID`) AS `customer_count`
FROM t_bz_config_customer
WHERE `IS_ACTIVE` = 1
LIMIT 10;""",
        "correct_sql": None
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "fusion_tables": ["t_bz_config_ci_ne_root"],
        "original_correct": True,
        "original_sql": """SELECT COUNT(`CI_ID`) AS `device_count`
FROM t_bz_config_ci_ne_root
WHERE `IS_DELETED` = 0
LIMIT 10;""",
        "correct_sql": None
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "fusion_tables": ["t_bz_config_ci_ne_root"],
        "original_correct": True,
        "original_sql": """SELECT COUNT(`CI_ID`) AS `new_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `ONLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
AND YEAR(`ONLINE_TIME`) = 2025
LIMIT 10;""",
        "correct_sql": None
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "fusion_tables": ["t_bz_config_ci_ne_root"],
        "original_correct": True,
        "original_sql": """SELECT COUNT(`CI_ID`) AS `offline_device_count`
FROM `t_bz_config_ci_ne_root`
WHERE `OFFLINE_TIME` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND `OFFLINE_TIME` < CURDATE()
LIMIT 10;""",
        "correct_sql": None
    },
    {
        "id": 7,
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "fusion_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer", "t_dc_release_type",
                         "t_dc_incident_accident_type", "t_bz_config_ci_rfc", "t_gn_weaknesses_attack",
                         "report_new_dev", "t_dc_service_source_type", "t_gn_vulnerability_weak_password"],
        "original_correct": False,
        "original_sql": """SELECT 
    `event_history`.`EVENT_TYPE_NAME`, 
    `event_history`.`EVENT_TIME`, 
    `event_history`.`ACK_TIME`
FROM `event_history`
JOIN `t_bz_config_ci_ne_root` ON `event_history`.`NE_ID` = `t_bz_config_ci_ne_root`.`NE_ID`
WHERE `event_history`.`EVENT_TIME` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    AND `event_history`.`IS_ACK` = 1
LIMIT 10;""",
        "correct_sql": """SELECT
 `t_bz_config_customer`.`CUSTOMER_NAME`,
 `t_bz_config_ci_ne_root`.`HOST_NAME`,
 `event_history`.`EVENT_NAME`,
 `event_history`.`EVENT_TIME`
FROM `event_history`
JOIN `t_bz_config_ci_ne_root` ON `event_history`.`NE_ID` = `t_bz_config_ci_ne_root`.`NE_ID`
JOIN `t_bz_config_customer` ON `event_history`.`CUSTOMER_ID` = `t_bz_config_customer`.ID
WHERE `event_history`.`EVENT_TIME` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
AND `event_history`.`EVENT_STATUS_NAME` = 'alarm'
AND `t_bz_config_customer`.`CUSTOMER_NAME` = 'xxx'
LIMIT 10;"""
    },
]

SQL_PROMPT = """你是一个资深的 MySQL 专家。请根据用户问题和数据库 Schema，生成正确的 SQL 查询。

## 用户问题
{question}

## 数据库 Schema
{schema}

## 任务
请仔细分析用户问题和数据库 Schema：
1. 深度思考：这个问题需要查询哪些表？表之间如何关联？
2. 反复推敲：选择最准确的字段，确保条件逻辑正确
3. 验证检查：SQL 语法是否正确？能否得到用户想要的结果？

请先进行深度思考，然后输出最终的 SQL 查询。

## SQL 查询
"""


def load_table_data(table_name):
    table_file = Path(TABLE_SCHEMA_DIR) / f"{table_name}.json"
    if table_file.exists():
        with open(table_file, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
    else:
        table_data = {"table_name": table_name}
    
    columns = []
    for col_file in Path(COLUMN_SCHEMA_DIR).glob("*.json"):
        with open(col_file, 'r', encoding='utf-8') as f:
            col_data = json.load(f)
        meta = col_data.get("meta_data", {})
        if meta.get("table_name", "").lower() == table_name.lower():
            columns.append({
                "name": col_data.get("column_name", ""),
                "type": col_data.get("column_types", ""),
                "description": col_data.get("column_descriptions", ""),
            })
    return table_data, columns


def format_full(tables):
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        lines = [f"表名: {table_name}"]
        if table_data.get("llm_description"):
            lines.append(f"描述: {table_data['llm_description']}")
        lines.append("列:")
        for col in columns:
            col_line = f"  - {col['name']} ({col['type']})"
            if col['description']:
                col_line += f": {col['description']}"
            lines.append(col_line)
        result.append("\n".join(lines))
    return "\n\n".join(result)


def format_minimal(tables):
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        desc = table_data.get("llm_description", "")[:80] + "..." if table_data.get("llm_description") else ""
        col_names = [c['name'] for c in columns]
        result.append(f"{table_name}: {desc}\n  列: {', '.join(col_names)}")
    return "\n\n".join(result)


def format_compact(tables):
    """精简格式：列名+类型，无描述"""
    result = []
    for table_name in tables:
        table_data, columns = load_table_data(table_name)
        lines = [f"表: {table_name}"]
        if table_data.get("llm_description"):
            lines.append(f"说明: {table_data['llm_description'][:100]}...")
        col_strs = [f"{c['name']}({c['type'][:20]})" for c in columns]
        lines.append(f"列: {', '.join(col_strs)}")
        result.append("\n".join(lines))
    return "\n\n".join(result)


def call_llm(prompt):
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.1,
            timeout=120.0
        )
        text = response.choices[0].message.content.strip()
        # 提取 SQL
        if "</think>" in text:
            text = text.split("</think>")[-1].strip()
        if "```sql" in text:
            start = text.find("```sql") + 6
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text
    except Exception as e:
        return f"ERROR: {e}"


def run_full_comparison():
    print("=" * 80)
    print("完整 SQL 对比测试（含基线）")
    print("=" * 80)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# SQL 生成完整对比报告\n\n")
        f.write("**日期**: 2025-12-17\n\n")
        f.write("## 测试说明\n\n")
        f.write("- **原始3表SQL**: 直接给 LLM 3 张正确的表，LLM 生成的 SQL（cc_result.csv）\n")
        f.write("- **正确答案**: 人工手写的正确 SQL\n")
        f.write("- **完整格式**: 给 LLM 融合后的 10+ 张表（完整描述）\n")
        f.write("- **最精简格式**: 给 LLM 融合后的 10+ 张表（只有列名）\n\n")
        f.write("---\n\n")
        
        for case in TEST_CASES:
            print(f"\n测试 {case['id']}: {case['question'][:30]}...")
            
            f.write(f"## 测试 {case['id']}: {case['question']}\n\n")
            f.write(f"**融合后表数**: {len(case['fusion_tables'])} 张\n\n")
            
            # 原始 3 表 SQL
            status = "✅ 正确" if case['original_correct'] else "❌ 错误"
            f.write(f"### 1. 原始3表SQL（{status}）\n\n```sql\n{case['original_sql']}\n```\n\n")
            
            # 正确答案
            if case['correct_sql']:
                f.write(f"### 2. 正确答案（人工手写）\n\n```sql\n{case['correct_sql']}\n```\n\n")
            else:
                f.write(f"### 2. 正确答案\n\n*原始 SQL 已正确*\n\n")
            
            # 完整格式
            print(f"  生成完整格式...")
            schema_full = format_full(case['fusion_tables'])
            prompt_full = SQL_PROMPT.format(question=case['question'], schema=schema_full)
            sql_full = call_llm(prompt_full)
            f.write(f"### 3. 完整格式（{len(schema_full)} 字符，{len(case['fusion_tables'])} 表）\n\n```sql\n{sql_full}\n```\n\n")
            
            # 精简格式
            print(f"  生成精简格式...")
            schema_compact = format_compact(case['fusion_tables'])
            prompt_compact = SQL_PROMPT.format(question=case['question'], schema=schema_compact)
            sql_compact = call_llm(prompt_compact)
            f.write(f"### 4. 精简格式（{len(schema_compact)} 字符，{len(case['fusion_tables'])} 表）\n\n```sql\n{sql_compact}\n```\n\n")
            
            # 最精简格式
            print(f"  生成最精简格式...")
            schema_min = format_minimal(case['fusion_tables'])
            prompt_min = SQL_PROMPT.format(question=case['question'], schema=schema_min)
            sql_min = call_llm(prompt_min)
            f.write(f"### 5. 最精简格式（{len(schema_min)} 字符，{len(case['fusion_tables'])} 表）\n\n```sql\n{sql_min}\n```\n\n")
            
            f.write("---\n\n")
    
    print(f"\n报告已保存: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_full_comparison()
