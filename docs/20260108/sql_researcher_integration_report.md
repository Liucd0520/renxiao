# FusionSQL + Open Deep Research 集成技术报告

**日期**: 2026-01-08
**作者**: Claude Code
**项目**: SQL Researcher - FusionSQL 与 Open Deep Research 深度集成

---

## 1. 项目概述

### 1.1 目标
将 FusionSQL（Text-to-SQL 系统）与 Open Deep Research（深度研究代理）整合，创建一个可以：
1. 接收用户复杂的数据库查询问题
2. 自动拆分成多个子问题
3. 使用 FusionSQL 生成 SQL 并执行
4. 生成结构化的研究报告

### 1.2 架构设计

```
用户输入复杂问题
    ↓
[clarify_with_user] - 澄清问题（可选）
    ↓
[decompose_question] - 拆分成子问题
    ↓
[sql_research_supervisor] - 调度并行研究
    ↓
[sql_researcher] × N（并行）
    ├─ fusionsql_tool - 生成 SQL（BGE-M3 检索 + LLM）
    └─ execute_sql_tool - 执行 SQL
    ↓
[compress_sql_research] - 压缩结果
    ↓
[final_sql_report] - 生成报告
```

---

## 2. 核心问题与解决方案

### 2.1 问题描述

在使用 vLLM 部署的 Qwen 模型（Qwen2.5-Coder-32B-Instruct）时，发现模型不支持 OpenAI 标准的函数调用（Function Calling）格式。

**vLLM 服务配置**:
- Endpoint: `http://172.31.24.112:33080/v1`
- Model: `Qwen2.5-Coder-32B-Instruct`
- 未启用 `--enable-auto-tool-choice` 和 `--tool-call-parser` 参数

**症状**:
当使用 LangChain 的 `bind_tools()` 时，模型的响应：
- `response.tool_calls` 始终为空列表 `[]`
- 工具调用信息被输出到 `response.content` 中

**模型实际输出格式**:
```
# 格式 1: <tools> 标签
<tools>
{"name": "conduct_sql_research", "arguments": {"research_topic": "统计客户数量"}}
</tools>

# 格式 2: <C> 标签
<C>
{"name": "SQLResearchComplete", "arguments": {"summary": "研究完成"}}
</C>

# 格式 3: 原始 JSON
{"name": "fusionsql_query", "arguments": {"question": "..."}}
```

### 2.2 解决方案

创建自定义的工具调用解析器 `parse_qwen_tool_calls()`，在模型响应后解析 content 中的工具调用，并注入到 `AIMessage.tool_calls` 中。

**解析器核心逻辑**:

```python
def parse_qwen_tool_calls(response: AIMessage) -> AIMessage:
    """解析 Qwen 模型的自定义工具调用格式"""

    if response.tool_calls:
        # 已有工具调用，无需解析
        return response

    content = response.content
    tool_calls = []

    # 方法 1: 解析 <tools>, <C>, <tool> 标签格式
    for tag in ["tools", "C", "tool"]:
        if f"<{tag}>" in content:
            pattern = rf'<{tag}>\s*(.*?)\s*</{tag}>'
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                parsed = _parse_json_tool_call(match.strip())
                if parsed:
                    tool_calls.extend(parsed)

    # 方法 2: 解析原始 JSON 格式
    if not tool_calls and content.strip().startswith('{'):
        parsed = _parse_json_tool_call(content.strip())
        if parsed:
            tool_calls.extend(parsed)

    # 方法 3: 在内容中查找 JSON 对象
    if not tool_calls:
        json_pattern = r'\{[^{}]*"name"\s*:\s*"[^"]+"\s*[^{}]*\}'
        matches = re.findall(json_pattern, content)
        for match in matches:
            parsed = _parse_json_tool_call(match)
            if parsed:
                tool_calls.extend(parsed)

    if tool_calls:
        return AIMessage(
            content=clean_content,
            tool_calls=tool_calls,
            id=response.id
        )

    return response
```

**使用位置**:
- `sql_supervisor()` 节点 - 解析 Supervisor 的工具调用
- `sql_researcher()` 节点 - 解析 Researcher 的工具调用

---

## 3. 文件结构与修改

### 3.1 新增文件

```
open_deep_research/
  src/
    sql_researcher/                    # 新增包
      __init__.py
      sql_deep_researcher.py           # 主工作流 + 工具调用解析器
      sql_configuration.py             # 配置类
      sql_state.py                     # 状态定义
      sql_prompts.py                   # Prompt 模板
      tools/
        __init__.py
        fusionsql_tool.py              # FusionSQL 工具封装
        sql_executor_tool.py           # SQL 执行工具
```

### 3.2 修改的配置文件

**langgraph.json**:
```json
{
  "graphs": {
    "Deep Researcher": "./src/open_deep_research/deep_researcher.py:deep_researcher",
    "SQL Researcher": "./src/sql_researcher/sql_deep_researcher.py:sql_researcher"
  }
}
```

**pyproject.toml**:
```toml
packages = ["open_deep_research", "sql_researcher", "legacy", "tests"]

[tool.setuptools.package-dir]
"sql_researcher" = "src/sql_researcher"
```

---

## 4. 关键代码

### 4.1 FusionSQL 工具封装

```python
# tools/fusionsql_tool.py
FUSIONSQL_PATH = "/Users/jason/Documents/实习/理想实习/FusionSQL"

@tool(description="将自然语言问题转换为 SQL")
def fusionsql_query(question: str, top_k: int = 10) -> str:
    pipeline = get_fusionsql_pipeline()
    result = pipeline.run_with_details(question, top_k=top_k)

    return f"""
## SQL Query Generated
**Question:** {result['question']}
**Top Retrieved Tables:** {result['retrieved_tables'][:5]}
**Generated SQL:**
```sql
{result['sql']}
```
"""
```

### 4.2 SQL 执行工具

```python
# tools/sql_executor_tool.py
DEFAULT_DB_CONFIG = {
    "host": "172.31.26.206",
    "port": 3306,
    "user": "ai_test",
    "password": "Netcare@13579",
    "database": "netcaredb_ai",
}

@tool(description="执行 SQL 查询")
def execute_sql(sql: str, max_rows: int = 100) -> str:
    # 安全检查 - 只允许 SELECT
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed"

    # 执行查询并返回 Markdown 表格
    ...
```

### 4.3 工作流节点

```python
async def sql_supervisor(state, config):
    """Supervisor 协调 SQL 研究"""
    response = await research_model.ainvoke(supervisor_messages)

    # 关键: 解析 Qwen 的工具调用格式
    response = parse_qwen_tool_calls(response)

    return Command(
        goto="sql_supervisor_tools",
        update={"supervisor_messages": [response]}
    )
```

---

## 5. 测试验证

### 5.1 工具调用解析测试

**测试输入**:
```
<tools>
{"name": "conduct_sql_research", "arguments": {"research_topic": "现在平台上有多少家客户"}}
</tools>
```

**解析结果**:
```python
[{
    'name': 'conduct_sql_research',
    'args': {'research_topic': '现在平台上有多少家客户'},
    'id': 'call_0950f5b5',
    'type': 'tool_call'
}]
```

### 5.2 端到端测试

**测试问题**: "现在平台上有多少家客户"

**执行流程**:
1. `decompose_question` - 识别为简单问题，无需拆分
2. `sql_supervisor` - 调用 `ConductSQLResearch` 工具
3. `sql_researcher` - 调用 `fusionsql_query` 生成 SQL
4. `sql_researcher` - 调用 `execute_sql` 执行查询
5. `compress_sql_research` - 压缩研究结果
6. `final_sql_report` - 生成最终报告

**生成的 SQL**:
```sql
SELECT COUNT(*) FROM t_bz_config_customer;
```

**查询结果**:
```
| COUNT(*) |
|----------|
|       150|
```

**最终报告**:
```markdown
## 客户数量统计报告

### 问题解答
现在平台上有 150 家客户。

### 使用的 SQL 查询
SELECT COUNT(*) FROM t_bz_config_customer;
```

---

## 6. 配置说明

### 6.1 环境变量 (.env)

```bash
OPENAI_API_KEY=yfzx202510
OPENAI_API_BASE=http://172.31.24.112:33080/v1
```

### 6.2 SQLConfiguration 默认配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| research_model | openai:Qwen2.5-Coder-32B-Instruct | 研究模型 |
| allow_clarification | False | 是否允许澄清问题 |
| max_concurrent_research_units | 3 | 最大并行研究员数 |
| max_researcher_iterations | 5 | 最大研究迭代次数 |
| db_host | 172.31.26.206 | 数据库主机 |
| db_name | netcaredb_ai | 数据库名称 |

---

## 7. 启动与使用

### 7.1 启动服务

```bash
cd /Users/jason/Documents/实习/理想实习/open_deep_research
source venv/bin/activate
langgraph dev --no-browser
```

### 7.2 API 调用

```bash
# 创建线程
curl -X POST http://127.0.0.1:2024/threads -H "Content-Type: application/json" -d '{}'

# 运行 SQL Researcher
curl -X POST http://127.0.0.1:2024/threads/{thread_id}/runs \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "SQL Researcher",
    "input": {
      "messages": [{"role": "user", "content": "现在平台上有多少家客户"}]
    }
  }'
```

---

## 8. 总结

### 8.1 解决的问题

1. **Qwen 模型工具调用格式不兼容** - 通过自定义解析器解决
2. **FusionSQL 集成** - 封装为 LangGraph 工具
3. **复杂问题拆分** - Supervisor-Researcher 架构
4. **端到端数据库查询** - 从自然语言到 SQL 执行到报告生成

### 8.2 架构优势

- **模块化**: FusionSQL、SQL执行、报告生成各自独立
- **可扩展**: 支持并行研究，可配置参数
- **兼容性**: 适配不支持标准工具调用的模型

### 8.3 后续优化方向

1. 支持更复杂的问题拆分和依赖关系处理
2. 添加 SQL 结果缓存
3. 优化报告模板
4. 支持更多模型的工具调用格式
