from models.langchain_model import text2sql_chain, sql_rewrite_chain
from utils.db_utils import extract_sql, abbr_process
from langchain_community.utilities import SQLDatabase
from urllib.parse import quote_plus
from decimal import Decimal 
import datetime 


def data_query(query):

    sql_content = text2sql_chain.invoke({"query": query, "schema": schema})

    extract_sql_sentence = extract_sql(sql_content.content)

    sql_sentence_dept = abbr_process(extract_sql_sentence, distinct_dept_dict)
    sql_sentence_proj = abbr_process(sql_sentence_dept, distinct_project_dict)

    sql_sentence = sql_sentence_proj

    if sql_sentence is None:
        return {"message": "Failed"}

    try:
        result = mysql_db.run(sql_sentence, include_columns=True)
    except Exception as e:
        print('------------------------')
        new_sql_command_result = sql_rewrite_chain.invoke({"schema": schema, "old_sql": sql_sentence, 'error': e})
        sql_sentence = extract_sql(new_sql_command_result.content)
        try:
            result = mysql_db.run(sql_sentence, include_columns=True)
        except Exception as e:
            result = str(e) 

    return sql_sentence, result




if __name__ == '__main__':
    
    # distinct_dept_dict ={
    #         'DEPT': ["大数据事业部", "研发中心", "纪委办公室", "金融数智事业部", "办公室", "运营商数智事业部", "智能云网事业部", "人力资源部", "智慧城市事业部", "营销部", "智能视频事业部", "工业数智事业部", "智能通信事业部", "信创与安全事业部"],
    #         "DEPARTMENT_NAME": ["政务行业应用业务部", "政务数据治理业务部", "电信电子渠道业务部"]}
    # distinct_project_dict = {
    #     "PROJECT_NAME": ['2023年业管中心运营数据分析服务项目 ', 'LX2024-DS063-统一门户与企业系统总线系统', '天翼云2025年智云全域运维支撑项目']}
    

    username =  'root'
    password = 'liucd123'
    host = '172.31.24.111'
    port = 3307
    database = 'renxiao'

    encoded_password = quote_plus(password)
    mysql_uri = f'mysql+mysqlconnector://{username}:{encoded_password}@{host}:{port}/{database}'


    mysql_db = SQLDatabase.from_uri(mysql_uri)

    proj_info = mysql_db.run('SELECT DISTINCT PROJECT_NAME FROM WH_MEMBER_T where  PROJECT_NAME IS NOT NULL ', include_columns=True)
    distinct_project_dict = {'PROJECT_NAME': [d['PROJECT_NAME'] for d in eval(proj_info)]}

    dept_info = mysql_db.run('SELECT DISTINCT `DEPT` FROM WH_MEMBER_T where  `DEPT` IS NOT NULL ', include_columns=True)
    department_name_info = mysql_db.run('SELECT DISTINCT `DEPARTMENT_NAME` FROM WH_MEMBER_T where  `DEPARTMENT_NAME` IS NOT NULL ', include_columns=True)
    
    distinct_dept_dict = {'DEPT': [d['DEPT'] for d in eval(dept_info)], 
                             'DEPARTMENT_NAME': [d['DEPARTMENT_NAME'] for d in eval(department_name_info)]}
    


    with open('schema_renxiao.txt', 'r', encoding='utf-8') as f:
        contents = f.readlines()

    schema = ''.join(contents)

    import pandas as pd 
    df = pd.read_excel('问题-郑立新-2025-11-12.xlsx')
    queries = df['问题'].tolist()

    query_list = []
    sql_cmd_list = []
    sql_res_list = []
    for idx, query in enumerate(queries):
        
        # query = "智能云网部的人在智云全域运维支撑项目中共填写了多少工时"

        query_list.append(query)

        # query = '本年度，截止目前为止，谁没有填报工时'
        try:
            sql_cmd, sql_result = data_query(query)
            print(sql_cmd, sql_result)
            sql_cmd_list.append(sql_cmd)
            sql_res_list.append(sql_result)
        except Exception as e:
            print(query)
            sql_cmd_list.append('')
            sql_res_list.append([f'执行错误: {e}'])
        
        # break 

    df_res = pd.DataFrame({"query": query_list, 'sql': sql_cmd_list, 'output': sql_res_list})
    df_res.to_excel('数据集输出3.xlsx', index=False)

