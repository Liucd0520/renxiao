import json
from decimal import Decimal



def fun():
    # 使用示例
    data = {'status': 'success', 'sql': "SELECT SUM(`PROJECTMEMBERWORKHOURS`) AS `total_workhours`\nFROM `WH_MEMBER_T`\nWHERE  `PROJECT_NAME` = '2024年三亚热线系统网络改造工程智慧政务热线服务平台软件开发项目' \nLIMIT 10;", 'result': [{'total_workhours': Decimal('12720')}]}
    return data 

if __name__ == '__main__':
    fun()
