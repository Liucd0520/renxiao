# SQL Researcher

基于 LangGraph 的智能数据分析助手，集成 FusionSQL 实现自然语言到 SQL 的查询生成和执行。

## 功能特点

- 🔍 **智能问题拆解** - 将复杂问题自动分解为可执行的子问题
- 👤 **Human-in-the-Loop** - 用户可审核和修改问题拆解结果
- 🔗 **FusionSQL 集成** - 使用 BGE-M3 向量检索 + LLM 生成 SQL
- ⚡ **并行化优化** - 跳过 Supervisor 直接并行执行，性能提升 75%
- 📊 **自动报告生成** - 汇总 SQL 查询结果生成结构化 Markdown 报告

---

## 快速开始

### 1. 安装依赖

```bash
cd FusionSQL
pip install langgraph langchain langchain-core flask httpx markdown
```

### 2. 启动 LangGraph 服务器

```bash
cd FusionSQL
langgraph dev --no-browser -c sql_researcher/langgraph.json
```

服务器启动后 API 运行在 `http://127.0.0.1:2024`

### 3. 启动 Web UI（新终端）

```bash
cd FusionSQL
python sql_researcher/tests/web_ui.py
```

打开浏览器访问：**http://127.0.0.1:5001**

---

## 目录结构

```
FusionSQL/
├── fusionsql/                 # FusionSQL 核心引擎
│   ├── pipeline.py            # 主流程
│   ├── sql_generator.py       # SQL 生成
│   └── ...
├── sql_researcher/            # LangGraph Agent
│   ├── sql_deep_researcher.py # 主流程 + 节点定义
│   ├── sql_state.py           # 状态定义
│   ├── sql_configuration.py   # 配置项
│   ├── sql_prompts.py         # Prompt 模板
│   ├── tools/
│   │   ├── fusionsql_tool.py  # FusionSQL 工具
│   │   └── sql_executor_tool.py
│   ├── tests/
│   │   ├── web_ui.py          # Web 界面
│   │   └── ...
│   └── langgraph.json         # LangGraph 配置
└── docs/                      # 文档和报告
```

---

## 性能优化

| 版本 | 复杂问题处理时间 | 提升 |
|-----|----------------|------|
| 优化前 (Supervisor 模式) | 9.5 分钟 | 基准 |
| 优化后 (并行跳过 Supervisor) | **2.5 分钟** | **~75%** |

详见 `docs/20260113/performance_optimization_report.md`

---

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `enable_decomposition_review` | 是否启用人工审核问题拆解 | `True` |
| `enable_parallel_bypass` | 跳过 Supervisor 直接并行执行 | `True` |
| `max_concurrent_research_units` | 最大并行研究数 | `10` |

---

## 测试问题示例

**简单问题**：
```
现在平台上有多少家客户和多少台设备
```

**复杂问题**：
```
我想了解一下咱们平台的整体情况。客户数量和设备数量大概是多少？
上个月设备的上下线情况怎么样？另外，有些设备好像一直是down的状态，
能不能看看哪些设备down了超过3个月，顺便告诉我是哪个客户的。
```
