# LinkAlign 快速开始指南

## 🎉 环境已配置完成！

所有依赖和配置都已完成，你可以立即开始使用 LinkAlign。

## 📋 配置检查清单

✅ Python 虚拟环境已创建 (`.venv`)
✅ 所有依赖包已安装
✅ LlamaIndex 源码已修改
✅ 配置文件已更新
✅ 目录结构已创建

## ⚙️ 配置 API Keys (必需)

在开始使用前，你需要配置至少一个大模型的 API Key。

编辑 `config.py` 文件:

```bash
vim config.py
# 或
code config.py
```

根据你选择的模型，修改对应的 API Key:

```python
# 通义千问 (推荐)
QWEN_API_KEY = "sk-xxxxxxxxxxxx"
LLM_NAME = "qwen"

# 或者 智谱AI
# ZHIPU_API_KEY = "xxxxxxxxxxxxxxx"
# LLM_NAME = "zhipu"

# 或者 DeepSeek
# DEEPSEEK_API = "sk-xxxxxxxxxxxx"
# LLM_NAME = "deepseek"
```

### 获取 API Keys

- **通义千问**: https://dashscope.console.aliyun.com/
- **智谱AI**: https://open.bigmodel.cn/
- **DeepSeek**: https://platform.deepseek.com/

## 📊 准备数据

LinkAlign 需要以下数据文件：

### 1. 数据库 Schema 文件

将数据库 schema 文件放在:

```
spider2_dev/schemas/{db_id}/
  ├── {table1}_{column1}.json
  ├── {table1}_{column2}.json
  └── ...
```

每个 JSON 文件格式:

```json
{
  "meta_data": {
    "db_id": "database_name",
    "table_name": "table_name"
  },
  "column_name": "column_name",
  "column_types": "VARCHAR(255)",
  "column_descriptions": "Description of the column",
  "sample_rows": ["sample1", "sample2"]
}
```

### 2. 数据集文件

创建 `spider2_dev/spider2_dev_preprocessed.json`:

```json
[
  {
    "instance_id": "001",
    "db_id": "database_name",
    "question": "Your SQL question here"
  }
]
```

### 3. 数据库信息文件

创建 `spider2_dev/db_info.json`:

```json
[
  {
    "db_id": "database_name",
    "count": 150
  }
]
```

### 4. 外部知识 (可选)

在 `spider2_dev/external_knowledge/` 目录下创建 `.txt` 文件:

```
spider2_dev/external_knowledge/
  ├── 001.txt
  ├── 002.txt
  └── ...
```

## 🚀 运行示例

### 1. 激活虚拟环境

```bash
cd ~/Documents/实习/LinkAlign
source .venv/bin/activate
```

### 2. 运行测试脚本

确认环境配置正确:

```bash
python test_setup.py
```

### 3. 运行主程序

生成 Schema:

```bash
python GenerateSchemas.py \
  --save_path ./spider2_dev/instance_schemas \
  --schema_path ./spider2_dev/schemas \
  --dataset ./spider2_dev/spider2_dev_preprocessed.json \
  --db_info_path ./spider2_dev/db_info.json \
  --links_save_path ./spider2_dev/schema_links \
  --external_info_path ./spider2_dev/external_knowledge
```

### 4. 查看结果

生成的结果会保存在:

- **Instance Schemas**: `./spider2_dev/instance_schemas/`
- **Schema Links**: `./spider2_dev/schema_links/`

## 🔧 自定义配置

### 修改嵌入模型

在 `config.py` 中:

```python
EMBED_MODEL_NAME = "BAAI/bge-large-en-v1.5"  # 默认
# 或使用其他模型
# EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
```

### 调整模型参数

在 `config.py` 中:

```python
TEMPERATURE = 0.45              # 控制生成的随机性
MAX_OUTPUT_TOKENS = 4096        # 最大输出 token 数
CONTEXT_WINDOW = 120000         # 上下文窗口大小
```

### 修改检索参数

在 `GenerateSchemas.py` 的 `get_schema()` 函数中:

```python
reserve_size = 90           # 小于此规模的数据库保留全部 schema
min_retrival_size = 250     # 超过此阈值启动检索
filter_chunk_size = 250     # 过滤块大小
post_retrieval_size = 90    # 后检索规模
post_retrieval_turn = 2     # 后检索轮数
reserve_rate = 0.6          # 保留比例
```

## 📖 项目架构

### 三步流程

LinkAlign 使用三步流程进行 Schema Linking:

1. **Step 1: 多轮语义增强检索**
   - 使用 RAG 检索潜在相关的数据库 schema
   - 通过多轮查询重写增强检索质量

2. **Step 2: 无关信息隔离**
   - 使用 Multi-Agent Debate 过滤无关 schema
   - 确定最相关的数据库

3. **Step 3: Schema 提取增强**
   - 提取生成 SQL 所需的表和列
   - 生成最终的 schema 链接

### 两种模式

- **Pipeline Mode**: 简单快速，适合小规模数据
- **Agent Mode**: 高质量，适合大规模复杂数据

## 🐛 故障排除

### 问题: 导入错误

```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 问题: API 调用失败

- 检查 API Key 是否正确
- 检查网络连接
- 检查 API 余额

### 问题: 内存不足

- 减小 `similarity_top_k` 参数
- 分批处理数据
- 增加系统内存

### 问题: 模型下载慢

设置 HuggingFace 镜像:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

## 📚 更多资源

- **论文**: arXiv:2503.18596
- **GitHub**: https://github.com/Satissss/LinkAlign
- **详细文档**: 查看 `SETUP.md`

## 💡 提示

1. 首次运行会下载嵌入模型，需要一些时间
2. 大规模数据处理可能需要较长时间
3. 建议先用小数据集测试
4. 注意 API 调用限制和费用

## 🎓 示例项目

查看 `spider2_dev/` 目录下的示例数据结构，了解如何组织你的数据。

---

**准备好了吗？开始使用 LinkAlign！** 🚀

如有问题，请查看 `SETUP.md` 或提交 Issue。
