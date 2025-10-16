from typing import Dict, List, Optional, Tuple

# guided_agent.py
# =============================================================================
# GUIDED AUTONOMOUS AGENT
# You control what happens next, with AI assistance
# =============================================================================

from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
from pathlib import Path

from src.core.memory import AgentMemory, extract_domain
from src.core.vision import Vision
from src.core.cognition import CognitiveEngine
from src.core.executor import ActionExecutor


class GuidedAgent:
    """
    Agent where YOU decide what to do next, but AI helps with suggestions
    """
    
    def __init__(self, api_key: str = None, debug: bool = True):
        self.debug = debug
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        print("🤖 Initializing Guided Agent (You're in control!)...")
        
        self.memory = AgentMemory(str(self.results_dir / "agent_brain.db"))
        self.vision = Vision(self.memory, debug=debug)
        self.cognition = CognitiveEngine(self.memory, api_key)
        
        print("✅ Agent ready\n")
    
    def run_guided(self, initial_task: str):
        """
        Run in guided mode - you control everything
        """
        
        print("=" * 80)
        print("🎯 GUIDED MODE - You're in control!")
        print("=" * 80)
        print("The agent will:")
        print("  • Complete the task you give it")
        print("  • Show you the results")
        print("  • Ask YOU what to do next")
        print("  • Provide AI suggestions to help")
        print("=" * 80 + "\n")
        
        with sync_playwright() as p:
            browser = self._setup_browser(p)
            page = browser.new_page()
            executor = ActionExecutor(page, self.memory)
            
            current_task = initial_task
            iteration = 0
            
            try:
                while True:
                    iteration += 1
                    
                    print(f"\n{'='*80}")
                    print(f"📍 TASK {iteration}")
                    print(f"{'='*80}")
                    print(f"🎯 {current_task}\n")
                    
                    # Execute task
                    success, data = self._execute_task(page, executor, current_task)
                    
                    # Save results
                    self._save_results(iteration, current_task, success, data)
                    
                    # Show results to user
                    self._show_results(current_task, success, data)
                    
                    # Ask user what's next
                    next_task = self._ask_user_next_action(current_task, data)
                    
                    if next_task:
                        current_task = next_task
                    else:
                        print("\n✅ All done!")
                        break
                    
                    time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n\n⏸️ Stopped by user")
            finally:
                input("\nPress Enter to close browser...")
                browser.close()
    
    def _execute_task(self, page, executor, task: str, max_steps: int = 25):
        """Execute a task"""
        
        self.cognition.reset_conversation()
        
        for step in range(1, max_steps + 1):
            print(f"\n{'─'*80}")
            print(f"📍 STEP {step}/{max_steps}")
            print(f"{'─'*80}\n")
            
            time.sleep(1.5)
            
            # Vision
            print("👁️  Detecting elements...")
            elements = self.vision.detect_all_elements(page)
            
            if len(elements) == 0:
                print("   ⚠️ No elements detected - retrying...")
                time.sleep(2)
                elements = self.vision.detect_all_elements(page)
            
            screenshot_bytes, screenshot_b64 = self.vision.create_labeled_screenshot(page, elements)
            
            if not screenshot_b64:
                print("   ❌ Screenshot failed")
                continue
            
            page_data = self.vision.extract_page_content(page)
            page_analysis = self.vision.analyze_page_structure(page)
            
            # Check for CAPTCHA
            if page_analysis.get('hasCaptcha'):
                print("\n🚨 CAPTCHA DETECTED!")
                print("Please solve it manually, then press Enter...")
                input()
                continue
            
            # Cognition
            print("🧠 Thinking...")
            decision = self.cognition.think(
                page=page,
                task=task,
                screenshot_b64=screenshot_b64,
                elements=elements,
                page_data=page_data,
                page_analysis=page_analysis
            )
            
            print(f"   Decision: {decision['action'].upper()}")
            print(f"   Confidence: {decision['confidence']}/10")
            
            if decision['action'] == 'done':
                print("\n✅ Task complete!")
                return True, page_data
            
            # Execute
            print(f"⚡ Executing {decision['action']}...")
            
            # Fix clicking issues
            if decision['action'] == 'click':
                details = decision['details'].strip()
                if len(details) > 10 and not details.isdigit():
                    import re
                    match = re.search(r'\[(\d+)\]', details)
                    if match:
                        decision['details'] = match.group(1)
            
            success, message = executor.execute(decision, elements)
            
            if success:
                print(f"   ✅ {message}")
            else:
                print(f"   ❌ {message}")
            
            # Check if stuck
            is_stuck, reason = self.memory.is_stuck()
            if is_stuck:
                print(f"\n⚠️ Agent seems stuck: {reason}")
                
                print("\nWhat would you like to do?")
                print("  1. Continue anyway")
                print("  2. Stop this task")
                
                choice = input("\nChoice [1]: ").strip() or "1"
                if choice == "2":
                    return False, page_data
        
        print("\n⏰ Max steps reached")
        return False, page_data
    
    def _show_results(self, task: str, success: bool, data: Dict):
        """Show results to user"""
        
        print(f"\n{'='*80}")
        print(f"📊 RESULTS")
        print(f"{'='*80}")
        print(f"Task: {task}")
        print(f"Status: {'✅ Success' if success else '⚠️ Incomplete'}")
        
        if data.get('products'):
            print(f"\n🛍️ Found {len(data['products'])} products:")
            
            for i, p in enumerate(data['products'][:10], 1):
                title = p.get('title', 'Unknown')[:70]
                price = p.get('price', 'N/A')
                rating = p.get('rating')
                
                print(f"\n{i}. {title}")
                print(f"   💰 ${price}", end="")
                if rating:
                    print(f" | ⭐ {rating}/5", end="")
                print()
            
            if len(data['products']) > 10:
                print(f"\n... and {len(data['products']) - 10} more")
        else:
            print(f"\nProducts: {len(data.get('products', []))}")
        
        print(f"{'='*80}")
    
    def _ask_user_next_action(self, completed_task: str, results: Dict) -> str:
        """Ask user what to do next"""
        
        # Get AI suggestion
        print(f"\n💡 Getting AI suggestion...")
        suggestion = self._get_ai_suggestion(completed_task, results)
        
        print(f"\n{'='*80}")
        print(f"❓ WHAT'S NEXT?")
        print(f"{'='*80}")
        
        if suggestion:
            print(f"\n🤖 AI Suggestion: {suggestion}")
        
        print(f"\nOptions:")
        print(f"  1. Use AI suggestion" + (f" ({suggestion[:50]}...)" if suggestion else " (none)"))
        print(f"  2. Enter your own task")
        print(f"  3. Refine current results (filter/sort)")
        print(f"  4. Compare on another site")
        print(f"  5. Stop here")
        
        choice = input(f"\nChoice [2]: ").strip() or "2"
        
        if choice == "1" and suggestion:
            return suggestion
        
        elif choice == "2":
            task = input("\n📋 Enter your task: ").strip()
            return task if task else None
        
        elif choice == "3":
            print("\nHow would you like to refine?")
            print("  a. Filter by price")
            print("  b. Filter by rating")
            print("  c. Sort by price")
            print("  d. Sort by rating")
            print("  e. Custom refinement")
            
            refine = input("\nChoice [e]: ").strip() or "e"
            
            if refine == "a":
                max_price = input("Max price: $").strip()
                return f"filter results to show only items under ${max_price}"
            elif refine == "b":
                min_rating = input("Min rating (1-5): ").strip()
                return f"filter to show only {min_rating}+ star rated products"
            elif refine == "c":
                return "sort results by price from low to high"
            elif refine == "d":
                return "sort results by customer rating from high to low"
            else:
                task = input("Describe refinement: ").strip()
                return task if task else None
        
        elif choice == "4":
            site = input("\nWhich site? (e.g., bestbuy.com, target.com): ").strip()
            if site:
                # Extract main keywords from completed task
                keywords = " ".join(completed_task.split()[:5])
                return f"search for {keywords} on {site}"
            return None
        
        else:
            return None
    
    def _get_ai_suggestion(self, completed_task: str, results: Dict) -> str:
        """Get AI suggestion"""
        
        products_info = ""
        if results.get('products'):
            products_info = f"Found {len(results['products'])} products. "
            if len(results['products']) > 0:
                top = results['products'][0]
                products_info += f"Top result: {top.get('title', 'Unknown')[:50]} (${top.get('price', 'N/A')})"
        
        prompt = f"""Task completed: {completed_task}
Results: {products_info}

Suggest ONE specific next action in 10 words or less. Examples:
- "Filter to 4+ star ratings only"
- "Sort by price low to high"  
- "Compare prices on bestbuy"

Respond with JUST the suggestion (no explanation), or "DONE" if satisfied."""
        
        try:
            response = self.cognition.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = response.content[0].text.strip()
            
            if "DONE" in answer.upper():
                return None
            
            return answer
            
        except:
            return None
    
    def _save_results(self, iteration: int, task: str, success: bool, data: Dict):
        """Save results"""
        
        filename = self.results_dir / f"task_{iteration}_{datetime.now().strftime('%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'iteration': iteration,
                'task': task,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }, f, indent=2)
    
    def _setup_browser(self, playwright):
        """Setup browser"""
        
        browser = playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        return browser


def main():
    import os
    import sys
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)
    
    print("\n🎯 GUIDED AGENT - You're in Control!")
    print("="*60)
    print("The agent helps, but YOU decide what happens next")
    print("="*60)
    
    task = input("\n📋 Initial task: ").strip()
    
    if not task:
        print("❌ No task provided")
        sys.exit(1)
    
    agent = GuidedAgent(debug=True)
    agent.run_guided(task)


if __name__ == "__main__":
    main()