# Scripts 目录

存放项目工具脚本，按功能分类。

## 目录结构

| 目录 | 说明 | 脚本 |
|-----|------|-----|
| `schema/` | Schema 提取 | 从数据库提取表/列元数据 |
| `enhance/` | 描述增强 | 使用 LLM 优化表描述 |
| `index/` | 向量索引 | 构建和管理向量索引 |
| `debug/` | 调试工具 | 调试和验证脚本 |

## 使用说明

```bash
# 从项目根目录运行
python scripts/schema/extract_table_level_schema.py --help
python scripts/enhance/enhance_schema_with_llm.py --help
python scripts/index/build_table_vector_index.py --help
```

## 各脚本说明

### schema/
- `extract_table_level_schema.py` - 提取表级别 Schema（推荐）
- `extract_mysql_schema.py` - 原始列级别 Schema 提取
- `GenerateSchemas.py` - 原 LinkAlign 的 Schema 生成

### enhance/
- `enhance_schema_with_llm.py` - LLM 批量优化表描述
- `generate_table_desc_v2.py` - 生成表描述 v2
- `translate_schema_to_english.py` - Schema 翻译为英文

### index/
- `build_table_vector_index.py` - 构建表级别向量索引
- `download_bge_m3.py` - 下载 BGE-M3 模型

### debug/
- `debug_schema_linking.py` - 调试 Schema Linking 流程
- `quick_validate.py` - 快速验证检索效果
