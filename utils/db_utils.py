import re  
import sqlparse

def extract_sql(text):
    # 使用非贪婪匹配，匹配第一个 ```sql ... ```
    match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None  # 或者 raise ValueError("No SQL block found")







def unstructured_clause(sql_query, special_column):
    # 使用 sqlparse 解析 SQL 查询
    parsed = sqlparse.parse(sql_query)

    # 提取 WHERE 子句的条件
    where_clause = None
    for statement in parsed:
        if statement.get_type() == 'SELECT' or statement.get_type() == 'select':
            # 找到查询中的 WHERE 子句
            tokens = [token for token in statement.tokens if token.ttype is None]
            for token in tokens:
                if 'WHERE' in token.value or 'where' in token.value:
                    where_clause = token.value.strip()

    # 如果找到了 WHERE 子句
    if where_clause:
        # print("WHERE 子句：", where_clause)
        where_clause = where_clause.replace('WHERE', '').replace('where', '')

        # 查找所有包含 `内容描述` 字段的条件
        conditions = []
        # 处理连接符 AND 和 OR
        # 将 AND 和 OR 替换为统一的符号，便于后续分割
        where_clause = where_clause.replace(' and ', ' AND ').replace('or', ' OR ')

        # 分割 WHERE 子句为独立的条件
        tokens = where_clause.split('AND')
        all_conditions = []
        for token in tokens:
            or_conditions = token.split('OR')
            for condition in or_conditions:
                all_conditions.append(condition.strip())

        # 查找包含 `内容描述` 字段的条件
        for condition in all_conditions:
            if special_column in condition: # special_column = related_columns[-1]
                conditions.append(condition.strip().replace('(', '').replace(')', ''))
        
        return conditions
    else:
        return []



def unstructure_value_extract(sql_query, abbr_field_list):

    conditions = []
    for abbr_field in abbr_field_list:
        condition = unstructured_clause(sql_query, abbr_field)
        conditions.extend(condition)

    value_dict = {}
    for condintion in conditions:
        if ' LIKE ' in condintion or ' like ' in condintion:
            pattern = r'like\s*([\'"])(.*?)\1'
            match = re.search(pattern, condintion, re.IGNORECASE)  # re.IGNORECASE 不缺乏大小写
            value = match.group(2)
            value = value.replace('%', '')  # 去掉like 后面的%
                
        elif '=' in condintion:
            pattern = r'=\s*([\'"])(.*?)\1' 
            match = re.search(pattern, condintion)
            
            value = match.group(2)
        
        # 3. IN 语句 暂不处理
        else:
            value = ''

        value_dict.update({condintion: value})  
    
    return value_dict




def keyword_matching(substring, main_strings):
    """
    查找并返回main_strings中所有包含substring所有字符的字符串。
    
    :param substring: 子串
    :param main_strings: 主字符串列表
    :return: 包含所有匹配成功的主字符串的列表
    """
    def check_all_chars_in_string(substring, main_string):
        for char in substring:
            if char not in main_string:
                return False
        return True

    matching_strings = []
    for main_string in main_strings:
        if check_all_chars_in_string(substring, main_string):
            matching_strings.append(main_string)

    return matching_strings

def sql_abbr_rewrite(sql_command: str, abbr_dict: dict, distinct_dept_dict: dict) -> str:
    """
    将 SQL 中涉及缩写的列替换为满足缩写匹配条件的字段值。
    
    优先在 'DEPT' 中匹配，其次在 'DEPARTMENT_NAME' 中匹配。
    """
    # 定义匹配优先级顺序
    priority_fields = list(distinct_dept_dict.keys())  # ['DEPT', 'DEPARTMENT_NAME']
    
    for ori_cmd, abbr_str in abbr_dict.items():
        matched_value = None
        matched_field = None
        
        for field in priority_fields:
            candidates = keyword_matching(abbr_str, distinct_dept_dict[field])
            if candidates:
                matched_value = candidates[0]  # 假设只取第一个匹配项
                matched_field = field
                break  # 找到就停止，按优先级
        
        if matched_value is not None:
            sql_command = sql_command.replace(
                ori_cmd, 
                f" `{matched_field}` = '{matched_value}' "
            )
        # 如果都没匹配上，可以选择保留原样（当前行为），或记录警告（可选）
    
    return sql_command

def abbr_process(sql_command, distinct_dept_dict):

    abbr_field_list = list(distinct_dept_dict.keys())
    abbr_dict = unstructure_value_extract(sql_command, abbr_field_list)       
    new_sql_command = sql_abbr_rewrite(sql_command, abbr_dict,distinct_dept_dict)

    return new_sql_command 


if __name__ == '__main__':
    # 没有处理 IN 的问题；比如DEPT IN (xxx, xxx)

    sql_command = """ SELECT * FROM table where `DEPARTMENT_NAME` LIKE '%大数据部%'  AND DEPT = '智能云网' AND `PROJECT_NAME` LIKE '%业管中心运营数据分析%' """


    distinct_dept_dict ={
            'DEPT': ["大数据事业部", "研发中心", "纪委办公室", "金融数智事业部", "办公室", "运营商数智事业部", "智能云网事业部", "人力资源部", "智慧城市事业部", "营销部", "智能视频事业部", "工业数智事业部", "智能通信事业部", "信创与安全事业部"],
            "DEPARTMENT_NAME": ["政务行业应用业务部", "政务数据治理业务部", "电信电子渠道业务部"]
        }
    distinct_project_dict = {
        "PROJECT_NAME": ['2023年业管中心运营数据分析服务项目 ', 'LX2024-DS063-统一门户与企业系统总线系统']
    }

    new_sql = abbr_process(sql_command, distinct_dept_dict)
    print(new_sql)
    res = abbr_process(new_sql, distinct_project_dict)
    print(res)





# def sql_abbr_rewrite(sql_command: str,  abbr_dict: dict, distinct_dept_dict:dict):
#     """
#     将sql中某写列是涉及缩写的，找出来替换成 满足缩写匹配条件的字段值
#     """


#     for ori_cmd, abbr_str in abbr_dict.items():  

#         abbr_values = keyword_matching(abbr_str, distinct_dept_dict['DEPT'])
#         if abbr_values: # 意味着匹配上了
#             abbr_values = abbr_values[0] # 默认只会匹配到一个
#             sql_command = sql_command.replace(ori_cmd, f""" `DEPT` = '{abbr_values}' """)
#         else:
#             abbr_values = keyword_matching(abbr_str, distinct_dept_dict['DEPARTMENT_NAME'])
#             if abbr_values:
#                 abbr_values = abbr_values[0] # 默认只会匹配到一个
#                 sql_command = sql_command.replace(ori_cmd, f""" `DEPARTMENT_NAME` = '{abbr_values}' """)
    
#     return sql_command
