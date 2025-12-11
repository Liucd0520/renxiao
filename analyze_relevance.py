# -*- coding: utf-8 -*-
"""
深度分析测试 - 检查检索结果与问题的实际匹配度
"""

import json
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试问题
TEST_QUESTION = "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？"

# 问题需要的关键语义元素
REQUIRED_CONCEPTS = [
    "客户",        # 需要客户表
    "设备",        # 需要设备表
    "告警类型",    # 需要告警类型字段
    "告警时间",    # 需要告警时间字段  
    "恢复时间",    # 需要恢复时间字段
]

SCHEMA_PATH = "./spider2_dev/schemas/netcaredb_ai"

def analyze_table_relevance():
    """分析各个表的相关性"""
    print(f"分析问题: {TEST_QUESTION}\n")
    print("=" * 80)
    
    # 收集所有表及其列信息
    tables = {}
    for filename in os.listdir(SCHEMA_PATH):
        if filename.endswith('.json'):
            with open(os.path.join(SCHEMA_PATH, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            table_name = data['meta_data']['table_name']
            if table_name not in tables:
                tables[table_name] = {'columns': [], 'descriptions': []}
            
            tables[table_name]['columns'].append(data['column_name'])
            if data['column_descriptions']:
                tables[table_name]['descriptions'].append(data['column_descriptions'])
    
    print(f"数据库共有 {len(tables)} 个表\n")
    
    # 评估每个表的相关性
    relevance_scores = {}
    
    # 关键词匹配
    keywords = {
        "客户": ["customer", "客户", "CUSTOMER"],
        "设备": ["device", "设备", "ne", "NE", "equipment", "ci"],
        "告警类型": ["alarm_type", "告警类型", "event_type", "ALARM_TYPE", "EVENT_TYPE"],
        "告警时间": ["alarm_time", "告警时间", "event_time", "occur_time", "ALARM_TIME", "EVENT_TIME", "OCCUR_TIME"],
        "恢复时间": ["recovery", "恢复", "clear", "CLEAR", "RECOVER", "ACK"]
    }
    
    for table_name, info in tables.items():
        score = 0
        matches = []
        
        # 检查表名
        table_lower = table_name.lower()
        for concept, kws in keywords.items():
            for kw in kws:
                if kw.lower() in table_lower:
                    score += 2
                    matches.append(f"表名包含'{kw}'")
                    break
        
        # 检查列名和描述
        all_text = ' '.join(info['columns'] + info['descriptions']).lower()
        for concept, kws in keywords.items():
            for kw in kws:
                if kw.lower() in all_text:
                    score += 1
                    matches.append(f"列/描述包含'{kw}'")
                    break
        
        if score > 0:
            relevance_scores[table_name] = {
                'score': score,
                'matches': matches,
                'columns': info['columns'][:10]  # 只显示前10列
            }
    
    # 按相关性排序
    sorted_tables = sorted(relevance_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    print("=" * 80)
    print("相关性排名 TOP 20:")
    print("=" * 80)
    
    for i, (table_name, info) in enumerate(sorted_tables[:20]):
        print(f"\n{i+1}. {table_name} (得分: {info['score']})")
        print(f"   匹配: {', '.join(info['matches'])}")
        print(f"   列: {', '.join(info['columns'][:5])}...")
    
    print("\n" + "=" * 80)
    print("建议的目标表（前5名）:")
    print("=" * 80)
    suggested_tables = [t[0] for t in sorted_tables[:5]]
    for t in suggested_tables:
        print(f"  - {t}")
    
    return sorted_tables


def compare_with_test_results():
    """对比测试结果与相关性分析"""
    print("\n" + "=" * 80)
    print("对比测试返回结果与相关性分析")
    print("=" * 80)
    
    # 读取测试结果
    result_file = "./spider2_dev/test_results/agent_5_1.xlsx"
    if os.path.exists(result_file):
        df = pd.read_excel(result_file)
        returned_tables = set(df['Table Name'].unique())
        print(f"\n测试返回的表 ({len(returned_tables)}个):")
        for t in sorted(returned_tables):
            print(f"  - {t}")


if __name__ == "__main__":
    sorted_tables = analyze_table_relevance()
    compare_with_test_results()
