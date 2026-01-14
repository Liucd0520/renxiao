#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Researcher 7题完整测试

测试流程：
1. 通过 LangGraph API 调用 SQL Researcher
2. 对7个问题进行完整的研究流程
3. 记录生成的 SQL 和执行结果
4. 生成测试报告

日期: 2026-01-08
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any

import httpx

# API 配置
BASE_URL = "http://127.0.0.1:2024"

# 7道测试题
TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "设备ciscoA，上个月发生了几次告警，按告警类型进行分类统计",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root"],
    },
    {
        "id": 2,
        "question": "列出平台上设备device state down状态超过3个月的设备清单及客户名称",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
    },
    {
        "id": 3,
        "question": "现在平台上有多少家客户",
        "expected_tables": ["t_bz_config_customer"],
    },
    {
        "id": 4,
        "question": "现在平台上有多少台设备",
        "expected_tables": ["t_bz_config_ci_ne_root"],
    },
    {
        "id": 5,
        "question": "上个月上线的新设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
    },
    {
        "id": 6,
        "question": "上个月下线的设备有多少",
        "expected_tables": ["t_bz_config_ci_ne_root"],
    },
    {
        "id": 7,
        "question": "某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？",
        "expected_tables": ["event_history", "t_bz_config_ci_ne_root", "t_bz_config_customer"],
    },
]


async def find_sql_researcher_assistant(client: httpx.AsyncClient) -> Dict[str, Any]:
    """查找 SQL Researcher assistant"""
    response = await client.post(f"{BASE_URL}/assistants/search", json={"limit": 10})
    if response.status_code != 200:
        raise Exception(f"Failed to search assistants: {response.text}")

    for assistant in response.json():
        if assistant["name"] == "SQL Researcher":
            return assistant

    raise Exception("SQL Researcher assistant not found")


async def run_single_question(
    client: httpx.AsyncClient,
    assistant_id: str,
    question: Dict[str, Any]
) -> Dict[str, Any]:
    """运行单个问题的测试"""
    print(f"\n[{question['id']}] {question['question'][:50]}...")

    # 创建线程
    thread_response = await client.post(f"{BASE_URL}/threads", json={})
    if thread_response.status_code != 200:
        return {"error": f"Failed to create thread: {thread_response.text}"}

    thread_id = thread_response.json()["thread_id"]

    # 创建运行
    run_response = await client.post(
        f"{BASE_URL}/threads/{thread_id}/runs",
        json={
            "assistant_id": assistant_id,
            "input": {
                "messages": [{"role": "user", "content": question["question"]}]
            }
        },
        timeout=300.0
    )

    if run_response.status_code != 200:
        return {"error": f"Failed to create run: {run_response.text}"}

    run_id = run_response.json()["run_id"]

    # 轮询等待完成
    for i in range(120):  # 最多等待 6 分钟
        await asyncio.sleep(3)
        state_response = await client.get(f"{BASE_URL}/threads/{thread_id}/runs/{run_id}")

        if state_response.status_code == 200:
            state = state_response.json()
            status = state.get("status")
            print(f"    Poll {i+1}: {status}")

            if status == "success":
                # 获取最终状态
                final_response = await client.get(f"{BASE_URL}/threads/{thread_id}/state")
                if final_response.status_code == 200:
                    return {
                        "success": True,
                        "thread_id": thread_id,
                        "run_id": run_id,
                        "values": final_response.json().get("values", {})
                    }

            elif status in ["error", "interrupted"]:
                return {"error": f"Run failed with status: {status}"}

    return {"error": "Timeout waiting for run to complete"}


def extract_sql_from_result(result: Dict[str, Any]) -> List[str]:
    """从结果中提取 SQL 查询"""
    sqls = []

    # 从 sql_results 中提取
    sql_results = result.get("values", {}).get("sql_results", [])
    for sr in sql_results:
        if sr and sr.get("sql"):
            sqls.append(sr["sql"])

    # 从 supervisor_messages 中提取
    sup_msgs = result.get("values", {}).get("supervisor_messages", [])
    for msg in sup_msgs:
        if isinstance(msg, dict) and msg.get("type") == "tool":
            content = msg.get("content", "")
            # 查找 ```sql ... ``` 代码块
            import re
            sql_matches = re.findall(r'```sql\n(.*?)\n```', content, re.DOTALL)
            sqls.extend(sql_matches)

    # 从 final_report 中提取
    report = result.get("values", {}).get("final_report", "")
    if report:
        import re
        sql_matches = re.findall(r'```sql\n(.*?)\n```', report, re.DOTALL)
        sqls.extend(sql_matches)

    return sqls


def check_table_usage(sqls: List[str], expected_tables: List[str]) -> tuple:
    """检查 SQL 是否使用了期望的表"""
    all_sql = " ".join(sqls).upper()
    missing = []
    for table in expected_tables:
        if table.upper() not in all_sql:
            missing.append(table)
    return len(missing) == 0, missing


async def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("SQL Researcher 7题完整测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = []
    correct_count = 0

    async with httpx.AsyncClient(timeout=300.0) as client:
        # 查找 assistant
        print("\n查找 SQL Researcher assistant...")
        try:
            assistant = await find_sql_researcher_assistant(client)
            print(f"找到: {assistant['assistant_id']}")
        except Exception as e:
            print(f"错误: {e}")
            return

        print("\n" + "-" * 70)
        print("开始测试")
        print("-" * 70)

        for q in TEST_QUESTIONS:
            start_time = datetime.now()
            result = await run_single_question(client, assistant["assistant_id"], q)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            if result.get("success"):
                sqls = extract_sql_from_result(result)
                tables_ok, missing = check_table_usage(sqls, q["expected_tables"])

                if tables_ok:
                    status = "PASS"
                    correct_count += 1
                else:
                    status = "FAIL"

                # 获取最终报告摘要
                report = result.get("values", {}).get("final_report", "")
                report_preview = report[:200] + "..." if len(report) > 200 else report

                test_result = {
                    "id": q["id"],
                    "question": q["question"],
                    "status": status,
                    "expected_tables": q["expected_tables"],
                    "missing_tables": missing,
                    "generated_sqls": sqls,
                    "report_preview": report_preview,
                    "duration_seconds": duration
                }

                print(f"    结果: {'✅' if tables_ok else '❌'} {status}")
                print(f"    期望表: {q['expected_tables']}")
                if sqls:
                    print(f"    生成的 SQL: {sqls[0][:80]}...")
                if missing:
                    print(f"    缺失表: {missing}")
                print(f"    耗时: {duration:.1f}s")

            else:
                test_result = {
                    "id": q["id"],
                    "question": q["question"],
                    "status": "ERROR",
                    "error": result.get("error"),
                    "duration_seconds": duration
                }
                print(f"    结果: ⚠️ ERROR - {result.get('error')}")

            results.append(test_result)

    # 汇总
    print("\n" + "=" * 70)
    print(f"测试结果汇总: {correct_count}/7 ({correct_count/7*100:.1f}%)")
    print("=" * 70)

    for r in results:
        status_icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else "⚠️")
        print(f"  [{r['id']}] {status_icon} {r['status']}: {r['question'][:40]}...")

    # 保存结果
    output = {
        "test_time": datetime.now().isoformat(),
        "test_type": "SQL Researcher Integration Test",
        "model": "Qwen2.5-Coder-32B-Instruct",
        "summary": {
            "total": 7,
            "passed": correct_count,
            "failed": 7 - correct_count,
            "accuracy": f"{correct_count/7*100:.1f}%"
        },
        "results": results
    }

    output_file = os.path.join(os.path.dirname(__file__), "sql_researcher_7q_test_result.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存: {output_file}")

    return correct_count, results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
