# vision.py
# =============================================================================
# VISION SERVICE - Stealth + Multi-Color Element Detection
# Anti-bot configuration, persistent context, color-coded elements by type
# =============================================================================

from playwright.sync_api import Page, BrowserContext
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re


# Color coding by element type
ELEMENT_COLORS = {
    'searchbox': '#00BFFF',      # 🔵 Bright Blue - SEARCH BOXES
    'button': '#00FF00',          # 🟢 Green - BUTTONS
    'link': '#FFD700',            # 🟡 Yellow - LINKS
    'img': '#9932CC',             # 🟣 Purple - IMAGES
    'textbox': '#00CED1',         # 🔷 Cyan - TEXT INPUTS
    'heading': '#FF8C00',         # 🟠 Orange - HEADERS
    'combobox': '#FF69B4',        # 🌸 Pink - DROPDOWNS
    'checkbox': '#FF0000',        # 🔴 Red - CHECKBOXES
    'radio': '#FF0000',           # 🔴 Red - RADIOS
    'tab': '#32CD32',             # 🟢 Lime - TABS
    'generic': '#C0C0C0'          # ⚪ Gray - GENERIC
}


class Vision:
    """
    Stealth vision service with multi-color element detection.
    
    Features:
    - Anti-bot browser configuration
    - Persistent context (saves cookies/cache)
    - Color-coded element highlighting by type
    - Separate detection for each element category
    - Double precision with ID overlays
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.last_screenshot_path: Optional[str] = None
        self.context: Optional[BrowserContext] = None
    
    @staticmethod
    def create_stealth_context(playwright_instance) -> BrowserContext:
        """
        Create a persistent, stealth browser context that avoids bot detection.
        
        Features:
        - Persistent user data (cookies, cache, localStorage)
        - Real user agent
        - Geolocation spoofing
        - Timezone matching
        - No automation flags
        """
        from playwright.sync_api import sync_playwright
        
        # Persistent context directory
        user_data_dir = Path.home() / ".agent_browser_profile"
        user_data_dir.mkdir(exist_ok=True)
        
        # Stealth browser args
        browser_args = [
            '--disable-blink-features=AutomationControlled',  # Hide automation
            '--disable-dev-shm-usage',
            '--disable-web-security',  # For testing only
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--window-size=1920,1080',
            '--start-maximized',
            '--disable-notifications',
            '--disable-popup-blocking'
        ]
        
        # Launch with persistent context
        browser = playwright_instance.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            args=browser_args,
            viewport={'width': 1920, 'height': 1080},
            
            # Real user agent (not headless Chrome)
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Geolocation (New York)
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation'],
            
            # Timezone
            timezone_id='America/New_York',
            
            # Locale
            locale='en-US',
            
            # Extra HTTP headers
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': 'https://www.google.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Add JavaScript to hide automation indicators
        for page_context in browser.pages or [browser.new_page()]:
            page_context.add_init_script("""
                // Override navigator properties
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                
                // Chrome object
                window.chrome = {runtime: {}};
                
                // Permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
                
                // Remove automation indicators
                delete navigator.__proto__.webdriver;
            """)
        
        return browser
    
    def perceive(self, page: Page) -> Dict:
        """
        Main perception method - returns blueprint-compliant payload with
        multi-color element detection.
        
        Returns:
        {
            "url": str,
            "title": str,
            "screenshot_b64": str,
            "elements": [...],  # Separated by type
            "forms": [...],
            "hints": {"hasVerification": bool, "isSearchResults": bool},
            "element_stats": {"searchbox": 2, "button": 15, ...}
        }
        """
        try:
            url = page.url
            title = page.title()
            
            # 1. Harvest elements (ARIA-first, separated by type)
            elements, element_stats = self._harvest_elements_by_type(page)
            
            # 2. Detect forms
            forms = self._detect_forms(page, elements)
            
            # 3. Scan for verification/CAPTCHA
            hints = self._generate_hints(page)
            
            # 4. Create multi-color labeled screenshot
            screenshot_b64 = self._create_multicolor_screenshot(page, elements)
            
            perception = {
                "url": url,
                "title": title,
                "screenshot_b64": screenshot_b64,
                "elements": elements,
                "forms": forms,
                "hints": hints,
                "element_stats": element_stats
            }
            
            if self.debug:
                print(f"\n👁️ VISION PERCEPTION:")
                print(f"   URL: {url}")
                print(f"   Total Elements: {len(elements)}")
                print(f"   By Type: {element_stats}")
                print(f"   Forms: {len(forms)}")
                print(f"   Has Verification: {hints.get('hasVerification', False)}")
            
            return perception
            
        except Exception as e:
            print(f"❌ Vision error: {e}")
            return self._empty_perception(page)
    
    def _harvest_elements_by_type(self, page: Page) -> Tuple[List[Dict], Dict]:
        """
        Harvest elements with ARIA-first strategy, separated by type.
        Returns (elements_list, stats_dict)
        """
        
        js_code = r"""
        () => {
            const elements = [];
            const stats = {};
            const seen = new Set();
            let id = 1;
            
            // Element type priority (search boxes are most important!)
            const typePriority = {
                'searchbox': 1,
                'textbox': 2,
                'button': 3,
                'link': 4,
                'combobox': 5,
                'img': 6,
                'heading': 7,
                'checkbox': 8,
                'radio': 9,
                'tab': 10,
                'generic': 99
            };
            
            // Helper: Check if element is visible and actionable
            function isActionable(el) {
                if (!el) return false;
                
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                
                // In viewport with buffer
                const inViewport = rect.top < window.innerHeight + 200 && 
                                  rect.bottom > -200 && 
                                  rect.left < window.innerWidth + 200;
                
                // Visible
                const isVisible = style.display !== 'none' && 
                                 style.visibility !== 'hidden' && 
                                 style.opacity !== '0' &&
                                 rect.width > 2 && 
                                 rect.height > 2;
                
                return inViewport && isVisible;
            }
            
            // Helper: Get role (explicit or implicit)
            function getRole(el) {
                // Explicit ARIA role
                const ariaRole = el.getAttribute('role');
                if (ariaRole) return ariaRole;
                
                // Implicit roles
                const tag = el.tagName.toLowerCase();
                const type = el.getAttribute('type')?.toLowerCase();
                
                // CRITICAL: Detect search boxes specifically
                if (tag === 'input' && (type === 'search' || el.name === 'q' || el.name === 'search')) {
                    return 'searchbox';
                }
                if (tag === 'textarea' && (el.getAttribute('aria-label')?.toLowerCase().includes('search') || 
                                          el.placeholder?.toLowerCase().includes('search'))) {
                    return 'searchbox';
                }
                if (el.hasAttribute('contenteditable') && el.getAttribute('aria-label')?.toLowerCase().includes('search')) {
                    return 'searchbox';
                }
                
                // Standard mappings
                if (tag === 'button' || (tag === 'input' && type === 'submit')) return 'button';
                if (tag === 'a' && el.href) return 'link';
                if (tag === 'input' && (type === 'text' || type === 'email' || type === 'tel' || type === 'url')) return 'textbox';
                if (tag === 'input' && type === 'checkbox') return 'checkbox';
                if (tag === 'input' && type === 'radio') return 'radio';
                if (tag === 'textarea') return 'textbox';
                if (tag === 'select') return 'combobox';
                if (tag === 'img') return 'img';
                if (['h1','h2','h3','h4','h5','h6'].includes(tag)) return 'heading';
                if (el.getAttribute('role') === 'tab' || el.closest('[role="tablist"]')) return 'tab';
                
                // Clickable divs
                if (el.onclick || el.hasAttribute('tabindex')) return 'button';
                
                return 'generic';
            }
            
            // Helper: Get accessible name
            function getName(el) {
                if (el.getAttribute('aria-label')) return el.getAttribute('aria-label');
                
                const labelledBy = el.getAttribute('aria-labelledby');
                if (labelledBy) {
                    const labelEl = document.getElementById(labelledBy);
                    if (labelEl) return labelEl.innerText.trim();
                }
                
                // Check associated label
                if (el.id) {
                    const label = document.querySelector(`label[for="${el.id}"]`);
                    if (label) return label.innerText.trim();
                }
                
                if (el.placeholder) return el.placeholder;
                if (el.alt) return el.alt;
                if (el.title) return el.title;
                if (el.value && el.value.length < 30) return el.value;
                
                let text = el.innerText?.trim() || '';
                if (text.length > 80) text = text.substring(0, 77) + '...';
                
                return text;
            }
            
            // Helper: Generate selectors
            function getSelectors(el, role, name) {
                const selectors = {};
                const tag = el.tagName.toLowerCase();
                
                // Role-based (preferred for modern sites)
                if (role && role !== 'generic') {
                    if (name && name.length > 0) {
                        const safeName = name.replace(/['"]/g, '').substring(0, 30);
                        selectors.role = `[role="${role}"][aria-label*="${safeName}" i]`;
                    } else {
                        selectors.role = `[role="${role}"]`;
                    }
                }
                
                // CSS selector
                if (el.id && /^[a-zA-Z][\w-]*$/.test(el.id)) {
                    selectors.css = `#${el.id}`;
                } else {
                    let css = tag;
                    const stableClasses = Array.from(el.classList).filter(c => 
                        !/^[a-f0-9]{6,}$/i.test(c) && c.length < 30
                    ).slice(0, 2);
                    
                    if (stableClasses.length > 0) {
                        css += '.' + stableClasses.join('.');
                    }
                    
                    if (el.name) css += `[name="${el.name}"]`;
                    if (el.type) css += `[type="${el.type}"]`;
                    
                    selectors.css = css;
                }
                
                // XPath (last resort)
                selectors.xpath = getXPath(el);
                
                return selectors;
            }
            
            // Helper: Generate XPath
            function getXPath(el) {
                if (el.id) return `//*[@id="${el.id}"]`;
                const parts = [];
                while (el && el.nodeType === Node.ELEMENT_NODE) {
                    let index = 0;
                    let sibling = el.previousSibling;
                    while (sibling) {
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === el.tagName) {
                            index++;
                        }
                        sibling = sibling.previousSibling;
                    }
                    const tagName = el.tagName.toLowerCase();
                    const pathIndex = index > 0 ? `[${index + 1}]` : '';
                    parts.unshift(tagName + pathIndex);
                    el = el.parentNode;
                }
                return '/' + parts.join('/');
            }
            
            // PHASE 1: Collect all candidates
            const candidates = [];
            
            // Search boxes (HIGHEST PRIORITY)
            document.querySelectorAll('input[type="search"], input[name="q"], input[name="search"], textarea[aria-label*="search" i], [role="searchbox"], [contenteditable="true"][aria-label*="search" i]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // Text inputs
            document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="url"], input[type="password"], textarea, [role="textbox"]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // Buttons
            document.querySelectorAll('button, input[type="submit"], input[type="button"], [role="button"], [onclick]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // Links
            document.querySelectorAll('a[href], [role="link"]').forEach(el => {
                if (isActionable(el) && el.href !== 'javascript:void(0)') candidates.push(el);
            });
            
            // Dropdowns
            document.querySelectorAll('select, [role="combobox"], [role="listbox"]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // Images (for visual understanding)
            document.querySelectorAll('img, [role="img"]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // Headers (for context)
            document.querySelectorAll('h1, h2, h3, [role="heading"]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // Checkboxes & radios
            document.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // Tabs
            document.querySelectorAll('[role="tab"]').forEach(el => {
                if (isActionable(el)) candidates.push(el);
            });
            
            // PHASE 2: Process and deduplicate
            const processed = new Map();
            
            for (const el of candidates) {
                const rect = el.getBoundingClientRect();
                const role = getRole(el);
                const name = getName(el);
                
                // Dedup key: position + role + name
                const key = `${Math.round(rect.left)},${Math.round(rect.top)},${role},${name.substring(0, 20)}`;
                
                if (!processed.has(key)) {
                    const selectors = getSelectors(el, role, name);
                    
                    processed.set(key, {
                        id: id++,
                        role: role,
                        name: name,
                        text: el.innerText?.trim().substring(0, 80) || name,
                        tag: el.tagName.toLowerCase(),
                        visible: true,
                        enabled: !el.disabled && !el.hasAttribute('aria-disabled'),
                        rect: {
                            x: Math.round(rect.left),
                            y: Math.round(rect.top),
                            w: Math.round(rect.width),
                            h: Math.round(rect.height)
                        },
                        selectors: selectors,
                        priority: typePriority[role] || 99
                    });
                    
                    // Update stats
                    stats[role] = (stats[role] || 0) + 1;
                }
            }
            
            // PHASE 3: Sort by priority and convert to array
            const sorted = Array.from(processed.values())
                .sort((a, b) => a.priority - b.priority)
                .slice(0, 120);  // Cap at 120
            
            // Reassign sequential IDs
            sorted.forEach((el, idx) => el.id = idx + 1);
            
            return {elements: sorted, stats: stats};
        }
        """
        
        try:
            result = page.evaluate(js_code)
            elements = result['elements']
            stats = result['stats']
            
            if self.debug:
                print(f"   📊 Element Stats: {stats}")
            
            return elements, stats
            
        except Exception as e:
            print(f"   ❌ Element harvesting error: {e}")
            return [], {}
    
    def _detect_forms(self, page: Page, elements: List[Dict]) -> List[Dict]:
        """
        Group form fields with their submit buttons.
        """
        
        js_code = r"""
        (elements) => {
            const forms = [];
            
            document.querySelectorAll('form').forEach((form, idx) => {
                const formId = form.id || `form-${idx}`;
                const fields = [];
                let submitElementId = null;
                
                // Find fields within this form
                form.querySelectorAll('input, textarea, select').forEach(field => {
                    const fieldRect = field.getBoundingClientRect();
                    
                    // Match with elements list
                    const matchedEl = elements.find(el => 
                        Math.abs(el.rect.x - fieldRect.left) < 5 &&
                        Math.abs(el.rect.y - fieldRect.top) < 5
                    );
                    
                    if (matchedEl) {
                        fields.push({
                            name: field.name || field.id || 'unnamed',
                            elementId: matchedEl.id,
                            type: field.type || 'text'
                        });
                    }
                });
                
                // Find submit button
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    const btnRect = submitBtn.getBoundingClientRect();
                    const matchedEl = elements.find(el => 
                        Math.abs(el.rect.x - btnRect.left) < 5 &&
                        Math.abs(el.rect.y - btnRect.top) < 5
                    );
                    if (matchedEl) submitElementId = matchedEl.id;
                }
                
                if (fields.length > 0) {
                    forms.push({
                        id: formId,
                        fields: fields,
                        submitElementId: submitElementId
                    });
                }
            });
            
            return forms;
        }
        """
        
        try:
            forms = page.evaluate(js_code, elements)
            return forms
        except:
            return []
    
    def _generate_hints(self, page: Page) -> Dict:
        """
        Scan page for verification prompts, search results, etc.
        """
        
        js_code = r"""
        () => {
            const hints = {
                hasVerification: false,
                isSearchResults: false,
                hasModal: false
            };
            
            const bodyText = document.body.innerText.toLowerCase();
            
            // Check for CAPTCHA/verification
            const verificationKeywords = [
                'captcha', 'recaptcha', 'are you human', 'verify you',
                'unusual traffic', 'automated', 'bot', 'security check',
                'prove you', 'not a robot'
            ];
            
            for (const keyword of verificationKeywords) {
                if (bodyText.includes(keyword)) {
                    hints.hasVerification = true;
                    break;
                }
            }
            
            // Check for search results
            if (document.querySelector('[role="main"] [data-ved], .g, .result, [data-sokoban-container]')) {
                hints.isSearchResults = true;
            }
            
            // Check for modals/overlays
            if (document.querySelector('[role="dialog"], .modal, [aria-modal="true"]')) {
                hints.hasModal = true;
            }
            
            return hints;
        }
        """
        
        try:
            return page.evaluate(js_code)
        except:
            return {"hasVerification": False, "isSearchResults": False, "hasModal": False}
    
    def _create_multicolor_screenshot(self, page: Page, elements: List[Dict]) -> str:
        """
        Create screenshot with multi-colored element boxes and ID labels.
        Each element type gets a different color.
        """
        try:
            # Take screenshot
            screenshot_bytes = page.screenshot(full_page=False)
            image = Image.open(io.BytesIO(screenshot_bytes))
            draw = ImageDraw.Draw(image, 'RGBA')
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 16)
                font_small = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
                font_small = font
            
            # Draw each element with its type-specific color
            for el in elements:
                rect = el['rect']
                role = el['role']
                el_id = el['id']
                
                # Get color for this element type
                color = ELEMENT_COLORS.get(role, ELEMENT_COLORS['generic'])
                
                # Convert hex to RGB
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                # Draw box (semi-transparent fill + solid border)
                box = [rect['x'], rect['y'], rect['x'] + rect['w'], rect['y'] + rect['h']]
                draw.rectangle(box, outline=(r, g, b, 255), width=3, fill=(r, g, b, 40))
                
                # Draw ID label (white background)
                label = f"#{el_id}"
                label_x = rect['x']
                label_y = rect['y'] - 20 if rect['y'] > 20 else rect['y']
                
                # Background for label
                try:
                    bbox = draw.textbbox((label_x, label_y), label, font=font)
                    draw.rectangle(bbox, fill=(r, g, b, 220))
                    draw.text((label_x, label_y), label, fill=(255, 255, 255), font=font)
                except:
                    draw.text((label_x, label_y), label, fill=(255, 255, 255))
                
                # Add role tag for search boxes (they're critical!)
                if role == 'searchbox':
                    role_label = "🔍 SEARCH"
                    role_y = label_y + 22
                    try:
                        bbox = draw.textbbox((label_x, role_y), role_label, font=font_small)
                        draw.rectangle(bbox, fill=(r, g, b, 220))
                        draw.text((label_x, role_y), role_label, fill=(255, 255, 255), font=font_small)
                    except:
                        pass
            
            # Add legend in top-right corner
            legend_x = image.width - 250
            legend_y = 10
            legend_items = [
                ('🔵 Search', 'searchbox'),
                ('🟢 Button', 'button'),
                ('🟡 Link', 'link'),
                ('🔷 Input', 'textbox'),
                ('🟣 Image', 'img')
            ]
            
            for i, (label, role) in enumerate(legend_items):
                color = ELEMENT_COLORS[role]
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                y = legend_y + i * 25
                # Color box
                draw.rectangle([legend_x, y, legend_x + 20, y + 20], fill=(r, g, b, 200))
                # Label
                try:
                    draw.text((legend_x + 25, y + 2), label, fill=(0, 0, 0), font=font_small)
                except:
                    pass
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            screenshot_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Save for debugging
            if self.debug:
                debug_path = Path("screenshots") / "debug_labeled.png"
                debug_path.parent.mkdir(exist_ok=True)
                image.save(debug_path)
                self.last_screenshot_path = str(debug_path)
            
            return screenshot_b64
            
        except Exception as e:
            print(f"   ❌ Screenshot error: {e}")
            # Return blank screenshot
            screenshot_bytes = page.screenshot()
            return base64.b64encode(screenshot_bytes).decode()
    
    def _empty_perception(self, page: Page) -> Dict:
        """Fallback empty perception"""
        try:
            url = page.url
            title = page.title()
        except:
            url = "unknown"
            title = "Error"
        
        return {
            "url": url,
            "title": title,
            "screenshot_b64": "",
            "elements": [],
            "forms": [],
            "hints": {"hasVerification": False, "isSearchResults": False},
            "element_stats": {}
        }