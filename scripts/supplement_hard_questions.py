#!/usr/bin/env python3
"""补充生成 hard 难度问题"""

import os, sys, json, re
from openai import OpenAI

os.chdir('/Users/jason/Documents/实习/理想实习/LinkAlign')

DEEPSEEK_API_KEY = 'sk-6670dc8295234c4192dbd5e579b4a0ac'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# 读取现有问题
with open('./docs/milestone_20241224/test_questions_3tables_300.json', 'r') as f:
    existing = json.load(f)

hard_count = sum(1 for q in existing if q.get('difficulty') == 'hard')
print(f'现有 hard 问题: {hard_count}')

# 如果不够就补充
target = 100
need = target - hard_count
if need > 0:
    print(f'需要补充 {need} 个 hard 问题...')
    
    for batch in range(3):  # 3 批次
        prompt = f'''请生成 25 个 hard 难度（3表关联复杂查询）的问题。

## 可用的表（只能使用这 3 张表）：
- t_bz_config_ci_ne_root: 设备主表 (CUSTOMER_ID, HOST_NAME, NE_ID, IS_ONLINE)
- t_bz_config_customer: 客户表 (CUSTOMER_ID, CUSTOMER_NAME)
- event_history: 告警历史表 (NE_ID, CUSTOMER_ID, EVENT_TYPE_NAME, SEVERITY, EVENT_TIME)

## 要求：必须使用全部 3 张表 JOIN
## 真实值：设备名 cx-sx-cc002, tdk-shanghai-b；客户名 测试客户, ngg-319009；告警类型 Ping event, Trap event

输出 JSON 数组：
[{{"question": "问题", "sql": "SELECT...", "tables": ["t_bz_config_ci_ne_root", "t_bz_config_customer", "event_history"], "difficulty": "hard"}}]
'''
        
        try:
            print(f'  批次 {batch+1}/3...')
            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=8000,
                temperature=0.8,
                timeout=180.0
            )
            
            text = response.choices[0].message.content
            # 尝试多种解析方式
            json_match = re.search(r'\[[\s\S]*\]', text)
            if json_match:
                new_questions = json.loads(json_match.group(0))
                for q in new_questions:
                    q['difficulty'] = 'hard'
                existing.extend(new_questions)
                print(f'    获得 {len(new_questions)} 个问题')
        except Exception as e:
            print(f'    失败: {e}')
            continue

# 保存
with open('./docs/milestone_20241224/test_questions_3tables_300.json', 'w') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

# 统计
simple = sum(1 for q in existing if q.get('difficulty') == 'simple')
medium = sum(1 for q in existing if q.get('difficulty') == 'medium')
hard = sum(1 for q in existing if q.get('difficulty') == 'hard')
print(f'\n最终统计: simple={simple}, medium={medium}, hard={hard}, 总计={len(existing)}')
