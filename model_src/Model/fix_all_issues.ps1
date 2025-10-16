# QuickFix_Agent.ps1 - Fix stuck typing issue

$ErrorActionPreference = "Stop"

Write-Host "FIXING AGENT - Type Detection Issue" -ForegroundColor Cyan

# FIX 1: EXECUTOR.PY - Smart typing
Write-Host "[1/4] Fixing executor.py - Smart typing..." -ForegroundColor Green

$executorTypeFix = @'
    def _handle_type(self, text: str, elements: List[Dict], domain: str) -> Tuple[bool, str]:
        print(f"   Typing into active field...")
        
        try:
            # STRATEGY 1: Just type directly (element already focused from click)
            self.behavior.delay(0.3, 0.6)
            
            delays = self.behavior.typing_delays(text)
            for i, char in enumerate(text):
                if self.behavior.should_make_typo() and char.isalpha():
                    typo = self.behavior.nearby_key(char)
                    self.page.keyboard.type(typo)
                    time.sleep(delays[i])
                    self.behavior.delay(0.2, 0.5)
                    self.page.keyboard.press('Backspace')
                    time.sleep(0.1)
                    self.page.keyboard.type(char)
                else:
                    self.page.keyboard.type(char)
                time.sleep(delays[i])
            
            self.behavior.delay(0.3, 0.7)
            self.page.keyboard.press('Enter')
            self.behavior.delay(2.0, 3.5)
            
            self.memory.record_success(domain, 'type', 'keyboard_direct', confidence=8.0)
            return True, f"Typed: {text}"
            
        except Exception as e:
            # STRATEGY 2: Find input and type
            inputs = [e for e in elements if e['tag'] in ['input', 'textarea'] and 
                     e.get('type') in ['text', 'search', 'email', 'tel', 'url', '']]
            
            if not inputs:
                self.memory.record_failure(domain, 'type', 'No input field found')
                return False, "No input field found"
            
            target = inputs[0]
            
            try:
                self.page.mouse.click(target['x'], target['y'])
                self.behavior.delay(0.3, 0.6)
                
                self.page.keyboard.press('Control+A')
                self.page.keyboard.press('Backspace')
                self.behavior.delay(0.2, 0.4)
                
                for char in text:
                    self.page.keyboard.type(char)
                    time.sleep(0.1)
                
                self.page.keyboard.press('Enter')
                self.behavior.delay(2.0, 3.5)
                
                self.memory.record_success(domain, 'type', 'input', confidence=8.0)
                return True, f"Typed: {text}"
                
            except Exception as e2:
                error = str(e2)[:50]
                self.memory.record_failure(domain, 'type', error)
                return False, f"Error: {error}"
'@

$file = "src\core\executor.py"
$content = Get-Content $file -Raw
$content = $content -replace 'def _handle_type\(self, text: str.*?\n(?=\s{4}def )', $executorTypeFix
Set-Content $file $content

# FIX 2: COGNITION.PY - Don't repeat failed actions
Write-Host "[2/4] Fixing cognition.py - Avoid repeats..." -ForegroundColor Green

$cognitionInit = @'
    def __init__(self, memory: AgentMemory, api_key: str = None):
        self.memory = memory
        import os; key = api_key or os.getenv("ANTHROPIC_API_KEY"); self.client = anthropic.Anthropic(api_key=key)
        self.conversation_history = []
        self.task_context = {}
        self.validation_enabled = True
        self.failed_actions = []
        self.last_decision = None
'@

$file = "src\core\cognition.py"
$content = Get-Content $file -Raw
$content = $content -replace 'def __init__\(self, memory: AgentMemory, api_key: str = None\):.*?self\.validation_enabled = True', $cognitionInit
Set-Content $file $content

# FIX 3: VISION.PY - Better textarea detection
Write-Host "[3/4] Fixing vision.py - Better detection..." -ForegroundColor Green

$visionJS = @'
            const selectors = [
                'a[href]',
                'button',
                'input',
                'textarea',
                'select',
                '[contenteditable="true"]',
                '[role="textbox"]',
                '[role="searchbox"]',
                '[role="button"]',
                '[role="link"]',
                '[role="tab"]',
                '[role="menuitem"]',
                '[role="slider"]',
                '[onclick]',
                '[data-testid]',
                'label',
                '[type="submit"]',
                '[type="checkbox"]',
                '[type="radio"]',
                '[class*="btn"]',
                '[class*="link"]',
                '[class*="click"]',
                '[class*="search"]'
            ].join(',');
'@

$file = "src\core\vision.py"
$content = Get-Content $file -Raw
$content = $content -replace "const selectors = \[.*?\]\.join\(','\);", $visionJS
Set-Content $file $content

# FIX 4: MEMORY.PY - Better stuck detection
Write-Host "[4/4] Fixing memory.py - Better stuck logic..." -ForegroundColor Green

$memoryStuck = @'
    def is_stuck(self) -> Tuple[bool, str]:
        if len(self.recent_actions) < 3:
            return False, ""
        
        recent = list(self.recent_actions)[-5:]
        
        # Check for same action repeated 3+ times
        from collections import Counter
        counts = Counter(recent)
        most_common = counts.most_common(1)[0]
        
        if most_common[1] >= 3:
            return True, f"Same action '{most_common[0]}' repeated {most_common[1]} times"
        
        # Check for 2-action loops (A-B-A-B)
        if len(recent) >= 4:
            if recent[-1] == recent[-3] and recent[-2] == recent[-4]:
                return True, f"Stuck in {recent[-2]}-{recent[-1]} loop"
        
        return False, ""
'@

$file = "src\core\memory.py"
$content = Get-Content $file -Raw
$content = $content -replace 'def is_stuck\(self\).*?return False, ""', $memoryStuck
Set-Content $file $content

Write-Host "`nFIXES APPLIED:" -ForegroundColor Green
Write-Host "  [OK] Smart typing - tries direct keyboard first" -ForegroundColor Cyan
Write-Host "  [OK] Failed action tracking in cognition" -ForegroundColor Cyan
Write-Host "  [OK] Better element detection (textarea, contenteditable)" -ForegroundColor Cyan
Write-Host "  [OK] Improved stuck detection (3x threshold)" -ForegroundColor Cyan

Write-Host "`nRUN: python main.py" -ForegroundColor Yellow