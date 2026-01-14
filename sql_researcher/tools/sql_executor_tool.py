"""SQL execution tool with configurable database connection."""

import asyncio
from typing import Optional

import pymysql
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

# Default database configuration (from FusionSQL config)
DEFAULT_DB_CONFIG = {
    "host": "172.31.26.206",
    "port": 3306,
    "user": "ai_test",
    "password": "Netcare@13579",
    "database": "netcaredb_ai",
}


SQL_EXECUTOR_DESCRIPTION = """
Execute a SQL query against the database and return formatted results.

Use this tool after generating SQL with fusionsql_query to get actual data.
The results will be returned as a formatted markdown table.

IMPORTANT: Only use SELECT queries. Do not use INSERT, UPDATE, DELETE, or other modifying statements.
"""


@tool(description=SQL_EXECUTOR_DESCRIPTION)
def execute_sql(
    sql: str,
    max_rows: int = 100
) -> str:
    """Execute SQL query and return formatted results.

    Args:
        sql: SQL query to execute (SELECT only)
        max_rows: Maximum number of rows to return (default 100)

    Returns:
        Formatted query results as markdown table or error message
    """
    # Security check - only allow SELECT queries
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for safety reasons."

    # Check for dangerous keywords
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "CREATE"]
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return f"Error: Query contains forbidden keyword '{keyword}'"

    try:
        connection = pymysql.connect(
            host=DEFAULT_DB_CONFIG["host"],
            port=DEFAULT_DB_CONFIG["port"],
            user=DEFAULT_DB_CONFIG["user"],
            password=DEFAULT_DB_CONFIG["password"],
            database=DEFAULT_DB_CONFIG["database"],
            charset='utf8mb4',
            connect_timeout=10,
            read_timeout=30
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)

                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()

                if not rows:
                    return "Query executed successfully but returned no results."

                # Limit rows
                total_rows = len(rows)
                rows = rows[:max_rows]

                # Build markdown table
                # Truncate long values for display
                def truncate_value(val, max_len=50):
                    s = str(val) if val is not None else "NULL"
                    return s[:max_len] + "..." if len(s) > max_len else s

                header = "| " + " | ".join(columns) + " |"
                separator = "|" + "|".join(["---"] * len(columns)) + "|"
                data_rows = "\n".join([
                    "| " + " | ".join(truncate_value(cell) for cell in row) + " |"
                    for row in rows
                ])

                result = f"""
## Query Results

**Rows returned:** {total_rows}

{header}
{separator}
{data_rows}
"""
                if total_rows > max_rows:
                    result += f"\n\n*Showing first {max_rows} of {total_rows} rows*"

                return result

        finally:
            connection.close()

    except pymysql.Error as e:
        return f"Database Error: {str(e)}"
    except Exception as e:
        return f"Error executing SQL: {str(e)}"


@tool(description="Test database connection")
def test_db_connection() -> str:
    """Test if the database connection is working.

    Returns:
        Connection status message
    """
    try:
        connection = pymysql.connect(
            host=DEFAULT_DB_CONFIG["host"],
            port=DEFAULT_DB_CONFIG["port"],
            user=DEFAULT_DB_CONFIG["user"],
            password=DEFAULT_DB_CONFIG["password"],
            database=DEFAULT_DB_CONFIG["database"],
            charset='utf8mb4',
            connect_timeout=5
        )
        connection.close()
        return f"Database connection successful: {DEFAULT_DB_CONFIG['database']}@{DEFAULT_DB_CONFIG['host']}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"
