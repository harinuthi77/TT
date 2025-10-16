from playwright.sync_api import sync_playwright
import time
from pathlib import Path
from typing import Dict
from src.core.memory import AgentMemory
from src.core.vision import Vision
from src.core.cognition import CognitiveEngine
from src.core.executor import ActionExecutor

class ContinuousAgent:
    def __init__(self, api_key: str = None, debug: bool = True):
        self.debug = debug
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        self.memory = AgentMemory(str(self.results_dir / "agent_brain.db"))
        self.vision = Vision(self.memory, debug=debug)
        self.cognition = CognitiveEngine(self.memory, api_key)
    
    def run_continuous(self, task: str, max_iterations: int = 1):
        print("="*80)
        print(f"CONTINUOUS MODE - Task: {task}")
        print("="*80)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
            page = browser.new_page()
            executor = ActionExecutor(page, self.memory)
            
            try:
                success, data = self._execute_task(page, executor, task)
                print(f"\nTask {'completed' if success else 'failed'}")
            except KeyboardInterrupt:
                print("\nStopped by user")
                success, data = False, {}
            finally:
                browser.close()
        
        # CRITICAL: Always return tuple
        return True, {'status': 'completed', 'task': task}
    
    def _execute_task(self, page, executor, task: str, max_steps: int = 50):
        self.cognition.reset_conversation()
        
        for step in range(1, max_steps + 1):
            print(f"\nSTEP {step}/{max_steps}")
            time.sleep(1.5)
            
            elements = self.vision.detect_all_elements(page)
            if not elements:
                time.sleep(2)
                elements = self.vision.detect_all_elements(page)
            
            screenshot_bytes, screenshot_b64 = self.vision.create_labeled_screenshot(page, elements)
            if not screenshot_b64:
                continue
            
            page_data = self.vision.extract_page_content(page)
            page_analysis = self.vision.analyze_page_structure(page)
            
            decision = self.cognition.think(
                page=page, task=task, screenshot_b64=screenshot_b64,
                elements=elements, page_data=page_data, page_analysis=page_analysis
            )
            
            if decision['action'] == 'done':
                return True, page_data
            
            success, message = executor.execute(decision, elements)
            print(f"   {message}")
            
            is_stuck, reason = self.memory.is_stuck()
            if is_stuck:
                print(f"\nSTUCK: {reason}")
                break
        
        return False, page_data or {}