# LinkAlign 项目部署说明

## 项目简介

LinkAlign 是一个用于 Text-to-SQL 任务的 Schema Linking 框架，专为大规模多数据库环境设计。

## 环境配置完成状态 ✅

### 已完成的步骤

1. ✅ **克隆项目**
   - 项目位置: `~/Documents/实习/LinkAlign`

2. ✅ **创建虚拟环境**
   - Python 虚拟环境: `.venv`

3. ✅ **安装依赖**
   - 已安装所有必要的 Python 包
   - 主要依赖:
     - sentence-transformers
     - transformers >= 4.42.0
     - torch >= 2.4.0
     - llama-index-core == 0.10.62
     - llama-index-embeddings-huggingface
     - openai
     - pandas
     - tqdm

4. ✅ **修改 LlamaIndex 源码**

   **修改文件 1: embeddings/huggingface/base.py**
   - 路径: `.venv/lib/python3.13/site-packages/llama_index/embeddings/huggingface/base.py`
   - 修改: 注释掉第87行的 `safe_serialization` 参数

   **修改文件 2: indices/vector_store/retrievers/retriever.py**
   - 路径: `.venv/lib/python3.13/site-packages/llama_index/core/indices/vector_store/retrievers/retriever.py`
   - 修改:
     - 在 `__init__` 方法中添加了 `self._orininal_ids = node_ids`
     - 添加了 `index` 属性
     - 添加了 `change_node_ids()` 方法
     - 添加了 `back_to_original_ids()` 方法

5. ✅ **配置 config.py**
   - 已更新路径为跨平台兼容的路径
   - 已创建必要的目录结构

## 使用前的配置

### 1. 激活虚拟环境

```bash
cd ~/Documents/实习/LinkAlign
source .venv/bin/activate
```

### 2. 配置 API Keys

编辑 `config.py` 文件，填写你的 API 密钥:

```python
# 选择一个你要使用的大模型，填写对应的 API Key
QWEN_API_KEY = "your_qwen_api_key_here"        # 通义千问
ZHIPU_API_KEY = "your_zhipu_api_key_here"      # 智谱AI
DEEPSEEK_API = "your_deepseek_api_key_here"    # DeepSeek
```

### 3. 准备数据

将你的数据文件放置在以下目录:

- **数据库 schema**: `./spider2_dev/schemas/`
- **数据集**: `./spider2_dev/spider2_dev_preprocessed.json`
- **数据库信息**: `./spider2_dev/db_info.json`
- **外部知识** (可选): `./spider2_dev/external_knowledge/`

## 运行项目

### 生成 Schema

```bash
python GenerateSchemas.py \
  --save_path ./spider2_dev/instance_schemas \
  --schema_path ./spider2_dev/schemas \
  --dataset ./spider2_dev/spider2_dev_preprocessed.json \
  --db_info_path ./spider2_dev/db_info.json \
  --links_save_path ./spider2_dev/schema_links \
  --external_info_path ./spider2_dev/external_knowledge
```

## 项目结构

```
LinkAlign/
├── .venv/                          # Python 虚拟环境
├── data/                           # 数据目录
├── dataset/                        # 数据集目录
├── logs/                           # 日志目录
├── spider2_dev/                    # Spider2.0 数据
│   ├── schemas/                    # 数据库 schema 文件
│   ├── instance_schemas/           # 生成的实例 schema
│   ├── schema_links/               # Schema 链接结果
│   └── external_knowledge/         # 外部知识
├── embed_model/                    # 嵌入模型
├── generate_data/                  # 数据生成工具
├── llms/                           # LLM 模型封装
│   ├── qwen/                       # 通义千问
│   ├── zhipu/                      # 智谱AI
│   └── deepseek/                   # DeepSeek
├── pipes/                          # RAG 管道
├── prompts/                        # 提示词模板
├── tools/                          # Schema Linking 工具
├── config.py                       # 配置文件
├── GenerateSchemas.py              # 主程序
├── utils.py                        # 工具函数
├── requirements.txt                # 依赖列表
└── SETUP.md                        # 本说明文档
```

## 技术栈

- **LLM 框架**: LlamaIndex 0.10.62
- **嵌入模型**: HuggingFace (bge-large-en-v1.5)
- **大语言模型**: 通义千问/智谱AI/DeepSeek
- **向量数据库**: LlamaIndex VectorStore
- **Python**: 3.13

## 注意事项

1. **首次运行**: 第一次运行时，嵌入模型会自动从 HuggingFace 下载，可能需要一些时间
2. **索引生成**: 如果数据目录更新，需要在 `config.py` 中设置 `IS_VECTOR_STORE_EXIST = False` 重新生成索引
3. **API 限制**: 注意大模型 API 的调用限制和费用
4. **内存需求**: Schema Linking 处理大规模数据库时可能需要较大内存

## 常见问题

### Q: 如何切换使用的大模型?
A: 在 `config.py` 中修改 `LLM_NAME` 参数为 "qwen", "zhipu" 或 "deepseek"

### Q: 如何使用本地嵌入模型?
A: 在 `embed_model/EmbedModelPathMap.py` 中配置本地模型路径

### Q: 遇到依赖冲突怎么办?
A: 删除 `.venv` 目录，重新创建虚拟环境并安装依赖

## 引用

如果使用本项目，请引用:

```bibtex
@article{wang2025linkalign,
  title={LinkAlign: Scalable Schema Linking for Real-World Large-Scale Multi-Database Text-to-SQL},
  author={Wang, Yihan and Liu, Peiyu and Yang, Xin},
  journal={arXiv preprint arXiv:2503.18596},
  year={2025}
}
```

## 许可证

查看 LICENSE 文件了解详情
