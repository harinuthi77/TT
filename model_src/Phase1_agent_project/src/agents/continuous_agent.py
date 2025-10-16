"""
Continuous Agent - COMPLETELY FIXED
Multi-step automated workflow with startup navigation and fallback strategies
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path
from typing import Dict, Tuple
import re

from src.core.memory import AgentMemory, extract_domain
from src.core.vision import Vision
from src.core.cognition import CognitiveEngine
from src.core.executor import ActionExecutor
from src.core.config import (
    MAX_STEPS_PER_TASK, 
    RESULTS_DIR,
    DEFAULT_START_URL,
    ENABLE_STARTUP_NAVIGATION,
    MAX_COGNITION_FAILURES,
    ENABLE_RULE_BASED_FALLBACK,
    FALLBACK_SEARCH_ENGINE
)


class ContinuousAgent:
    """
    Agent with startup navigation and intelligent fallback
    Works on ANY website with robust error recovery
    """
    
    def __init__(self, api_key: str = None, debug: bool = True):
        self.debug = debug
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize core systems
        self.memory = AgentMemory(str(self.results_dir / "agent_brain.db"))
        self.vision = Vision(self.memory, debug=debug)
        self.cognition = CognitiveEngine(self.memory, api_key)
        
        # Track failures for fallback
        self.cognition_failures = 0
        self.using_fallback = False
        
        if self.debug:
            print("✅ Continuous Agent initialized")
    
    def run_continuous(self, task: str, max_iterations: int = 1) -> Tuple[bool, Dict]:
        """
        Run agent in continuous mode with startup navigation
        
        Args:
            task: Task description
            max_iterations: Not used, kept for compatibility
            
        Returns:
            (success, data) tuple
        """
        
        print("=" * 80)
        print(f"🌐 CONTINUOUS MODE - Task: {task}")
        print("=" * 80)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            executor = ActionExecutor(page, self.memory)
            
            try:
                # CRITICAL FIX: Navigate to starting URL
                if ENABLE_STARTUP_NAVIGATION:
                    startup_url = self._determine_startup_url(task)
                    print(f"\n🚀 Starting at: {startup_url}")
                    page.goto(startup_url, wait_until='domcontentloaded', timeout=30000)
                    time.sleep(2)
                
                # Execute task
                success, data = self._execute_task(page, executor, task)
                
                # Print summary
                print(f"\n{'=' * 80}")
                print(f"📊 TASK SUMMARY")
                print(f"{'=' * 80}")
                print(f"Task: {task}")
                print(f"Status: {'✅ Completed' if success else '⏸️ Incomplete'}")
                
                if data:
                    if data.get('products'):
                        print(f"\n🛒 Products found: {len(data['products'])}")
                    if data.get('articles'):
                        print(f"📄 Articles found: {len(data['articles'])}")
                    if data.get('tables'):
                        print(f"📊 Tables found: {len(data['tables'])}")
                    if data.get('links'):
                        print(f"🔗 Links found: {len(data['links'])}")
                
                if self.using_fallback:
                    print(f"\n⚠️  Used rule-based fallback (Claude API issues)")
                
                print(f"{'=' * 80}\n")
                
            except KeyboardInterrupt:
                print("\n⏸️ Stopped by user")
                success, data = False, {}
            finally:
                browser.close()
        
        return success, data or {'status': 'completed', 'task': task}
    
    def _determine_startup_url(self, task: str) -> str:
        """
        Intelligently determine starting URL from task
        
        CRITICAL FIX: Never start at blank page!
        """
        task_lower = task.lower()
        
        # Check for explicit domains
        domain_patterns = [
            (r'amazon\.com|amazon', 'https://www.amazon.com'),
            (r'github\.com|github', 'https://github.com/trending'),
            (r'wikipedia|wiki', 'https://en.wikipedia.org'),
            (r'reddit\.com|reddit', 'https://www.reddit.com'),
            (r'youtube\.com|youtube', 'https://www.youtube.com'),
            (r'google\.com|google', 'https://www.google.com'),
            (r'stackoverflow|stack overflow', 'https://stackoverflow.com'),
            (r'hacker\s*news|news\.ycombinator', 'https://news.ycombinator.com'),
        ]
        
        for pattern, url in domain_patterns:
            if re.search(pattern, task_lower):
                return url
        
        # Default: Google search with task keywords
        keywords = self._extract_search_keywords(task)
        if keywords:
            search_query = '+'.join(keywords[:5])
            return f"{FALLBACK_SEARCH_ENGINE}{search_query}"
        
        return DEFAULT_START_URL
    
    def _extract_search_keywords(self, task: str) -> list:
        """Extract meaningful keywords for search"""
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                     'for', 'of', 'with', 'by', 'from', 'find', 'search', 'get',
                     'go', 'navigate', 'can', 'you', 'me', 'about', 'give'}
        
        words = re.findall(r'\b\w+\b', task.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return keywords
    
    def _execute_task(self, page, executor, task: str, 
                     max_steps: int = MAX_STEPS_PER_TASK) -> Tuple[bool, Dict]:
        """Execute task with fallback strategy"""
        
        self.cognition.reset_conversation()
        self.memory.clear_recent_actions()
        
        for step in range(1, max_steps + 1):
            print(f"\n{'=' * 80}")
            print(f"STEP {step}/{max_steps}")
            print(f"{'=' * 80}")
            
            time.sleep(1.5)
            
            # CRITICAL FIX: Check if page is blank
            if page.url in ('', 'about:blank', 'data:,'):
                print("   ⚠️  Blank page detected - navigating to start URL")
                startup_url = self._determine_startup_url(task)
                page.goto(startup_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
            
            # Vision: detect elements
            print("\n👁️ VISION PHASE")
            elements = self.vision.detect_all_elements(page)
            
            if not elements:
                print("   ⚠️ No elements detected - retrying with scroll...")
                page.evaluate("window.scrollTo(0, 300)")
                time.sleep(1)
                elements = self.vision.detect_all_elements(page)
            
            # Create labeled screenshot
            screenshot_bytes, screenshot_b64 = self.vision.create_labeled_screenshot(page, elements)
            
            if not screenshot_b64:
                print("   ❌ Screenshot failed - skipping step")
                continue
            
            # Extract page data
            page_data = self.vision.extract_page_content(page)
            page_analysis = self.vision.analyze_page_structure(page)
            
            # Show what we found
            if page_data.get('products'):
                print(f"   🛒 {len(page_data['products'])} products found")
            if page_data.get('articles'):
                print(f"   📄 {len(page_data['articles'])} articles found")
            if page_data.get('tables'):
                print(f"   📊 {len(page_data['tables'])} tables found")
            if page_data.get('links'):
                print(f"   🔗 {len(page_data['links'])} navigation links found")
            
            # Cognition: decide action
            print("\n🧠 COGNITION PHASE")
            
            # CRITICAL FIX: Use fallback if too many failures
            if self.cognition_failures >= MAX_COGNITION_FAILURES and ENABLE_RULE_BASED_FALLBACK:
                if not self.using_fallback:
                    print(f"   ⚠️  Switching to RULE-BASED FALLBACK (Claude API failed {self.cognition_failures}x)")
                    self.using_fallback = True
                
                decision = self._rule_based_decision(task, page, elements, page_data)
            else:
                decision = self.cognition.think(
                    page=page,
                    task=task,
                    screenshot_b64=screenshot_b64,
                    elements=elements,
                    page_data=page_data,
                    page_analysis=page_analysis
                )
                
                # Track failures
                if 'Claude API error' in str(decision.get('thinking', '')):
                    self.cognition_failures += 1
                else:
                    self.cognition_failures = 0
            
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
                self.memory.clear_recent_actions()
                
                # Try to recover by going back or to start URL
                if step > 10:
                    print("   🔄 Navigating to start URL to recover...")
                    startup_url = self._determine_startup_url(task)
                    page.goto(startup_url, wait_until='domcontentloaded', timeout=30000)
                    time.sleep(2)
                
                continue
        
        print(f"\n⏰ Max steps ({max_steps}) reached")
        return False, page_data or {}
    
    def _rule_based_decision(self, task: str, page, elements: list, 
                            page_data: dict) -> Dict:
        """
        Simple rule-based fallback when Claude API fails
        
        CRITICAL FIX: Prevents infinite wait loops
        """
        
        task_lower = task.lower()
        url = page.url
        
        # Rule 1: If we have data, extract it
        if page_data.get('products') or page_data.get('articles') or page_data.get('tables'):
            return {
                'thinking': 'Found data on page - extracting',
                'action': 'extract',
                'details': 'all',
                'confidence': 8,
                'analysis': 'Rule-based decision'
            }
        
        # Rule 2: If search box exists, use it
        search_inputs = [e for e in elements if e.get('type') in ['search', 'text'] and e.get('visible')]
        if search_inputs and 'search' not in url.lower():
            # Extract search query from task
            keywords = self._extract_search_keywords(task)
            query = ' '.join(keywords[:3])
            
            return {
                'thinking': f'Found search box - searching for: {query}',
                'action': 'type',
                'details': query,
                'confidence': 8,
                'analysis': 'Rule-based decision'
            }
        
        # Rule 3: Click first relevant link
        for elem in elements[:10]:
            if not elem.get('visible'):
                continue
            
            elem_text = (elem.get('text') or '').lower()
            
            # Check if element text matches task keywords
            keywords = self._extract_search_keywords(task)
            matches = sum(1 for kw in keywords if kw in elem_text)
            
            if matches >= 1:
                return {
                    'thinking': f'Clicking relevant element: {elem["text"][:50]}',
                    'action': 'click',
                    'details': str(elem['id']),
                    'confidence': 7,
                    'analysis': 'Rule-based decision'
                }
        
        # Rule 4: Scroll down if no options
        return {
            'thinking': 'No clear action - scrolling to see more content',
            'action': 'scroll',
            'details': '600',
            'confidence': 6,
            'analysis': 'Rule-based decision'
        }
    
    def close(self):
        """Clean up resources"""
        if self.memory:
            self.memory.close()