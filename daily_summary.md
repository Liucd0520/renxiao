# 今日工作总结 - LinkAlign 深度分析与优化尝试

**日期**: 2025-12-12（星期四）  
**工作时长**: 约 6 小时

---

## 📋 工作概述

今天主要对 LinkAlign（Text-to-SQL 的 Schema Linking 工具）进行了深度分析和优化尝试，重点解决批量测试中发现的**表召回率低**和 **SQL 生成错误**问题。

---

## 🔍 主要工作内容

### 1. SQL 对比分析（上午）

**任务**: 分析昨天批量测试的 7 个测试用例，对比 LinkAlign 生成的 SQL 与正确 SQL

**完成内容**:
- 详细对比分析每个测试用例的 SQL 生成结果
- 发现 **SQL 正确率 0/7 (0%)**
- 识别错误原因：
  - 表名选择错误（如使用 `report_new_dev` 而非 `t_bz_config_ci_ne_root`）
  - 强制 JOIN 导致无意义关联
  - LLM 输出包含大量 `<think>` 标签

**产出**: 
- `sql_analysis_report.md` - SQL 对比分析报告
- 识别了两大问题：Schema 元数据缺失 + Prompt 模板不合理

---

### 2. 根因定位（上午-中午）

**发现**: 查看 Schema 文件时发现：

```json
{
  "column_name": "ONLINE_TIME",
  "column_descriptions": null  // ❌ 50% 的列描述为空
}
```

**深入调查**:
1. 检查了 `extract_mysql_schema.py` 源码
2. 确认 schema 是从 MySQL 数据库的 `COLUMN_COMMENT` 提取
3. **统计结果**: 3353 个列中，1679 个（50%）描述为 null

**结论**: 
- LinkAlign 不自带 schema 生成工具
- 论文测试用的是高质量公开数据集（Spider/BIRD）
- 我们的真实业务数据库注释不完整

---

### 3. Schema 自动增强方案设计与实现（中午-下午）

**设计思路**:
> 如果数据库列没有注释，就用 LLM 基于列名、类型、样本数据自动生成描述

**实现**:

创建了 `extract_mysql_schema_enhanced.py`：
```python
def generate_description_with_llm(table_name, column_name, column_type, sample_rows):
    prompt = f"""根据以下信息生成列描述（10-20字）：
    表名: {table_name}
    列名: {column_name}
    类型: {column_type}
    示例: {sample_rows}
    """
    return llm.complete(prompt).text
```

**优化过程**:
1. 第一版：包含 `<think>` 标签，需要清理
2. 改进 Prompt：明确禁止思考过程
3. 添加响应清理函数：去除噪音

**测试效果**:
```
3 个表，42 列
- 数据库已有注释: 5 个 (12%)
- LLM 生成描述: 37 个 (88%)
- 耗时: 277.5 秒
```

---

### 4. 核心表 Schema 增强（下午）

**优化策略**: 先只处理核心表，快速验证效果

创建了 `enhance_core_tables.py`，处理 3 个核心表：
- `t_bz_config_ci_ne_root` - 设备主表
- `t_bz_config_customer` - 客户表
- `event_history` - 事件历史表

**生成结果**:
```
✨ ONLINE_TIME: 配置项上线时间
✨ OFFLINE_TIME: 配置项离线时间记录
✨ IS_DELETED: 是否已删除的标志位，0表示未删除
```

**统计**:
- 处理 155 列
- LLM 生成 34 个描述
- 已有描述 121 个

---

### 5. SQL Prompt 优化（下午）

**修改前**:
```python
SQL_PROMPT = """你是专业SQL工程师。
【要求】
2. 使用JOIN关联多个表  ❌ 强制要求
```

**修改后**:
```python
SQL_PROMPT = """根据以下 Schema 信息回答用户的问题。
【规则】
1. 直接输出 SQL，不要任何思考过程或解释
2. 必须使用 Schema 中实际存在的表名和列名
3. 根据问题复杂度决定是否使用 JOIN（简单查询不需要强制 JOIN）
4. 时间条件使用动态函数如 DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
```

---

### 6. 验证测试（下午）

**测试流程**:
1. 重建向量索引（使用增强后的 schema）
2. 运行测试用例 5："上个月上线的新设备有多少"
3. 追踪每个阶段的表保留情况

**测试结果**:

| 阶段 | 结果 |
|------|------|
| 向量检索 | ✅ 找到 `t_bz_config_ci_ne_root` |
| Reserve 保护 | ⚠️ 未进入保护列表 |
| LLM 过滤轮次1 | ❌ 被过滤掉（142表→53表） |
| 表召回率 | 0% |

**意外发现**: 
- Schema 增强**没有解决**表过滤问题
- 反而在更早的轮次就被过滤了

---

## 💡 关键洞察

### 发现真正的问题

通过这次深度测试，定位了根本原因：

**不是 Schema 描述的问题，而是 LinkAlign 的过滤算法缺陷！**

**问题机制**:
```
LinkAlign 按列投票判断表是否相关：

t_bz_config_ci_ne_root (75列):
  - ONLINE_TIME: 相关 ✅
  - 其他74列: 不相关 ❌
  
投票结果: 1/75 = 1.3%
判定: 过滤掉整个表 ❌
```

**应该的逻辑**:
```
只要有一个关键列相关 → 保留整表
```

---

## 📊 成果与产出

### 技术产出

1. **Schema 增强工具**
   - `extract_mysql_schema_enhanced.py` - 全量增强版
   - `enhance_core_tables.py` - 核心表快速增强版

2. **测试脚本**
   - `quick_validate.py` - 单用例快速验证脚本

3. **分析报告**
   - `sql_analysis_report.md` - SQL 对比分析
   - `validation_report.md` - Schema 增强验证报告

### 知识收获

1. **对 LinkAlign 的深入理解**
   - 了解了完整的 schema linking 流程
   - 识别了算法在真实业务场景的局限性

2. **Text-to-SQL 的实践经验**
   - Schema 质量对结果影响巨大
   - 学术数据集与生产环境的巨大差异
   - 人工干预（如白名单）的必要性

3. **LLM 应用技巧**
   - Prompt 设计需要反复迭代
   - 响应清理的重要性
   - 批量处理的时间估算

---

## 🎯 下一步计划

### 立即可做（明天）

**方案 B: 核心表白名单**
- 修改 `batch_test.py` 添加强制保留逻辑
- 重新运行测试验证效果
- 预计耗时: 1小时实现 + 1.5小时测试

### 中期规划

如果白名单方案有效：
1. 全量 Schema 增强（处理剩余 1645 个列）
2. 完整批量测试（7 个用例）
3. 与原始结果对比分析

如果效果仍不佳：
1. 尝试修改 `response_filtering` 投票逻辑（方案 A）
2. 或考虑其他 schema linking 方法

---

## 🤔 思考与反思

### 问题导向的研究方法

今天的工作体现了完整的问题解决流程：
1. **现象观察**: SQL 生成错误
2. **初步分析**: 表被错误过滤
3. **假设提出**: Schema 描述缺失导致
4. **验证实验**: 增强 Schema 后测试
5. **推翻假设**: 问题仍存在
6. **深入挖掘**: 定位到过滤算法
7. **新假设**: 算法逻辑需改进

### 学术 vs 工程的差距

- **论文**关注理想条件下的算法创新
- **工程**需要处理真实世界的复杂性和不完美数据
- 桥接这个差距需要**大量的适配和优化工作**

---

## ⏱️ 时间分配

| 任务 | 耗时 |
|------|------|
| SQL 对比分析 | 1.5h |
| 根因定位与调研 | 1h |
| Schema 增强工具开发 | 2h |
| 验证测试与问题分析 | 1h |
| 文档整理 | 0.5h |
| **总计** | **6h** |

---

*总结生成时间: 2025-12-12 14:57*
