from typing import Any
import os
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback
from openai import OpenAI
from config import *

class QwenModel(CustomLLM):
    context_window: int = CONTEXT_WINDOW
    max_tokens: int = MAX_OUTPUT_TOKENS
    model_name: str = QWEN_MODEL

    temperature: float = TEMPERATURE
    is_call: bool = True
    client: Any
    is_stream: bool = False
    input_token = 0

    def __init__(self,
                 model_name: str = None,
                 api_key: str = None,
                 base_url: str = None,
                 is_call: bool = True,
                 temperature: float = None,
                 max_token: int = None,
                 stream: bool = None,
                 **kwargs):
        super().__init__(**kwargs)  # 调用父类构造函数
        api_key = QWEN_API_KEY if not api_key else api_key
        # 支持自定义 base_url，优先使用传入的参数，否则从 config 读取
        if base_url is None:
            base_url = getattr(globals().get('config'), 'QWEN_BASE_URL', None) or \
                       globals().get('QWEN_BASE_URL', None) or \
                       "https://dashscope.aliyuncs.com/compatible-mode/v1"

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model_name = self.model_name if not model_name else model_name
        self.is_call = is_call  # is_call 为真时调用 llm 并返回交互结果，is_call 为假时仅返回调用提示词
        self.temperature = self.temperature if not temperature else temperature
        self.max_tokens = self.max_tokens if not max_token else max_token
        self.is_stream = stream if stream else self.is_stream

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.max_tokens,
            model_name=self.model_name,
        )

    def set_api_key(self, api_key: str):
        self.client.api_key = api_key

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        # print(prompt)
        # print("----------------------------------------------")
        if self.is_call:
            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "stream": self.is_stream,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "timeout": 300.0,
            }

            # 对于 Qwen3 等支持思考模式的模型，添加 extra_body 来禁用思考
            # 这会让模型直接输出结果，不输出 <think> 标签
            if 'qwen' in self.model_name.lower() or 'Qwen' in self.model_name:
                request_params["extra_body"] = {"enable_thinking": False}

            response = self.client.chat.completions.create(**request_params)
            if not self.is_stream:
                completion_response = response.choices[0].message.content
                # self.input_token += response.usage.prompt_tokens
            else:
                completion_response = ""
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                        pass
                        # print(delta.reasoning_content, end='', flush=True)
                    else:
                        completion_response += delta.content

        else:
            completion_response = prompt

        return CompletionResponse(text=completion_response)

    @llm_completion_callback()
    def stream_complete(
            self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        response = ""
        for token in self.dummy_response:
            response += token
            yield CompletionResponse(text=response, delta=token)


if __name__ == "__main__":
    question_text = """桌子上有4个苹果，小红吃了1个，小刚拿走了2个，还剩下几个苹果？"""
    llm = QwenModel(model_name="deepseek-r1", max_token=8192)
    answer = llm.complete(question_text).text
    print(answer)
