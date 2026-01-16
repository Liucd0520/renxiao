# LSH Entity Linking 集成报告

**日期**: 2026-01-16  
**项目**: FusionSQL  
**模型**: Qwen3-30B-A3B (MoE)

---

## 1. 背景与目标

### 1.1 问题描述

在 Text-to-SQL 任务中，用户问题可能包含**具体实体名**（如设备名 `ciscoA`、状态值 `down`），这些实体在数据库中可能有不同的表示方式。

**示例**：
- 用户说 `ciscoA` → 数据库中可能是 `HOST_NAME='cisco'`
- 用户说 `down` → 数据库中可能是 `device_status='down'`

### 1.2 解决方案

参考 [CHESS 论文](https://arxiv.org/abs/2405.16755) 的 **Entity Linking** 方法：

1. **LLM 关键词提取**: 从问题中提取可能对应数据库值的关键词
2. **LSH 值匹配**: 用 MinHash LSH 在数据库值中快速搜索相似匹配
3. **提示增强**: 将匹配结果作为提示传给 SQL 生成 LLM

---

## 2. 实现架构

### 2.1 流程图

```
用户问题: "设备ciscoA上个月告警统计"
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│           Step 1 & 2 并行执行（优化后）                        │
│  ┌────────────────────────┐  ┌────────────────────────────┐ │
│  │ BGE-M3 检索            │  │ LLM 关键词提取 + LSH 搜索   │ │
│  │ → TOP-10 表            │  │ → 值匹配提示               │ │
│  └────────────────────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: SQL 生成                                            │
│  Prompt = Schema + "值匹配提示: 'cisco'" + 问题               │
│  → 生成 SQL: WHERE HOST_NAME = 'ciscoA'                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 并行优化

BGE 检索和 LLM+LSH Entity Linking 互不依赖，可以并行执行：

```python
with ThreadPoolExecutor(max_workers=2) as executor:
    future_retrieval = executor.submit(do_retrieval)      # BGE
    future_linking = executor.submit(do_entity_linking)   # LLM+LSH
    
    retrieved = future_retrieval.result()
    matched_hint = future_linking.result()
```

---

## 3. 核心代码修改

### 3.1 修改文件

| 文件 | 修改内容 |
|------|---------|
| `fusionsql/pipeline.py` | 添加 `_extract_keywords()` 和修改 `_find_matched_values()` |
| `fusionsql/value_search/search.py` | 优化 `find_entity_values()` 只处理英文关键词 |

### 3.2 LLM 关键词提取

```python
def _extract_keywords(self, question: str) -> list:
    """使用 LLM 从问题中提取关键词（CHESS 论文方法）"""
    prompt = '''从问题中提取实体关键词，这些关键词可能对应数据库中的具体值。
只提取：设备名、客户名、厂商名、状态值等具体实体。
如果问题中没有具体实体，返回"无"。

示例1:
问题: 设备ciscoA，上个月发生了几次告警
提取: ciscoA

示例2:
问题: 设备状态down超过3个月
提取: down

当前问题: {}
提取:'''.format(question)
    
    response = self.generator.llm.complete(prompt)
    # 解析并返回关键词列表
```

### 3.3 值匹配提示格式

> **重要**: 提示中**不能包含表名**，否则会误导 LLM 使用 LSH 匹配到的表而非 BGE 检索到的表。

```python
def _format_matched_values(self, matched_values: dict) -> str:
    # 只提供值信息，不提及表名
    lines = [
        "## 值匹配提示（仅供参考，请以检索到的表为准）",
        f"问题中提到的值在数据库中可能对应: {', '.join(repr(v) for v in values)}"
    ]
    return "\n".join(lines)
```

---

## 4. 测试结果

### 4.1 7 题标准测试集

| 指标 | 禁用 LSH | 启用 LSH | 差异 |
|------|----------|----------|------|
| **通过率** | 6/7 (85.7%) | 6/7 (85.7%) | 0 |
| **表召回率** | 95.2% | 95.2% | 0 |
| **列使用率** | 47.6% | 47.6% | 0 |

### 4.2 Entity Linking 效果

| 问题 | LLM 提取关键词 | LSH 匹配 |
|------|---------------|---------|
| 设备ciscoA上个月告警 | `ciscoA` | `'cisco'` ✅ |
| device state down超过3个月 | `down` | `'down'` ✅ |
| 现在平台上有多少家客户 | (无) | (无) ✅ |

---

## 5. 遇到的问题与解决方案

### 5.1 问题：LSH 匹配误导 LLM 选择错误的表

**现象**：启用 LSH 后，测试 2 的表召回从 100% 降到 33%

**根因**：LSH 提示包含表名 `t_gn_topo_device.device_status='down'`，LLM 误认为这是正确的表

**解决**：修改提示格式，只告诉 LLM 值的匹配信息，不提及表名

### 5.2 问题：中文 n-gram 匹配不可靠

**现象**：`告警` 匹配到 `测试`、`增加` 等无关词（相似度 1.0）

**根因**：中文字符本身就是一个 n-gram，容易产生假阳性

**解决**：`find_entity_values()` 只处理英文/数字关键词

---

## 6. 结论

1. **LSH Entity Linking 已正确集成**，按照 CHESS 论文方式实现
2. **在当前 7 题测试集上无明显提升**，因为大多数问题是语义性的
3. **LSH 的价值**在于处理包含**具体实体名**的问题（如设备名、客户名）
4. **建议**保持启用，对后续更复杂的测试用例可能有帮助

---

## 7. 相关文件

- `fusionsql/pipeline.py` - Entity Linking 主逻辑
- `fusionsql/value_search/search.py` - LSH 搜索
- `fusionsql/lsh_index/` - 预构建的 LSH 索引
- `tests/test_lsh_entity_linking.py` - 测试脚本
