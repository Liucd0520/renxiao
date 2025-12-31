#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试问题 - 限定使用 3 张表

目标表：
- t_bz_config_ci_ne_root (设备主表)
- t_bz_config_customer (客户表)
- event_history (告警历史表)

问题分布：
- 简单 100 个（单表查询）
- 中等 100 个（2 表关联）
- 困难 100 个（3 表关联）
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from openai import OpenAI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# DeepSeek 配置
DEEPSEEK_API_KEY = "sk-6670dc8295234c4192dbd5e579b4a0ac"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 输出路径
OUTPUT_DIR = "./docs/milestone_20241224"
OUTPUT_JSON = f"{OUTPUT_DIR}/test_questions_3tables_300.json"
OUTPUT_CSV = f"{OUTPUT_DIR}/test_questions_3tables_300.csv"

# 目标三张表
TARGET_TABLES = [
    "t_bz_config_ci_ne_root",  # 设备主表
    "t_bz_config_customer",     # 客户表
    "event_history"             # 告警历史表
]

# 从 MySQL 获取三张表的 Schema
TABLE_SCHEMAS = {
    "t_bz_config_ci_ne_root": """
表名: t_bz_config_ci_ne_root (设备主表)
描述: 存储平台上所有设备的基础信息
主要列:
- CI_ID: 设备ID（主键）
- NE_ID: 网元ID
- CUSTOMER_ID: 客户ID（外键，关联 t_bz_config_customer）
- HOST_NAME: 设备名称/主机名
- NE_IP: 设备IP地址
- NE_MODEL: 设备型号
- IS_ACTIVE: 是否激活（1=是，0=否）
- IS_ONLINE: 是否在线（1=在线，0=离线）
- NE_TYPE_ID: 设备类型ID
- REGION_ID: 区域ID
- LOCATION_ID: 位置ID
- CREATE_TIME: 创建时间
- UPDATE_TIME: 更新时间
""",
    "t_bz_config_customer": """
表名: t_bz_config_customer (客户表)
描述: 存储所有客户的基本信息
主要列:
- CUSTOMER_ID: 客户ID（主键）
- CUSTOMER_NAME: 客户名称
- CUSTOMER_DESC: 客户描述
- CUSTOMER_NO: 客户编号
- CUSTOMER_ABB: 客户简称
- CUSTOMER_PHONE: 联系电话
- CUSTOMER_EMAIL: 联系邮箱
- IS_ACTIVE: 是否激活
- CREATE_TIME: 创建时间
""",
    "event_history": """
表名: event_history (告警历史表)
描述: 存储所有设备的历史告警记录
主要列:
- EVENT_ID: 告警ID（主键）
- NE_ID: 关联的设备ID（外键，关联 t_bz_config_ci_ne_root.NE_ID）
- EVENT_TYPE_ID: 告警类型ID
- EVENT_TYPE_NAME: 告警类型名称（如 Ping event, Trap event, Threshold event）
- EVENT_NAME: 告警名称
- EVENT_STATUS: 告警状态（1=活动，2=已恢复，3=已确认）
- EVENT_STATUS_NAME: 告警状态名称
- SEVERITY: 告警级别（1=严重，2=主要，3=次要，4=警告）
- EVENT_TIME: 告警发生时间
- RECOVER_TIME: 告警恢复时间
- EVENT_DESC: 告警描述
- CUSTOMER_ID: 客户ID（外键）
"""
}

# 真实数据库值（用于生成真实的问题）
REAL_VALUES = {
    "设备名": ["cx-sx-cc002", "tdk-shanghai-b", "v6-dcs21", "ciscoA", "ngg-rt-01", 
               "poller1", "demo-switch-01", "test-router-02"],
    "客户名": ["中国电信上海理想", "测试客户", "南京研发中心", "ngg-319009", "上海理想公司"],
    "告警类型": ["Ping event", "Trap event", "Threshold event", "Syslog event"],
    "告警级别": ["严重", "主要", "次要", "警告"],
    "时间范围": ["今天", "昨天", "最近7天", "最近30天", "本月", "上个月", "过去三个月"]
}


def call_deepseek(prompt, max_tokens=8000):
    """调用 DeepSeek API"""
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是网络运维平台的数据库专家，熟悉设备管理、告警监控业务。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.8,
            timeout=180.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def parse_json_response(text):
    """解析 JSON 响应"""
    if not text:
        return []
    
    patterns = [
        r'```json\s*(\[.*?\])\s*```',
        r'```\s*(\[.*?\])\s*```',
        r'\[\s*\{.*?\}\s*\]',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if match.lastindex else match.group(0)
                return json.loads(json_str)
            except:
                continue
    
    try:
        return json.loads(text)
    except:
        return []


def generate_questions(difficulty, count):
    """生成指定难度的问题"""
    
    schema_text = "\n\n".join(TABLE_SCHEMAS.values())
    
    difficulty_config = {
        "simple": {
            "desc": "单表查询",
            "tables_hint": "只使用 1 张表",
            "examples": [
                "查询所有在线设备数量",
                "统计客户测试客户名下有多少设备",
                "查询今天发生的严重告警"
            ]
        },
        "medium": {
            "desc": "2表关联查询",
            "tables_hint": "必须使用 2 张表 JOIN",
            "examples": [
                "统计每个客户拥有的设备数量",
                "查询客户ngg-319009名下设备的告警总数",
                "统计最近7天每个客户的严重告警数量"
            ]
        },
        "hard": {
            "desc": "3表关联复杂查询",
            "tables_hint": "必须使用全部 3 张表 JOIN",
            "examples": [
                "查询上个月告警最多的客户及其设备清单",
                "统计每个客户每种告警类型的发生次数并按客户分组",
                "找出最近30天没有任何告警的客户及其设备数量"
            ]
        }
    }
    
    config = difficulty_config[difficulty]
    
    prompt = f"""请生成 {count} 个 {difficulty} 难度（{config['desc']}）的自然语言问题，用于查询网络运维数据库。

## 可用的表（只能使用这 3 张表！）：
{schema_text}

## 表之间的关系：
- t_bz_config_ci_ne_root.CUSTOMER_ID → t_bz_config_customer.CUSTOMER_ID
- event_history.NE_ID → t_bz_config_ci_ne_root.NE_ID
- event_history.CUSTOMER_ID → t_bz_config_customer.CUSTOMER_ID

## 真实值（必须在问题中使用！）：
- 设备名: {', '.join(REAL_VALUES['设备名'])}
- 客户名: {', '.join(REAL_VALUES['客户名'])}
- 告警类型: {', '.join(REAL_VALUES['告警类型'])}
- 告警级别: {', '.join(REAL_VALUES['告警级别'])}
- 时间范围: {', '.join(REAL_VALUES['时间范围'])}

## {difficulty.upper()} 难度要求：
- {config['tables_hint']}
- 示例: {', '.join(config['examples'])}

## 输出格式（JSON 数组）：
```json
[
  {{"question": "问题描述", "sql": "SELECT...", "tables": ["表名1", "表名2"], "difficulty": "{difficulty}"}}
]
```

## 重要要求：
1. 问题必须用口语化的中文，不要使用引号
2. SQL 必须是可执行的 MySQL 语法
3. tables 数组必须准确列出用到的表名
4. 必须使用上面提供的真实设备名、客户名等
5. 禁止使用假数据如"ABC公司"、"设备A"等

请生成 {count} 个问题：
"""
    
    print(f"  正在调用 DeepSeek 生成 {difficulty} 问题...")
    response = call_deepseek(prompt)
    
    if response:
        questions = parse_json_response(response)
        # 确保每个问题都有正确的难度标记
        for q in questions:
            q["difficulty"] = difficulty
        return questions
    
    return []


def main():
    print("=" * 70)
    print("生成测试问题 - 限定 3 张表")
    print("=" * 70)
    print(f"目标表: {', '.join(TARGET_TABLES)}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_questions = []
    
    for difficulty in ["simple", "medium", "hard"]:
        print(f"\n{'='*50}")
        print(f"生成 {difficulty} 难度问题 (目标: 100 个)")
        print(f"{'='*50}")
        
        difficulty_questions = []
        batch_size = 25
        batches = 4
        
        for batch in range(batches):
            print(f"  批次 {batch+1}/{batches}...")
            questions = generate_questions(difficulty, batch_size)
            if questions:
                difficulty_questions.extend(questions)
                print(f"    获得 {len(questions)} 个问题")
            else:
                print(f"    生成失败，跳过")
        
        print(f"  {difficulty} 共获得: {len(difficulty_questions)} 个问题")
        all_questions.extend(difficulty_questions)
    
    # 验证 tables 字段
    print("\n验证问题...")
    valid_questions = []
    for q in all_questions:
        tables = q.get("tables", [])
        if all(t in TARGET_TABLES for t in tables):
            valid_questions.append(q)
        else:
            print(f"  跳过无效问题（使用了非目标表）: {tables}")
    
    print(f"\n总计生成: {len(valid_questions)} 个有效问题")
    
    # 保存 JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(valid_questions, f, ensure_ascii=False, indent=2)
    print(f"已保存 JSON: {OUTPUT_JSON}")
    
    # 保存 CSV
    import csv
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["question", "sql", "tables", "difficulty"])
        for q in valid_questions:
            tables = ",".join(q.get("tables", []))
            writer.writerow([q.get("question", ""), q.get("sql", ""), tables, q.get("difficulty", "")])
    print(f"已保存 CSV: {OUTPUT_CSV}")
    
    # 统计
    print("\n" + "=" * 50)
    print("统计")
    print("=" * 50)
    for d in ["simple", "medium", "hard"]:
        count = sum(1 for q in valid_questions if q.get("difficulty") == d)
        print(f"{d}: {count} 个")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
