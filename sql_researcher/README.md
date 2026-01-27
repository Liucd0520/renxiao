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

> **重要**：所有命令都必须在 `FusionSQL` 根目录下执行！

### 1. 进入项目目录

```bash
cd FusionSQL
```

### 2. 安装依赖

```bash
source .venv/bin/activate
pip install langchain langgraph langchain-core langchain-openai flask httpx markdown langgraph-cli langgraph-api python-dotenv
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key 和 API Base URL
```

`.env` 文件内容示例：

```
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=http://your-api-endpoint/v1
```

### 4. 启动 LangGraph 服务器

```bash
source .venv/bin/activate
langgraph dev --no-browser
```

服务器启动后 API 运行在 `http://127.0.0.1:2024`

### 5. 启动 Web UI（新终端）

打开另一个终端，同样进入 FusionSQL 目录：

```bash
cd FusionSQL
source .venv/bin/activate
python sql_researcher/tests/web_ui.py
```

打开浏览器访问：**http://127.0.0.1:5001**

---

## 目录结构

```
FusionSQL/                     # ← 必须在这个目录下运行命令！
├── fusionsql/                 # FusionSQL 核心引擎
├── sql_researcher/            # LangGraph Agent
│   ├── sql_deep_researcher.py # 主流程
│   ├── sql_configuration.py   # 配置项
│   ├── tools/                 # 工具（FusionSQL、SQL执行器）
│   └── tests/
│       └── web_ui.py          # Web 界面
├── langgraph.json             # LangGraph 配置
├── .env.example               # 环境变量模板
└── docs/                      # 文档和报告
```

---

## 性能优化

| 版本   | 复杂问题处理时间   | 提升           |
| ------ | ------------------ | -------------- |
| 优化前 | 9.5 分钟           | 基准           |
| 优化后 | **2.5 分钟** | **~75%** |

---

## 常见问题

**Q: `langgraph.json` 找不到？**
A: 确保已经 `cd` 进入 FusionSQL 根目录后再运行命令

**Q: `OPENAI_API_KEY` 未设置？**
A: 复制 `.env.example` 为 `.env` 并填入 API 配置

**Q: 端口被占用？**
A: 用 `lsof -i :2024` 查找并 `kill` 占用进程



## 测试问题示例

**简单问题**：

```
现在平台上有多少家客户和多少台设备
```

**复杂问题**（测试 HITL 功能）：

```
我想了解一下咱们平台的整体情况。客户数量和设备数量大概是多少？上个月设备的上下线情况怎么样？另外，有些设备好像一直是down的状态，能不能看看哪些设备down了超过3个月，顺便告诉我是哪个客户的。
```
