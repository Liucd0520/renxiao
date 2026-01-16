#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSH Entity Linking SQL 生成测试

对比启用/禁用 LSH 对 SQL 生成质量的影响
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, "/Users/jason/Documents/实习/理想实习/FusionSQL")

# 测试用例
TEST_CASES = [
    {
        "id": 1,
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root"],
        "key_columns": ["EVENT_TYPE_NAME", "HOST_NAME"],
    },
    {
        "id": 2,
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
        "key_columns": ["EVENT_NAME", "device_status", "CUSTOMER_NAME"],
    },
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "expected_tables": ["t_bz_config_customer"],
        "key_columns": ["CUSTOMER_ID"],
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "key_columns": ["CI_ID"],
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "key_columns": ["ONLINE_TIME"],
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
        "key_columns": ["OFFLINE_TIME"],
    },
    {
        "id": 7,
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
        "key_columns": ["EVENT_NAME", "EVENT_TIME", "RECOVERY_TIME"],
    },
]


def check_table_recall(sql: str, expected_tables: list) -> dict:
    """检查表召回率"""
    sql_upper = sql.upper()
    hit = []
    miss = []
    for t in expected_tables:
        if t.upper() in sql_upper:
            hit.append(t)
        else:
            miss.append(t)
    return {
        "hit": hit,
        "miss": miss,
        "recall": len(hit) / len(expected_tables) if expected_tables else 1.0
    }


def check_column_usage(sql: str, key_columns: list) -> dict:
    """检查关键列是否被使用"""
    sql_upper = sql.upper()
    hit = []
    miss = []
    for c in key_columns:
        if c.upper() in sql_upper:
            hit.append(c)
        else:
            miss.append(c)
    return {
        "hit": hit,
        "miss": miss,
        "usage": len(hit) / len(key_columns) if key_columns else 1.0
    }


def test_with_lsh(enable_lsh: bool):
    """测试 SQL 生成"""
    from fusionsql.pipeline import TextToSQL
    
    print(f"\n{'='*60}")
    print(f"测试 LSH={'启用' if enable_lsh else '禁用'}")
    print(f"{'='*60}")
    
    # 初始化 Pipeline
    pipeline = TextToSQL(enable_lsh=enable_lsh)
    
    results = []
    total_recall = 0
    total_column_usage = 0
    
    for tc in TEST_CASES:
        print(f"\n## 测试 {tc['id']}: {tc['question'][:30]}...")
        
        try:
            result = pipeline.run_with_details(tc['question'], top_k=10)
            sql = result['sql']
            tables = result['retrieved_tables']
            matched_values = result.get('matched_values', {})
            
            # 检查表召回
            table_check = check_table_recall(sql, tc['expected_tables'])
            total_recall += table_check['recall']
            
            # 检查列使用
            column_check = check_column_usage(sql, tc['key_columns'])
            total_column_usage += column_check['usage']
            
            # 打印结果
            print(f"   表召回: {len(table_check['hit'])}/{len(tc['expected_tables'])} ({table_check['recall']*100:.0f}%)")
            if table_check['miss']:
                print(f"   缺失表: {table_check['miss']}")
            print(f"   列使用: {len(column_check['hit'])}/{len(tc['key_columns'])} ({column_check['usage']*100:.0f}%)")
            
            # LSH Entity Linking 信息
            if matched_values:
                print(f"   LSH Entity Linking:")
                for t, cols in list(matched_values.items())[:2]:
                    for c, vals in cols.items():
                        print(f"     - {t}.{c} = {vals[:2]}")
            
            results.append({
                "id": tc['id'],
                "status": "PASS" if table_check['recall'] == 1.0 else "PARTIAL",
                "table_recall": table_check['recall'],
                "column_usage": column_check['usage'],
                "sql": sql[:200],
                "lsh_matches": len(matched_values)
            })
            
        except Exception as e:
            print(f"   错误: {e}")
            results.append({
                "id": tc['id'],
                "status": "ERROR",
                "error": str(e)
            })
    
    # 汇总
    avg_recall = total_recall / len(TEST_CASES)
    avg_column_usage = total_column_usage / len(TEST_CASES)
    passed = sum(1 for r in results if r.get('table_recall', 0) == 1.0)
    
    print(f"\n{'='*60}")
    print(f"汇总 (LSH={'启用' if enable_lsh else '禁用'})")
    print(f"{'='*60}")
    print(f"通过: {passed}/7 ({passed/7*100:.1f}%)")
    print(f"平均表召回率: {avg_recall*100:.1f}%")
    print(f"平均列使用率: {avg_column_usage*100:.1f}%")
    
    return {
        "enable_lsh": enable_lsh,
        "passed": passed,
        "total": 7,
        "avg_table_recall": avg_recall,
        "avg_column_usage": avg_column_usage,
        "results": results
    }


if __name__ == "__main__":
    print("LSH Entity Linking SQL 生成测试")
    print(f"时间: {datetime.now()}")
    
    # 禁用 LSH 测试
    result_no_lsh = test_with_lsh(enable_lsh=False)
    
    # 启用 LSH 测试
    result_with_lsh = test_with_lsh(enable_lsh=True)
    
    # 对比
    print("\n" + "="*60)
    print("对比结果")
    print("="*60)
    print(f"| 指标 | 禁用 LSH | 启用 LSH | 差异 |")
    print(f"|------|----------|----------|------|")
    print(f"| 通过率 | {result_no_lsh['passed']}/7 | {result_with_lsh['passed']}/7 | {result_with_lsh['passed'] - result_no_lsh['passed']:+d} |")
    print(f"| 表召回 | {result_no_lsh['avg_table_recall']*100:.1f}% | {result_with_lsh['avg_table_recall']*100:.1f}% | {(result_with_lsh['avg_table_recall'] - result_no_lsh['avg_table_recall'])*100:+.1f}% |")
    print(f"| 列使用 | {result_no_lsh['avg_column_usage']*100:.1f}% | {result_with_lsh['avg_column_usage']*100:.1f}% | {(result_with_lsh['avg_column_usage'] - result_no_lsh['avg_column_usage'])*100:+.1f}% |")
    
    # 保存结果
    output = {
        "test_time": datetime.now().isoformat(),
        "comparison": {
            "no_lsh": result_no_lsh,
            "with_lsh": result_with_lsh
        }
    }
    
    output_path = "/Users/jason/Documents/实习/理想实习/FusionSQL/docs/20260116_lsh_entity_linking_test.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_path}")
