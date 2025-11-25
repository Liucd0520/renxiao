from langchain_openai import  ChatOpenAI
from langchain.prompts import PromptTemplate
from models.prompts import * 


# model = ChatOpenAI(
#     model="Qwen2.5-Coder-32B-Instruct", # "qwen3-coder", #"qwen3-max",  
#     base_url='http://172.31.24.112:33080/v1',  
#     api_key='yfzx202510',
#     temperature=0,)

model = ChatOpenAI(
    model="GLM-4.6", # "qwen3-coder", #"qwen3-max",  
    base_url='https://open.bigmodel.cn/api/anthropic',  
    api_key='6d741c50611344c6a5568a109d534c36.ySL8zJVND7YKuTAz',
    temperature=0,)


gen_prompt = PromptTemplate(template=sql_gen_prompt, input_variables=["query", "schema"])
text2sql_chain = gen_prompt | model 



feedback_prompt = PromptTemplate(template=sql_feedback_prompt, input_variables=["schema", "old_sql", "error"])
sql_rewrite_chain = feedback_prompt | model 

if __name__ == '__main__':
    
    result = model.invoke('你好')
    print(result)

