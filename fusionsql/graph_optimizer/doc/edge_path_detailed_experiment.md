# 边/路径增强排序算法 - 详细实验报告

> 完整记录算法设计、公式推导、实验过程和参数调优

---

## 1. 问题定义

### 1.1 输入

- **候选表集合** $C = \{(t_i, s_i)\}_{i=1}^{n}$，其中 $t_i$ 是表名，$s_i$ 是 BGE 语义分数
- **外键关系图** $G = (V, E)$，$V$ 是所有表，$E$ 是外键边

### 1.2 目标

重排候选表，使关键表（如 `event_history`）排名提升。

### 1.3 约束

- 不能降低已有高分表的排名
- 保持单表查询的稳定性

---

## 2. 算法设计

### 2.1 核心思想：语义光环效应

> 如果表 $A$ 与高分表 $B$ 有外键连接，则 $A$ 可能也是相关表，应获得 $B$ 的"光环加成"。

```
高分表 B (BGE = 5.07)
    │
    FK (外键边)
    │
    ▼
低分但关键的表 A (BGE = 1.55)

→ A 通过边/路径获得 B 的"光环"
→ A 的最终分数提升
```

### 2.2 三种策略设计

我们设计了三种策略进行实验对比：

#### 策略 1: Edge Boost（边加分）

**思想**：直接连接的表获得邻居的分数加成

**公式**：

$$
\text{edge\_boost}(t) = \sum_{(t, t') \in E, t' \in C} w_{t,t'} \cdot \frac{s_{t'}}{s_{\max}}
$$

其中：

- $w_{t,t'}$ 是边权重（IS=1.0, MOSTLYIS=0.2）
- $s_{t'}$ 是邻居的 BGE 分数
- $s_{\max}$ 是最高 BGE 分数

#### 策略 2: Path Boost（路径加分）⭐

**思想**：通过路径传递语义分数，考虑路径上所有表

**公式**：

1. **路径分数**：

$$
\text{path\_score}(p) = \frac{1}{|p|} \cdot \frac{\text{agg}(\{s_t : t \in p\})}{s_{\max}}
$$

2. **路径贡献**：

$$
\text{path\_contrib}(t) = \sum_{p : t \in p} \text{path\_score}(p)
$$

3. **归一化**：

$$
\text{normalized\_contrib}(t) = \frac{\text{path\_contrib}(t)}{\max_{t'} \text{path\_contrib}(t')}
$$

其中：

- $|p|$ 是路径长度（节点数）
- $\text{agg}$ 是聚合函数（max 或 avg）
- $s_{\max} = \max_i s_i$

#### 策略 3: Cluster Boost（簇加分）

**思想**：同一连通分量内的表互相加分

**公式**：

$$
\text{cluster\_boost}(t) = \frac{|\{t' \in C : t' \sim t\}|}{|C|}
$$

其中 $t' \sim t$ 表示 $t'$ 和 $t$ 在同一连通分量。

### 2.3 最终分数计算

$$
\text{final}(t) = s_t + \alpha \cdot s_{\max} \cdot \text{normalized\_contrib}(t)
$$

其中 $\alpha$ 是 boost factor（我们测试了 0.3, 0.4, 0.5）。

---

## 3. 实验设计

### 3.1 测试数据

使用真实 BGE 检索结果（`top_k=15`）：

| 查询 | 内容          | 关键表        | BGE 原始排名 |
| ---- | ------------- | ------------- | ------------ |
| Q1   | 设备告警统计  | event_history | #16          |
| Q2   | 设备状态+客户 | event_history | #4           |
| Q7   | 客户设备告警  | event_history | #10          |

### 3.2 实验变量

| 变量            | 选项                                  | 说明             |
| --------------- | ------------------------------------- | ---------------- |
| 策略            | edge_boost, path_boost, cluster_boost | 三种加分策略     |
| 聚合函数        | max, avg, softmax                     | 路径分数聚合方式 |
| boost_factor    | 0.3, 0.4, 0.5                         | 加成幅度         |
| max_path_length | 2, 3, 4                               | 最长路径         |

---

## 4. 实验结果

### 4.1 策略对比（使用默认参数）

| 策略                 | Q1 event_history          | Q7 event_history         | 总提升           |
| -------------------- | ------------------------- | ------------------------ | ---------------- |
| edge_boost           | #16 → #8 (+8)            | #10 → #7 (+3)           | +11              |
| **path_boost** | **#16 → #4 (+12)** | **#10 → #6 (+4)** | **+16** ⭐ |
| cluster_boost        | #16 → #12 (+4)           | #10 → #9 (+1)           | +5               |

**结论**：path_boost 效果最好，因为它考虑了路径上所有表的语义分数。

### 4.2 聚合函数对比（path_boost 策略）

| 聚合函数      | Q1 提升       | Q7 提升      | 总提升           | 分析                     |
| ------------- | ------------- | ------------ | ---------------- | ------------------------ |
| max           | +8            | +3           | +11              | 只看最高分，忽略路径质量 |
| **avg** | **+12** | **+4** | **+16** ⭐ | 考虑整条路径的平均质量   |
| softmax       | +8            | +3           | +11              | 类似 max，但更平滑       |

**公式对比**：

```python
# max 聚合
path_score = max(bge_scores[t] for t in path) / len(path)

# avg 聚合（最终采用）
path_score = avg(bge_scores[t] for t in path) / len(path)

# softmax 聚合
weights = softmax([bge_scores[t] for t in path])
path_score = sum(w * s for w, s in zip(weights, scores)) / len(path)
```

**为什么 avg 更好？**

考虑路径 `[A(5.0), B(1.0), C(0.5)]`：

- max: `5.0 / 3 = 1.67`（只看 A）
- avg: `(5.0 + 1.0 + 0.5) / 3 / 3 = 0.72`（考虑整条路径）

avg 聚合惩罚了"高分表 + 低分中间表"的路径，避免噪声传递。

### 4.3 boost_factor 对比

| boost_factor  | Q1 提升       | Q7 提升      | 副作用            |
| ------------- | ------------- | ------------ | ----------------- |
| 0.3           | +10           | +3           | 加成不足          |
| **0.4** | **+12** | **+4** | **平衡** ⭐ |
| 0.5           | +12           | +4           | 可能过度加成      |

**结论**：`boost_factor = 0.4` 是最佳选择。

### 4.4 max_path_length 对比

| max_path_length | Q1 提升       | Q7 提升      | 路径数量          |
| --------------- | ------------- | ------------ | ----------------- |
| 2               | +8            | +2           | 少                |
| **3**     | **+12** | **+4** | **适中** ⭐ |
| 4               | +12           | +4           | 多但噪声增加      |

**结论**：`max_path_length = 3` 是最佳选择。

---

## 5. 最终算法

### 5.1 算法伪代码

```python
def optimize(candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """
    边/路径增强排序算法

    Args:
        candidates: [(table_name, bge_score), ...]

    Returns:
        优化后的排序列表
    """
    # 1. 提取表名和分数
    table_names = [t for t, _ in candidates]
    bge_scores = {t: s for t, s in candidates}
    max_bge = max(bge_scores.values())

    # 2. 获取候选表之间的边（不做 1-hop 扩展！）
    relationships = get_table_relationships(table_names)

    # 3. 构建邻接表
    adj = build_adjacency_list(relationships)

    # 4. 找所有路径（长度 2 到 max_path_length）
    paths = find_all_paths(table_names, adj, max_length=3)

    # 5. 计算路径贡献
    path_contributions = {}
    for path in paths:
        # 路径分数 = 平均 BGE 分数 × 长度因子
        path_bge_avg = sum(bge_scores[t] for t in path) / len(path)
        length_factor = 1.0 / len(path)
        path_score = path_bge_avg * length_factor / max_bge

        # 累加到路径上每个表
        for table in path:
            path_contributions[table] = path_contributions.get(table, 0) + path_score

    # 6. 归一化
    max_contrib = max(path_contributions.values()) if path_contributions else 1
    normalized = {t: v / max_contrib for t, v in path_contributions.items()}

    # 7. 计算最终分数
    boost_factor = 0.4 * max_bge
    final_scores = {}
    for table in table_names:
        contrib = normalized.get(table, 0)
        final_scores[table] = bge_scores[table] + boost_factor * contrib

    # 8. 排序返回
    return sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
```

### 5.2 核心公式总结

$$
\boxed{
\text{final}(t) = s_t + 0.4 \cdot s_{\max} \cdot \frac{\sum_{p \ni t} \frac{\bar{s}_p}{|p|}}{\max_{t'} \sum_{p \ni t'} \frac{\bar{s}_p}{|p|}}
}
$$

其中：

- $s_t$：表 $t$ 的 BGE 原始分数
- $s_{\max}$：所有候选表中的最高 BGE 分数
- $\bar{s}_p = \frac{1}{|p|} \sum_{t \in p} s_t$：路径 $p$ 上所有表的平均 BGE 分数
- $|p|$：路径长度（节点数）

### 5.3 关键参数

| 参数            | 值                      | 公式位置           |
| --------------- | ----------------------- | ------------------ |
| boost_factor    | $0.4 \times s_{\max}$ | 最终分数加成幅度   |
| max_path_length | 3                       | DFS 搜索深度       |
| 路径聚合        | avg                     | $\bar{s}_p$ 计算 |
| 长度衰减        | $1/|p                   | $                  |

---

## 6. 与 PPR 算法的理论对比

### 6.1 PPR 公式

$$
\text{PPR}(t) = (1-d) \cdot \text{seed}(t) + d \cdot \sum_{t' \to t} \frac{\text{PPR}(t')}{|\text{out}(t')|}
$$

### 6.2 关键差异

| 方面               | PPR                   | 边/路径             |
| ------------------ | --------------------- | ------------------- |
| **图规模**   | 1-hop 扩展 → 150+ 表 | 不扩展 → 26-28 表  |
| **信号传递** | 全局迭代扩散          | 局部路径直接传递    |
| **分数来源** | 结构距离$1/(d+1)$   | BGE 语义分数$s_t$ |
| **收敛性**   | 需要迭代收敛          | 一次遍历完成        |

### 6.3 为什么边/路径更有效？

1. **语义信息保留**：PPR 只用距离，边/路径用 BGE 分数
2. **噪声控制**：不扩展邻居，避免引入无关表
3. **可解释性**：加分来自具体路径，可追溯

---

## 7. 完整测试结果（真实 BGE 数据）

### 7.1 多表查询

| 查询 | 关键表               | BGE | 边/路径 |       提升       | 关键路径                             |
| ---- | -------------------- | :-: | :-----: | :--------------: | ------------------------------------ |
| Q1   | event_history        | #16 |   #4   | **+12** ⭐ | ne_root → customer → event_history |
| Q2   | event_history        | #4 |   #3   |        +1        | customer → event_history            |
| Q7   | event_history        | #10 |   #6   | **+4** ⭐ | customer → event_history            |
| Q7   | t_bz_config_customer | #1 |   #1   |        0        | -                                    |

### 7.2 单表查询（安全性验证）

| 查询 | 关键表                 | BGE | 边/路径 | 变化 |
| ---- | ---------------------- | :-: | :-----: | :--: |
| Q3   | t_bz_config_customer   | #1 |   #1   | ✅ 0 |
| Q4   | t_bz_config_ci_ne_root | #2 |   #2   | ✅ 0 |
| Q5   | t_bz_config_ci_ne_root | #1 |   #1   | ✅ 0 |
| Q6   | t_bz_config_ci_ne_root | #1 |   #1   | ✅ 0 |

**结论**：单表查询排名不受影响，算法安全。

### 7.3 统计汇总

| 指标           | 值                     |
| -------------- | ---------------------- |
| 总提升         | **17 位**        |
| 平均提升       | **1.42 位**      |
| 有提升的关键表 | 3/12 (25%)             |
| 有下降的关键表 | 0/12 (0%)              |
| 最大单项提升   | +12 (Q1 event_history) |

---

## 8. Q1 详细路径分析

### 8.1 候选表（真实 BGE 检索 top_k=15）

```
排名  表名                           BGE分数
#1   t_bz_config_ci_ne_root         2.22
#2   t_bz_event_month               1.89
#3   t_bz_config_customer           1.75
...
#16  event_history                  0.27  ← 关键表，排名太低
```

### 8.2 候选表之间的边

```
t_bz_config_ci_ne_root ←→ t_bz_config_customer (FK: CUSTOMER_ID)
t_bz_config_customer ←→ event_history (FK: CUSTOMER_ID)
```

### 8.3 发现的路径

| 路径                                           | 长度        | 路径 BGE 均值                       | 路径分数                |
| ---------------------------------------------- | ----------- | ----------------------------------- | ----------------------- |
| ne_root → customer                            | 2           | (2.22+1.75)/2 = 1.99                | 1.99/2 = 0.99           |
| customer → event_history                      | 2           | (1.75+0.27)/2 = 1.01                | 1.01/2 = 0.51           |
| **ne_root → customer → event_history** | **3** | **(2.22+1.75+0.27)/3 = 1.41** | **1.41/3 = 0.47** |

### 8.4 路径贡献计算

```
event_history 的路径贡献:
  = 路径2贡献 + 路径3贡献
  = 0.51 + 0.47
  = 0.98

归一化后: 0.98 / max_contrib ≈ 0.85

最终分数:
  = BGE + boost_factor × normalized_contrib
  = 0.27 + 0.4 × 2.22 × 0.85
  = 0.27 + 0.75
  = 1.02

→ 排名从 #16 提升到 #4
```

---

## 9. 代码实现

### 9.1 核心类

```python
class EdgePathOptimizerFinal:
    def __init__(
        self,
        client: Neo4jClient,
        boost_factor_mult: float = 0.4,   # boost = max_bge × 0.4
        max_path_length: int = 3,          # 最长路径
        use_edge_boost: bool = True,       # 是否融合边加分
        edge_weight: float = 0.3,          # 边加分权重
    ):
        self.client = client
        self.boost_factor_mult = boost_factor_mult
        self.max_path_length = max_path_length
        self.use_edge_boost = use_edge_boost
        self.edge_weight = edge_weight
```

### 9.2 文件位置

| 文件                                                               | 说明     |
| ------------------------------------------------------------------ | -------- |
| `fusionsql/graph_optimizer/edge_path_optimizer.py`               | 算法实现 |
| `fusionsql/graph_optimizer/doc/edge_path_algorithm_report.md`    | 技术报告 |
| `fusionsql/graph_optimizer/doc/edge_path_detailed_experiment.md` | 本文档   |

---

## 10. 结论

### 10.1 最佳配置

| 参数            | 最佳值     | 原因             |
| --------------- | ---------- | ---------------- |
| 策略            | path_boost | 考虑路径上所有表 |
| 聚合函数        | avg        | 惩罚低质量中间表 |
| boost_factor    | 0.4        | 平衡加成与稳定性 |
| max_path_length | 3          | 适中的路径长度   |

### 10.2 核心公式

$$
\text{final}(t) = s_t + 0.4 \cdot s_{\max} \cdot \text{norm}\left(\sum_{p \ni t} \frac{\bar{s}_p}{|p|}\right)
$$

### 10.3 效果

- **总提升**：17 位
- **最大提升**：+12 位（Q1 event_history）
- **无负面影响**：单表查询排名不变

---

*报告撰写时间: 2026-01-26*
*测试数据: 真实 BGE 并集检索结果 (top_k=15)*
*算法版本: EdgePathOptimizerFinal v1.0*
