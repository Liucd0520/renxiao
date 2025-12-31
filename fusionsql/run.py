#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text-to-SQL 命令行入口

使用方法:
    # 交互模式
    python run.py
    
    # 单次查询
    python run.py --question "查询客户测试客户名下有多少设备"
    
    # 使用 32B 模型
    python run.py --model 32b
"""

import os
import sys
import argparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(
        description="Text-to-SQL 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式
  python run.py
  
  # 单次查询
  python run.py -q "查询平台上有多少客户"
  
  # 使用 32B 模型
  python run.py -q "查询告警" --model 32b
        """
    )
    parser.add_argument("-q", "--question", type=str, help="要查询的自然语言问题")
    parser.add_argument("--model", type=str, default="moe", choices=["moe", "32b"],
                        help="使用的模型：moe(默认) 或 32b")
    parser.add_argument("--top-k", type=int, default=10, help="检索 TOP-K（默认10）")
    parser.add_argument("--show-tables", action="store_true", help="显示检索到的表")
    
    args = parser.parse_args()
    
    # 延迟导入（加速帮助信息显示）
    print("正在初始化...")
    
    # 确保可以导入
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.dirname(current_dir))
    
    from fusionsql.pipeline import TextToSQL
    from fusionsql.llm import QwenLLM
    
    # 选择模型
    if args.model == "32b":
        llm = QwenLLM.create_32b()
    else:
        llm = QwenLLM.create_moe()
    
    print(f"模型: {llm.model_name}")
    
    # 初始化 Pipeline
    pipeline = TextToSQL()
    
    def process_question(question):
        """处理单个问题"""
        result = pipeline.run_with_details(question, top_k=args.top_k)
        
        if args.show_tables:
            print(f"\n检索到的表: {result['retrieved_tables'][:5]}...")
        
        print(f"\nSQL:\n{result['sql']}")
        return result['sql']
    
    if args.question:
        # 单次查询模式
        process_question(args.question)
    else:
        # 交互模式
        print("\n" + "=" * 60)
        print("Text-to-SQL 交互模式")
        print("输入自然语言问题，按回车生成 SQL")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 60)
        
        while True:
            try:
                question = input("\n问题> ").strip()
                if not question:
                    continue
                if question.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                
                process_question(question)
                
            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")


if __name__ == "__main__":
    main()
