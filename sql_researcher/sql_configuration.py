"""Configuration management for SQL Research system."""

import os
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class SQLConfiguration(BaseModel):
    """Configuration for SQL Deep Research agent."""

    # General Configuration
    max_structured_output_retries: int = Field(
        default=3,
        metadata={"description": "Maximum retries for structured output"}
    )
    allow_clarification: bool = Field(
        default=False,
        metadata={"description": "Allow clarifying questions before research"}
    )
    enable_decomposition_review: bool = Field(
        default=True,
        metadata={"description": "Enable human review of question decomposition before execution"}
    )
    max_concurrent_research_units: int = Field(
        default=10,  # 从 3 提升到 10，允许更多并行研究
        metadata={"description": "Maximum parallel SQL researchers"}
    )
    enable_parallel_bypass: bool = Field(
        default=True,
        metadata={"description": "跳过 Supervisor 直接并行执行所有研究任务"}
    )
    max_researcher_iterations: int = Field(
        default=5,
        metadata={"description": "Maximum research iterations"}
    )
    max_react_tool_calls: int = Field(
        default=5,
        metadata={"description": "Maximum tool calls per researcher"}
    )

    # Model Configuration
    research_model: str = Field(
        default="openai:Qwen2.5-Coder-32B-Instruct",
        metadata={"description": "Model for research and SQL generation"}
    )
    research_model_max_tokens: int = Field(
        default=8192,
        metadata={"description": "Max tokens for research model"}
    )
    compression_model: str = Field(
        default="openai:Qwen2.5-Coder-32B-Instruct",
        metadata={"description": "Model for compressing research"}
    )
    compression_model_max_tokens: int = Field(
        default=4096,
        metadata={"description": "Max tokens for compression model"}
    )
    final_report_model: str = Field(
        default="openai:Qwen2.5-Coder-32B-Instruct",
        metadata={"description": "Model for final report generation"}
    )
    final_report_model_max_tokens: int = Field(
        default=8192,
        metadata={"description": "Max tokens for final report model"}
    )

    # Database Configuration
    db_host: str = Field(
        default="172.31.26.206",
        metadata={"description": "Database host"}
    )
    db_port: int = Field(
        default=3306,
        metadata={"description": "Database port"}
    )
    db_user: str = Field(
        default="ai_test",
        metadata={"description": "Database user"}
    )
    db_password: str = Field(
        default="Netcare@13579",
        metadata={"description": "Database password"}
    )
    db_name: str = Field(
        default="netcaredb_ai",
        metadata={"description": "Database name"}
    )

    # FusionSQL Configuration
    fusionsql_top_k: int = Field(
        default=10,
        metadata={"description": "Number of tables to retrieve"}
    )
    execute_sql: bool = Field(
        default=True,
        metadata={"description": "Whether to execute SQL queries"}
    )
    max_sql_results_rows: int = Field(
        default=100,
        metadata={"description": "Maximum rows to return from SQL"}
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "SQLConfiguration":
        """Create SQLConfiguration from RunnableConfig."""
        configurable = config.get("configurable", {}) if config else {}
        field_names = list(cls.model_fields.keys())
        values: dict[str, Any] = {
            field_name: os.environ.get(field_name.upper(), configurable.get(field_name))
            for field_name in field_names
        }
        return cls(**{k: v for k, v in values.items() if v is not None})

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
