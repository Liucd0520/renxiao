#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
32B Coder 温度测试脚本
温度: 0, 0.1
每个温度测试100轮
"""

import sys
import os
import json
from datetime import datetime
from tqdm import tqdm

sys.path.insert(0, '/Users/jason/Documents/实习/理想实习/FusionSQL')
os.chdir('/Users/jason/Documents/实习/理想实习/FusionSQL')

from fusionsql.retriever import FastRetriever
from fusionsql.sql_generator import SQLGenerator

# 7题测试数据
TEST_QUESTIONS = [
    {"id": 1, "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计", 
     "expected_tables": ["event_history", "t_bz_config_ci_ne_root"]},
    {"id": 2, "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称", 
     "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]},
    {"id": 3, "question": "现在平台上有多少家客户", 
     "expected_tables": ["t_bz_config_customer"]},
    {"id": 4, "question": "现在平台上有多少台设备", 
     "expected_tables": ["t_bz_config_ci_ne_root"]},
    {"id": 5, "question": "上个月上线的新设备有多少", 
     "expected_tables": ["t_bz_config_ci_ne_root"]},
    {"id": 6, "question": "上个月下线的设备有多少", 
     "expected_tables": ["t_bz_config_ci_ne_root"]},
    {"id": 7, "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？", 
     "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"]},
]

BAD_COLUMNS = ['ALARM_CLEAR_TIME', 'CLEAR_TIME', 'RECOVER_TIME', 'RECOVERY_TIME']

def check_sql(sql, expected_tables):
    sql_upper = sql.upper()
    missing = [t for t in expected_tables if t.upper() not in sql_upper]
    bad_cols = [c for c in BAD_COLUMNS if c.upper() in sql_upper]
    return {
        "tables_ok": len(missing) == 0,
        "missing_tables": missing,
        "bad_columns": bad_cols,
        "truly_correct": len(missing) == 0 and len(bad_cols) == 0
    }

def run_temperature_test(temperature, rounds=100):
    """运行指定温度的测试"""
    print(f"\n{'='*60}")
    print(f"温度 = {temperature}，运行 {rounds} 轮")
    print(f"{'='*60}")
    
    # 初始化
    retriever = FastRetriever()
    generator = SQLGenerator(
        schema_dir='/Users/jason/Documents/实习/理想实习/FusionSQL/fusionsql/schemas',
        model_name="Qwen2.5-Coder-32B-Instruct",
        base_url="http://172.31.24.112:33080/v1",
        api_key="yfzx202510",
        temperature=temperature
    )
    print(f"模型: {generator.llm.model_name}")
    
    all_results = []
    progress = tqdm(range(1, rounds + 1), desc=f"T={temperature}")
    
    for r in progress:
        round_results = []
        round_correct = 0
        
        for q in TEST_QUESTIONS:
            # 检索
            retrieved = retriever.retrieve(q['question'], top_k=15)
            table_names = [t[0] for t in retrieved]
            
            # 生成SQL
            sql = generator.generate_sql(q['question'], table_names)
            check = check_sql(sql, q['expected_tables'])
            
            round_results.append({
                "id": q['id'],
                "sql": sql,
                "truly_correct": check['truly_correct'],
                **check
            })
            if check['truly_correct']:
                round_correct += 1
        
        all_results.append({
            "round": r, 
            "correct": round_correct,
            "results": round_results
        })
        progress.set_postfix({"correct": f"{round_correct}/7"})
    
    # 统计
    avg_correct = sum(r['correct'] for r in all_results) / len(all_results)
    
    # 每题统计
    q_stats = []
    for i in range(7):
        passed = sum(1 for r in all_results if r['results'][i]['truly_correct'])
        q_stats.append({"id": i+1, "passed": passed, "total": rounds, "rate": passed/rounds})
    
    return {
        "temperature": temperature,
        "rounds": rounds,
        "avg_correct": avg_correct,
        "avg_accuracy": avg_correct / 7,
        "question_stats": q_stats,
        "details": all_results
    }

def main():
    print("=" * 60)
    print("Qwen2.5-Coder-32B 温度测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("温度: 0, 0.1")
    print("每个温度: 100轮")
    print("=" * 60)
    
    temperatures = [0, 0.1]
    all_results = {}
    
    for temp in temperatures:
        result = run_temperature_test(temp, rounds=100)
        all_results[str(temp)] = result
        
        # 保存中间结果
        output_path = '/Users/jason/Documents/实习/理想实习/FusionSQL/docs/20260106/32b_temperature_100rounds.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"  已保存中间结果")
    
    # 生成汇总
    print("\n" + "=" * 60)
    print("汇总统计")
    print("=" * 60)
    
    print("\n温度 | 平均正确 | 准确率")
    print("-" * 35)
    for temp in temperatures:
        r = all_results[str(temp)]
        print(f" {temp:.1f}  |  {r['avg_correct']:.2f}/7  | {r['avg_accuracy']*100:.1f}%")
    
    print("\n每题通过率 (100轮):")
    print("温度 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7")
    print("-" * 50)
    for temp in temperatures:
        r = all_results[str(temp)]
        qs = [f"{q['rate']*100:.0f}%" for q in r['question_stats']]
        print(f" {temp:.1f} | {' | '.join(qs)}")
    
    print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    main()
