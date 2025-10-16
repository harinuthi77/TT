# agent.py
# =============================================================================
# AUTONOMOUS WEB AGENT - MAIN ORCHESTRATOR
# Coordinates vision, cognition, and execution for intelligent web automation
# =============================================================================

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# ===== IMPORT ALL MODULES =====
from src.core.memory import AgentMemory, extract_domain
from src.core.vision import Vision
from src.core.cognition import CognitiveEngine
from src.core.executor import ActionExecutor


# =============================================================================
# MAIN AGENT CLASS
# =============================================================================

class SingleTaskAgent:
    """
    Autonomous web agent that can understand and complete web tasks.
    
    Architecture:
        Vision → Sees the page (detects elements, captures screenshots)
        Cognition → Thinks deeply (analyzes, validates, decides)
        Executor → Acts humanly (clicks, types, navigates)
        Memory → Learns continuously (successes, failures, patterns)
    
    Principle: SEE → THINK → VALIDATE → ACT → LEARN
    """
    
    def __init__(self, 
                 api_key: str = None,
                 db_path: str = "agent_brain.db",
                 headless: bool = False,
                 debug: bool = False):
        """
        Initialize the autonomous agent.
        
        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
            db_path: Path to memory database
            headless: Run browser in headless mode
            debug: Enable detailed debug output
        """
        
        self.debug = debug
        self.headless = headless
        
        # Initialize all components
        print("🧠 Initializing Autonomous Agent...")
        
        # Memory - persistent learning
        self.memory = AgentMemory(db_path)
        if self.debug:
            stats = self.memory.get_stats()
            print(f"   💾 Memory: {stats['patterns_learned']} patterns, "
                  f"{stats['tasks_completed']} tasks completed")
        
        # Vision - sees and understands pages
        self.vision = Vision(self.memory)
        print("   👁️  Vision system ready")
        
        # Cognition - intelligent decision making
        self.cognition = CognitiveEngine(self.memory, api_key)
        print("   🧠 Cognitive engine ready")
        
        print("   ✅ All systems initialized\n")
        
    # =========================================================================
    # MAIN RUN LOOP
    # =========================================================================
    
    def run(self, task: str, max_steps: int = 25, save_results: bool = True):
        """
        Run the agent to complete a task.
        
        Args:
            task: The task to complete (e.g., "find headphones under $50 on amazon")
            max_steps: Maximum number of steps before stopping
            save_results: Save extracted data to JSON file
        """
        
        print(f"\n{'=' * 80}")
        print(f"🤖 AUTONOMOUS WEB AGENT - TASK EXECUTION")
        print(f"{'=' * 80}")
        print(f"📋 Task: {task}")
        print(f"⏱️  Start time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'=' * 80}\n")
        
        # Start browser
        with sync_playwright() as p:
            browser, page = self._setup_browser(p)
            
            # Initialize executor with page
            executor = ActionExecutor(page, self.memory)
            
            # Track session
            start_time = time.time()
            steps_taken = 0
            task_success = False
            final_data = None
            
            # Reset cognitive conversation for new task
            self.cognition.reset_conversation()
            
            # ===== MAIN LOOP: SEE → THINK → ACT =====
            try:
                for step in range(1, max_steps + 1):
                    steps_taken = step
                    
                    print(f"\n{'─' * 80}")
                    print(f"📍 STEP {step}/{max_steps}")
                    print(f"{'─' * 80}")
                    
                    # Small delay between steps (human pacing)
                    time.sleep(1.5)
                    
                    # ═══════════════════════════════════════════════════════
                    # PHASE 1: SEE (Vision)
                    # ═══════════════════════════════════════════════════════
                    
                    print("\n👁️  VISION PHASE")
                    
                    # Detect all interactive elements
                    elements = self.vision.detect_all_elements(page)
                    visible_count = len([e for e in elements if e.get('visible', False)])
                    
                    if self.debug:
                        print(f"   Found {len(elements)} elements ({visible_count} visible)")
                    
                    # Create labeled screenshot for Claude to see
                    screenshot_bytes, screenshot_b64 = self.vision.create_labeled_screenshot(
                        page, elements
                    )
                    
                    if not screenshot_b64:
                        print("   ❌ Failed to capture screenshot")
                        break
                    
                    # Extract page data (products, forms, etc.)
                    page_data = self.vision.extract_page_content(page)
                    
                    # Analyze page structure
                    page_analysis = self.vision.analyze_page_structure(page)
                    
                    # ═══════════════════════════════════════════════════════
                    # PHASE 2: THINK (Cognition)
                    # ═══════════════════════════════════════════════════════
                    
                    print("\n🧠 COGNITION PHASE")
                    
                    # Deep thinking with validation
                    decision = self.cognition.think(
                        page=page,
                        task=task,
                        screenshot_b64=screenshot_b64,
                        elements=elements,
                        page_data=page_data,
                        page_analysis=page_analysis
                    )
                    
                    # Check if task is done
                    if decision['action'] == 'done':
                        print("\n✅ Agent believes task is complete")
                        task_success = True
                        
                        # Extract final data before finishing
                        final_data = page_data
                        break
                    
                    # Check for critical issues
                    if decision['confidence'] < 3:
                        print(f"   ⚠️  Very low confidence ({decision['confidence']}/10)")
                        print(f"   💭 Considering alternative approach...")
                    
                    # ═══════════════════════════════════════════════════════
                    # PHASE 3: ACT (Executor)
                    # ═══════════════════════════════════════════════════════
                    
                    print("\n⚡ EXECUTION PHASE")
                    
                    # Execute the decision
                    success, message = executor.execute(decision, elements)
                    
                    print(f"   {message}")
                    
                    if not success:
                        print(f"   ⚠️  Action failed - agent will adapt next step")
                    
                    # ═══════════════════════════════════════════════════════
                    # PHASE 4: LEARN (Memory)
                    # ═══════════════════════════════════════════════════════
                    
                    # Check if stuck
                    is_stuck, stuck_reason = self.memory.is_stuck()
                    if is_stuck:
                        print(f"\n⚠️  STUCK DETECTED: {stuck_reason}")
                        print(f"   Agent will try different approach next step")
                    
                    # End of step
                    print(f"\n{'─' * 80}")
                
            except KeyboardInterrupt:
                print("\n\n⏸️  Task interrupted by user")
                task_success = False
                
            except Exception as e:
                print(f"\n\n❌ Unexpected error: {e}")
                task_success = False
            
            # ═════════════════════════════════════════════════════════════
            # SESSION COMPLETE
            # ═════════════════════════════════════════════════════════════
            
            duration = time.time() - start_time
            
            print(f"\n{'=' * 80}")
            print(f"📊 SESSION SUMMARY")
            print(f"{'=' * 80}")
            print(f"   Task: {task}")
            print(f"   Status: {'✅ SUCCESS' if task_success else '⏸️  INCOMPLETE'}")
            print(f"   Steps taken: {steps_taken}")
            print(f"   Duration: {duration:.1f}s ({duration/60:.1f} minutes)")
            print(f"   Final URL: {page.url}")
            
            # Extract final data if not done yet
            if not final_data:
                final_data = self.vision.extract_page_content(page)
            
            # Show results
            if final_data.get('products'):
                print(f"\n📦 EXTRACTED DATA:")
                print(f"   Products found: {len(final_data['products'])}")
                
                # Show top 5 products
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
            
            # ═════════════════════════════════════════════════════════════
            # ADAPTIVE LEARNING - ANALYZE & IMPROVE
            # ═════════════════════════════════════════════════════════════
            
            try:
                from adaptive_learning import analyze_and_improve
                
                # Count stuck occurrences and bot detections from session
                domain_insight = self.memory.get_domain_insight(domain)
                bot_detected = domain_insight.get('has_bot_detection', False) if domain_insight else False
                
                # Count how many times stuck was detected
                stuck_count = sum(1 for msg in self.cognition.conversation_history 
                                if 'STUCK' in str(msg))
                
                print("\n🔍 Running adaptive learning analysis...")
                analysis = analyze_and_improve(
                    memory=self.memory,
                    task=task,
                    domain=domain,
                    success=task_success,
                    steps_taken=steps_taken,
                    final_url=page.url,
                    stuck_count=stuck_count,
                    bot_detected=bot_detected
                )
                
            except ImportError:
                print("\n   ⚠️  Adaptive learning module not available")
            except Exception as e:
                print(f"\n   ⚠️  Adaptive learning error: {e}")
            
            # Keep browser open for review
            input("\n👀 Press Enter to close browser...")
            browser.close()
        
        return task_success, final_data
    
    # =========================================================================
    # BROWSER SETUP
    # =========================================================================
    
    def _setup_browser(self, playwright):
        """
        Setup browser with anti-detection measures.
        """
        
        print("🌐 Launching browser...")
        
        # Launch browser with anti-detection flags
        browser = playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--start-maximized'
            ]
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # New York
            permissions=['geolocation']
        )
        
        # Create page
        page = context.new_page()
        
        # Inject anti-detection scripts
        page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Add chrome object
            window.chrome = {
                runtime: {}
            };
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        print("   ✅ Browser ready with anti-detection measures\n")
        
        return browser, page
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _save_results(self, task: str, data: Dict, success: bool, 
                     steps: int, duration: float, url: str) -> str:
        """Save results to JSON file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_results_{timestamp}.json"
        
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


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface"""
    
    import sys
    
    print("\n🤖 AUTONOMOUS WEB AGENT")
    print("=" * 60)
    print("Intelligent web automation with vision + cognition")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='your-key'  # Mac/Linux")
        print("  $env:ANTHROPIC_API_KEY='your-key'   # Windows PowerShell")
        sys.exit(1)
    
    # Get task from user
    print("\n💬 What should the agent do?")
    print("Examples:")
    print("  • go to amazon.com and find wireless headphones under $50")
    print("  • search for queen bed frames on walmart.com under $250")
    print("  • find the top 5 rated laptops on bestbuy.com")
    print()
    
    task = input("Task: ").strip()
    
    if not task:
        print("❌ No task provided")
        sys.exit(1)
    
    # Optional: Advanced settings
    print("\n⚙️  Advanced settings (press Enter for defaults):")
    max_steps_input = input("   Max steps [25]: ").strip()
    max_steps = int(max_steps_input) if max_steps_input else 25
    
    debug_input = input("   Debug mode? [y/N]: ").strip().lower()
    debug = debug_input == 'y'
    
    # Create and run agent
    print()
    agent = AutonomousAgent(debug=debug)
    
    try:
        success, data = agent.run(task, max_steps=max_steps)
        
        if success:
            print("\n✅ Task completed successfully!")
        else:
            print("\n⏸️  Task incomplete - review the results above")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
    finally:
        agent.close()


# =============================================================================
# PROGRAMMATIC API
# =============================================================================

class Agent:
    """
    Simple API for programmatic use.
    
    Example:
        from agent import Agent
        
        agent = Agent()
        success, data = agent.run("find headphones under $50 on amazon")
        
        if data and 'products' in data:
            for product in data['products']:
                print(product['title'], product['price'])
    """
    
    def __init__(self, **kwargs):
        self._agent = AutonomousAgent(**kwargs)
    
    def run(self, task: str, max_steps: int = 25) -> tuple:
        """Run a task and return (success, data)"""
        return self._agent.run(task, max_steps=max_steps)
    
    def close(self):
        """Close the agent"""
        self._agent.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()