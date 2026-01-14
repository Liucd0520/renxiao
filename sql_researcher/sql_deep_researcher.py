"""Main LangGraph implementation for SQL Deep Research agent."""

import asyncio
import json
import re
import sys
import uuid
from datetime import datetime
from typing import Literal, List, Dict, Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    filter_messages,
    get_buffer_string,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from sql_researcher.sql_configuration import SQLConfiguration
from sql_researcher.sql_state import (
    SQLAgentState,
    SQLAgentInputState,
    SQLSupervisorState,
    SQLResearcherState,
    SQLResearcherOutputState,
    ClarifyWithUser,
    DecomposeResult,
    ConductSQLResearch,
    SQLResearchComplete,
)
from sql_researcher.sql_prompts import (
    sql_clarify_instructions,
    sql_decompose_prompt,
    sql_supervisor_prompt,
    sql_researcher_prompt,
    sql_compress_research_prompt,
    sql_final_report_prompt,
)
from sql_researcher.tools.fusionsql_tool import fusionsql_query, get_table_schema
from sql_researcher.tools.sql_executor_tool import execute_sql

# Initialize configurable model
configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "api_key"),
)


def get_today_str() -> str:
    """Get current date formatted for display."""
    now = datetime.now()
    return f"{now:%Y-%m-%d}"


def get_api_key_for_model(model_name: str, config: RunnableConfig):
    """Get API key based on model prefix."""
    import os
    model_lower = model_name.lower()
    if model_lower.startswith("openai:"):
        return os.getenv("OPENAI_API_KEY")
    elif model_lower.startswith("anthropic:"):
        return os.getenv("ANTHROPIC_API_KEY")
    return None


def parse_qwen_tool_calls(response: AIMessage) -> AIMessage:
    """Parse Qwen's custom tool call format and inject tool_calls into AIMessage.

    Qwen outputs tool calls in various formats:
    1. <tools>{"name": "tool_name", "arguments": {...}}</tools>
    2. Raw JSON: {"name": "tool_name", "arguments": {...}}
    3. Multiple tool calls

    This function parses these formats and creates proper tool_calls.
    """
    if response.tool_calls:
        # Already has tool calls, no need to parse
        return response

    content = response.content
    if not content:
        return response

    tool_calls = []
    clean_content = content

    # Method 1: Try <tools>...</tools> or <C>...</C> format (Qwen variants)
    for tag in ["tools", "C", "tool"]:
        if f"<{tag}>" in content:
            tool_pattern = rf'<{tag}>\s*(.*?)\s*</{tag}>'
            matches = re.findall(tool_pattern, content, re.DOTALL)

            for match in matches:
                parsed = _parse_json_tool_call(match.strip())
                if parsed:
                    tool_calls.extend(parsed)

            if tool_calls:
                clean_content = re.sub(tool_pattern, '', content, flags=re.DOTALL).strip()
                break

    # Method 2: Try raw JSON format (entire content is a tool call)
    if not tool_calls and content.strip().startswith('{'):
        parsed = _parse_json_tool_call(content.strip())
        if parsed:
            tool_calls.extend(parsed)
            clean_content = ""

    # Method 3: Try to find JSON objects in the content (handle nested braces)
    if not tool_calls:
        # Find position of "name" and extract the surrounding JSON object
        idx = 0
        while True:
            # Find next occurrence of "name"
            name_pos = content.find('"name"', idx)
            if name_pos == -1:
                break
            
            # Find the opening brace before "name"
            brace_pos = content.rfind('{', 0, name_pos)
            if brace_pos == -1:
                idx = name_pos + 1
                continue
            
            # Count braces to find matching closing brace
            brace_count = 0
            end_pos = brace_pos
            for i, char in enumerate(content[brace_pos:], start=brace_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            
            if end_pos > brace_pos:
                candidate = content[brace_pos:end_pos]
                parsed = _parse_json_tool_call(candidate)
                if parsed:
                    tool_calls.extend(parsed)
                    clean_content = content.replace(candidate, '').strip()
            
            idx = end_pos if end_pos > brace_pos else name_pos + 1

    if tool_calls:
        return AIMessage(
            content=clean_content,
            tool_calls=tool_calls,
            id=response.id
        )

    return response


def _parse_json_tool_call(text: str) -> List[Dict[str, Any]]:
    """Parse a JSON string as tool call(s)."""
    tool_calls = []

    try:
        tool_data = json.loads(text)

        # Handle single tool call
        if isinstance(tool_data, dict) and "name" in tool_data:
            name = tool_data.get("name")
            args = tool_data.get("arguments") or tool_data.get("args", {})
            if name:
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "name": name,
                    "args": args if isinstance(args, dict) else {}
                })

        # Handle list of tool calls
        elif isinstance(tool_data, list):
            for item in tool_data:
                if isinstance(item, dict) and "name" in item:
                    name = item.get("name")
                    args = item.get("arguments") or item.get("args", {})
                    if name:
                        tool_calls.append({
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "name": name,
                            "args": args if isinstance(args, dict) else {}
                        })

    except json.JSONDecodeError:
        # Try to split multiple JSON objects
        try:
            parts = re.split(r'\}\s*\{', text)
            for i, part in enumerate(parts):
                if len(parts) == 1:
                    json_str = part
                elif i == 0:
                    json_str = part + '}'
                elif i == len(parts) - 1:
                    json_str = '{' + part
                else:
                    json_str = '{' + part + '}'

                try:
                    tool_data = json.loads(json_str)
                    name = tool_data.get("name")
                    args = tool_data.get("arguments") or tool_data.get("args", {})
                    if name:
                        tool_calls.append({
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "name": name,
                            "args": args if isinstance(args, dict) else {}
                        })
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass

    return tool_calls


@tool(description="Strategic reflection tool for research planning")
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress."""
    return f"Reflection recorded: {reflection}"


# ============ Node Functions ============

async def clarify_with_user(
    state: SQLAgentState, config: RunnableConfig
) -> Command[Literal["decompose_question", "__end__"]]:
    """Analyze user messages and ask clarifying questions if needed."""
    configurable = SQLConfiguration.from_runnable_config(config)

    if not configurable.allow_clarification:
        return Command(goto="decompose_question")

    messages = state["messages"]
    model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }

    clarification_model = (
        configurable_model
        .with_structured_output(ClarifyWithUser)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(model_config)
    )

    prompt_content = sql_clarify_instructions.format(
        messages=get_buffer_string(messages),
        date=get_today_str()
    )
    response = await clarification_model.ainvoke([HumanMessage(content=prompt_content)])

    if response.need_clarification:
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        return Command(
            goto="decompose_question",
            update={"messages": [AIMessage(content=response.verification)]}
        )


async def decompose_question(
    state: SQLAgentState, config: RunnableConfig
) -> Command[Literal["review_decomposition"]]:
    """Decompose complex question into SQL-answerable sub-questions."""
    configurable = SQLConfiguration.from_runnable_config(config)

    # Get feedback from previous decomposition attempt (if any)
    feedback_list = state.get("decomposition_feedback", [])
    feedback = " ".join(feedback_list) if feedback_list else ""
    
    if feedback:
        print(f"[DEBUG decompose_question] Using feedback: {feedback}")

    model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }

    decompose_model = (
        configurable_model
        .with_structured_output(DecomposeResult)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(model_config)
    )

    base_question = get_buffer_string(state.get("messages", []))
    
    # Include feedback in prompt if available
    if feedback:
        prompt = sql_decompose_prompt.format(
            question=f"""{base_question}

===== 用户反馈 =====
用户对之前的问题拆解不满意，请根据以下反馈重新拆解：
"{feedback}"
请务必按照用户的反馈调整子问题！
====================""",
            date=get_today_str()
        )
    else:
        prompt = sql_decompose_prompt.format(
            question=base_question,
            date=get_today_str()
        )

    response = await decompose_model.ainvoke([HumanMessage(content=prompt)])

    return Command(
        goto="review_decomposition",
        update={
            "research_brief": response.research_strategy,
            "sub_questions": response.sub_questions,
        }
    )


async def review_decomposition(
    state: SQLAgentState, config: RunnableConfig
) -> Command[Literal["decompose_question", "sql_research_supervisor", "final_sql_report"]]:
    """Review decomposed questions with human-in-the-loop.

    This node uses interrupt to get user feedback on the decomposed sub-questions.
    If user approves, proceed to research. If user provides feedback, go back to decompose.
    
    优化：如果 enable_parallel_bypass=True，跳过 Supervisor 直接并行执行所有研究。
    """
    configurable = SQLConfiguration.from_runnable_config(config)

    # DEBUG: 打印配置值
    print(f"[DEBUG review_decomposition] enable_decomposition_review = {configurable.enable_decomposition_review}")
    print(f"[DEBUG review_decomposition] enable_parallel_bypass = {configurable.enable_parallel_bypass}")

    sub_questions = state.get("sub_questions", [])
    research_brief = state.get("research_brief", "")

    # Skip review if disabled
    if not configurable.enable_decomposition_review:
        # 如果启用并行旁路，直接执行所有研究
        if configurable.enable_parallel_bypass:
            return await _execute_parallel_research(sub_questions, research_brief, config)
        
        # 否则走原来的 Supervisor 流程
        sub_q_text = "\n".join([
            f"{q.id}. {q.question} (依赖: {q.depends_on if q.depends_on else '无'})"
            for q in sub_questions
        ])
        
        supervisor_system = sql_supervisor_prompt.format(
            date=get_today_str(),
            research_brief=research_brief,
            sub_questions=sub_q_text,
            completed_summary="暂无",
            max_concurrent_research_units=configurable.max_concurrent_research_units,
            max_researcher_iterations=configurable.max_researcher_iterations
        )
        
        return Command(
            goto="sql_research_supervisor",
            update={
                "decomposition_feedback": [],  # Clear feedback
                "supervisor_messages": {
                    "type": "override",
                    "value": [
                        SystemMessage(content=supervisor_system),
                        HumanMessage(content=research_brief)
                    ]
                }
            }
        )
    
    # Build display for user review
    sub_q_display = "\n".join([
        f"{q.id}. {q.question}"
        for q in sub_questions
    ])
    
    confirm_message = f"""我将您的问题分解为以下子问题：

{sub_q_display}

研究策略: {research_brief}

请确认这些子问题是否正确：
- 输入 'true' 或 'yes' 确认继续执行
- 或输入修改建议，我会重新分解问题"""

    user_feedback = interrupt(confirm_message)
    
    # Check if user approves
    user_approved = False
    if isinstance(user_feedback, bool) and user_feedback is True:
        user_approved = True
    elif isinstance(user_feedback, str):
        if user_feedback.lower() in ['true', 'yes', '确认', '是', 'ok', 'y']:
            user_approved = True
        else:
            # User provided feedback, go back to decompose
            print(f"[DEBUG review_decomposition] User feedback: {user_feedback}")
            return Command(
                goto="decompose_question",
                update={"decomposition_feedback": [user_feedback]}
            )
    
    if not user_approved:
        # 如果没确认，也当作需要重新分解
        return Command(
            goto="decompose_question",
            update={"decomposition_feedback": ["用户未明确确认"]}
        )
    
    # User approved - 检查是否启用并行旁路
    if configurable.enable_parallel_bypass:
        print(f"[DEBUG review_decomposition] 启用并行旁路，直接执行 {len(sub_questions)} 个研究任务")
        return await _execute_parallel_research(sub_questions, research_brief, config)
    
    # 否则走原来的 Supervisor 流程
    sub_q_text = "\n".join([
        f"{q.id}. {q.question} (依赖: {q.depends_on if q.depends_on else '无'})"
        for q in sub_questions
    ])
    
    supervisor_system = sql_supervisor_prompt.format(
        date=get_today_str(),
        research_brief=research_brief,
        sub_questions=sub_q_text,
        completed_summary="暂无",
        max_concurrent_research_units=configurable.max_concurrent_research_units,
        max_researcher_iterations=configurable.max_researcher_iterations
    )
    
    return Command(
        goto="sql_research_supervisor",
        update={
            "decomposition_feedback": [],  # Clear feedback
            "supervisor_messages": {
                "type": "override",
                "value": [
                    SystemMessage(content=supervisor_system),
                    HumanMessage(content=research_brief)
                ]
            }
        }
    )


async def _execute_parallel_research(sub_questions, research_brief, config):
    """并行执行所有子问题的研究，跳过 Supervisor。
    
    Args:
        sub_questions: 子问题列表
        research_brief: 研究简报
        config: RunnableConfig
    
    Returns:
        Command 跳转到 final_sql_report
    """
    print(f"[DEBUG _execute_parallel_research] 开始并行执行 {len(sub_questions)} 个研究任务")
    
    # 构建所有任务
    tasks = [
        sql_researcher_subgraph.ainvoke({
            "researcher_messages": [HumanMessage(content=sq.question)],
            "research_topic": sq.question,
            "context": None,  # 简化：暂不处理依赖
            "tool_call_iterations": 0
        }, config)
        for sq in sub_questions
    ]
    
    # 并行执行
    results = await asyncio.gather(*tasks)
    
    # 收集结果
    sql_results = []
    notes = []
    
    for result, sq in zip(results, sub_questions):
        compressed = result.get("compressed_research", "研究完成但无结果")
        notes.append(compressed)
        
        if result.get("sql_query"):
            sql_results.append({
                "topic": sq.question,
                "sql": result.get("sql_query"),
                "result": result.get("sql_result")
            })
    
    print(f"[DEBUG _execute_parallel_research] 完成！sql_results={len(sql_results)}, notes={len(notes)}")
    
    # 直接跳转到报告生成
    return Command(
        goto="final_sql_report",
        update={
            "sql_results": sql_results,
            "notes": notes,
            "research_brief": research_brief
        }
    )


async def sql_supervisor(
    state: SQLSupervisorState, config: RunnableConfig
) -> Command[Literal["sql_supervisor_tools"]]:
    """Supervisor that coordinates SQL research."""
    configurable = SQLConfiguration.from_runnable_config(config)

    model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }

    tools = [ConductSQLResearch, SQLResearchComplete, think_tool]

    research_model = (
        configurable_model
        .bind_tools(tools)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(model_config)
    )

    supervisor_messages = state.get("supervisor_messages", [])
    response = await research_model.ainvoke(supervisor_messages)

    # DEBUG: 打印原始响应
    print(f"[DEBUG sql_supervisor] Raw response content: {repr(response.content[:200]) if response.content else 'None'}")
    print(f"[DEBUG sql_supervisor] Raw response tool_calls: {response.tool_calls}")

    # Parse Qwen's custom <tools> format if needed
    response = parse_qwen_tool_calls(response)

    # DEBUG: 打印解析后的响应
    print(f"[DEBUG sql_supervisor] Parsed tool_calls: {response.tool_calls}")

    return Command(
        goto="sql_supervisor_tools",
        update={
            "supervisor_messages": [response],
            "research_iterations": state.get("research_iterations", 0) + 1
        }
    )


async def sql_supervisor_tools(
    state: SQLSupervisorState, config: RunnableConfig
) -> Command[Literal["sql_supervisor", "__end__"]]:
    """Execute SQL supervisor tool calls."""
    configurable = SQLConfiguration.from_runnable_config(config)
    supervisor_messages = state.get("supervisor_messages", [])
    research_iterations = state.get("research_iterations", 0)
    most_recent_message = supervisor_messages[-1]

    # Check exit conditions
    exceeded_iterations = research_iterations > configurable.max_researcher_iterations
    no_tool_calls = not most_recent_message.tool_calls
    research_complete = any(
        tc["name"] == "SQLResearchComplete"
        for tc in (most_recent_message.tool_calls or [])
    )

    # DEBUG: 打印工具调用状态
    print(f"[DEBUG sql_supervisor_tools] research_iterations={research_iterations}")
    print(f"[DEBUG sql_supervisor_tools] tool_calls={most_recent_message.tool_calls}")
    print(f"[DEBUG sql_supervisor_tools] no_tool_calls={no_tool_calls}, research_complete={research_complete}")

    if exceeded_iterations or no_tool_calls or research_complete:
        notes = [
            msg.content for msg in filter_messages(
                supervisor_messages, include_types="tool"
            )
        ]
        return Command(
            goto=END,
            update={
                "notes": notes,
                "research_brief": state.get("research_brief", "")
            }
        )

    # Process tool calls
    all_tool_messages = []
    update_payload = {"supervisor_messages": []}

    # Handle think_tool
    for tc in most_recent_message.tool_calls:
        if tc["name"] == "think_tool":
            all_tool_messages.append(ToolMessage(
                content=f"Reflection recorded: {tc['args']['reflection']}",
                name="think_tool",
                tool_call_id=tc["id"]
            ))

    # Handle ConductSQLResearch
    research_calls = [
        tc for tc in most_recent_message.tool_calls
        if tc["name"] == "ConductSQLResearch"
    ]

    if research_calls:
        allowed = research_calls[:configurable.max_concurrent_research_units]

        tasks = [
            sql_researcher_subgraph.ainvoke({
                "researcher_messages": [
                    HumanMessage(content=tc["args"]["research_topic"])
                ],
                "research_topic": tc["args"]["research_topic"],
                "context": tc["args"].get("context"),
                "tool_call_iterations": 0
            }, config)
            for tc in allowed
        ]

        results = await asyncio.gather(*tasks)

        for result, tc in zip(results, allowed):
            compressed = result.get("compressed_research", "研究完成但无法获取结果")
            all_tool_messages.append(ToolMessage(
                content=compressed,
                name=tc["name"],
                tool_call_id=tc["id"]
            ))

            if result.get("sql_query"):
                update_payload.setdefault("sql_results", []).append({
                    "topic": tc["args"]["research_topic"],
                    "sql": result.get("sql_query"),
                    "result": result.get("sql_result")
                })

    update_payload["supervisor_messages"] = all_tool_messages
    return Command(goto="sql_supervisor", update=update_payload)


async def sql_researcher(
    state: SQLResearcherState, config: RunnableConfig
) -> Command[Literal["sql_researcher_tools"]]:
    """Individual SQL researcher."""
    configurable = SQLConfiguration.from_runnable_config(config)

    model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }

    tools = [fusionsql_query, execute_sql, think_tool]

    research_model = (
        configurable_model
        .bind_tools(tools)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(model_config)
    )

    prompt = sql_researcher_prompt.format(
        date=get_today_str(),
        research_topic=state.get("research_topic", ""),
        context=state.get("context") or "无上下文"
    )

    messages = [SystemMessage(content=prompt)] + state.get("researcher_messages", [])
    response = await research_model.ainvoke(messages)

    # Parse Qwen's custom <tools> format if needed
    response = parse_qwen_tool_calls(response)

    # DEBUG: 打印 researcher LLM 响应
    print(f"[DEBUG sql_researcher] research_topic={state.get('research_topic', '')[:50]}")
    print(f"[DEBUG sql_researcher] response.content={response.content[:200] if response.content else 'None'}...")
    print(f"[DEBUG sql_researcher] tool_calls={response.tool_calls}")

    return Command(
        goto="sql_researcher_tools",
        update={
            "researcher_messages": [response],
            "tool_call_iterations": state.get("tool_call_iterations", 0) + 1
        }
    )


async def sql_researcher_tools(
    state: SQLResearcherState, config: RunnableConfig
) -> Command[Literal["sql_researcher", "compress_sql_research"]]:
    """Execute SQL researcher tool calls."""
    configurable = SQLConfiguration.from_runnable_config(config)
    researcher_messages = state.get("researcher_messages", [])
    most_recent_message = researcher_messages[-1]

    if not most_recent_message.tool_calls:
        return Command(goto="compress_sql_research")

    # Execute tools
    tools_by_name = {
        "fusionsql_query": fusionsql_query,
        "execute_sql": execute_sql,
        "think_tool": think_tool
    }

    tool_outputs = []
    sql_query = state.get("sql_query")
    sql_result = state.get("sql_result")

    for tc in most_recent_message.tool_calls:
        tool_fn = tools_by_name.get(tc["name"])
        if tool_fn:
            try:
                print(f"[DEBUG sql_researcher_tools] Executing: {tc['name']}({tc['args']})")
                result = tool_fn.invoke(tc["args"])
                print(f"[DEBUG sql_researcher_tools] Result length: {len(str(result))} chars")
            except Exception as e:
                result = f"Error: {str(e)}"
                print(f"[DEBUG sql_researcher_tools] Error: {e}")

            tool_outputs.append(ToolMessage(
                content=str(result),
                name=tc["name"],
                tool_call_id=tc["id"]
            ))

            # DEBUG: Show actual result content
            print(f"[DEBUG sql_researcher_tools] Result preview: {repr(result[:200])}")

            # Capture SQL info and FORCE execute_sql after fusionsql_query
            if tc["name"] == "fusionsql_query":
                # Extract SQL from result - try multiple formats
                extracted_sql = None
                import re
                
                # Format 1: SQL语句: followed by SQL (with or without newline)
                # Match: "SQL语句:\nSELECT..." or "SQL语句：SELECT..."
                match = re.search(r'SQL语句[：:]\s*\n?(SELECT\s+.+?;)', result, re.IGNORECASE | re.DOTALL)
                if match:
                    extracted_sql = match.group(1).strip()
                
                # Format 2: ```sql ... ```
                if not extracted_sql and "```sql" in result:
                    sql_start = result.find("```sql") + 6
                    sql_end = result.find("```", sql_start)
                    if sql_end > sql_start:
                        extracted_sql = result[sql_start:sql_end].strip()
                
                # Format 3: Direct SQL (starts with SELECT anywhere)
                if not extracted_sql:
                    match = re.search(r'(SELECT\s+.+?;)', result, re.IGNORECASE | re.DOTALL)
                    if match:
                        extracted_sql = match.group(1).strip()
                
                if extracted_sql:
                    sql_query = extracted_sql
                    print(f"[DEBUG sql_researcher_tools] Extracted SQL: {sql_query[:100]}...")
                    
                    # 🔥 FORCE execute_sql - bypass LLM decision!
                    print(f"[DEBUG sql_researcher_tools] FORCING execute_sql...")
                    try:
                        exec_result = execute_sql.invoke({"sql": sql_query})
                        sql_result = exec_result
                        print(f"[DEBUG sql_researcher_tools] execute_sql result length: {len(str(exec_result))} chars")
                        
                        # Add execute_sql result as another tool message
                        tool_outputs.append(ToolMessage(
                            content=str(exec_result),
                            name="execute_sql",
                            tool_call_id=f"forced_{tc['id']}"
                        ))
                    except Exception as e:
                        print(f"[DEBUG sql_researcher_tools] execute_sql error: {e}")
                        sql_result = f"Error executing SQL: {str(e)}"
                else:
                    print(f"[DEBUG sql_researcher_tools] Could not extract SQL from result")
                    
            elif tc["name"] == "execute_sql":
                sql_result = result

    # After forced execution, go directly to compress (skip LLM second round)
    if sql_query and sql_result:
        print(f"[DEBUG sql_researcher_tools] Forced chain complete, going to compress")
        return Command(
            goto="compress_sql_research",
            update={
                "researcher_messages": tool_outputs,
                "sql_query": sql_query,
                "sql_result": sql_result
            }
        )

    # Check exit conditions
    if state.get("tool_call_iterations", 0) >= configurable.max_react_tool_calls:
        return Command(
            goto="compress_sql_research",
            update={
                "researcher_messages": tool_outputs,
                "sql_query": sql_query,
                "sql_result": sql_result
            }
        )

    return Command(
        goto="sql_researcher",
        update={
            "researcher_messages": tool_outputs,
            "sql_query": sql_query,
            "sql_result": sql_result
        }
    )


async def compress_sql_research(
    state: SQLResearcherState, config: RunnableConfig
):
    """Compress SQL research findings."""
    configurable = SQLConfiguration.from_runnable_config(config)

    synthesizer_model = configurable_model.with_config({
        "model": configurable.compression_model,
        "max_tokens": configurable.compression_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.compression_model, config),
        "tags": ["langsmith:nostream"]
    })

    researcher_messages = state.get("researcher_messages", [])
    compression_prompt = sql_compress_research_prompt.format(date=get_today_str())

    messages = [SystemMessage(content=compression_prompt)] + researcher_messages
    response = await synthesizer_model.ainvoke(messages)

    return {
        "compressed_research": str(response.content),
        "sql_query": state.get("sql_query"),
        "sql_result": state.get("sql_result")
    }


async def final_sql_report(state: SQLAgentState, config: RunnableConfig):
    """Generate final SQL research report."""
    configurable = SQLConfiguration.from_runnable_config(config)

    writer_model_config = {
        "model": configurable.final_report_model,
        "max_tokens": configurable.final_report_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.final_report_model, config),
        "tags": ["langsmith:nostream"]
    }

    # Collect SQL queries
    sql_queries = []
    for result in state.get("sql_results", []):
        if result and result.get("sql"):
            sql_queries.append(f"-- {result.get('topic', 'Query')}\n{result['sql']}")

    sql_queries_text = "\n\n".join(sql_queries) if sql_queries else "无 SQL 查询"
    findings = "\n\n---\n\n".join(state.get("notes", []))

    prompt = sql_final_report_prompt.format(
        research_brief=state.get("research_brief", ""),
        messages=get_buffer_string(state.get("messages", [])),
        date=get_today_str(),
        findings=findings,
        sql_queries=sql_queries_text
    )

    final_report = await configurable_model.with_config(writer_model_config).ainvoke([
        HumanMessage(content=prompt)
    ])

    return {
        "final_report": final_report.content,
        "messages": [final_report],
        "notes": {"type": "override", "value": []}
    }


# ============ Build Graphs ============

# SQL Researcher Subgraph
sql_researcher_builder = StateGraph(
    SQLResearcherState,
    output=SQLResearcherOutputState,
    config_schema=SQLConfiguration
)
sql_researcher_builder.add_node("sql_researcher", sql_researcher)
sql_researcher_builder.add_node("sql_researcher_tools", sql_researcher_tools)
sql_researcher_builder.add_node("compress_sql_research", compress_sql_research)
sql_researcher_builder.add_edge(START, "sql_researcher")
sql_researcher_builder.add_edge("compress_sql_research", END)
sql_researcher_subgraph = sql_researcher_builder.compile()

# SQL Supervisor Subgraph
sql_supervisor_builder = StateGraph(SQLSupervisorState, config_schema=SQLConfiguration)
sql_supervisor_builder.add_node("sql_supervisor", sql_supervisor)
sql_supervisor_builder.add_node("sql_supervisor_tools", sql_supervisor_tools)
sql_supervisor_builder.add_edge(START, "sql_supervisor")
sql_supervisor_subgraph = sql_supervisor_builder.compile()

# Main SQL Deep Researcher Graph
sql_researcher_graph_builder = StateGraph(
    SQLAgentState,
    input=SQLAgentInputState,
    config_schema=SQLConfiguration
)
sql_researcher_graph_builder.add_node("clarify_with_user", clarify_with_user)
sql_researcher_graph_builder.add_node("decompose_question", decompose_question)
sql_researcher_graph_builder.add_node("review_decomposition", review_decomposition)
sql_researcher_graph_builder.add_node("sql_research_supervisor", sql_supervisor_subgraph)
sql_researcher_graph_builder.add_node("final_sql_report", final_sql_report)

sql_researcher_graph_builder.add_edge(START, "clarify_with_user")
# decompose_question -> review_decomposition (via Command)
# review_decomposition -> sql_research_supervisor or decompose_question (via Command)
sql_researcher_graph_builder.add_edge("sql_research_supervisor", "final_sql_report")
sql_researcher_graph_builder.add_edge("final_sql_report", END)

# Compile final graph
sql_researcher = sql_researcher_graph_builder.compile()

