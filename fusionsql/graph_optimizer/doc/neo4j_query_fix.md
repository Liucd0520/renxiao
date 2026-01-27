# Neo4j 查询修复报告

> 修复日期: 2026-01-23
> 作者: Claude

---

## 问题发现

### 原始问题

在 `fusionsql/graph_optimizer/neo4j_client.py` 中，所有查询都假设 **外键关系 (IS/MOSTLYIS) 存在于 Table 节点之间**：

```cypher
-- 错误的查询
MATCH (t1:Table)-[r:IS|MOSTLYIS]-(t2:Table)
```

### 实际数据模型

通过深度诊断发现，Neo4j 数据库的实际结构是：

```
Database (1) 
    └── Table (343)
         └── Column (3348)
              └── IS/MOSTLYIS → Column
```

**外键关系存储在 Column 节点之间，而不是 Table 节点之间！**

```cypher
-- 实际关系示例
(:Column {name: 'CUSTOMER_ID'}) -[:MOSTLYIS]-> (:Column {name: 'customer_id'})
(:Column {name: 'PARENT_ID'}) -[:IS]-> (:Column {name: 'ID'})
```

### 影响

| 查询方式 | 结果 |
|----------|------|
| 错误查询 (直接 Table-Table) | **0 条关系** |
| 正确查询 (通过 Column 推导) | **4650 对 Table 有外键关系** |

---

## 修复内容

### 修复的方法

1. **`get_table_relationships()`** - 获取表间关系
2. **`get_connected_tables()`** - BFS 扩展获取邻居表
3. **`get_table_degrees()`** - 获取表的度信息
4. **`get_shortest_path_length()`** - 获取两表之间的最短路径

### 查询修复对比

#### get_table_relationships

```diff
- MATCH (t1:Table)-[r:IS|MOSTLYIS]-(t2:Table)
- WHERE t1.name IN $tables AND t2.name IN $tables
+ MATCH (t1:Table)-[:COLUMN]-(c1:Column)-[r:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(t2:Table)
+ WHERE t1.name IN $tables AND t2.name IN $tables AND t1 <> t2
  RETURN DISTINCT t1.name AS source, t2.name AS target, type(r) AS rel_type
```

#### get_connected_tables

```diff
- MATCH path = (seed:Table)-[:IS|MOSTLYIS*0..N]-(neighbor:Table)
+ MATCH (seed:Table)-[:COLUMN]-(c1:Column)-[:IS|MOSTLYIS]-(c2:Column)-[:COLUMN]-(neighbor:Table)
+ WHERE seed.name IN $seeds AND seed <> neighbor
  RETURN DISTINCT neighbor.name AS table_name
```

#### get_table_degrees

```diff
- OPTIONAL MATCH (t)-[r1:IS]-()
- OPTIONAL MATCH (t)-[r2:MOSTLYIS]-()
+ OPTIONAL MATCH (t)-[:COLUMN]-(c1:Column)-[r1:IS]-(c2:Column)-[:COLUMN]-(other1:Table)
+ WHERE t <> other1
+ WITH t, count(DISTINCT other1) AS is_count
+ OPTIONAL MATCH (t)-[:COLUMN]-(c3:Column)-[r2:MOSTLYIS]-(c4:Column)-[:COLUMN]-(other2:Table)
+ WHERE t <> other2
```

---

## 修复后验证结果

### 核心表之间的关系

修复后成功发现核心表之间的外键关系：

```
t_bz_config_customer --> event_history [MOSTLYIS]
event_history --> t_bz_config_customer [MOSTLYIS]
t_bz_config_ci_ne_root --> t_bz_config_customer [MOSTLYIS]
t_bz_config_customer --> t_bz_config_ci_ne_root [MOSTLYIS]
```

### 核心表的连接度

| 表名 | IS 连接 | MOSTLYIS 连接 | 总连接 |
|------|---------|---------------|--------|
| `event_history` | 0 | 57 | **57** |
| `t_bz_config_customer` | 6 | 50 | **56** |
| `t_bz_config_ci_ne_root` | 0 | 11 | **11** |

### 核心表的邻居表

| 表名 | 邻居表数量 |
|------|-----------|
| `t_bz_config_ci_ne_root` | 11 个邻居 |
| `event_history` | 57 个邻居 |
| `t_bz_config_customer` | 56 个邻居 |

---

## 影响分析

### 图优化模块现在可以正常工作

修复前：
- 图优化返回空结果，因为查不到任何表间关系
- 所有核心表都被认为是"孤立表"
- PPR、连通性分数等全部为 0

修复后：
- 图优化可以正确获取表间关系
- 核心表之间的连接被正确识别
- PPR 和连通性分数可以正确计算

### 预期性能提升

在多表 JOIN 查询（如 Q1、Q2、Q7）中：
- 相关表的排名会因外键连接而提升
- 孤立的噪声表会被正确降权
- 图优化真正发挥作用

---

## 修复的文件

- `fusionsql/graph_optimizer/neo4j_client.py`

## 测试脚本

- `tests/verify_core_tables_fk.py` - 原始问题诊断
- `tests/neo4j_deep_diagnosis.py` - 深度诊断
- `tests/verify_correct_query.py` - 正确查询验证
- `tests/test_neo4j_fixed.py` - 修复后验证

---

*报告完成*
