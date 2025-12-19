#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 DeepSeek 生成 100 个测试问题和 SQL 答案

让 DeepSeek 阅读整个数据库的 schema（344 张表），
模仿 cc_result.csv 中的提问风格来生成问题和对应的 SQL 答案
"""

import os
import sys
import json
import csv
from pathlib import Path
from openai import OpenAI
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-6670dc8295234c4192dbd5e579b4a0ac"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 文件路径
TABLE_SCHEMA_DIR = "./spider2_dev/schemas_table_level_enhanced/netcaredb_ai"
OUTPUT_CSV = "./test_questions_100.csv"
OUTPUT_JSON = "./test_questions_100.json"


def load_all_table_schemas():
    """加载所有 344 个表的 schema"""
    schemas = []
    table_dir = Path(TABLE_SCHEMA_DIR)
    
    if not table_dir.exists():
        print(f"错误: 目录不存在 {TABLE_SCHEMA_DIR}")
        return []
    
    for json_file in sorted(table_dir.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                table_name = data.get("table_name", json_file.stem)
                description = data.get("llm_description", "")[:150]  # 限制描述长度
                schemas.append({
                    "name": table_name,
                    "description": description
                })
        except Exception as e:
            print(f"加载 {json_file} 失败: {e}")
    
    return schemas


def format_schema_list(schemas):
    """格式化所有表的描述（简洁版）"""
    lines = []
    for i, s in enumerate(schemas, 1):
        lines.append(f"{i}. {s['name']}: {s['description']}")
    return "\n".join(lines)


def load_example_questions():
    """加载 cc_result.csv 中的示例问题"""
    examples = []
    csv_file = Path("./cc_result.csv")
    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('query'):
                    sql = row.get('sql', '')
                    examples.append({
                        "question": row['query'],
                        "sql": sql[:200] + "..." if len(sql) > 200 else sql
                    })
    return examples


GENERATION_PROMPT = """你是一个数据库专家。请根据以下数据库 Schema（共 {table_count} 张表），生成 {batch_size} 个中文业务问题及其对应的 SQL 查询。

## 数据库 Schema（344 张表的描述）

{schema}

## 示例问题（参考这些问题的风格和难度）

{examples}

## 要求

1. **模仿示例问题的风格**: 问题应该是简洁的业务问题
2. **问题必须基于上述 schema 中的表**: 每个问题应该使用 1-3 张表
3. **SQL 必须正确可执行**: 使用 MySQL 语法
4. **问题类型多样化**:
   - 统计类: "有多少..."
   - 排名类: "TOP N..."、"最多/最少..."
   - 时间筛选: "近一周/月/年..."
   - 条件筛选: "某客户..."、"指定设备..."
   - 分组统计: "按...分类统计"
5. **覆盖不同的表**: 不要只用少数几张表，尽量覆盖不同类型的表

## 输出格式

请用 JSON 格式输出：
```json
[
  {{
    "question": "中文问题",
    "sql": "SELECT ...",
    "tables": ["table1", "table2"],
    "difficulty": "easy/medium/hard"
  }}
]
```

请生成 {batch_size} 个问题：
"""


def call_deepseek(prompt, max_tokens=8192):
    """调用 DeepSeek API"""
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的数据库专家，精通 MySQL 语法。请生成真实业务场景的查询问题。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.8,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def extract_json_from_response(response):
    """从响应中提取 JSON"""
    if not response:
        return []
    
    import re
    # 查找 JSON 代码块
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 尝试找到 [ 开始的位置
        start = response.find('[')
        end = response.rfind(']') + 1
        if start != -1 and end > start:
            json_str = response[start:end]
        else:
            json_str = response
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}")
        # 尝试修复常见问题
        try:
            # 替换单引号为双引号
            fixed = json_str.replace("'", '"')
            return json.loads(fixed)
        except:
            return []


def generate_questions(total=100, batch_size=25):
    """批量生成问题"""
    print("=" * 60)
    print("使用 DeepSeek 生成测试问题")
    print("=" * 60)
    print(f"目标: 生成 {total} 个问题")
    print(f"批次大小: {batch_size}")
    
    # 加载所有表的 schema
    schemas = load_all_table_schemas()
    print(f"加载表数: {len(schemas)}")
    
    if not schemas:
        print("错误: 没有加载到任何表")
        return []
    
    # 格式化 schema
    schema_text = format_schema_list(schemas)
    print(f"Schema 总字符数: {len(schema_text)}")
    
    # 加载示例问题
    examples = load_example_questions()
    examples_str = "\n".join([f"问题: {e['question']}\nSQL: {e['sql']}\n" for e in examples[:5]])
    print(f"示例问题: {len(examples)} 个")
    
    all_questions = []
    num_batches = (total + batch_size - 1) // batch_size
    
    for batch_idx in range(num_batches):
        remaining = total - len(all_questions)
        current_batch_size = min(batch_size, remaining)
        
        print(f"\n批次 {batch_idx + 1}/{num_batches}: 生成 {current_batch_size} 个问题...")
        
        prompt = GENERATION_PROMPT.format(
            schema=schema_text,
            examples=examples_str,
            batch_size=current_batch_size,
            table_count=len(schemas)
        )
        
        response = call_deepseek(prompt, max_tokens=8192)
        
        if response:
            questions = extract_json_from_response(response)
            if questions:
                all_questions.extend(questions)
                print(f"  ✅ 成功生成 {len(questions)} 个问题，累计 {len(all_questions)} 个")
            else:
                print(f"  ❌ JSON 解析失败，跳过此批次")
                # 保存原始响应用于调试
                with open(f"debug_batch_{batch_idx}.txt", 'w', encoding='utf-8') as f:
                    f.write(response)
        else:
            print(f"  ❌ API 调用失败，跳过此批次")
        
        if len(all_questions) >= total:
            break
    
    return all_questions[:total]


def save_results(questions):
    """保存结果"""
    # 保存 JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON 保存到: {OUTPUT_JSON}")
    
    # 保存 CSV
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'question', 'sql', 'tables', 'difficulty'])
        writer.writeheader()
        for i, q in enumerate(questions, 1):
            tables = q.get('tables', [])
            if isinstance(tables, list):
                tables_str = ','.join(tables)
            else:
                tables_str = str(tables)
            writer.writerow({
                'id': i,
                'question': q.get('question', ''),
                'sql': q.get('sql', ''),
                'tables': tables_str,
                'difficulty': q.get('difficulty', '')
            })
    print(f"✅ CSV 保存到: {OUTPUT_CSV}")


def main():
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    questions = generate_questions(total=100, batch_size=25)
    
    if questions:
        save_results(questions)
        
        print("\n" + "=" * 60)
        print(f"🎉 生成完成！共 {len(questions)} 个问题")
        print("=" * 60)
        
        # 统计难度分布
        difficulties = {}
        for q in questions:
            d = q.get('difficulty', 'unknown')
            difficulties[d] = difficulties.get(d, 0) + 1
        
        print("\n难度分布:")
        for d, count in sorted(difficulties.items()):
            print(f"  {d}: {count}")
        
        # 统计表使用情况
        table_usage = {}
        for q in questions:
            tables = q.get('tables', [])
            if isinstance(tables, list):
                for t in tables:
                    table_usage[t] = table_usage.get(t, 0) + 1
        
        print(f"\n涉及表数: {len(table_usage)}")
        print("使用最多的表:")
        for name, count in sorted(table_usage.items(), key=lambda x: -x[1])[:10]:
            print(f"  {name}: {count}")
    else:
        print("\n❌ 生成失败，请检查 API 配置或网络")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
