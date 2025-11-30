"""
Logger Module
Provides logging utilities for the PVZ bot
"""

import sys
import time
from typing import Optional
from enum import IntEnum


class LogLevel(IntEnum):
    """Log levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class Logger:
    """
    Simple logger for the PVZ bot
    
    Supports different log levels and optional file output.
    """
    
    LEVEL_NAMES = {
        LogLevel.DEBUG: "DEBUG",
        LogLevel.INFO: "INFO",
        LogLevel.WARNING: "WARN",
        LogLevel.ERROR: "ERROR",
        LogLevel.CRITICAL: "CRIT",
    }
    
    LEVEL_COLORS = {
        LogLevel.DEBUG: "\033[36m",  # Cyan
        LogLevel.INFO: "\033[32m",   # Green
        LogLevel.WARNING: "\033[33m", # Yellow
        LogLevel.ERROR: "\033[31m",   # Red
        LogLevel.CRITICAL: "\033[35m", # Magenta
    }
    
    RESET_COLOR = "\033[0m"
    
    def __init__(self, name: str = "PVZ", level: LogLevel = LogLevel.INFO,
                 use_colors: bool = True, file_path: Optional[str] = None):
        self.name = name
        self.level = level
        self.use_colors = use_colors
        self.file_path = file_path
        self._file = None
        
        if file_path:
            self._file = open(file_path, 'a', encoding='utf-8')
    
    def _format_message(self, level: LogLevel, message: str, 
                       include_colors: bool = True) -> str:
        """Format a log message"""
        timestamp = time.strftime("%H:%M:%S")
        level_name = self.LEVEL_NAMES.get(level, "???")
        
        if include_colors and self.use_colors:
            color = self.LEVEL_COLORS.get(level, "")
            return f"{color}[{timestamp}] [{level_name}] [{self.name}] {message}{self.RESET_COLOR}"
        else:
            return f"[{timestamp}] [{level_name}] [{self.name}] {message}"
    
    def _log(self, level: LogLevel, message: str):
        """Internal log method"""
        if level < self.level:
            return
        
        # Console output with colors
        formatted = self._format_message(level, message, include_colors=True)
        print(formatted)
        
        # File output without colors
        if self._file:
            formatted_plain = self._format_message(level, message, include_colors=False)
            self._file.write(formatted_plain + "\n")
            self._file.flush()
    
    def debug(self, message: str):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message)
    
    def info(self, message: str):
        """Log info message"""
        self._log(LogLevel.INFO, message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._log(LogLevel.WARNING, message)
    
    def error(self, message: str):
        """Log error message"""
        self._log(LogLevel.ERROR, message)
    
    def critical(self, message: str):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message)
    
    def set_level(self, level: LogLevel):
        """Set logging level"""
        self.level = level
    
    def close(self):
        """Close file handle if open"""
        if self._file:
            self._file.close()
            self._file = None
    
    def __del__(self):
        """Clean up on destruction"""
        self.close()


# Global logger instance
_global_logger: Optional[Logger] = None


def get_logger(name: str = "PVZ", level: LogLevel = LogLevel.INFO) -> Logger:
    """Get or create a logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(name, level)
    return _global_logger


def status_line(message: str, end: str = ""):
    """Print a status line (overwrites current line)"""
    sys.stdout.write(f"\r{message}" + " " * 20 + end)
    sys.stdout.flush()
