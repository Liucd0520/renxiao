# 在这里添加模型和本地地址的映射
# 使用本地下载的 bge-large-en-v1.5 模型
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
embed_model_map_name_to_path = {
    "BAAI/bge-large-en-v1.5": os.path.join(base_dir, "embed_model_cache/bge-large-en-v1.5")
}
