"""
Human-in-the-Loop 交互式测试脚本 (修复版)

使用方法:
1. 确保 LangGraph 服务器在运行: cd open_deep_research && langgraph dev
2. 运行此脚本: python interactive_hitl_test.py
3. 输入你的问题
4. 查看问题拆解结果
5. 选择确认(yes)或输入修改建议
"""

import asyncio
import httpx
import os
from datetime import datetime

API_BASE = "http://127.0.0.1:2024"


async def wait_for_interrupt(client, thread_id, run_id):
    """等待 interrupt 或运行结束"""
    for _ in range(120):  # 最多等待4分钟
        await asyncio.sleep(2)
        
        state = await client.get(f'{API_BASE}/threads/{thread_id}/state')
        state_json = state.json()
        
        # 检查是否有 interrupt
        for task in state_json.get('tasks', []):
            if task.get('interrupts'):
                return 'interrupt', task['interrupts'][0].get('value', '')
        
        # 检查运行状态
        run = await client.get(f'{API_BASE}/threads/{thread_id}/runs/{run_id}')
        status = run.json().get('status')
        if status == 'success':
            # 可能已完成
            report = state_json.get('values', {}).get('final_report', '')
            if report:
                return 'success', report
        elif status == 'error':
            return 'error', 'Run failed'
    
    return 'timeout', 'Timeout waiting for response'


async def main():
    async with httpx.AsyncClient(timeout=600.0) as client:
        # 获取 assistant
        a = await client.post(f'{API_BASE}/assistants/search', json={'limit': 10})
        assistant_id = None
        for ast in a.json():
            if ast['name'] == 'SQL Researcher':
                assistant_id = ast['assistant_id']
                break
        
        if not assistant_id:
            print("❌ 找不到 SQL Researcher，请确保 LangGraph 服务器运行中")
            return
        
        print("="*70)
        print("🧪 Human-in-the-Loop 交互式测试 (修复版)")
        print("="*70)
        print()
        
        # 用户输入问题
        question = input("📝 请输入你的问题: ").strip()
        if not question:
            question = "平台上有多少客户和设备？"
        
        print()
        print(f"发送问题: {question}")
        print()
        
        # 创建 thread
        t = await client.post(f'{API_BASE}/threads', json={})
        thread_id = t.json()['thread_id']
        
        # 开始运行
        r = await client.post(
            f'{API_BASE}/threads/{thread_id}/runs',
            json={'assistant_id': assistant_id, 'input': {'messages': [{'role': 'user', 'content': question}]}}
        )
        current_run_id = r.json()['run_id']
        
        print("⏳ 等待系统分解问题...")
        
        while True:
            result_type, result_value = await wait_for_interrupt(client, thread_id, current_run_id)
            
            if result_type == 'interrupt':
                print()
                print("="*70)
                print("🛑 【问题拆解完成，请审核】")
                print("="*70)
                print()
                print(result_value)
                print()
                print("="*70)
                
                # 用户选择
                user_input = input("👉 输入 'yes' 确认，或输入修改建议: ").strip()
                
                if user_input.lower() in ['yes', 'y', 'true', '确认', '是', 'ok']:
                    print()
                    print("✅ 确认继续执行...")
                    
                    # Resume with True
                    resume_r = await client.post(
                        f'{API_BASE}/threads/{thread_id}/runs',
                        json={'assistant_id': assistant_id, 'command': {'resume': True}}
                    )
                    current_run_id = resume_r.json().get('run_id')
                    print(f"Resume Run ID: {current_run_id}")
                    print()
                    print("⏳ 执行中，请耐心等待...")
                    
                    # 继续循环等待完成
                    continue
                    
                else:
                    print()
                    print(f"📝 发送修改建议: {user_input}")
                    print("⏳ 等待重新分解问题...")
                    
                    # Resume with feedback string
                    resume_r = await client.post(
                        f'{API_BASE}/threads/{thread_id}/runs',
                        json={'assistant_id': assistant_id, 'command': {'resume': user_input}}
                    )
                    current_run_id = resume_r.json().get('run_id')
                    print(f"New Run ID: {current_run_id}")
                    
                    # 继续循环等待新的 interrupt
                    continue
            
            elif result_type == 'success':
                print()
                print("="*70)
                print("📊 【最终报告】")
                print("="*70)
                print()
                print(result_value)
                
                # 保存报告
                save_dir = "/Users/jason/Documents/实习/理想实习/FusionSQL/docs/20260109/reports"
                os.makedirs(save_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{save_dir}/report_{timestamp}.md"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# SQL Research 报告\n\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"## 原始问题\n\n{question}\n\n")
                    f.write(f"## 报告内容\n\n{result_value}")
                
                print()
                print(f"💾 报告已保存到: {filename}")
                break
                
            elif result_type == 'error':
                print(f"❌ 错误: {result_value}")
                break
                
            else:
                print(f"⏰ 超时: {result_value}")
                break


if __name__ == "__main__":
    asyncio.run(main())
