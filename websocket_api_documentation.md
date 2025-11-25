# WebSocket 接口文档

## 概述

这是一个基于FastAPI的WebSocket数据查询服务器，提供实时数据库查询功能。服务器通过WebSocket连接接收自然语言查询请求，使用AI模型生成SQL语句并返回查询结果。

## 服务信息

- **服务名称**: 数据查询WebSocket服务器
- **框架**: FastAPI
- **WebSocket连接地址**: `ws://localhost:8000/ws`
- **HTTP服务地址**: `http://localhost:8000`

## 连接方式

### WebSocket端点
```
ws://localhost:8000/ws
```

### 连接示例
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

## 消息格式

### 1. 客户端请求消息

客户端发送的查询请求必须为JSON格式：

```json
{
    "type": "query",
    "query": "用户的自然语言查询内容"
}
```

**字段说明：**
- `type` (string, 必需): 消息类型，固定为 `"query"`
- `query` (string, 必需): 自然语言查询内容，如"一共有多少条数据"

**请求示例：**
```json
{
    "type": "query",
    "query": "查询所有员工信息"
}
```

### 2. 服务端响应消息

#### 2.1 处理状态消息 (文本消息)
在查询处理过程中，服务器会发送多个状态更新消息：

```
正在处理查询请求...
正在调用text2sql模型生成SQL语句...
最终SQL语句: SELECT COUNT(*) FROM WH_MEMBER_T
正在执行SQL查询...
SQL查询成功，结果行数: 150
FLAG_DONE
```

#### 2.2 最终查询结果 (JSON消息)

**成功响应：**
```json
{
    "type": "query_result",
    "status": "success",
    "query": "查询所有员工信息",
    "sql": "SELECT * FROM WH_MEMBER_T",
    "result": [
        {"ID": 1, "NAME": "张三", "DEPT": "技术部", ...},
        {"ID": 2, "NAME": "李四", "DEPT": "市场部", ...}
    ],
    "row_count": 150,
    "timestamp": "2025-11-25T10:30:00.000000"
}
```

**错误响应：**
```json
{
    "type": "query_result",
    "status": "error",
    "query": "查询所有员工信息",
    "error": "SQL语句生成失败",
    "timestamp": "2025-11-25T10:30:00.000000"
}
```

**响应字段说明：**
- `type` (string): 固定为 `"query_result"`
- `status` (string): 查询状态，`"success"` 或 `"error"`
- `query` (string): 原始查询内容
- `sql` (string): 生成的SQL语句（仅成功时包含）
- `result` (array/object): 查询结果数据（仅成功时包含）
- `row_count` (number): 结果行数（仅成功且结果为数组时包含）
- `error` (string): 错误信息（仅失败时包含）
- `timestamp` (string): 响应时间戳，ISO格式

## 处理流程

1. **连接建立**: 客户端连接到 `/ws` 端点
2. **接收查询**: 服务器接收客户端的JSON查询消息
3. **SQL生成**: 使用text2sql模型将自然语言转换为SQL
4. **缩写处理**: 自动处理部门和项目名称缩写
5. **SQL执行**: 执行生成的SQL查询
6. **错误重试**: 如果SQL执行失败，自动使用模型重写SQL
7. **返回结果**: 发送查询结果和完成标志 `FLAG_DONE`

## 错误处理

### 常见错误类型

1. **JSON格式错误**: 客户端发送的消息不是有效JSON
2. **SQL生成失败**: AI模型无法生成有效的SQL语句
3. **SQL执行错误**: 生成的SQL语句执行失败
4. **重写失败**: SQL重写后仍然无法执行

### 错误处理机制

- 服务器会自动尝试重写失败的SQL语句
- 所有错误都会包含详细的错误信息
- 每个请求结束都会发送 `FLAG_DONE` 标志

## 特性功能

### 1. 智能SQL重写
当SQL查询失败时，系统会自动：
- 记录错误信息
- 使用AI模型重写SQL语句
- 重新执行查询
- 返回重写后的结果

### 2. 缩写处理
系统自动处理常见的缩写：
- 部门名称缩写映射
- 项目名称缩写映射

### 3. 实时状态更新
查询过程中会发送多个状态消息，包括：
- 查询处理开始
- SQL生成状态
- SQL执行状态
- 结果行数统计

## 客户端实现示例

### JavaScript/HTML
```html
<!DOCTYPE html>
<html>
<head>
    <title>数据查询客户端</title>
</head>
<body>
    <div id="messages"></div>
    <input type="text" id="queryInput" placeholder="输入查询...">
    <button onclick="sendQuery()">查询</button>

    <script>
        const ws = new WebSocket('ws://localhost:8000/ws');
        const messages = document.getElementById('messages');

        ws.onmessage = function(event) {
            const message = event.data;
            const div = document.createElement('div');
            div.textContent = message;
            messages.appendChild(div);

            if (message === 'FLAG_DONE') {
                console.log('查询完成');
            }
        };

        function sendQuery() {
            const query = document.getElementById('queryInput').value;
            ws.send(JSON.stringify({
                type: "query",
                query: query
            }));
        }
    </script>
</body>
</html>
```

### Python客户端
```python
import asyncio
import websockets
import json

async def query_websocket(query_text):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # 发送查询请求
        request = {
            "type": "query",
            "query": query_text
        }
        await websocket.send(json.dumps(request, ensure_ascii=False))

        # 接收响应
        while True:
            response = await websocket.recv()
            if response == 'FLAG_DONE':
                break
            print(response)

# 使用示例
asyncio.run(query_websocket("一共有多少条数据"))
```

## 依赖要求

- FastAPI
- uvicorn
- websockets
- langchain
- mysql数据库连接

## 注意事项

1. **连接管理**: 客户端需要正确处理WebSocket连接断开的情况
2. **消息解析**: 客户端需要能够解析JSON响应和文本状态消息
3. **编码支持**: 服务器支持UTF-8编码，可以处理中文查询和结果
4. **错误恢复**: 建议客户端实现重连机制以处理网络中断
5. **并发限制**: 根据服务器配置，可能存在并发连接数限制

## 日志记录

服务器会记录详细的日志信息，包括：
- 查询请求内容
- SQL生成过程
- 查询执行结果
- 错误信息
- 连接状态

日志文件位置：`server.log`