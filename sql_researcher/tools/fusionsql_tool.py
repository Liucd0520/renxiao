"""FusionSQL tool wrapper for LangGraph integration.

支持同步和异步调用。
"""

import sys
import os
from typing import List, Optional, Annotated

from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig

# Add FusionSQL to path
FUSIONSQL_PATH = "/Users/jason/Documents/实习/理想实习/FusionSQL"
if FUSIONSQL_PATH not in sys.path:
    sys.path.insert(0, FUSIONSQL_PATH)

# Lazy loading for FusionSQL pipeline
_sync_pipeline = None
_async_pipeline = None


def get_fusionsql_pipeline():
    """Lazy initialization of sync FusionSQL pipeline."""
    global _sync_pipeline
    if _sync_pipeline is None:
        import sys
        import io
        
        # 抑制初始化时的输出
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        
        try:
            from fusionsql import TextToSQL
            _sync_pipeline = TextToSQL(enable_lsh=True)  # 启用 LSH 三路融合检索
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    return _sync_pipeline


def get_async_fusionsql_pipeline():
    """Lazy initialization of async FusionSQL pipeline."""
    global _async_pipeline
    if _async_pipeline is None:
        import sys
        import io
        
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        
        try:
            from fusionsql.pipeline import AsyncTextToSQL
            _async_pipeline = AsyncTextToSQL(enable_lsh=True)  # 启用 LSH 三路融合检索
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    return _async_pipeline


FUSIONSQL_TOOL_DESCRIPTION = """
Use this tool to convert a natural language question about database data into SQL.

The tool will:
1. Find relevant database tables based on the question using BGE-M3 retrieval
2. Generate appropriate SQL query using LLM
3. Return the SQL query and retrieved table information

Input: A natural language question about the database (in Chinese or English)
Output: Generated SQL query with table information

Examples:
- "现在平台上有多少家客户" -> SELECT COUNT(*) FROM t_bz_config_customer
- "设备ciscoA上个月发生了几次告警" -> SELECT with JOIN on event_history
"""


@tool(description=FUSIONSQL_TOOL_DESCRIPTION)
async def fusionsql_query(
    question: str,
    top_k: int = 10
) -> str:
    """Convert natural language question to SQL using FusionSQL (async version).

    Args:
        question: Natural language question about database data
        top_k: Number of tables to retrieve (default 10)

    Returns:
        Formatted string with SQL query and table information
    """
    try:
        # 使用异步 Pipeline
        pipeline = get_async_fusionsql_pipeline()
        result = await pipeline.run_with_details(question, top_k=top_k)

        # 极简输出格式
        tables = ', '.join(result['retrieved_tables'][:3])
        sql = result['sql']
        
        output = f"""成功生成SQL。

相关表: {tables}

SQL语句:
{sql}

请你现在调用 execute_sql 执行上面的 SQL 语句。"""
        return output

    except Exception as e:
        return f"错误: {str(e)}"


@tool(description=FUSIONSQL_TOOL_DESCRIPTION.replace("fusionsql_query", "fusionsql_query_sync"))
def fusionsql_query_sync(
    question: str,
    top_k: int = 10
) -> str:
    """Convert natural language question to SQL using FusionSQL (sync version).

    Args:
        question: Natural language question about database data
        top_k: Number of tables to retrieve (default 10)

    Returns:
        Formatted string with SQL query and table information
    """
    import concurrent.futures
    
    def _run_pipeline(q: str, k: int):
        pipeline = get_fusionsql_pipeline()
        return pipeline.run_with_details(q, top_k=k)
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_pipeline, question, top_k)
            result = future.result(timeout=120)

        tables = ', '.join(result['retrieved_tables'][:3])
        sql = result['sql']
        
        output = f"""成功生成SQL。

相关表: {tables}

SQL语句:
{sql}

请你现在调用 execute_sql 执行上面的 SQL 语句。"""
        return output

    except Exception as e:
        return f"错误: {str(e)}"


@tool(description="Get detailed information about a specific database table schema")
def get_table_schema(table_name: str) -> str:
    """Get schema information for a specific table.

    Args:
        table_name: Name of the database table

    Returns:
        Table schema information including columns and descriptions
    """
    try:
        pipeline = get_fusionsql_pipeline()

        if hasattr(pipeline, 'generator') and hasattr(pipeline.generator, 'schemas'):
            schema = pipeline.generator.schemas.get(table_name)
            if schema:
                columns_info = []
                for col in schema.get('columns', []):
                    col_desc = col.get('description') or 'No description'
                    columns_info.append(
                        f"  - {col['name']} ({col['type']}): {col_desc}"
                    )

                output = f"""
## Table: {table_name}

**Description:** {schema.get('llm_description', 'No description')}

**Columns:**
{chr(10).join(columns_info)}
"""
                return output

        return f"Table '{table_name}' not found in schema cache"

    except Exception as e:
        return f"Error getting table schema: {str(e)}"

