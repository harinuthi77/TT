# Only the CHANGED sections (full file too long):

# CHANGE 1: In execute() method around line 93
def execute(self, decision: Dict, elements: List[Dict]) -> Tuple[bool, str]:
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
    
    # 🔴 PHASE 1 FIX: Only execute on confidence 9-10
    if confidence < 9:
        print(f"   ⛔ CONFIDENCE TOO LOW: {confidence}/10 (need 9+)")
        print(f"   🔄 Rejecting action - agent will re-analyze...")
        self.memory.record_failure(domain, action, f"Confidence {confidence}/10 too low")
        return False, f"⛔ Confidence {confidence}/10 insufficient (need 9+)"
    
    # Pre-action delay (thinking/moving mouse)
    self.behavior.delay(1.0, 2.0)
    # ... rest of method


# CHANGE 2: Uncomment bot handler (lines 175-220)
def _enhanced_bot_detection_handler(self, page, action_type: str = "navigation"):
    """Multi-strategy bot detection handler"""
    import random
    
    content = page.content().lower()
    bot_indicators = ['robot', 'captcha', 'unusual traffic', 'verify you are human']
    
    if not any(indicator in content for indicator in bot_indicators):
        return True
    
    print(f"   🚨 Bot detection during {action_type}")
    
    strategies = [
        ('Brief Pause', lambda: page.wait_for_timeout(random.randint(8000, 12000))),
        ('Human Movement', lambda: self._simulate_human_movement(page)),
        ('Cookie Reset', lambda: self._reset_cookies(page)),
        ('Fresh Navigation', lambda: self._navigate_fresh(page))
    ]
    
    for idx, (name, action) in enumerate(strategies):
        try:
            print(f"   Strategy {idx + 1}: {name}")
            action()
            page.wait_for_timeout(random.randint(2000, 4000))
            
            new_content = page.content().lower()
            if not any(indicator in new_content for indicator in bot_indicators):
                print(f"   ✅ Cleared with {name}")
                return True
        except Exception as e:
            print(f"   ❌ {name} failed: {e}")
    
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


# CHANGE 3: Use handler in _handle_goto (line 240)
def _handle_goto(self, url: str, domain: str) -> Tuple[bool, str]:
    if not url.startswith('http'):
        url = 'https://' + url
    
    print(f"   🌐 Navigating to {url}...")
    
    try:
        self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
        self.behavior.delay(2.0, 3.5)
        
        # 🔴 PHASE 1 FIX: Use enhanced bot handler
        content = self.page.content().lower()
        bot_indicators = ['captcha', 'robot', 'unusual traffic', 'verify you are human']
        
        if any(indicator in content for indicator in bot_indicators):
            print(f"   🚨 Bot detection - using multi-strategy handler...")
            
            cleared = self._enhanced_bot_detection_handler(self.page, "navigation")
            
            if not cleared:
                self.memory.record_failure(domain, 'goto', 'Bot detection', page_url=url)
                self.memory.update_domain_insight(domain, 1, False, has_bot_detection=True)
                return False, "⚠️ Bot detection - all strategies failed"
        
        self.memory.record_success(domain, 'goto', url, confidence=8.0)
        return True, f"✅ Loaded {url}"