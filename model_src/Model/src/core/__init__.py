"""
Core components for the autonomous web agent.

This package contains the fundamental building blocks:
- Memory: Persistent learning and pattern tracking
- Vision: Element detection and visual perception  
- Cognition: AI-powered decision making
- Executor: Action execution with human behavior
"""

from .memory import AgentMemory, extract_domain
from .vision import Vision
from .cognition import CognitiveEngine
from .executor import ActionExecutor

__all__ = [
    'AgentMemory',
    'extract_domain',
    'Vision',
    'CognitiveEngine',
    'ActionExecutor',
]