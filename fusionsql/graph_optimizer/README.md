# FusionSQL 图论优化模块

> 让 AI 不仅找到"语义相关"的表，还要找到"能 JOIN 起来"的表

---

## 目录

1. [问题背景：为什么需要图优化？](#1-问题背景为什么需要图优化)
2. [解决方案：用外键关系图来筛选](#2-解决方案用外键关系图来筛选)
3. [核心算法详解](#3-核心算法详解)
4. [模块架构](#4-模块架构)
5. [使用指南](#5-使用指南)
6. [配置说明](#6-配置说明)
7. [性能优化](#7-性能优化)
8. [FAQ](#8-faq)

---

## 1. 问题背景：为什么需要图优化？

### 1.1 现有流程的问题

FusionSQL 的 Text-to-SQL 流程是这样的：

```
用户问题 → BGE-M3 检索 → 返回 10-20 张候选表 → LLM 生成 SQL
```

**BGE-M3 检索**用的是语义相似度，它会找到"意思相关"的表。

但这里有个问题：**语义相关 ≠ 结构相关**。

### 1.2 举个例子

假设用户问：`"查询客户张三的所有设备告警"`

BGE 可能返回这些表（按相似度排序）：

| 排名 | 表名 | 语义相关度 | 问题 |
|------|------|-----------|------|
| 1 | `ne_customer` | 0.92 | ✅ 有客户信息 |
| 2 | `ne_alert` | 0.88 | ✅ 有告警信息 |
| 3 | `ne_device` | 0.85 | ✅ 有设备信息 |
| 4 | `log_operation` | 0.82 | ❌ 操作日志，和查询无关 |
| 5 | `sys_user` | 0.80 | ❌ 系统用户表，和客户无关 |
| 6 | `ne_device_extend` | 0.78 | ✅ 设备扩展信息 |

问题来了：
- `log_operation` 和 `sys_user` 语义上沾边，但**和其他表没有外键关系**，根本 JOIN 不起来
- `ne_device_extend` 排名靠后，但它**和 `ne_device` 有外键**，是真正需要的表

### 1.3 这会导致什么？

1. **LLM 生成错误 SQL**：给它一堆不相关的表，它可能瞎 JOIN
2. **浪费 token**：把无用的表 schema 塞给 LLM
3. **准确率下降**：真正需要的表可能被挤出 top-k

---

## 2. 解决方案：用外键关系图来筛选

### 2.1 核心思路

我们在 Neo4j 里存了所有表的外键关系：

```
ne_customer ──IS──> ne_device ──IS──> ne_alert
                        │
                        └──IS──> ne_device_extend
```

- `IS` 关系 = 确定的外键（如 `device.customer_id = customer.id`）
- `MOSTLYIS` 关系 = 推断的外键（通过列名/数据推断）

**图优化的思路**：在 BGE 返回的候选表基础上，用图关系来：
1. **提升**：和其他候选表有外键连接的表
2. **降低**：孤立的、连不上的表

### 2.2 优化前 vs 优化后

```
优化前（纯 BGE）：
ne_customer(0.92) → ne_alert(0.88) → ne_device(0.85) → log_operation(0.82) → sys_user(0.80)

优化后（BGE + 图）：
ne_customer(0.89) → ne_device(0.87) → ne_alert(0.85) → ne_device_extend(0.72) → log_operation(0.45)
                                                                                    ↑
                                                                              分数被压低了
```

`log_operation` 因为和其他表没有外键关系，分数被大幅降低。

---

## 3. 核心算法详解

### 3.1 综合评分公式

我们不是完全抛弃 BGE 分数，而是综合多个因素：

```
最终分数 = 0.70 × BGE分数
         + 0.15 × 个性化PageRank
         + 0.10 × 连通性分数
         + 0.05 × 全局度中心性
```

**为什么 BGE 占 70%？**
- BGE 检索本身很准，图优化只是"微调"
- 如果图权重太高，可能会选一些语义不相关但连接多的表

### 3.2 个性化 PageRank（PPR）

#### 什么是 PageRank？

PageRank 是 Google 发明的算法，用来衡量网页重要性。核心思想：

> 被越多重要页面链接的页面，自己也越重要

用在表关系图上：
> 被越多重要表连接的表，自己也越重要

#### 什么是"个性化" PageRank？

普通 PageRank 计算所有节点的全局重要性。但我们的场景不同：

- 我们只关心**和当前查询相关**的表
- BGE 已经告诉我们哪些表可能相关

所以我们用 **个性化 PageRank**：

```
以 BGE 候选表为"种子节点"，从它们出发计算 PageRank
```

**类比**：
- 普通 PageRank：计算整个互联网所有网站的重要性
- 个性化 PageRank：只计算"和我的搜索相关"的网站的重要性

#### 算法流程

```python
1. 初始化：给每个 BGE 候选表分配相等的初始分数
2. 迭代传播：每轮把分数沿着外键关系传递给邻居
3. 阻尼：每次传播保留 15% 的分数回到种子节点（防止分数跑太远）
4. 收敛：分数稳定后停止
```

**效果**：
- 种子节点（BGE 候选）分数高
- 和种子节点直接相连的表分数较高
- 离种子节点远的表分数低
- 孤立的表分数很低

### 3.3 连通性分数

这个更直观：

```
连通性分数 = 该表直接连接的 TOP 候选表数量 / TOP 候选表总数
```

**例子**：

TOP 5 候选表：`ne_customer`, `ne_device`, `ne_alert`, `ne_vendor`, `ne_area`

| 表 | 直接连接的 TOP 表 | 连通性分数 |
|---|------------------|-----------|
| `ne_device` | customer, alert, vendor | 3/5 = 0.6 |
| `log_operation` | 无 | 0/5 = 0.0 |

### 3.4 全局度中心性

**度 = 一个表有多少条外键关系**

```
ne_device: 连接 15 张表 → 度 = 15
log_operation: 连接 2 张表 → 度 = 2
```

度高的表通常是"核心表"（如 `ne_device`），在 JOIN 时更可能被用到。

**归一化**：`归一化度 = 该表的度 / 最大度`

### 3.5 三种优化策略

| 策略 | 适用场景 | 原理 |
|------|---------|------|
| `hybrid`（推荐） | 通用场景 | 综合 BGE + PPR + 连通性 + 度 |
| `steiner_tree` | 明确需要多表 JOIN | 找连接所有高分表的最小子图 |
| `connectivity` | 过滤孤立表 | 优先保留最大连通分量中的表 |

#### Steiner Tree 策略

**问题**：给定几个"必须包含"的表，找到连接它们的最小表集合

**类比**：你要从 A 地开车到 B 地和 C 地，怎么走最短路线？

```
候选表：ne_customer, ne_device, ne_alert

Steiner Tree 找到：
ne_customer ── ne_device ── ne_alert
     └─────────────┘
     （如果它们直接相连）

或者：
ne_customer ── ne_contract ── ne_device ── ne_alert
                    ↑
              中间节点（不在原候选中，但需要用来连接）
```

---

## 4. 模块架构

### 4.1 文件结构

```
fusionsql/graph_optimizer/
│
├── config.py          # 配置文件
│   ├── Neo4j 连接信息
│   ├── 关系权重 (IS=1.0, MOSTLYIS=0.2)
│   └── 算法参数
│
├── neo4j_client.py    # Neo4j 数据库客户端
│   ├── get_table_relationships()  # 获取表间关系
│   ├── get_connected_tables()     # BFS 扩展邻居
│   └── get_table_degrees()        # 获取度信息
│
├── graph_cache.py     # 缓存模块
│   ├── 预计算全局 PageRank
│   ├── 预计算全局度中心性
│   └── 缓存到本地文件
│
├── algorithms.py      # 图算法实现
│   ├── TableGraph 类           # 图数据结构
│   ├── personalized_pagerank() # 个性化 PageRank
│   ├── find_steiner_subgraph() # Steiner 树
│   ├── compute_connectivity_score()  # 连通性评分
│   └── find_connected_components()   # 连通分量
│
├── optimizer.py       # 核心优化器
│   ├── optimize()              # 主入口
│   ├── _hybrid_selection()     # hybrid 策略
│   ├── _steiner_selection()    # steiner_tree 策略
│   └── _connectivity_selection() # connectivity 策略
│
└── __init__.py        # 模块导出
```

### 4.2 数据流

```
                    ┌─────────────────┐
                    │   Neo4j 图数据库  │
                    │  (表外键关系)     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │ 离线预计算 │       │ 在线查询  │       │ 在线查询  │
   │ 全局指标   │       │ 表间关系  │       │ 邻居表    │
   └────┬─────┘       └────┬─────┘       └────┬─────┘
        │                  │                  │
        ▼                  ▼                  ▼
   ┌──────────┐       ┌──────────────────────────┐
   │ 本地缓存  │──────>│      GraphOptimizer      │
   │ .pkl 文件 │       │                          │
   └──────────┘       │  1. 构建子图              │
                      │  2. 计算 PPR              │
                      │  3. 计算连通性            │
                      │  4. 综合评分              │
                      │  5. 排序返回              │
                      └─────────────┬────────────┘
                                    │
                                    ▼
                         ┌─────────────────┐
                         │  优化后的候选表  │
                         │  [(表名, 分数)]  │
                         └─────────────────┘
```

### 4.3 Pipeline 集成点

```python
# fusionsql/pipeline.py

class TextToSQL:
    def run(self, question):
        # Step 1: BGE 检索
        retrieved = self.retriever.retrieve(question, top_k=15)
        # 返回: [("ne_device", 0.92), ("ne_alert", 0.88), ...]

        # Step 1.5: 图优化 ← 新增！
        if self.graph_optimizer:
            retrieved = self.graph_optimizer.optimize(retrieved)
        # 返回: [("ne_device", 0.89), ("ne_customer", 0.87), ...]
        # 顺序可能变化，孤立表分数降低

        # Step 2: Entity Linking
        # Step 3: SQL 生成
        ...
```

---

## 5. 使用指南

### 5.1 安装依赖

```bash
pip install neo4j
```

### 5.2 基本使用

```python
from fusionsql import TextToSQL

# 启用图优化
pipeline = TextToSQL(
    enable_graph_optimizer=True,        # 开启图优化
    graph_optimizer_strategy="hybrid",  # 使用 hybrid 策略（推荐）
)

# 正常使用
sql = pipeline.run("查询客户张三的设备告警")
```

### 5.3 查看优化效果

```python
# 使用 run_with_details 查看详细信息
result = pipeline.run_with_details("查询客户张三的设备告警")

print("检索到的表:", result["retrieved_tables"])
print("表分数:", result["table_scores"])
print("是否经过图优化:", result["graph_optimized"])
print("生成的 SQL:", result["sql"])
```

### 5.4 预计算缓存（推荐）

为了提升性能，建议预先计算全局图指标：

```bash
python scripts/precompute_graph_cache.py
```

这会：
1. 连接 Neo4j
2. 计算所有表的全局 PageRank 和度中心性
3. 保存到 `fusionsql/graph_optimizer/cache/global_metrics.pkl`

预计算后，在线查询只需计算子图的 PPR，速度更快。

### 5.5 单独使用优化器

```python
from fusionsql.graph_optimizer import GraphOptimizer

# 创建优化器
optimizer = GraphOptimizer()

# BGE 检索结果
candidates = [
    ("ne_device", 0.92),
    ("ne_alert", 0.88),
    ("log_operation", 0.82),
    ("sys_user", 0.80),
]

# 优化
optimized = optimizer.optimize(candidates, strategy="hybrid")

print("优化后:", optimized)
# 输出: [("ne_device", 0.89), ("ne_alert", 0.85), ...]
```

### 5.6 运行测试

```bash
# 运行所有测试
python -m pytest tests/test_graph_optimizer.py -v

# 只运行算法测试（不需要 Neo4j）
python -m pytest tests/test_graph_optimizer.py -v -k "not Integration"
```

---

## 6. 配置说明

### 6.1 Neo4j 连接

```python
# fusionsql/graph_optimizer/config.py

NEO4J_URI = "neo4j://172.31.24.111:7689"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
```

也可以通过环境变量覆盖：

```bash
export NEO4J_URI="neo4j://your-host:7687"
export NEO4J_USER="your-user"
export NEO4J_PASSWORD="your-password"
```

### 6.2 关系权重

```python
RELATION_WEIGHTS = {
    "IS": 1.0,        # 精确外键，权重最高
    "MOSTLYIS": 0.2,  # 推断外键，权重较低
}
```

**为什么 MOSTLYIS 权重低？**

- `IS` 关系是确定的外键（51条）
- `MOSTLYIS` 是推断的（2678条），可能有误报
- 如果给 MOSTLYIS 同等权重，会引入噪声

### 6.3 评分权重

```python
WEIGHTS = {
    "bge": 0.70,           # BGE 检索分数
    "ppr": 0.15,           # 个性化 PageRank
    "connectivity": 0.10,  # 子图连通性
    "degree": 0.05,        # 全局度中心性
}
```

**调参建议**：

| 场景 | 调整方向 |
|------|---------|
| BGE 检索已经很准 | 提高 `bge` 权重 (0.75-0.80) |
| 表之间 JOIN 关系很重要 | 提高 `ppr` + `connectivity` 权重 |
| 有很多噪声表 | 提高 `connectivity` 权重 |

### 6.4 表数量配置

```python
TARGET_TABLES = 8   # 目标返回表数量
MIN_TABLES = 5      # 最少返回表数量
MAX_TABLES = 10     # 最多返回表数量
```

---

## 7. 性能优化

### 7.1 优化策略

| 优化点 | 方案 | 效果 |
|--------|------|------|
| 全局指标计算 | 离线预计算，启动时加载 | 节省每次查询 2-3 秒 |
| Neo4j 查询 | 一次查询获取子图，避免多次往返 | 减少网络延迟 |
| 图计算范围 | 只计算候选表 + 1-hop 邻居 | 避免全图计算 |
| MOSTLYIS 噪声 | 带权处理 (0.2) | 减少误判 |

### 7.2 延迟初始化

```python
# 默认延迟初始化，第一次查询时才连接 Neo4j
optimizer = GraphOptimizer(lazy_init=True)  # 默认

# 如果想启动时就连接（预热）
optimizer = GraphOptimizer(lazy_init=False)
```

### 7.3 典型耗时

| 步骤 | 首次查询 | 后续查询 |
|------|---------|---------|
| Neo4j 连接 | 100-200ms | 0ms（复用连接） |
| 加载缓存 | 50-100ms | 0ms（已加载） |
| 子图构建 | 50-100ms | 50-100ms |
| PPR 计算 | 10-30ms | 10-30ms |
| 评分排序 | <5ms | <5ms |
| **总计** | **200-400ms** | **60-130ms** |

---

## 8. FAQ

### Q1: 图优化会不会误删重要的表？

**不会**。因为：
1. BGE 分数占 70%，图特征只占 30%
2. 即使一个表和其他表没有外键，只要 BGE 分数够高，它仍会被保留
3. 我们是"重排序"而非"过滤"

### Q2: 没有 Neo4j 能用吗？

可以，但图优化会被跳过：

```python
pipeline = TextToSQL(enable_graph_optimizer=True)
# 如果 Neo4j 连不上，会自动降级到纯 BGE 检索
```

### Q3: MOSTLYIS 关系是怎么来的？

这是通过分析数据库 schema 推断的：
- 列名相似（如 `device_id` 和 `id`）
- 数据类型匹配
- 值域有交集

比 `IS`（确定的外键约束）准确率低，所以权重也低。

### Q4: 为什么不直接用 Neo4j 的 PageRank？

Neo4j 有内置 PageRank，但：
1. **全局 vs 个性化**：Neo4j 算的是全局 PageRank，我们需要个性化的
2. **实时性**：我们需要根据当前候选表实时计算，不是预先算好的
3. **灵活性**：自己实现可以调参、融合其他因素

### Q5: Steiner Tree 策略什么时候用？

当你的查询**明确需要多表 JOIN** 时：

```
"查询客户张三在项目A中使用设备B产生的告警"
     ↑         ↑         ↑           ↑
  customer  project    device      alert
```

这种情况，Steiner Tree 会找到连接这四张表的最短路径，可能比 hybrid 更精准。

### Q6: 如何验证优化效果？

```python
# 对比实验
from fusionsql import TextToSQL

# 不用图优化
pipeline_baseline = TextToSQL(enable_graph_optimizer=False)

# 用图优化
pipeline_optimized = TextToSQL(enable_graph_optimizer=True)

question = "查询客户张三的设备告警"

result_baseline = pipeline_baseline.run_with_details(question)
result_optimized = pipeline_optimized.run_with_details(question)

print("Baseline 表:", result_baseline["retrieved_tables"])
print("Optimized 表:", result_optimized["retrieved_tables"])
```

### Q7: 遇到问题怎么调试？

开启日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 这样会打印：
# - Neo4j 查询详情
# - PPR 收敛过程
# - 每个表的各项分数
```

---

## 附录：Neo4j 数据结构

### 节点类型

| 类型 | 数量 | 说明 |
|------|------|------|
| Database | 1 | 数据库节点 |
| Table | 343 | 表节点 |
| Column | 3348 | 列节点 |

### 关系类型

| 类型 | 数量 | 说明 |
|------|------|------|
| IS | 51 | 精确外键关系 |
| MOSTLYIS | 2678 | 推断外键关系 |

### 示例查询

```cypher
-- 查看某表的所有外键关系
MATCH (t:Table {name: 'ne_device'})-[r:IS|MOSTLYIS]-(other:Table)
RETURN t.name, type(r), other.name

-- 查看两表之间的最短路径
MATCH path = shortestPath(
    (t1:Table {name: 'ne_customer'})-[:IS|MOSTLYIS*]-(t2:Table {name: 'ne_alert'})
)
RETURN path
```

---

## 总结

图优化模块解决了一个核心问题：**让 AI 选出的表不仅语义相关，还要能 JOIN 起来**。

通过结合 BGE 语义检索和 Neo4j 图关系，我们实现了：

1. ✅ 保留语义相关的表（BGE 70%）
2. ✅ 提升结构连通的表（图特征 30%）
3. ✅ 降低孤立噪声表（PPR + 连通性）
4. ✅ 离线预计算 + 在线微调（性能优化）

最终目标：**提高 Text-to-SQL 的准确率**。
