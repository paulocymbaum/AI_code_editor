"""
Centralized logging configuration for AI Code Editor

This module provides a consistent logging setup across all components,
eliminating duplicate logging configuration code.
"""

import logging
from pathlib import Path
from typing import Optional


class AgentLogger:
    """
    Centralized logger with consistent formatting for the AI agent.
    
    Provides structured logging to both file and console with different
    verbosity levels, making debugging and monitoring easier.
    """
    
    _initialized = False
    _loggers = {}
    
    @staticmethod
    def setup(
        log_file: str = "agent_execution.log",
        level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        console_level: int = logging.INFO
    ) -> str:
        """
        Setup detailed logging to both file and console.
        
        Args:
            log_file: Path to log file
            level: Root logger level (default: INFO)
            file_level: File handler level for detailed logs (default: DEBUG)
            console_level: Console handler level for important logs (default: INFO)
        
        Returns:
            Path to log file
        
        Example:
            >>> AgentLogger.setup("my_agent.log", level=logging.DEBUG)
            'my_agent.log'
        """
        if AgentLogger._initialized:
            return log_file
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler - detailed logs
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        
        # Console handler - important logs only
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.handlers.clear()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        AgentLogger._initialized = True
        
        # Log initialization
        logger = AgentLogger.get_logger(__name__)
        logger.info(f"📝 Logging configured: {log_file}")
        
        return log_file
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get or create a logger for a specific module.
        
        Args:
            name: Logger name (typically __name__)
        
        Returns:
            Logger instance
        
        Example:
            >>> logger = AgentLogger.get_logger(__name__)
            >>> logger.info("Processing started")
        """
        if name not in AgentLogger._loggers:
            AgentLogger._loggers[name] = logging.getLogger(name)
        return AgentLogger._loggers[name]
    
    @staticmethod
    def reset():
        """Reset logging configuration (useful for testing)"""
        AgentLogger._initialized = False
        AgentLogger._loggers.clear()
        logging.getLogger().handlers.clear()


def setup_logging(log_file: str = "agent_execution.log", level: int = logging.INFO) -> str:
    """
    Convenience function for backward compatibility.
    
    Args:
        log_file: Path to log file
        level: Logging level
    
    Returns:
        Path to log file
    """
    return AgentLogger.setup(log_file, level)
