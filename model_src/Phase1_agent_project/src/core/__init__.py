"""
Core components for the universal autonomous agent.

This package contains:
- Memory: Persistent learning and pattern tracking
- Vision: Element detection and content extraction  
- Cognition: AI-powered decision making
- Executor: Action execution with human behavior
- FileHandler: File operations (read, write, analyze)
- CodeExecutor: Safe Python code execution
- Config: Centralized configuration
"""

from .memory import AgentMemory, extract_domain
from .vision import Vision
from .cognition import CognitiveEngine
from .executor import ActionExecutor
from .file_handler import FileHandler
from .code_executor import CodeExecutor
from .config import *

__all__ = [
    'AgentMemory',
    'extract_domain',
    'Vision',
    'CognitiveEngine',
    'ActionExecutor',
    'FileHandler',
    'CodeExecutor',
]