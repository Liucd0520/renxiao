#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 BGE-M3 模型（使用 ModelScope 国内镜像）

使用方法（关掉梯子后运行）:
    .venv/bin/python3 download_bge_m3.py
"""

import os

# 设置使用 ModelScope 中国站点
os.environ['MODELSCOPE_DOMAIN'] = 'modelscope.cn'

from modelscope import snapshot_download

print("=" * 60)
print("下载 BGE-M3 模型（使用 modelscope.cn 国内镜像）")
print("=" * 60)
print()
print("⚠️  请确保已关闭梯子/VPN 再运行此脚本！")
print()

# 下载模型，排除 ONNX 文件（我们用不到，且很大）
model_dir = snapshot_download(
    'BAAI/bge-m3', 
    cache_dir='./embed_model_cache',
    ignore_file_pattern=['onnx/*', '*.onnx', '*.onnx_data']  # 排除 ONNX 文件
)

print()
print("=" * 60)
print(f"✅ 下载完成！")
print(f"📁 模型路径: {model_dir}")
print("=" * 60)
print()
print("下一步: 下载完成后联系我进行测试！")
