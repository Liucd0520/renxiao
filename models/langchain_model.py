from langchain_openai import  ChatOpenAI
from langchain.prompts import PromptTemplate
from models.prompts import * 


model = ChatOpenAI(
    model="Qwen2.5-Coder-32B-Instruct", # "qwen3-coder", #"qwen3-max",  
    base_url='http://172.31.24.112:33080/v1',  
    api_key='yfzx202510',
    temperature=0,)

# model = ChatOpenAI(
#     model="qwen-plus", # "qwen3-coder", #"qwen3-max",  
#     base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',  
#     api_key='sk-4e27d583808849128b07458af74724a6',
#     temperature=0,)

gen_prompt = PromptTemplate(template=sql_gen_prompt, input_variables=["query", "schema"])
text2sql_chain = gen_prompt | model 



feedback_prompt = PromptTemplate(template=sql_feedback_prompt, input_variables=["schema", "old_sql", "error"])
sql_rewrite_chain = feedback_prompt | model 

if __name__ == '__main__':
    
    result = model.invoke('你好')
    print(result)

