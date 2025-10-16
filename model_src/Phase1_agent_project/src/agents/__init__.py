"""
Agent implementations for different execution modes.

Agents:
- UniversalAgent: Handles ANY task (web, file, code) - RECOMMENDED
- ContinuousAgent: Multi-step web automation workflow  
"""

from .universal_agent import UniversalAgent
from .continuous_agent import ContinuousAgent

__all__ = [
    'UniversalAgent',
    'ContinuousAgent',
]