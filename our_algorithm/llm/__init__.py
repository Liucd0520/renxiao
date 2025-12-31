"""
LLM 子模块

支持 Qwen3 MoE（默认）和 Qwen2.5-32B
"""

from .qwen import QwenLLM, BaseLLM, get_default_llm, get_qwen32b_llm

__all__ = ["QwenLLM", "BaseLLM", "get_default_llm", "get_qwen32b_llm"]
