"""
Single Task Agent - Complete one focused task
FIXED: Proper imports, browser setup, integration
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import json
import os
from datetime import datetime
from typing import Dict, Tuple
from pathlib import Path

from src.core.memory import AgentMemory, extract_domain
from src.core.vision import Vision
from src.core.cognition import CognitiveEngine
from src.core.executor import ActionExecutor
from src.core.config import (
    HEADLESS,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
    USER_AGENT,
    MAX_STEPS_PER_TASK,
    RESULTS_DIR
)


class SingleTaskAgent:
    """
    Single-task focused agent with comprehensive workflow
    """
    
    def __init__(self, api_key: str = None, debug: bool = False):
        self.debug = debug
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
        
        print("🧠 Initializing Single Task Agent...")
        
        # Initialize components
        self.memory = AgentMemory(str(self.results_dir / "agent_brain.db"))
        self.vision = Vision(self.memory, debug=debug)
        self.cognition = CognitiveEngine(self.memory, api_key)
        
        if self.debug:
            stats = self.memory.get_stats()
            print(f"   💾 Memory: {stats['patterns_learned']} patterns learned")
        
        print("   ✅ All systems initialized\n")
    
    def run(self, task: str, max_steps: int = MAX_STEPS_PER_TASK, 
            save_results: bool = True) -> Tuple[bool, Dict]:
        """
        Run agent to complete a task
        
        Args:
            task: Task description
            max_steps: Maximum steps before stopping
            save_results: Save results to JSON
            
        Returns:
            (success, data) tuple
        """
        
        print(f"\n{'=' * 80}")
        print(f"🤖 SINGLE TASK AGENT - TASK EXECUTION")
        print(f"{'=' * 80}")
        print(f"📋 Task: {task}")
        print(f"⏱️ Start: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'=' * 80}\n")
        
        # Start browser
        with sync_playwright() as p:
            browser, page = self._setup_browser(p)
            executor = ActionExecutor(page, self.memory)
            
            # Track session
            start_time = time.time()
            steps_taken = 0
            task_success = False
            final_data = None
            
            # Reset conversation
            self.cognition.reset_conversation()
            self.memory.clear_recent_actions()
            
            # Main execution loop
            try:
                for step in range(1, max_steps + 1):
                    steps_taken = step
                    
                    print(f"\n{'─' * 80}")
                    print(f"🔍 STEP {step}/{max_steps}")
                    print(f"{'─' * 80}")
                    
                    time.sleep(1.5)
                    
                    # VISION PHASE
                    print("\n👁️ VISION")
                    elements = self.vision.detect_all_elements(page)
                    
                    if not elements:
                        time.sleep(2)
                        elements = self.vision.detect_all_elements(page)
                    
                    screenshot_bytes, screenshot_b64 = self.vision.create_labeled_screenshot(page, elements)
                    
                    if not screenshot_b64:
                        print("   ❌ Screenshot failed")
                        continue
                    
                    page_data = self.vision.extract_page_content(page)
                    page_analysis = self.vision.analyze_page_structure(page)
                    
                    # COGNITION PHASE
                    print("\n🧠 COGNITION")
                    decision = self.cognition.think(
                        page=page,
                        task=task,
                        screenshot_b64=screenshot_b64,
                        elements=elements,
                        page_data=page_data,
                        page_analysis=page_analysis
                    )
                    
                    # Check completion
                    if decision['action'] == 'done':
                        print("\n✅ Agent believes task is complete")
                        task_success = True
                        final_data = page_data
                        break
                    
                    # EXECUTION PHASE
                    print("\n⚡ EXECUTION")
                    success, message = executor.execute(decision, elements)
                    print(f"   {message}")
                    
                    # Track action
                    domain = extract_domain(page.url)
                    element_id = decision.get('details') if decision['action'] == 'click' else None
                    self.memory.record_action(decision['action'], element_id, page.url)
                    
                    # Check if stuck
                    is_stuck, stuck_reason = self.memory.is_stuck()
                    if is_stuck:
                        print(f"\n⚠️ STUCK: {stuck_reason}")
                        self.memory.clear_recent_actions()
                
            except KeyboardInterrupt:
                print("\n\n⏸️ Task interrupted by user")
                task_success = False
                
            except Exception as e:
                print(f"\n\n❌ Unexpected error: {e}")
                task_success = False
            
            # SESSION COMPLETE
            duration = time.time() - start_time
            
            print(f"\n{'=' * 80}")
            print(f"📊 SESSION SUMMARY")
            print(f"{'=' * 80}")
            print(f"   Task: {task}")
            print(f"   Status: {'✅ SUCCESS' if task_success else '⏸️ INCOMPLETE'}")
            print(f"   Steps: {steps_taken}")
            print(f"   Duration: {duration:.1f}s ({duration/60:.1f} min)")
            print(f"   Final URL: {page.url}")
            
            # Extract final data
            if not final_data:
                final_data = self.vision.extract_page_content(page)
            
            # Show results
            if final_data.get('products'):
                print(f"\n📦 EXTRACTED DATA:")
                print(f"   Products found: {len(final_data['products'])}")
                
                for i, product in enumerate(final_data['products'][:5], 1):
                    print(f"\n   {i}. {product.get('title', 'Unknown')[:70]}")
                    if product.get('price'):
                        print(f"      💰 ${product['price']}")
                    if product.get('rating'):
                        print(f"      ⭐ {product['rating']}/5")
                
                if len(final_data['products']) > 5:
                    print(f"\n   ... and {len(final_data['products']) - 5} more")
            
            # Save results
            if save_results and final_data.get('products'):
                filename = self._save_results(task, final_data, task_success, 
                                             steps_taken, duration, page.url)
                print(f"\n💾 Results saved to: {filename}")
            
            # Update memory
            domain = extract_domain(page.url)
            self.memory.save_task(
                task=task,
                success=task_success,
                steps_taken=steps_taken,
                duration=duration,
                final_url=page.url,
                data_collected=final_data
            )
            self.memory.update_domain_insight(domain, steps_taken, task_success)
            
            print(f"{'=' * 80}")
            
            # Keep browser open for review
            input("\n👀 Press Enter to close browser...")
            browser.close()
        
        return task_success, final_data
    
    def _setup_browser(self, playwright):
        """Setup browser with minimal configuration"""
        
        print("🌐 Launching browser...")
        
        # Simple, stable browser setup
        browser = playwright.chromium.launch(headless=HEADLESS)
        
        context = browser.new_context(
            viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
            user_agent=USER_AGENT
        )
        
        page = context.new_page()
        
        # Minimal anti-detection (optional)
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print("   ✅ Browser ready\n")
        
        return browser, page
    
    def _save_results(self, task: str, data: Dict, success: bool, 
                     steps: int, duration: float, url: str) -> str:
        """Save results to JSON file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"agent_results_{timestamp}.json"
        
        output = {
            'task': task,
            'success': success,
            'steps_taken': steps,
            'duration_seconds': duration,
            'final_url': url,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def close(self):
        """Clean up resources"""
        if self.memory:
            self.memory.close()


def main():
    """CLI interface"""
    
    import sys
    
    print("\n🤖 SINGLE TASK AGENT")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)
    
    # Get task
    print("\n💬 What should the agent do?")
    print("Examples:")
    print("  • Go to Amazon and find wireless headphones under $50")
    print("  • Search for laptops on Best Buy")
    print()
    
    task = input("Task: ").strip()
    
    if not task:
        print("❌ No task provided")
        sys.exit(1)
    
    # Create and run agent
    print()
    agent = SingleTaskAgent(debug=True)
    
    try:
        success, data = agent.run(task)
        
        if success:
            print("\n✅ Task completed successfully!")
        else:
            print("\n⏸️ Task incomplete")
        
    except KeyboardInterrupt:
        print("\n\n⏸️ Stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
    finally:
        agent.close()


if __name__ == "__main__":
    main()