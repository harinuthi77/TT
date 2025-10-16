# executor.py
# =============================================================================
# ACTION EXECUTOR - THE HANDS
# Executes actions with human-like behavior and anti-bot techniques
# UPDATED: Added slider support for price filters, etc.
# =============================================================================

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
import time
import random
import math
from typing import Dict, List, Tuple, Optional

# ===== INTERLINK WITH OTHER MODULES =====
from .memory import AgentMemory, extract_domain


# =============================================================================
# HUMAN BEHAVIOR SIMULATOR
# =============================================================================

class HumanBehavior:
    """
    Simulates realistic human interactions to avoid bot detection.
    All timings and movements are randomized to appear natural.
    """
    
    @staticmethod
    def delay(min_sec: float = 0.8, max_sec: float = 2.5):
        """Random delay between actions"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def reading_time(text: str) -> float:
        """Calculate realistic reading time based on text length"""
        if not text:
            return random.uniform(0.3, 0.8)
        
        words = len(text.split())
        # Average reading speed: 200-250 words per minute
        base_time = (words / 225) * 60
        # Add randomness (some people read faster/slower)
        return base_time * random.uniform(0.7, 1.3)
    
    @staticmethod
    def mouse_path(start_x: int, start_y: int, end_x: int, end_y: int, 
                   steps: int = 30) -> List[Tuple[int, int]]:
        """
        Generate a realistic curved mouse path using Bezier curves.
        Humans don't move mouse in straight lines!
        """
        path = []
        
        # Create control points for Bezier curve
        # Add some randomness to make it look natural
        ctrl1_x = start_x + (end_x - start_x) * random.uniform(0.2, 0.4)
        ctrl1_y = start_y + (end_y - start_y) * random.uniform(-0.2, 0.2)
        ctrl2_x = start_x + (end_x - start_x) * random.uniform(0.6, 0.8)
        ctrl2_y = start_y + (end_y - start_y) * random.uniform(-0.2, 0.2)
        
        for i in range(steps):
            t = i / steps
            
            # Cubic Bezier curve formula
            x = (1-t)**3 * start_x + \
                3*(1-t)**2*t * ctrl1_x + \
                3*(1-t)*t**2 * ctrl2_x + \
                t**3 * end_x
            
            y = (1-t)**3 * start_y + \
                3*(1-t)**2*t * ctrl1_y + \
                3*(1-t)*t**2 * ctrl2_y + \
                t**3 * end_y
            
            # Add micro-jitter (hand tremor)
            jitter_x = random.uniform(-2, 2)
            jitter_y = random.uniform(-2, 2)
            
            path.append((int(x + jitter_x), int(y + jitter_y)))
        
        # Ensure we end exactly at target
        path.append((end_x, end_y))
        
        return path
    
    @staticmethod
    def typing_delays(text: str) -> List[float]:
        """
        Generate realistic typing delays for each character.
        Includes natural pauses and variations.
        """
        delays = []
        
        for i, char in enumerate(text):
            # Base typing speed: 80-150ms per character
            base_delay = random.uniform(0.08, 0.15)
            
            # Spaces take longer (thinking pause)
            if char == ' ':
                base_delay += random.uniform(0.1, 0.3)
            
            # Occasional longer pauses (thinking/looking at keyboard)
            if random.random() < 0.05:
                base_delay += random.uniform(0.3, 0.8)
            
            # Sometimes faster when in "flow"
            if i > 0 and random.random() < 0.3:
                base_delay *= 0.7
            
            delays.append(base_delay)
        
        return delays
    
    @staticmethod
    def should_make_typo() -> bool:
        """3% chance of making a typo (realistic!)"""
        return random.random() < 0.03
    
    @staticmethod
    def nearby_key(char: str) -> str:
        """Get a nearby key for typo simulation"""
        keyboard_layout = {
            'a': ['s', 'q', 'w', 'z'], 'b': ['v', 'g', 'n', 'h'],
            'c': ['x', 'd', 'v', 'f'], 'd': ['s', 'e', 'f', 'c', 'x'],
            'e': ['w', 'r', 'd', 's'], 'f': ['d', 'r', 'g', 'c', 'v'],
            'g': ['f', 't', 'h', 'v', 'b'], 'h': ['g', 'y', 'j', 'b', 'n'],
            'i': ['u', 'o', 'k', 'j'], 'j': ['h', 'u', 'k', 'n', 'm'],
            'k': ['j', 'i', 'l', 'm'], 'l': ['k', 'o', 'p'],
            'm': ['n', 'j', 'k'], 'n': ['b', 'h', 'm', 'j'],
            'o': ['i', 'p', 'l', 'k'], 'p': ['o', 'l'],
            'q': ['w', 'a', 's'], 'r': ['e', 't', 'f', 'd'],
            's': ['a', 'w', 'd', 'x', 'z'], 't': ['r', 'y', 'g', 'f'],
            'u': ['y', 'i', 'h', 'j'], 'v': ['c', 'f', 'b', 'g'],
            'w': ['q', 'e', 's', 'a'], 'x': ['z', 's', 'c', 'd'],
            'y': ['t', 'u', 'h', 'g'], 'z': ['a', 's', 'x']
        }
        
        char_lower = char.lower()
        if char_lower in keyboard_layout and keyboard_layout[char_lower]:
            return random.choice(keyboard_layout[char_lower])
        return char


# =============================================================================
# ACTION EXECUTOR
# =============================================================================

class ActionExecutor:
    """
    Executes actions with human-like behavior.
    Integrates with memory to learn from successes and failures.
    """
    
    def __init__(self, page: Page, memory: AgentMemory):
        """
        Initialize executor.
        
        Args:
            page: Playwright page object
            memory: AgentMemory instance for learning
        """
        self.page = page
        self.memory = memory
        self.behavior = HumanBehavior()
        self.current_mouse_pos = (0, 0)
        self.last_action_success = True
        
    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    

    def _enhanced_bot_detection_handler(self, page, action_type: str = "navigation"):
        """Multi-strategy bot detection handler"""
        import random
        
        content = page.content().lower()
        bot_indicators = ['robot', 'captcha', 'unusual traffic', 'verify you are human']
        
        if not any(indicator in content for indicator in bot_indicators):
            return True
        
        self.logger.warning(f"Bot detection during {action_type}")
        
        strategies = [
            ('Brief Pause', lambda: page.wait_for_timeout(random.randint(8000, 12000))),
            ('Human Movement', lambda: self._simulate_human_movement(page)),
            ('Cookie Reset', lambda: self._reset_cookies(page)),
            ('Fresh Navigation', lambda: self._navigate_fresh(page))
        ]
        
        for idx, (name, action) in enumerate(strategies):
            try:
                self.logger.info(f"   Strategy {idx + 1}: {name}")
                action()
                page.wait_for_timeout(random.randint(2000, 4000))
                
                new_content = page.content().lower()
                if not any(indicator in new_content for indicator in bot_indicators):
                    self.logger.info(f"   [OK] Cleared with {name}")
                    return True
            except Exception as e:
                self.logger.error(f"   [ERROR] {name} failed: {e}")
        
        return False
    
    def _simulate_human_movement(self, page):
        """Simulate human mouse movements"""
        import random
        for _ in range(random.randint(3, 5)):
            x, y = random.randint(100, 800), random.randint(100, 600)
            page.mouse.move(x, y)
            page.wait_for_timeout(random.randint(200, 500))
        page.evaluate(f"window.scrollTo(0, {random.randint(100, 400)})")
    
    def _reset_cookies(self, page):
        """Clear cookies and reload"""
        page.context.clear_cookies()
        page.wait_for_timeout(2000)
        page.reload(wait_until='domcontentloaded')
    
    def _navigate_fresh(self, page):
        """Navigate to homepage then back"""
        import random
        current_url = page.url
        domain = current_url.split('/')[2] if '/' in current_url else current_url
        page.goto(f"https://{domain}", wait_until='domcontentloaded', timeout=10000)
        page.wait_for_timeout(random.randint(3000, 5000))
        page.goto(current_url, wait_until='domcontentloaded', timeout=15000)
    def execute(self, decision: Dict, elements: List[Dict]) -> Tuple[bool, str]:
        """
        Execute an action based on cognitive decision.
        
        Args:
            decision: Decision dict from cognition engine
            elements: List of detected elements
        
        Returns:
            (success, message)
        """
        
        action = decision['action']
        details = decision['details']
        confidence = decision.get('confidence', 5)
        
        url = self.page.url
        domain = extract_domain(url)
        
        print(f"\n⚡ EXECUTING ACTION")
        print(f"   {'─' * 60}")
        print(f"   Action: {action.upper()}")
        print(f"   Details: {details}")
        print(f"   Confidence: {confidence}/10")
        
        # Pre-action delay (thinking/moving mouse)
        self.behavior.delay(1.0, 2.0)
        
        try:
            # Route to appropriate handler
            if action == "done":
                return self._handle_done()
            elif action == "goto":
                return self._handle_goto(details, domain)
            elif action == "type":
                return self._handle_type(details, elements, domain)
            elif action == "click":
                return self._handle_click(details, elements, domain)
            elif action == "scroll":
                return self._handle_scroll(details, domain)
            elif action == "extract":
                return self._handle_extract(domain)
            elif action == "slider":
                return self._handle_slider(details, elements, domain)
            elif action == "wait":
                return self._handle_wait(details)
            else:
                return False, f"Unknown action: {action}"
                
        except Exception as e:
            error_msg = str(e)[:100]
            self.memory.record_failure(domain, action, error_msg, page_url=url)
            return False, f"❌ Error: {error_msg}"
    
    # =========================================================================
    # ACTION HANDLERS
    # =========================================================================
    
    def _handle_done(self) -> Tuple[bool, str]:
        """Handle task completion"""
        print("   ✅ Task marked as complete")
        return True, "Task completed"
    
    def _handle_goto(self, url: str, domain: str) -> Tuple[bool, str]:
        """
        Navigate to URL with bot detection handling.
        """
        # Ensure URL has protocol
        if not url.startswith('http'):
            url = 'https://' + url
        
        print(f"   🌐 Navigating to {url}...")
        
        try:
            # Navigate
            self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for page to settle
            self.behavior.delay(2.0, 3.5)
            
            # Check for bot detection
            content = self.page.content().lower()
            bot_indicators = [
                'captcha', 'robot', 'unusual traffic', 
                'verify you are human', 'press & hold',
                'security check', 'automated'
            ]
            
            if any(indicator in content for indicator in bot_indicators):
                print(f"   ⚠️  Bot detection - using strategies...")
                
                # Wait longer and move mouse naturally
                self.behavior.delay(5.0, 8.0)
                
                # Move mouse to appear human
                try:
                    self.page.mouse.move(500, 500)
                    self.behavior.delay(1.0, 2.0)
                    self.page.mouse.move(800, 400)
                except:
                    pass
                
                # Check again
                content = self.page.content().lower()
                if any(indicator in content for indicator in bot_indicators):
                    self.memory.record_failure(domain, 'goto', 'Bot detection', page_url=url)
                    self.memory.update_domain_insight(domain, 1, False, has_bot_detection=True)
                    return False, "⚠️  Bot detection - may need manual intervention"
            
            # Success
            self.memory.record_success(domain, 'goto', url, confidence=8.0)
            return True, f"✅ Loaded {url}"
            
        except PlaywrightTimeout:
            self.memory.record_failure(domain, 'goto', 'Timeout', page_url=url)
            return False, "⏱️  Page load timeout"
            
        except Exception as e:
            error = str(e)[:50]
            self.memory.record_failure(domain, 'goto', error, page_url=url)
            return False, f"❌ {error}"
    
    def _handle_type(self, text: str, elements: List[Dict], domain: str) -> Tuple[bool, str]:
        """
        Type text into input field with realistic human behavior.
        """
        # Find input fields
        inputs = [e for e in elements if e['tag'] == 'input' and 
                 e.get('type') in ['text', 'search', 'email', 'tel', 'url', '']]
        
        if not inputs:
            self.memory.record_failure(domain, 'type', 'No input field found')
            return False, "❌ No input field found"
        
        # Use first visible input
        target = inputs[0]
        
        print(f"   ⌨️  Typing into input field...")
        
        # Move mouse to input with curved path
        path = self.behavior.mouse_path(
            self.current_mouse_pos[0], self.current_mouse_pos[1],
            target['x'], target['y']
        )
        
        for x, y in path:
            self.page.mouse.move(x, y)
            time.sleep(0.01)  # Smooth movement
        
        self.current_mouse_pos = (target['x'], target['y'])
        
        # Click input field
        self.page.mouse.click(target['x'], target['y'])
        self.behavior.delay(0.3, 0.6)
        
        # Clear existing text
        self.page.keyboard.press('Control+A')
        self.page.keyboard.press('Backspace')
        self.behavior.delay(0.2, 0.4)
        
        # Type with realistic delays and occasional typos
        delays = self.behavior.typing_delays(text)
        
        for i, char in enumerate(text):
            # Occasionally make a typo and correct it
            if self.behavior.should_make_typo() and char.isalpha():
                typo = self.behavior.nearby_key(char)
                self.page.keyboard.type(typo)
                time.sleep(delays[i])
                
                # Realize mistake, pause
                self.behavior.delay(0.2, 0.5)
                
                # Backspace and correct
                self.page.keyboard.press('Backspace')
                time.sleep(0.1)
                self.page.keyboard.type(char)
            else:
                self.page.keyboard.type(char)
            
            time.sleep(delays[i])
        
        # Pause before pressing Enter (human hesitation)
        self.behavior.delay(0.3, 0.7)
        
        # Press Enter to submit
        self.page.keyboard.press('Enter')
        
        # Wait for results to load
        self.behavior.delay(2.0, 3.5)
        
        # Record success
        self.memory.record_success(domain, 'type', 'input', confidence=8.0)
        
        return True, f"✅ Typed: {text}"
    
    def _handle_click(self, identifier: str, elements: List[Dict], domain: str) -> Tuple[bool, str]:
        """
        Click an element with human-like mouse movement.
        """
        # Find target element
        target = None
        
        # Try to parse as element ID
        try:
            elem_id = int(identifier.strip())
            target = next((e for e in elements if e['id'] == elem_id), None)
        except:
            # Try to find by text content
            search_text = identifier.lower().strip()
            for e in elements:
                elem_text = (e.get('text') or '').lower()
                if search_text in elem_text:
                    target = e
                    break
        
        if not target:
            self.memory.record_failure(domain, 'click', f'Element not found: {identifier}')
            return False, f"❌ Element not found: {identifier}"
        
        print(f"   🖱️  Clicking element [{target['id']}]: {target.get('text', '')[:40]}...")
        
        # Scroll if element not in viewport
        if not target.get('visible') or target['top'] < 50 or target['top'] > 900:
            print(f"   📜 Scrolling to element...")
            scroll_to = max(0, target['top'] - 300)
            self.page.evaluate(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}})")
            self.behavior.delay(0.8, 1.3)
        
        # Move mouse with curved path
        path = self.behavior.mouse_path(
            self.current_mouse_pos[0], self.current_mouse_pos[1],
            target['x'], target['y']
        )
        
        for x, y in path:
            self.page.mouse.move(x, y)
            time.sleep(0.01)
        
        self.current_mouse_pos = (target['x'], target['y'])
        
        # Hover and "read" the element
        if target.get('text'):
            hover_time = self.behavior.reading_time(target['text'])
            time.sleep(min(hover_time, 2.0))  # Max 2 seconds
        else:
            self.behavior.delay(0.3, 0.8)
        
        # Click with realistic press/release
        self.page.mouse.down()
        time.sleep(random.uniform(0.05, 0.15))  # Button press duration
        self.page.mouse.up()
        
        # Wait for response
        self.behavior.delay(1.5, 2.5)
        
        # Record success
        selector = f"{target['tag']}"
        if target.get('className'):
            selector += f".{target['className'].split()[0]}"
        
        self.memory.record_success(domain, 'click', selector, 
                                   context=target.get('text', '')[:30],
                                   confidence=8.0)
        
        return True, f"✅ Clicked: {target.get('text', 'element')[:40]}"
    
    def _handle_slider(self, details: str, elements: List[Dict], domain: str) -> Tuple[bool, str]:
        """
        Set slider value with proper event dispatching.
        Format: "element_id value"
        Example: "42 250" sets slider [42] to 250
        """
        try:
            # Parse "element_id value"
            parts = details.split()
            if len(parts) < 2:
                return False, "❌ Slider format: 'element_id value'"
            
            elem_id = int(parts[0])
            value = float(parts[1])
            
            # Find slider element
            target = next((e for e in elements if e['id'] == elem_id), None)
            
            if not target:
                return False, f"❌ Element {elem_id} not found"
            
            if target.get('type') != 'range' and target.get('role') != 'slider':
                return False, f"❌ Element {elem_id} is not a slider"
            
            print(f"   🎚️  Setting slider [{elem_id}] to {value}...")
            
            # Move mouse to slider
            self.page.mouse.move(target['x'], target['y'])
            self.behavior.delay(0.5, 1.0)
            
            # Set slider value with proper events
            success = self.page.evaluate("""
                ({x, y, value}) => {
                    const el = document.elementFromPoint(x, y);
                    if (!el) return false;
                    
                    let slider = el;
                    if (el.tagName.toLowerCase() !== 'input') {
                        slider = el.closest('input[type="range"]') || 
                                el.querySelector('input[type="range"]');
                    }
                    
                    if (slider && slider.type === 'range') {
                        slider.value = value;
                        slider.dispatchEvent(new Event('input', { bubbles: true }));
                        slider.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                    
                    // Try ARIA slider
                    if (el.getAttribute('role') === 'slider') {
                        el.setAttribute('aria-valuenow', value);
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                    
                    return false;
                }
            """, {'x': target['x'], 'y': target['y'], 'value': value})
            
            if success:
                self.memory.record_success(domain, 'slider', f"slider.{elem_id}", confidence=8.0)
                return True, f"✅ Set slider to {value}"
            else:
                self.memory.record_failure(domain, 'slider', 'Failed to set value')
                return False, "❌ Failed to set slider value"
                
        except Exception as e:
            error = str(e)[:50]
            self.memory.record_failure(domain, 'slider', error)
            return False, f"❌ Slider error: {error}"
    
    def _handle_scroll(self, details: str, domain: str) -> Tuple[bool, str]:
        """Scroll the page"""
        # Parse scroll amount
        pixels = 600  # Default
        try:
            pixels = int(details) if details else 600
        except:
            pass
        
        print(f"   📜 Scrolling {pixels}px...")
        
        # Smooth scroll
        self.page.evaluate(f"window.scrollBy({{top: {pixels}, behavior: 'smooth'}})")
        self.behavior.delay(1.2, 2.0)
        
        self.memory.record_success(domain, 'scroll', 'page', confidence=9.0)
        return True, f"✅ Scrolled {pixels}px"
    
    def _handle_extract(self, domain: str) -> Tuple[bool, str]:
        """
        Extract data from current page.
        This will be handled by vision module in the main agent.
        """
        print(f"   📊 Extracting data...")
        return True, "✅ Data extraction requested"
    
    def _handle_wait(self, details: str) -> Tuple[bool, str]:
        """Wait/pause"""
        print(f"   ⏸️  Waiting...")
        self.behavior.delay(3.0, 5.0)
        return True, "⏸️  Waited"
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return self.current_mouse_pos
    
    def reset_position(self):
        """Reset mouse position"""
        self.current_mouse_pos = (0, 0)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("🖱️  Testing Action Executor (requires browser)\n")
    
    from playwright.sync_api import sync_playwright
    from .memory import AgentMemory
    
    memory = AgentMemory("test_brain.db")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.walmart.com")
        
        executor = ActionExecutor(page, memory)
        
        # Test goto
        print("\n1. Testing goto...")
        decision = {'action': 'goto', 'details': 'https://www.google.com', 'confidence': 8}
        success, msg = executor.execute(decision, [])
        print(f"   Result: {msg}")
        
        # Test typing (would need input field)
        print("\n2. Testing human behavior...")
        print(f"   Reading time for 'Hello World': {executor.behavior.reading_time('Hello World'):.2f}s")
        print(f"   Typing delays: {executor.behavior.typing_delays('test')}")
        
        # Test mouse path
        print("\n3. Testing mouse movement...")
        path = executor.behavior.mouse_path(0, 0, 500, 500, steps=10)
        print(f"   Generated {len(path)} waypoints")
        
        input("\nPress Enter to close...")
        browser.close()
    
    memory.close()
    print("\n✅ Executor test complete!")