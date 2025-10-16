"""
Intelligent Agent - Automatic Mode Selection
FIXED: Proper imports, correct web mode routing
"""

import os
from typing import Dict

from src.core.config import ANTHROPIC_API_KEY


class IntelligentAgent:
    """
    Intelligent router that selects best execution mode
    Currently focuses on web automation
    """
    
    def __init__(self, api_key: str = None, debug: bool = False):
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.debug = debug
        
        if self.debug:
            print("✅ Intelligent Agent initialized")
    
    def execute(self, task: str) -> Dict:
        """
        Execute task by routing to appropriate agent
        
        Args:
            task: User's task description
            
        Returns:
            Result dictionary with status and data
        """
        
        if self.debug:
            print(f"📋 Task: {task[:80]}...")
        
        # For now, route all tasks to continuous web agent
        # Future: Add analysis to choose between modes
        return self._web_mode(task)
    
    def _web_mode(self, task: str) -> Dict:
        """Execute web automation task"""
        
        from src.agents.continuous_agent import ContinuousAgent
        
        if self.debug:
            print("🌐 Mode: Web Automation (Continuous)")
        
        agent = ContinuousAgent(api_key=self.api_key, debug=self.debug)
        
        try:
            # Run task
            success, data = agent.run_continuous(task=task, max_iterations=1)
            
            return {
                'status': 'success' if success else 'failed',
                'data': data,
                'mode': 'continuous'
            }
            
        except Exception as e:
            if self.debug:
                print(f"❌ Execution error: {e}")
            
            return {
                'status': 'error',
                'reason': str(e),
                'mode': 'continuous'
            }
        finally:
            agent.close()
    
    def suggest_next_action(self):
        """Suggest next action (placeholder)"""
        return None
    
    def close(self):
        """Cleanup resources"""
        pass