from models.langchain_model import text2sql_chain, sql_rewrite_chain
from utils.db_utils import extract_sql, abbr_process
from langchain_community.utilities import SQLDatabase
import datetime
import logging
import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from config import mysql_uri
from utils.utils import DecimalEncoder
from decimal import Decimal


# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# 创建FastAPI应用
app = FastAPI(title="数据查询WebSocket服务器", description="基于FastAPI的WebSocket数据查询服务")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket端点，仅处理数据查询请求

    Args:
        websocket: FastAPI WebSocket连接对象
    """
    await websocket.accept()

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()

            try:
                # 解析JSON消息
                message = json.loads(data)

                if message.get("type") == "query":
                    query_text = message.get("query", "")

                    # 使用查询函数
                    result = await data_query_websocket(websocket, query_text)
                    
                    # 发送最终查询结果
                    if result.get("status") == "success":
                        try:
                            # 尝试解析结果数据
                            if isinstance(result.get("result"), str):
                                result_data = eval(result.get("result"))
                                row_count = len(result_data)
                            else:
                                result_data = result.get("result", [])
                                row_count = len(result_data)

                            response = {
                                "type": "query_result",
                                "status": "success",
                                "query": query_text,
                                "sql": result.get("sql"),
                                "result": result_data,
                                "row_count": row_count,
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                        except Exception:
                            response = {
                                "type": "query_result",
                                "status": "success",
                                "query": query_text,
                                "sql": result.get("sql"),
                                "result": str(result.get("result")),
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                    else:
                        response = {
                            "type": "query_result",
                            "status": "error",
                            "query": query_text,
                            "error": result.get("message"),
                            "timestamp": datetime.datetime.now().isoformat()
                        }

                    response_json = json.dumps(response, cls=DecimalEncoder, ensure_ascii=False)
                    logger.info(f"WebSocket发送: 查询结果JSON - {response_json}")
                    await websocket.send_text(response_json)

                    done_flag = 'FLAG_DONE'
                    logger.info(f"WebSocket发送: {done_flag}")
                    await websocket.send_text(done_flag)

            except json.JSONDecodeError:
                done_flag = 'FLAG_DONE'
                logger.info(f"WebSocket发送: {done_flag} (JSON解码错误)")
                await websocket.send_text(done_flag)

            except Exception as e:
                done_flag = 'FLAG_DONE'
                logger.info(f"WebSocket发送: {done_flag} (异常处理);报错信息: {e}")
                await websocket.send_text(done_flag)

    except WebSocketDisconnect:
        pass



async def data_query_websocket(websocket: WebSocket, query: str):
    """
    支持WebSocket返回的数据查询函数

    Args:
        websocket: WebSocket连接对象
        query (str): 查询文本

    Returns:
        dict: 包含状态、SQL语句和查询结果的字典
    """
    try:
        # 发送开始状态
        status_msg = "正在处理查询请求..."
        logger.info(f"WebSocket发送: {status_msg}")
        await websocket.send_text(status_msg)

        # 生成SQL语句
        status_msg = "正在调用text2sql模型生成SQL语句..."
        logger.info(f"WebSocket发送: {status_msg}")
        await websocket.send_text(status_msg)
        
        # sql_content = await text2sql_chain.ainvoke({"query": query, "schema": schema})

        async def query_insight_generator(chain, query: str, schema: str, ):
            async for chunk in chain.astream({ 
                "query": query, "schema": schema, 
                }):
                yield chunk  # 逐个 token 输出
                await asyncio.sleep(0.01)  # 可选：控制流速

        full_content = []
        async for chunk in query_insight_generator(text2sql_chain, query, schema,):
            chunk_msg = chunk.content
            logger.info(f"WebSocket发送流式chunk: {chunk_msg}")
            await websocket.send_text(chunk_msg)  # 将每个 chunk 发送给客户端
            full_content.append(chunk_msg)

        done_msg = 'DONE'
        logger.info(f"WebSocket发送: {done_msg}")
        await websocket.send_text(done_msg)
        candidate_sql_sentence = ''.join(full_content)

        # 从内容中提取SQL
        extract_sql_sentence = extract_sql(candidate_sql_sentence)

        # 处理部门缩写
        sql_sentence_dept = abbr_process(extract_sql_sentence, distinct_dept_dict)

        # 处理项目缩写
        sql_sentence_proj = abbr_process(sql_sentence_dept, distinct_project_dict)
        sql_sentence = sql_sentence_proj

        if sql_sentence is None:
            error_msg = "SQL语句生成失败"
            logger.info(f"WebSocket发送: {error_msg}")
            await websocket.send_text(error_msg)
            return {"status": "error", "message": "SQL语句生成失败"}

        final_sql_msg = f"最终SQL语句: {sql_sentence}"
        logger.info(f"WebSocket发送: {final_sql_msg}")
        await websocket.send_text(final_sql_msg)

        # 执行SQL查询
        try:
            exec_msg = "正在执行SQL查询..."
            logger.info(f"WebSocket发送: {exec_msg}")
            await websocket.send_text(exec_msg)
            result = mysql_db.run(sql_sentence, include_columns=True)
            if isinstance(result, str):
                result_data = eval(result)
                row_count = len(result_data)
            else:
                result_data = result
                row_count = len(result)
           
            success_msg = f"SQL查询成功，结果行数: {row_count}"
            logger.info(f"WebSocket发送: {success_msg}")
            await websocket.send_text(success_msg)
           
        except Exception as e:
            error_msg = f"SQL查询失败: {str(e)}"
            logger.info(f"WebSocket发送: {error_msg}")
            await websocket.send_text(error_msg)

            retry_msg = "正在尝试重写SQL语句..."
            logger.info(f"WebSocket发送: {retry_msg}")
            await websocket.send_text(retry_msg)

            new_sql_command_result = await sql_rewrite_chain.ainvoke({"schema": schema, "old_sql": sql_sentence, 'error': e})
            rewrite_content_msg = f"模型重写的SQL内容: {new_sql_command_result.content}"
            logger.info(f"WebSocket发送: {rewrite_content_msg}")
            await websocket.send_text(rewrite_content_msg)

            sql_sentence = extract_sql(new_sql_command_result.content)
            rewrite_sql_msg = f"重写后的SQL语句: {sql_sentence}"
            logger.info(f"WebSocket发送: {rewrite_sql_msg}")
            await websocket.send_text(rewrite_sql_msg)

            try:
                retry_exec_msg = "正在执行重写后的SQL查询..."
                logger.info(f"WebSocket发送: {retry_exec_msg}")
                await websocket.send_text(retry_exec_msg)
                result = mysql_db.run(sql_sentence, include_columns=True)
                if isinstance(result, str):
                    result_data = eval(result)
                    row_count = len(result_data)
                else:
                    result_data = result
                    row_count = len(result)
                retry_success_msg = "重写后的SQL查询成功"
                logger.info(f"WebSocket发送: {retry_success_msg}")
                await websocket.send_text(retry_success_msg)
            except Exception as e:
                retry_error_msg = f"重写后的SQL查询仍然失败: {str(e)}"
                logger.info(f"WebSocket发送: {retry_error_msg}")
                await websocket.send_text(retry_error_msg)
                result = str(e)
                result_data = result
       
        return {"status": "success", "sql": sql_sentence, "result": result_data}

    except Exception as e:
        exception_msg = f"查询处理过程中发生异常: {str(e)}"
        logger.info(f"WebSocket发送: {exception_msg}")
        await websocket.send_text(exception_msg)
        return {"status": "error", "message": f"查询处理失败: {str(e)}"}


def data_query(query):
    """
    原始数据查询函数，用于向后兼容

    Args:
        query (str): 查询文本

    Returns:
        dict: 包含状态、SQL语句和查询结果的字典
    """
    logger.info(f"开始处理查询请求: {query}")

    try:
        # 生成SQL语句
        logger.info("正在调用text2sql模型生成SQL语句...")
        sql_content = text2sql_chain.invoke({"query": query, "schema": schema})
        logger.info(f"模型生成的SQL内容: {sql_content.content}")

        # 提取SQL语句
        extract_sql_sentence = extract_sql(sql_content.content)
        logger.info(f"提取的SQL语句: {extract_sql_sentence}")

        # 处理部门缩写
        logger.info("正在处理部门缩写...")
        sql_sentence_dept = abbr_process(extract_sql_sentence, distinct_dept_dict)
        if extract_sql_sentence != sql_sentence_dept:
            logger.info(f"部门缩写处理后的SQL: {sql_sentence_dept}")

        # 处理项目缩写
        logger.info("正在处理项目缩写...")
        sql_sentence_proj = abbr_process(sql_sentence_dept, distinct_project_dict)
        if sql_sentence_proj != sql_sentence_dept:
            logger.info(f"项目缩写处理后的SQL: {sql_sentence_proj}")

        sql_sentence = sql_sentence_proj

        if sql_sentence is None:
            logger.error("SQL语句生成失败")
            return {"status": "error", "message": "SQL语句生成失败"}

        logger.info(f"最终SQL语句: {sql_sentence}")

        # 执行SQL查询
        try:
            logger.info("正在执行SQL查询...")
            result = mysql_db.run(sql_sentence, include_columns=True)
            if isinstance(result, str):
                result_data = eval(result)
                row_count = len(result_data)
            else:
                result_data = result
                row_count = len(result)
            logger.info(f"SQL查询成功，结果行数: {row_count}")
        except Exception as e:
            logger.warning(f"SQL查询失败: {str(e)}")
            logger.info("正在尝试重写SQL语句...")

            new_sql_command_result = sql_rewrite_chain.invoke({"schema": schema, "old_sql": sql_sentence, 'error': e})
            logger.info(f"模型重写的SQL内容: {new_sql_command_result.content}")

            sql_sentence = extract_sql(new_sql_command_result.content)
            logger.info(f"重写后的SQL语句: {sql_sentence}")

            try:
                logger.info("正在执行重写后的SQL查询...")
                result = mysql_db.run(sql_sentence, include_columns=True)
                if isinstance(result, str):
                    result_data = eval(result)
                    row_count = len(result_data)
                else:
                    result_data = result
                    row_count = len(result)
                logger.info("重写后的SQL查询成功")
            except Exception as e:
                logger.error(f"重写后的SQL查询仍然失败: {str(e)}")
                result = str(e)
                result_data = result

        return {"status": "success", "sql": sql_sentence, "result": result_data}

    except Exception as e:
        logger.error(f"查询处理过程中发生异常: {str(e)}")
        return {"status": "error", "message": f"查询处理失败: {str(e)}"}




def initialize_data():
    """初始化数据库连接和数据字典"""
    global mysql_db, distinct_project_dict, distinct_dept_dict, schema

    logger.info("正在初始化数据库连接...")

    # 初始化数据库连接
    mysql_db = SQLDatabase.from_uri(mysql_uri)
    logger.info("数据库连接成功")

    # 获取项目信息
    logger.info("正在加载项目字典...")
    proj_info = mysql_db.run('SELECT DISTINCT PROJECT_NAME FROM WH_MEMBER_T where PROJECT_NAME IS NOT NULL', include_columns=True)
    distinct_project_dict = {'PROJECT_NAME': [d['PROJECT_NAME'] for d in eval(proj_info)]}
    logger.info(f"加载了{len(distinct_project_dict['PROJECT_NAME'])}个项目名称")

    # 获取部门信息
    logger.info("正在加载部门字典...")
    dept_info = mysql_db.run('SELECT DISTINCT `DEPT` FROM WH_MEMBER_T where `DEPT` IS NOT NULL', include_columns=True)
    department_name_info = mysql_db.run('SELECT DISTINCT `DEPARTMENT_NAME` FROM WH_MEMBER_T where `DEPARTMENT_NAME` IS NOT NULL', include_columns=True)

    distinct_dept_dict = {
        'DEPT': [d['DEPT'] for d in eval(dept_info)],
        'DEPARTMENT_NAME': [d['DEPARTMENT_NAME'] for d in eval(department_name_info)]
    }
    logger.info(f"加载了{len(distinct_dept_dict['DEPT'])}个部门代码和{len(distinct_dept_dict['DEPARTMENT_NAME'])}个部门名称")

    # 加载数据库模式
    logger.info("正在加载数据库模式...")
    try:
        with open('schema_renxiao.txt', 'r', encoding='utf-8') as f:
            contents = f.readlines()
        schema = ''.join(contents)
        logger.info("数据库模式加载成功")
    except FileNotFoundError:
        logger.error("schema_renxiao.txt文件未找到")
        raise
    except Exception as e:
        logger.error(f"加载数据库模式失败: {str(e)}")
        raise

    logger.info("数据初始化完成")


def test_query():
    """测试查询功能"""
    logger.info("正在执行测试查询...")
    query = '一共有多少条数据'

    result = data_query(query)

    if result.get("status") == "success":
        logger.info(f"测试查询成功")
        logger.info(f"生成的SQL: {result.get('sql')}")
        logger.info(f"查询结果: {result.get('result')}")
    else:
        logger.error(f"测试查询失败: {result.get('message')}")



if __name__ == '__main__':
    try:
        # 初始化数据
        initialize_data()

        # 执行测试查询
        test_query()

        logger.info("启动FastAPI服务器...")
        logger.info("访问 http://localhost:8000 进行测试")
        logger.info("WebSocket连接地址: ws://localhost:8000/ws")

        # 使用uvicorn运行服务器
        import uvicorn
        uvicorn.run(
            app,
            host="localhost",
            port=8000,
            log_level="info"
        )

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
    