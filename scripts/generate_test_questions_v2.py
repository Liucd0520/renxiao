#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实数据库值生成 300 个测试问题

关键改进：
- 使用数据库中真实的设备名、客户名、区域名等
- 让 DeepSeek 在问题中使用这些真实值
- 这样列级别检索才能匹配到真实数据
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

# 路径配置
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
REAL_VALUES_FILE = "./docs/milestone_20241219/real_values_from_db.json"
OUTPUT_JSON = "./docs/milestone_20241219/test_questions_300_v2.json"
OUTPUT_CSV = "./docs/milestone_20241219/test_questions_300_v2.csv"


def load_real_values():
    """加载真实数据库值"""
    with open(REAL_VALUES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_table_schemas():
    """加载所有表的 Schema 描述（精简版）"""
    schemas = []
    table_dir = Path(TABLE_SCHEMA_DIR)
    
    for json_file in sorted(table_dir.glob("*.json")):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_name = data.get("table_name", json_file.stem)
        desc = data.get("llm_description", data.get("description", ""))[:100]
        
        schemas.append(f"- {table_name}: {desc}")
    
    return "\n".join(schemas)


def call_deepseek(prompt, max_tokens=8000):
    """调用 DeepSeek API"""
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
    
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是网络运维平台的资深用户，熟悉设备管理、告警监控、客户服务等业务。"},
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
        r'\[\s*\{.*?\}\s*\]',
        r'```json\s*(\[.*?\])\s*```',
        r'```\s*(\[.*?\])\s*```',
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
        pass
    
    return []


def generate_questions_by_difficulty(difficulty, count, schema_text, real_values):
    """按难度生成问题，使用真实值"""
    
    difficulty_desc = {
        "easy": """
【简单问题特点】
- 单表查询，不需要 JOIN
- 简单的 COUNT、SUM 统计
- 直接的条件过滤
""",
        "medium": """
【中等问题特点】
- 需要 2-3 张表 JOIN
- 带有时间范围过滤
- 需要 GROUP BY 分组统计
""",
        "hard": """
【困难问题特点】
- 需要 3 张以上表 JOIN
- 复杂的时间条件
- 需要排名、TOP N、子查询
"""
    }
    
    # 核心表和真实值
    real_values_text = f"""
## 真实数据库值（必须在问题中使用！）：

### 真实设备名（来自 t_bz_config_ci_ne_root.HOST_NAME）：
{', '.join(real_values.get('设备名_HOST_NAME', [])[:10])}

### 真实客户名（来自 t_bz_config_customer.CUSTOMER_NAME）：
{', '.join(real_values.get('客户名_CUSTOMER_NAME', [])[:10])}

### 真实区域名（来自 t_bz_config_region.REGION_NAME）：
{', '.join(real_values.get('区域名_REGION_NAME', [])[:10])}

### 真实告警类型（来自 event_history.EVENT_TYPE_NAME）：
{', '.join(real_values.get('告警类型_EVENT_TYPE_NAME', [])[:7])}

### 真实设备类型（来自 ne_type.NE_TYPE_NAME）：
{', '.join(real_values.get('设备类型_NE_TYPE_NAME', [])[:10])}

### 真实采集机名（来自 collector_v2.COLLECTOR_NAME）：
{', '.join(real_values.get('采集机名_COLLECTOR_NAME', [])[:10])}
"""
    
    core_tables = """
## 核心表（必须使用真实表名！）：
- t_bz_config_ci_ne_root: 设备表（HOST_NAME 是设备名）
- t_bz_config_customer: 客户表（CUSTOMER_NAME 是客户名）
- event_history: 告警历史表（EVENT_TYPE_NAME 是告警类型）
- collector_v2: 采集机表（COLLECTOR_NAME 是采集机名）
- ne_type: 设备类型表（NE_TYPE_NAME 是设备类型）
- t_bz_config_region: 区域表（REGION_NAME 是区域名）
"""
    
    prompt = f"""请生成 {count} 个 {difficulty} 难度的自然语言问题，用于查询网络运维数据库。

{difficulty_desc[difficulty]}

{real_values_text}

{core_tables}

## Schema（部分）：
{schema_text[:6000]}

## ⚠️ 最重要的要求 ⚠️：
1. **问题中必须使用上面提供的真实值！** 例如：
   - 设备名用 cx-sx-cc002、tdk-shanghai-b 等真实设备名
   - 客户名用 测试、ngg-319009、南京研发中心 等真实客户名
   - 区域名用 上海、浦东、南京 等真实区域名
   - 告警类型用 Ping event、Trap event 等真实告警类型

2. **禁止使用假数据！** 如 ABC公司、Router-01、华东区域 等都禁止使用！

3. **表名必须使用真实表名**：设备表用 t_bz_config_ci_ne_root，不能简化！

4. **问题风格**：口语化，不要使用引号和括号

## 输出格式（JSON）：
```json
[
  {{"question": "设备cx-sx-cc002上个月告警次数统计", "sql": "SELECT...", "tables": ["t_bz_config_ci_ne_root", "event_history"], "difficulty": "{difficulty}"}}
]
```

请生成 {count} 个问题，必须使用真实的设备名、客户名、区域名：
"""
    
    print(f"正在生成 {difficulty} 难度问题...")
    response = call_deepseek(prompt)
    
    if response:
        questions = parse_json_response(response)
        for q in questions:
            q["difficulty"] = difficulty
        return questions
    
    return []


def main():
    print("=" * 70)
    print("使用真实数据库值生成 300 个测试问题")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载真实值
    print("加载真实数据库值...")
    real_values = load_real_values()
    for key, values in real_values.items():
        print(f"  {key}: {len(values)} 个")
    
    # 加载 Schema
    print("加载数据库 Schema...")
    schema_text = load_all_table_schemas()
    
    all_questions = []
    
    # 分批生成
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n{'='*50}")
        print(f"生成 {difficulty} 难度问题 (目标: 100 个)")
        print(f"{'='*50}")
        
        difficulty_questions = []
        batch_size = 25
        batches = 4
        
        for batch in range(batches):
            print(f"  批次 {batch+1}/{batches}...")
            questions = generate_questions_by_difficulty(difficulty, batch_size, schema_text, real_values)
            if questions:
                difficulty_questions.extend(questions)
                print(f"    获得 {len(questions)} 个问题")
            else:
                print(f"    生成失败，跳过")
        
        print(f"  {difficulty} 共获得: {len(difficulty_questions)} 个问题")
        all_questions.extend(difficulty_questions)
    
    print(f"\n总计生成: {len(all_questions)} 个问题")
    
    # 保存 JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    print(f"已保存 JSON: {OUTPUT_JSON}")
    
    # 保存 CSV
    import csv
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["question", "sql", "tables", "difficulty"])
        for q in all_questions:
            tables = ",".join(q.get("tables", []))
            writer.writerow([q.get("question", ""), q.get("sql", ""), tables, q.get("difficulty", "")])
    print(f"已保存 CSV: {OUTPUT_CSV}")
    
    # 统计
    print("\n" + "=" * 50)
    print("统计")
    print("=" * 50)
    for d in ["easy", "medium", "hard"]:
        count = sum(1 for q in all_questions if q.get("difficulty") == d)
        print(f"{d}: {count} 个")
    
    # 验证真实值使用情况
    print("\n验证真实值使用情况:")
    real_names = set(real_values.get('设备名_HOST_NAME', []) + real_values.get('客户名_CUSTOMER_NAME', []))
    used = 0
    for q in all_questions:
        for name in real_names:
            if name in q.get("question", ""):
                used += 1
                break
    print(f"  使用真实值的问题: {used}/{len(all_questions)} = {used/len(all_questions)*100:.1f}%")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
