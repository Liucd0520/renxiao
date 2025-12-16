#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速批量翻译中文 Schema 到英文

直接加载已有的中文 schema，一次性翻译所有表描述。
"""

import os
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llms.qwen.QwenModel import QwenModel


BATCH_TRANSLATE_PROMPT = """Translate the following table descriptions from Chinese to English. 
Keep them concise (30-50 words each). Output format: one line per table, format "table_name: description"

{descriptions}

English translations:"""


def main():
    # 源目录（中文描述）
    cn_schema_dir = Path("./spider2_dev/schemas_table_level_enhanced/netcaredb_ai")
    
    # 目标目录（英文描述）
    en_schema_dir = Path("./spider2_dev/schemas_table_level_english/netcaredb_ai")
    en_schema_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("批量翻译中文 Schema 到英文".center(60))
    print("=" * 60)
    
    # 加载所有中文 schema
    print("加载中文 Schema...")
    cn_schemas = {}
    for json_file in cn_schema_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        table_name = data["meta_data"]["table_name"]
        cn_desc = data.get("llm_description", "")
        cn_schemas[table_name] = {
            "data": data,
            "cn_desc": cn_desc
        }
    
    print(f"✅ 加载了 {len(cn_schemas)} 张表")
    
    # 初始化 LLM
    print("初始化 LLM...")
    llm = QwenModel(model_name="qwen-turbo", temperature=0.1)
    
    # 分批翻译（每批 30 张表）
    batch_size = 30
    table_names = list(cn_schemas.keys())
    translations = {}
    
    for i in range(0, len(table_names), batch_size):
        batch = table_names[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(table_names) + batch_size - 1) // batch_size
        print(f"\n翻译批次 {batch_num}/{total_batches}...")
        
        # 构建批量翻译 prompt
        desc_lines = []
        for name in batch:
            cn_desc = cn_schemas[name]["cn_desc"]
            if cn_desc:
                desc_lines.append(f"{name}: {cn_desc}")
            else:
                desc_lines.append(f"{name}: (no description)")
        
        prompt = BATCH_TRANSLATE_PROMPT.format(descriptions="\n".join(desc_lines))
        
        try:
            response = llm.complete(prompt).text.strip()
            
            # 清理响应
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            response = re.sub(r'<think>.*', '', response, flags=re.DOTALL)
            
            # 解析翻译结果
            for line in response.split('\n'):
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    table_name = parts[0].strip().strip('`').strip('"')
                    en_desc = parts[1].strip() if len(parts) > 1 else ""
                    
                    # 尝试匹配表名
                    for name in batch:
                        if name.lower() in table_name.lower() or table_name.lower() in name.lower():
                            translations[name] = en_desc
                            break
            
            print(f"  ✅ 翻译了 {len([n for n in batch if n in translations])} 张表")
            
        except Exception as e:
            print(f"  ⚠️ 批次翻译失败: {e}")
    
    # 保存英文版 schema
    print("\n保存英文 Schema...")
    for table_name, info in cn_schemas.items():
        data = info["data"].copy()
        
        # 获取英文翻译
        en_desc = translations.get(table_name, "")
        if not en_desc:
            # 如果没翻译成功，用原始表名
            en_desc = f"Table {table_name}"
        
        data["llm_description_en"] = en_desc
        
        # 构建英文版 embedding_text
        embedding_text = en_desc
        embedding_text += f"\nTable: {table_name}"
        columns = data.get("columns", [])
        embedding_text += f"\nColumns: {', '.join([c['name'] for c in columns[:15]])}"
        data["embedding_text"] = embedding_text
        
        # 保存
        file_path = en_schema_dir / f"{table_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 生成 db_info 文件
    db_info = [{"db_id": "netcaredb_ai", "count": len(cn_schemas), "level": "table", "language": "english"}]
    parent_dir = en_schema_dir.parent
    with open(parent_dir / "db_info_table_level.json", 'w', encoding='utf-8') as f:
        json.dump(db_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！保存了 {len(cn_schemas)} 张表")
    print(f"📁 保存位置: {en_schema_dir}")
    
    # 显示几个翻译示例
    print("\n翻译示例:")
    for name in list(translations.keys())[:3]:
        cn = cn_schemas[name]["cn_desc"]
        en = translations[name]
        print(f"\n{name}:")
        print(f"  中: {cn[:60]}..." if len(cn) > 60 else f"  中: {cn}")
        print(f"  英: {en[:60]}..." if len(en) > 60 else f"  英: {en}")


if __name__ == "__main__":
    main()
