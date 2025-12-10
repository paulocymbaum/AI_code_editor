"""
Centralized configuration management for AI Code Editor

Provides type-safe, environment-based configuration using Pydantic.
Eliminates scattered os.getenv() calls throughout the codebase.
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqConfig(BaseModel):
    """Groq API configuration"""
    api_key: str = Field(..., description="Groq API key")
    model: str = Field(
        default="qwen/qwen3-32b",
        description="Groq model to use"
    )
    temperature: float = Field(default=0.2, description="Model temperature")
    max_tokens: int = Field(default=4000, description="Max tokens per request")


class AgentConfig(BaseModel):
    """Agent execution configuration"""
    max_iterations: int = Field(
        default=10,
        description="Maximum execution iterations"
    )
    tool_timeout: int = Field(
        default=30,
        description="Tool execution timeout in seconds"
    )
    enable_safety_checks: bool = Field(
        default=True,
        description="Enable safety checks for dangerous operations"
    )


class PathConfig(BaseModel):
    """Path configuration for file operations"""
    output_dir: str = Field(
        default="./demo",
        description="Default output directory for generated files"
    )
    config_dir: str = Field(
        default="./config",
        description="Configuration files directory"
    )
    components_dir: str = Field(
        default="./src/components",
        description="Default components directory"
    )


class FeatureFlags(BaseModel):
    """Feature toggles for optional functionality"""
    enable_redis: bool = Field(
        default=False,
        description="Enable Redis for short-term memory"
    )
    enable_chroma: bool = Field(
        default=False,
        description="Enable ChromaDB for vector storage"
    )
    enable_postgres: bool = Field(
        default=False,
        description="Enable PostgreSQL for long-term storage"
    )
    enable_observability: bool = Field(
        default=True,
        description="Enable observability features"
    )


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR"
    )
    file_level: str = Field(
        default="DEBUG",
        description="File log level (more detailed)"
    )
    console_level: str = Field(
        default="INFO",
        description="Console log level (less detailed)"
    )
    log_dir: str = Field(
        default="./logs",
        description="Directory for log files"
    )


class Settings(BaseModel):
    """
    Main application settings.
    
    Loads configuration from environment variables with sensible defaults.
    Use get_settings() to get cached instance.
    """
    groq: GroqConfig
    agent: AgentConfig
    paths: PathConfig
    features: FeatureFlags
    logging: LoggingConfig
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create Settings from environment variables.
        
        Returns:
            Settings instance
        
        Example:
            >>> settings = Settings.from_env()
            >>> print(settings.groq.model)
            'qwen/qwen3-32b'
        """
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required. "
                "Set it in .env file or environment."
            )
        
        return cls(
            groq=GroqConfig(
                api_key=groq_api_key,
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                temperature=float(os.getenv("GROQ_TEMPERATURE", "0.2")),
                max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "4000")),
            ),
            agent=AgentConfig(
                max_iterations=int(os.getenv("MAX_ITERATIONS", "10")),
                tool_timeout=int(os.getenv("TOOL_TIMEOUT", "30")),
                enable_safety_checks=os.getenv("ENABLE_SAFETY_CHECKS", "true").lower() == "true",
            ),
            paths=PathConfig(
                output_dir=os.getenv("OUTPUT_DIR", "./demo"),
                config_dir=os.getenv("CONFIG_DIR", "./config"),
                components_dir=os.getenv("COMPONENTS_DIR", "./src/components"),
            ),
            features=FeatureFlags(
                enable_redis=os.getenv("ENABLE_REDIS", "false").lower() == "true",
                enable_chroma=os.getenv("ENABLE_CHROMA", "false").lower() == "true",
                enable_postgres=os.getenv("ENABLE_POSTGRES", "false").lower() == "true",
                enable_observability=os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true",
            ),
            logging=LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                file_level=os.getenv("FILE_LOG_LEVEL", "DEBUG"),
                console_level=os.getenv("CONSOLE_LOG_LEVEL", "INFO"),
                log_dir=os.getenv("LOG_DIR", "./logs"),
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Settings are loaded once and cached for performance.
    
    Returns:
        Settings instance
    
    Example:
        >>> from src.core.config import get_settings
        >>> settings = get_settings()
        >>> client = AsyncGroq(api_key=settings.groq.api_key)
    """
    return Settings.from_env()


def reset_settings():
    """
    Reset cached settings (useful for testing).
    
    Example:
        >>> reset_settings()
        >>> settings = get_settings()  # Reloads from environment
    """
    get_settings.cache_clear()
