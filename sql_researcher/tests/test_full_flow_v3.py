#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整流程计时测试 v3 - 正确处理 interrupt 和 resume

核心改动：
1. resume 后获取新的 run_id
2. 基于 thread state 的 next 字段判断流程是否完成
3. 简化状态检测逻辑

用法:
    1. 启动 langgraph: cd open_deep_research && langgraph dev --no-browser
    2. 运行: uv run python tests/sql_researcher/test_full_flow_v3.py
"""

import asyncio
import time
from datetime import datetime
import httpx
import json

# 简单的测试问题
SIMPLE_QUESTION = "平台上有多少客户？设备数量是多少？"

# 复杂问题
COMPLEX_QUESTION = """我想了解一下咱们平台的整体情况。客户数量和设备数量大概是多少？上个月设备的上下线情况怎么样？另外，有些设备好像一直是down的状态，能不能看看哪些设备down了超过3个月，顺便告诉我是哪个客户的。还有ciscoA这台设备上个月告警挺多的，帮我看看具体是什么类型的告警。最近一周某个客户的设备告警情况也想了解一下。"""

BASE_URL = "http://127.0.0.1:2024"


class Timer:
    """阶段计时器"""
    def __init__(self):
        self.stages = []
        self.start_time = None
        self.current_stage = None
        self.current_start = None

    def start(self):
        self.start_time = time.perf_counter()
        print(f"\n⏱️  测试开始: {datetime.now().strftime('%H:%M:%S')}")

    def stage(self, name: str):
        now = time.perf_counter()
        if self.current_stage:
            elapsed = now - self.current_start
            self.stages.append((self.current_stage, elapsed))
            print(f"  ✓ {self.current_stage}: {elapsed:.1f}s")
        self.current_stage = name
        self.current_start = now
        print(f"\n▶ 开始: {name}")

    def end(self):
        now = time.perf_counter()
        if self.current_stage:
            elapsed = now - self.current_start
            self.stages.append((self.current_stage, elapsed))
            print(f"  ✓ {self.current_stage}: {elapsed:.1f}s")

        total = now - self.start_time
        print("\n" + "=" * 60)
        print("📊 耗时汇总")
        print("=" * 60)
        for stage, t in self.stages:
            pct = t / total * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {stage:35s} {t:6.1f}s ({pct:4.1f}%) {bar}")
        print(f"\n  {'总计':35s} {total:6.1f}s ({total/60:.1f}分钟)")
        return total


def has_interrupt(state_data: dict) -> tuple[bool, str]:
    """检查 state 中是否有 interrupt"""
    tasks = state_data.get('tasks', [])
    for task in tasks:
        interrupts = task.get('interrupts', [])
        if interrupts:
            value = interrupts[0].get('value', '') if isinstance(interrupts[0], dict) else str(interrupts[0])
            return True, value
    return False, ''


async def wait_for_completion_or_interrupt(client, thread_id, timeout=300, initial_wait=3):
    """等待流程完成或遇到 interrupt
    
    Returns:
        (completed, has_interrupt, state_data)
    """
    # 先等待一下，让 run 开始执行
    await asyncio.sleep(initial_wait)
    
    start = time.time()
    last_log_time = start
    seen_running = False  # 是否已经看到流程开始运行
    
    while time.time() - start < timeout:
        state = await client.get(f'{BASE_URL}/threads/{thread_id}/state')
        state_data = state.json()
        
        next_nodes = state_data.get('next', [])
        is_interrupt, _ = has_interrupt(state_data)
        
        # 如果有 next 节点，说明流程在运行
        if next_nodes:
            seen_running = True
        
        # 每 10 秒打印一次状态
        if time.time() - last_log_time > 10:
            values = state_data.get('values', {})
            sql_results = values.get('sql_results', [])
            print(f"    [{int(time.time()-start)}s] next={next_nodes}, sql_results={len(sql_results)}")
            last_log_time = time.time()
        
        if is_interrupt:
            return False, True, state_data
        
        # 只有在看到流程运行后，next 为空才表示完成
        if seen_running and not next_nodes:
            return True, False, state_data
        
        await asyncio.sleep(2)
    
    return False, False, state_data


async def resume_and_continue(client, thread_id, assistant_id, input_value=True):
    """Resume 并返回新的 run_id"""
    resp = await client.post(
        f'{BASE_URL}/threads/{thread_id}/runs',
        json={
            'assistant_id': assistant_id,
            'command': {'resume': input_value}
        }
    )
    if resp.status_code in [200, 201]:
        return resp.json().get('run_id')
    else:
        print(f"    ⚠️ Resume 失败: {resp.status_code} - {resp.text[:100]}")
        return None


async def test_full_flow(question: str = SIMPLE_QUESTION):
    """运行完整流程并计时"""
    timer = Timer()
    timer.start()

    async with httpx.AsyncClient(timeout=600.0) as client:
        # ===== 阶段1: 初始化 =====
        timer.stage("初始化连接")

        # 创建 thread
        t = await client.post(f'{BASE_URL}/threads', json={})
        if t.status_code != 200:
            print(f"❌ 创建线程失败: {t.text}")
            return
        thread_id = t.json()['thread_id']
        print(f"  Thread ID: {thread_id}")

        # 获取 assistant
        a = await client.post(f'{BASE_URL}/assistants/search', json={'limit': 10})
        assistants = a.json()
        assistant_id = None
        for ast in assistants:
            if ast['name'] == 'SQL Researcher':
                assistant_id = ast['assistant_id']
                break

        if not assistant_id:
            print("❌ 找不到 SQL Researcher!")
            return
        print(f"  Assistant ID: {assistant_id}")

        # ===== 阶段2: 发送问题 =====
        timer.stage("发送问题")
        print(f"  问题: {question[:50]}...")

        r = await client.post(
            f'{BASE_URL}/threads/{thread_id}/runs',
            json={
                'assistant_id': assistant_id,
                'input': {'messages': [{'role': 'user', 'content': question}]}
            }
        )
        run_id = r.json()['run_id']
        print(f"  Run ID: {run_id}")

        # ===== 阶段3: 问题拆解 =====
        timer.stage("问题拆解")
        
        completed, interrupted, state_data = await wait_for_completion_or_interrupt(client, thread_id, timeout=120)
        
        if interrupted:
            values = state_data.get('values', {})
            sub_questions = values.get('sub_questions', [])
            print(f"    拆解成 {len(sub_questions)} 个子问题")
            for sq in sub_questions[:3]:
                if isinstance(sq, dict):
                    print(f"      - {sq.get('question', str(sq))[:50]}...")
                else:
                    print(f"      - {str(sq)[:50]}...")
            if len(sub_questions) > 3:
                print(f"      ... 还有 {len(sub_questions) - 3} 个")

        # ===== 阶段4: 确认并继续 =====
        if interrupted:
            timer.stage("用户确认")
            print("    自动发送 'true' 确认")
            new_run_id = await resume_and_continue(client, thread_id, assistant_id, True)
            if new_run_id:
                print(f"    新 Run ID: {new_run_id}")

        # ===== 阶段5: SQL 研究执行 =====
        timer.stage("SQL 研究执行")
        
        max_wait = 600  # 最多等 10 分钟
        start_research = time.time()
        
        while time.time() - start_research < max_wait:
            completed, interrupted, state_data = await wait_for_completion_or_interrupt(
                client, thread_id, timeout=30
            )
            
            if completed:
                print("    ✅ 流程完成！")
                break
            
            if interrupted:
                # 自动确认 interrupt
                print(f"    🔄 遇到 interrupt，自动确认...")
                await resume_and_continue(client, thread_id, assistant_id, True)
                continue
            
            # 超时但没完成，继续等
            pass
        
        # ===== 阶段6: 获取结果 =====
        timer.stage("获取最终结果")

        final = await client.get(f'{BASE_URL}/threads/{thread_id}/state')
        final_data = final.json()
        values = final_data.get('values', {})

        report = values.get('final_report', '')
        sql_results = values.get('sql_results', [])
        sub_questions = values.get('sub_questions', [])

        print(f"    子问题数: {len(sub_questions)}")
        print(f"    SQL 结果数: {len(sql_results)}")
        print(f"    报告长度: {len(report)} 字符")

        if report:
            print("\n" + "-" * 40)
            print("报告预览 (前500字):")
            print("-" * 40)
            print(report[:500])
            print("...")

        # 显示 SQL 结果详情
        if sql_results:
            print("\n" + "-" * 40)
            print("SQL 结果详情:")
            print("-" * 40)
            for i, result in enumerate(sql_results[:5]):
                if isinstance(result, dict):
                    q = result.get('question', '未知')[:40]
                    sql = result.get('sql', '无')[:60]
                    print(f"  Q{i+1}: {q}...")
                    print(f"      SQL: {sql}...")

    # 打印最终汇总
    total_time = timer.end()

    # 保存结果
    result = {
        "test_time": datetime.now().isoformat(),
        "question": question,
        "stages": timer.stages,
        "total_seconds": total_time,
        "total_minutes": total_time / 60,
        "sub_questions_count": len(sub_questions) if sub_questions else 0,
        "sql_results_count": len(sql_results) if sql_results else 0,
        "report_length": len(report) if report else 0,
    }

    output_file = "test_full_flow_v3_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n结果已保存: {output_file}")

    return result


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("SQL Researcher 完整流程计时测试 v3")
    print("=" * 60)
    
    # 可以通过命令行参数选择测试问题
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        question = SIMPLE_QUESTION
        print("\n使用简单问题测试")
    else:
        question = COMPLEX_QUESTION
        print("\n使用复杂问题测试")
    
    print(f"\n测试问题:\n{question}\n")
    
    asyncio.run(test_full_flow(question))
