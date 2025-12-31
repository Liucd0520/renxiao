# Chess-Plus vs LinkAlign 方案对比分析

**日期**: 2024-12-23  
**目的**: 深入对比两种 Text-to-SQL 方案的技术实现和效果差异

---

## 1. 架构对比

| 模块 | LinkAlign + 我们的方法 | Chess-Plus |
|-----|----------------------|-----------|
| **Schema Linking** | BGE-M3 Sparse 向量检索 | LLM 直接判断 + 关键词/实体检索 |
| **实体检索** | ❌ 没有 | LSH + 编辑距离 + Embedding 三重过滤 |
| **表选择** | 向量相似度 TOP K | LLM 判断哪些表相关 |
| **列选择** | 列级别增强描述 + 向量检索 | LLM 判断哪些列相关 |
| **SQL 生成** | Qwen 32B 单次生成 | 多模板并行生成多个候选 |
| **验证机制** | ❌ 没有 | Unit Tester 单元测试 |
| **多轮对话** | ❌ 没有 | ✅ 支持 |

---

## 2. Schema Linking 方法对比

### 2.1 LinkAlign（我们的方法）

```
流程:
用户问题 
  → BGE-M3 编码 (Sparse)
  → 计算与所有 Schema 的相似度
  → 取 TOP 10
  → 返回表列表

优点:
- 快速（预计算后 36ms/问题）
- 简单

缺点:
- 依赖描述质量
- 无法处理具体值（如 "ciscoA"）
- 全量增强时噪音太大
```

### 2.2 Chess-Plus

```
流程:
用户问题
  → 1. ExtractKeywords (LLM 抽取关键词)
  → 2. RetrieveEntity (在数据库中搜索关键词对应的值)
     - LSH 近似匹配
     - 编辑距离过滤
     - Embedding 相似度验证
  → 3. SelectTables (LLM 判断需要哪些表)
  → 4. SelectColumns (LLM 判断需要哪些列)
  → 返回精选 Schema

优点:
- 能处理具体值（如 "ciscoA" → 找到 HOST_NAME 列）
- LLM 理解更准确
- 自适应

缺点:
- 需要多次 LLM 调用（成本高）
- 需要预处理数据库（LSH 索引）
- 速度较慢
```

---

## 3. 实体检索（Chess-Plus 独有）

Chess-Plus 的核心优势之一是 **RetrieveEntity**：

```python
# 三重过滤机制
1. LSH 近似匹配（快速召回候选）
   query_lsh("ciscoA") → 找到相似的数据库值
   
2. 编辑距离过滤（去除误匹配）
   difflib.SequenceMatcher("ciscoA", "cisco123").ratio() > 0.3
   
3. Embedding 相似度验证（语义匹配）
   similarity = dot(keyword_embedding, value_embedding) > 0.6
```

**这是我们之前讨论的"数据库值索引"的完整实现！**

---

## 4. SQL 生成对比

### 4.1 LinkAlign（我们的方法）

```
单次生成:
Qwen 32B + Schema + 问题 → 一个 SQL
```

### 4.2 Chess-Plus

```
多候选生成 + 验证:
1. 并行调用多个 LLM 配置生成多个 SQL 候选
2. 执行每个 SQL 获取结果
3. 按执行结果聚类
4. 用 Unit Test 评估选择最佳候选
```

---

## 5. 验证机制（Chess-Plus 独有）

Chess-Plus 的 **Unit Tester** 模块：

```
流程:
1. GenerateUnitTest: LLM 生成测试用例
   "结果应该包含设备名" 
   "结果应该有 created_time 列"
   
2. Evaluate: 执行所有 SQL 候选，检查是否满足测试用例

3. 选择得分最高的 SQL
```

**这是我们完全没有的功能！**

---

## 6. 当前效果对比

| 指标 | LinkAlign（我们的方法） | Chess-Plus |
|-----|----------------------|-----------|
| 表召回率 | **99.7%** (301/302) | 待测试 |
| 速度 | 36 ms/问题 | 预计更慢（多次 LLM 调用） |
| 含具体值问题 | 可能不佳 | 应该更好 |
| 边缘问题 | 8 个失败 | 待测试 |

---

## 7. Chess-Plus 可借鉴的模块

| 模块 | 是否值得借鉴 | 理由 |
|-----|------------|-----|
| **RetrieveEntity** | ⭐⭐⭐⭐⭐ | 解决具体值问题，这是我们的短板 |
| SelectTables (LLM) | ⭐⭐⭐ | 可能比向量检索更智能，但成本高 |
| **Unit Tester** | ⭐⭐⭐⭐⭐ | 能有效验证和筛选 SQL |
| 多候选生成 | ⭐⭐⭐⭐ | 增加正确率，但成本高 |

---

## 8. 推荐融合方案

```
保留我们的优势:
- BGE-M3 Sparse 检索（快速、准确）
- 核心列增强（99.7% 召回率）
- Qwen 32B（已有配置）

借鉴 Chess-Plus:
- RetrieveEntity（实体检索）
  - 从问题中抽取具体值
  - 在数据库中搜索匹配表/列
  
- Unit Tester（验证机制）
  - 执行生成的 SQL
  - 检查结果是否合理
```

---

## 9. 下一步建议

1. **配置 Chess-Plus 使用 Qwen 32B**（已有 API）
2. **接入 netcaredb_ai 数据库**
3. **用相同的 302 问题测试 Chess-Plus**
4. **对比两者效果**
5. **提取 RetrieveEntity 模块整合到我们的方案**

---

*分析完成时间: 2024-12-23*
