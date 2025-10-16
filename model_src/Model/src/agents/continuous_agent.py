"""
Continuous Agent - Multi-step automated workflow
FIXED: Proper imports, integration with new modules, element tracking
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path
from typing import Dict, Tuple

from src.core.memory import AgentMemory, extract_domain
from src.core.vision import Vision
from src.core.cognition import CognitiveEngine
from src.core.executor import ActionExecutor
from src.core.config import MAX_STEPS_PER_TASK, RESULTS_DIR


class ContinuousAgent:
    """
    Agent that runs continuously until task completion or max steps
    """
    
    def __init__(self, api_key: str = None, debug: bool = True):
        self.debug = debug
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize core systems
        self.memory = AgentMemory(str(self.results_dir / "agent_brain.db"))
        self.vision = Vision(self.memory, debug=debug)
        self.cognition = CognitiveEngine(self.memory, api_key)
        
        if self.debug:
            print("✅ Continuous Agent initialized")
    
    def run_continuous(self, task: str, max_iterations: int = 1) -> Tuple[bool, Dict]:
        """
        Run agent in continuous mode
        
        Args:
            task: Task description
            max_iterations: Not used, kept for compatibility
            
        Returns:
            (success, data) tuple
        """
        
        print("=" * 80)
        print(f"CONTINUOUS MODE - Task: {task}")
        print("=" * 80)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            executor = ActionExecutor(page, self.memory)
            
            try:
                success, data = self._execute_task(page, executor, task)
                print(f"\nTask {'completed ✅' if success else 'failed ❌'}")
            except KeyboardInterrupt:
                print("\n⏸️ Stopped by user")
                success, data = False, {}
            finally:
                browser.close()
        
        # Always return tuple
        return success, data or {'status': 'completed', 'task': task}
    
    def _execute_task(self, page, executor, task: str, 
                     max_steps: int = MAX_STEPS_PER_TASK) -> Tuple[bool, Dict]:
        """Execute task with proper element tracking"""
        
        self.cognition.reset_conversation()
        self.memory.clear_recent_actions()
        
        for step in range(1, max_steps + 1):
            print(f"\n{'=' * 80}")
            print(f"STEP {step}/{max_steps}")
            print(f"{'=' * 80}")
            
            # Small delay
            time.sleep(1.5)
            
            # Vision: detect elements
            print("\n👁️ VISION PHASE")
            elements = self.vision.detect_all_elements(page)
            
            if not elements:
                print("   ⚠️ No elements detected - retrying...")
                time.sleep(2)
                elements = self.vision.detect_all_elements(page)
            
            # Create labeled screenshot
            screenshot_bytes, screenshot_b64 = self.vision.create_labeled_screenshot(page, elements)
            
            if not screenshot_b64:
                print("   ❌ Screenshot failed")
                continue
            
            # Extract page data
            page_data = self.vision.extract_page_content(page)
            page_analysis = self.vision.analyze_page_structure(page)
            
            # Cognition: decide action
            print("\n🧠 COGNITION PHASE")
            decision = self.cognition.think(
                page=page,
                task=task,
                screenshot_b64=screenshot_b64,
                elements=elements,
                page_data=page_data,
                page_analysis=page_analysis
            )
            
            # Check for completion
            if decision['action'] == 'done':
                print("\n✅ Task complete!")
                return True, page_data
            
            # Execute action
            print(f"\n⚡ EXECUTION PHASE")
            success, message = executor.execute(decision, elements)
            print(f"   {message}")
            
            # Record action with element tracking
            domain = extract_domain(page.url)
            element_id = decision.get('details') if decision['action'] == 'click' else None
            self.memory.record_action(decision['action'], element_id, page.url)
            
            # Check if stuck
            is_stuck, reason = self.memory.is_stuck()
            if is_stuck:
                print(f"\n⚠️ STUCK: {reason}")
                print("   Agent will try different approach...")
                # Clear stuck state
                self.memory.clear_recent_actions()
                continue
        
        print(f"\n⏱️ Max steps ({max_steps}) reached")
        return False, page_data or {}
    
    def close(self):
        """Clean up resources"""
        if self.memory:
            self.memory.close()