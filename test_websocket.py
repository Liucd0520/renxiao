import asyncio
import websockets
import json

async def test_websocket():
    """
    测试WebSocket接口功能 - 简化版支持流式输出
    """
    uri = "ws://localhost:8000/ws"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")

            # 测试查询
            test_queries = [
                "一共有多少条数据",
                "显示所有部门名称"
            ]

            for i, query in enumerate(test_queries, 1):
                print(f"\n📝 测试查询 {i}: {query}")
                print("=" * 60)

                # 发送查询消息
                message = {
                    "type": "query",
                    "query": query
                }

                await websocket.send(json.dumps(message, ensure_ascii=False))
                print(f"📤 发送查询请求")

                # 接收流式响应
                message_count = 0
                while True:
                    response = await websocket.recv()
                    message_count += 1

                    # 检查是否是完成标记
                    if response == 'FLAG_DONE':
                        print(f"\n✅ 查询完成 (共收到 {message_count} 条消息)")
                        break

                    # 尝试解析JSON，如果不是JSON则直接显示
                    try:
                        data = json.loads(response)

                        if isinstance(data, dict):
                            if data.get("type") == "query_result":
                                print(f"\n📊 查询结果:")
                                if data.get("status") == "success":
                                    print(f"  ✅ 状态: 成功")
                                    print(f"  📈 返回记录数: {data.get('row_count', 'N/A')}")
                                    print(f"  🔍 SQL语句: {data.get('sql', 'N/A')}")

                                    # 显示结果摘要
                                    result = data.get('result', [])
                                    if isinstance(result, list) and len(result) > 0:
                                        print(f"  📋 结果预览: {json.dumps(result[:2], ensure_ascii=False, indent=2)}")
                                        if len(result) > 2:
                                            print(f"  ... 还有 {len(result) - 2} 条记录")
                                    else:
                                        print(f"  📋 完整结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                                else:
                                    print(f"  ❌ 状态: 失败")
                                    print(f"  💥 错误信息: {data.get('error', 'N/A')}")
                            else:
                                print(f"  📄 消息 {message_count}: {json.dumps(data, ensure_ascii=False)}")
                        else:
                            print(f"  📄 消息 {message_count}: {json.dumps(data, ensure_ascii=False)}")
                    except json.JSONDecodeError:
                        # 不是JSON格式，直接显示
                        print(f"  💬 消息 {message_count}: {response}")

                print("=" * 60)

            print("\n🎉 所有测试完成")

    except websockets.exceptions.ConnectionRefused:
        print("❌ 连接被拒绝，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🚀 开始WebSocket功能测试...")
    print("📍 服务器地址: ws://localhost:8000/ws")
    print("📝 此测试将展示流式输出功能")
    print("🔧 仅支持 type: 'query' 的查询请求")
    print("-" * 50)

    asyncio.run(test_websocket())