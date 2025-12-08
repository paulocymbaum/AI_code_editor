"""
Configuration Management
Loads and validates environment variables
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class GroqConfig(BaseModel):
    """Groq API configuration"""
    api_key: str = Field(..., env="GROQ_API_KEY")
    model: str = Field(default="llama-3.1-70b-versatile", env="GROQ_MODEL")
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=4000)


class RedisConfig(BaseModel):
    """Redis configuration"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")


class ChromaConfig(BaseModel):
    """ChromaDB configuration"""
    host: str = Field(default="localhost", env="CHROMA_HOST")
    port: int = Field(default=8000, env="CHROMA_PORT")
    persist_dir: str = Field(default="./chroma_data", env="CHROMA_PERSIST_DIR")


class PostgresConfig(BaseModel):
    """PostgreSQL configuration"""
    host: str = Field(default="localhost", env="POSTGRES_HOST")
    port: int = Field(default=5432, env="POSTGRES_PORT")
    database: str = Field(default="ai_agent", env="POSTGRES_DB")
    user: str = Field(default="postgres", env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class AgentConfig(BaseModel):
    """Agent configuration"""
    max_iterations: int = Field(default=10, env="MAX_ITERATIONS")
    tool_timeout: int = Field(default=30, env="TOOL_TIMEOUT")
    enable_safety_checks: bool = Field(default=True, env="ENABLE_SAFETY_CHECKS")


class Config(BaseModel):
    """Main configuration"""
    groq: GroqConfig
    redis: RedisConfig
    chroma: ChromaConfig
    postgres: PostgresConfig
    agent: AgentConfig
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")


def load_config() -> Config:
    """Load configuration from environment"""
    return Config(
        groq=GroqConfig(api_key=os.getenv("GROQ_API_KEY", "")),
        redis=RedisConfig(),
        chroma=ChromaConfig(),
        postgres=PostgresConfig(password=os.getenv("POSTGRES_PASSWORD", "")),
        agent=AgentConfig()
    )
