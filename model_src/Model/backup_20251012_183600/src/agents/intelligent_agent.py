import os, anthropic, logging
from typing import Dict

class IntelligentAgent:
    def __init__(self, api_key: str = None, debug: bool = False):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.debug = debug
        self.logger = logging.getLogger('IntelligentAgent')
        if not self.logger.handlers:
            self.logger.addHandler(logging.StreamHandler())
            self.logger.setLevel(logging.INFO)
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def execute(self, task: str) -> Dict:
        print(f"Analyzing task: {task[:80]}...")
        analysis = {'mode': 'continuous', 'max_iterations': 1}  # Simple default
        
        print(f"Executing in CONTINUOUS mode")
        from src.agents.continuous_agent import ContinuousAgent
        agent = ContinuousAgent(api_key=self.api_key, debug=self.debug)
        
        try:
            result = agent.run_continuous(task=task, max_iterations=1)
            if result is None:
                return {'status': 'failed', 'reason': 'No results'}
            success, data = result
            return {'status': 'success' if success else 'failed', 'data': data}
        except Exception as e:
            print(f"Error: {e}")
            return {'status': 'error', 'reason': str(e)}
    def suggest_next_action(self):
        """Suggest next action"""
        return None
    
    def close(self):
        """Close agent"""
        pass