"""
LLM 封装模块

支持多种 LLM 后端：
- Qwen2.5-Coder-32B-Instruct
- Qwen3 MoE (30B A3B) - 默认
"""

from typing import Any, Optional
import os
from openai import OpenAI


class BaseLLM:
    """LLM 基类"""
    
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class QwenLLM(BaseLLM):
    """
    Qwen 模型封装
    
    支持本地部署的 Qwen 和阿里云 DashScope
    默认使用 Qwen3 MoE 模型
    """
    
    # 预设模型配置
    MODEL_PRESETS = {
        "qwen3_moe": {
            "model_name": "qwen3_30b_a3b_2507",
            "base_url": "http://172.31.24.112:8502/v1",
            "api_key": "EMPTY",
        },
        "qwen32b": {
            "model_name": "Qwen2.5-Coder-32B-Instruct",
            "base_url": "http://172.31.24.112:33080/v1",
            "api_key": "yfzx202510",
        },
    }
    
    def __init__(
        self,
        model_name: str = None,
        api_key: str = None,
        base_url: str = None,
        temperature: float = 0,  # 温度=0 更稳定
        max_tokens: int = 4096,
        preset: str = "qwen3_moe",  # 默认使用 MoE
    ):
        """
        初始化
        
        Args:
            model_name: 模型名称（覆盖 preset）
            api_key: API 密钥（覆盖 preset）
            base_url: API 地址（覆盖 preset）
            temperature: 温度
            max_tokens: 最大输出 token 数
            preset: 预设配置，可选 "qwen3_moe"(默认) 或 "qwen32b"
        """
        # 加载预设配置
        if preset in self.MODEL_PRESETS:
            preset_config = self.MODEL_PRESETS[preset]
            self.model_name = model_name or preset_config["model_name"]
            self.base_url = base_url or preset_config["base_url"]
            self.api_key = api_key or preset_config["api_key"]
        else:
            self.model_name = model_name or "qwen3_30b_a3b_2507"
            self.base_url = base_url or os.environ.get("QWEN_BASE_URL", "http://172.31.24.112:8502/v1")
            self.api_key = api_key or os.environ.get("QWEN_API_KEY", "EMPTY")
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def complete(self, prompt: str) -> str:
        """
        生成回复
        
        Args:
            prompt: 输入提示
            
        Returns:
            生成的文本
        """
        request_params = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": 300.0,
        }
        
        # 禁用思考模式（避免 <think> 标签）
        if 'qwen' in self.model_name.lower():
            request_params["extra_body"] = {"enable_thinking": False}
        
        response = self.client.chat.completions.create(**request_params)
        return response.choices[0].message.content
    
    def __call__(self, prompt: str) -> str:
        """便捷调用"""
        return self.complete(prompt)
    
    @classmethod
    def create_moe(cls, **kwargs) -> "QwenLLM":
        """创建 Qwen3 MoE 模型实例"""
        return cls(preset="qwen3_moe", **kwargs)
    
    @classmethod
    def create_32b(cls, **kwargs) -> "QwenLLM":
        """创建 Qwen2.5-32B 模型实例"""
        return cls(preset="qwen32b", **kwargs)


# 便捷函数
def get_default_llm(**kwargs) -> QwenLLM:
    """获取默认 LLM（Qwen3 MoE）"""
    return QwenLLM.create_moe(**kwargs)


def get_qwen32b_llm(**kwargs) -> QwenLLM:
    """获取 Qwen2.5-32B LLM"""
    return QwenLLM.create_32b(**kwargs)


# 测试
if __name__ == "__main__":
    print("=== 测试 Qwen3 MoE（默认）===")
    llm_moe = QwenLLM()  # 默认 MoE
    print(f"模型: {llm_moe.model_name}")
    
    print("\n=== 测试 Qwen2.5-32B ===")
    llm_32b = QwenLLM.create_32b()
    print(f"模型: {llm_32b.model_name}")
    
    print("\n=== 测试生成 ===")
    response = llm_moe.complete("你好，请用一句话介绍你自己。")
    print(f"回复: {response[:100]}...")
