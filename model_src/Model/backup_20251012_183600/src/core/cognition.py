# cognition.py
# =============================================================================
# COGNITIVE THINKING ENGINE - THE BRAIN
# Deep analysis, validation, and intelligent decision making
# =============================================================================

import anthropic
from typing import Dict, List, Optional, Tuple
import json
import re
from datetime import datetime

# ===== INTERLINK WITH OTHER MODULES =====
from src.core.memory import AgentMemory, extract_domain
from src.core.vision import Vision


class CognitiveEngine:
    """
    The brain of the autonomous agent.
    Analyzes situations, validates options, and makes intelligent decisions.
    
    Principle: SEE → ANALYZE → VALIDATE → DECIDE → ACT
    """
    
    def __init__(self, memory: AgentMemory, api_key: str = None):
        """
        Initialize the cognitive engine.
        
        Args:
            memory: AgentMemory instance for learning
            api_key: Anthropic API key (or uses env var)
        """
        self.memory = memory
        import os; key = api_key or os.getenv("ANTHROPIC_API_KEY"); self.client = anthropic.Anthropic(api_key=key)
        self.conversation_history = []
        self.task_context = {}
        self.validation_enabled = True
        
    # =========================================================================
    # MAIN THINKING PROCESS
    # =========================================================================
    
    def think(self, 
              page,
              task: str,
              screenshot_b64: str,
              elements: List[Dict],
              page_data: Dict,
              page_analysis: Dict) -> Dict:
        """
        MAIN THINKING PROCESS - This is where intelligence happens.
        
        Steps:
        1. Understand current state
        2. Analyze what's visible
        3. Check memory for patterns
        4. Generate possible actions
        5. Validate each option
        6. Choose best action
        7. Assign confidence
        
        Args:
            page: Playwright page object
            task: User's goal
            screenshot_b64: Base64 encoded labeled screenshot
            elements: List of detected elements
            page_data: Extracted page data
            page_analysis: Page structure analysis
        
        Returns:
            Decision dict with action, reasoning, confidence
        """
        
        url = page.url
        domain = extract_domain(url)
        
        print(f"\n🧠 COGNITIVE ANALYSIS")
        print(f"   {'─' * 60}")
        
        # ===== STEP 1: UNDERSTAND CURRENT STATE =====
        state = self._analyze_current_state(
            url, domain, task, elements, page_data, page_analysis
        )
        
        print(f"   📍 State: {state['summary']}")
        
        # ===== STEP 2: CHECK MEMORY FOR INSIGHTS =====
        insights = self._get_memory_insights(domain, state)
        
        if insights:
            print(f"   💾 Memory: {insights['summary']}")
        
        # ===== STEP 3: DETECT PROBLEMS =====
        problems = self._detect_problems(state, page_analysis)
        
        if problems:
            print(f"   ⚠️  Issues: {', '.join(problems)}")
        
        # ===== STEP 4: GENERATE OPTIONS =====
        print(f"   🤔 Generating options...")
        options = self._generate_action_options(state, elements, insights, problems)
        
        print(f"   💭 Considering {len(options)} possible actions")
        
        # ===== STEP 5: DEEP THINKING WITH CLAUDE =====
        print(f"   🧪 Deep analysis with validation...")
        decision = self._deep_think_with_validation(
            task, state, options, screenshot_b64, elements, page_data, insights, problems
        )
        
        # ===== STEP 6: FINAL VALIDATION =====
        if self.validation_enabled:
            decision = self._validate_decision(decision, state, problems)
        
        print(f"   ✅ Decision: {decision['action'].upper()}")
        print(f"   🎯 Confidence: {decision['confidence']}/10")
        print(f"   💭 Reasoning: {decision['thinking'][:100]}...")
        
        # Record this decision in short-term memory
        self.memory.record_action(decision['action'])
        
        return decision
    
    # =========================================================================
    # STATE ANALYSIS
    # =========================================================================
    
    def _analyze_current_state(self, url: str, domain: str, task: str,
                               elements: List[Dict], page_data: Dict,
                               page_analysis: Dict) -> Dict:
        """
        Analyze current state comprehensively.
        """
        
        state = {
            'url': url,
            'domain': domain,
            'page_type': page_analysis.get('pageType', 'unknown'),
            'task': task,
            'task_keywords': self._extract_task_keywords(task),
            'visible_elements': len([e for e in elements if e.get('visible', False)]),
            'total_elements': len(elements),
            'has_search': page_analysis.get('hasSearch', False),
            'has_products': page_analysis.get('hasProducts', False),
            'has_forms': page_analysis.get('hasForms', False),
            'needs_scroll': page_analysis.get('needsScroll', False),
            'products_found': len(page_data.get('products', [])),
            'forms_found': len(page_data.get('forms', [])),
            'is_stuck': self.memory.is_stuck()[0],
            'stuck_reason': self.memory.is_stuck()[1]
        }
        
        # Generate summary
        summary_parts = []
        
        if state['is_stuck']:
            summary_parts.append(f"STUCK: {state['stuck_reason']}")
        
        if state['page_type'] == 'captcha':
            summary_parts.append("CAPTCHA page")
        elif state['page_type'] == 'product_listing':
            summary_parts.append(f"{state['products_found']} products visible")
        elif state['page_type'] == 'search':
            summary_parts.append("Search page")
        elif state['page_type'] == 'auth':
            summary_parts.append("Login/Auth page")
        else:
            summary_parts.append(f"{state['visible_elements']} interactive elements")
        
        state['summary'] = ', '.join(summary_parts) if summary_parts else "Ready"
        
        return state
    
    def _extract_task_keywords(self, task: str) -> List[str]:
        """Extract important keywords from task"""
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
                     'find', 'search', 'look', 'get', 'go', 'navigate'}
        
        words = re.findall(r'\b\w+\b', task.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return keywords[:10]  # Top 10 keywords
    
    # =========================================================================
    # MEMORY INTEGRATION
    # =========================================================================
    
    def _get_memory_insights(self, domain: str, state: Dict) -> Optional[Dict]:
        """
        Get relevant insights from memory.
        """
        
        insights = {
            'domain_info': self.memory.get_domain_insight(domain),
            'recent_failures': self.memory.get_recent_failures(domain, limit=3),
            'best_click_selectors': self.memory.get_best_selectors(domain, 'click', limit=3),
            'best_type_selectors': self.memory.get_best_selectors(domain, 'type', limit=3)
        }
        
        # Generate summary
        summary_parts = []
        
        if insights['domain_info']:
            info = insights['domain_info']
            if info.get('has_bot_detection'):
                summary_parts.append("Has bot detection")
            if info.get('success_rate', 0) > 0.7:
                summary_parts.append(f"{info['success_rate']*100:.0f}% success rate")
        
        if insights['recent_failures']:
            summary_parts.append(f"{len(insights['recent_failures'])} recent failures")
        
        if insights['best_click_selectors']:
            summary_parts.append(f"Known good selectors available")
        
        insights['summary'] = ', '.join(summary_parts) if summary_parts else None
        
        return insights if insights['summary'] else None
    
    # =========================================================================
    # PROBLEM DETECTION
    # =========================================================================
    
    def _detect_problems(self, state: Dict, page_analysis: Dict) -> List[str]:
        """
        Detect potential problems that need special handling.
        """
        
        problems = []
        
        # CAPTCHA detection
        if page_analysis.get('hasCaptcha', False):
            problems.append("CAPTCHA_DETECTED")
        
        # Stuck in loop
        if state['is_stuck']:
            problems.append("STUCK_IN_LOOP")
        
        # No visible elements
        if state['visible_elements'] < 3:
            problems.append("FEW_ELEMENTS")
        
        # Modal/overlay blocking
        if page_analysis.get('hasModals', False):
            problems.append("MODAL_PRESENT")
        
        # Page didn't load properly
        if state['page_type'] == 'unknown' and state['visible_elements'] < 5:
            problems.append("PAGE_LOAD_ISSUE")
        
        # No products on expected product page
        if 'product' in state['task'].lower() and state['products_found'] == 0:
            if state['page_type'] == 'product_listing':
                problems.append("NO_PRODUCTS_FOUND")
        
        return problems
    
    # =========================================================================
    # ACTION GENERATION
    # =========================================================================
    
    def _generate_action_options(self, state: Dict, elements: List[Dict],
                                 insights: Optional[Dict], problems: List[str]) -> List[Dict]:
        """
        Generate possible action options based on current state.
        This is a rule-based pre-filter before AI thinking.
        """
        
        options = []
        task_lower = state['task'].lower()
        keywords = state['task_keywords']
        
        # ===== OPTION 1: Navigate to website =====
        if 'http' not in state['url'].lower() or state['domain'] == 'unknown':
            # Need to go somewhere
            for keyword in keywords:
                if '.' in keyword or 'www' in keyword:
                    options.append({
                        'action': 'goto',
                        'target': keyword,
                        'reason': f"Task mentions {keyword}, should navigate there",
                        'priority': 10
                    })
        
        # ===== OPTION 2: Handle CAPTCHA =====
        if 'CAPTCHA_DETECTED' in problems:
            options.append({
                'action': 'wait',
                'target': '',
                'reason': "CAPTCHA detected, need to wait or manual intervention",
                'priority': 1
            })
        
        # ===== OPTION 3: Break out of stuck loop =====
        if 'STUCK_IN_LOOP' in problems:
            if state['needs_scroll']:
                options.append({
                    'action': 'scroll',
                    'target': '',
                    'reason': "Stuck in loop, try scrolling to see new content",
                    'priority': 7
                })
            else:
                options.append({
                    'action': 'extract',
                    'target': '',
                    'reason': "Stuck in loop, try extracting current data",
                    'priority': 6
                })
        
        # ===== OPTION 4: Close modals =====
        if 'MODAL_PRESENT' in problems:
            # Look for close buttons
            for elem in elements:
                if elem.get('visible') and elem.get('text'):
                    text = elem['text'].lower()
                    if any(word in text for word in ['close', 'dismiss', 'no thanks', '×', 'x']):
                        options.append({
                            'action': 'click',
                            'target': str(elem['id']),
                            'reason': f"Close modal: '{elem['text'][:30]}'",
                            'priority': 8
                        })
        
        # ===== OPTION 5: Search for keywords =====
        if state['has_search'] and any(kw in task_lower for kw in ['find', 'search', 'look']):
            # Find search box
            for elem in elements:
                if elem.get('visible') and elem['tag'] == 'input':
                    if elem.get('type') in ['search', 'text', '']:
                        # Construct search query from task keywords
                        search_query = ' '.join(keywords[:3])
                        options.append({
                            'action': 'type',
                            'target': search_query,
                            'reason': f"Search for: {search_query}",
                            'priority': 9
                        })
                        break
        
        # ===== OPTION 6: Click on product links =====
        if state['has_products'] and state['products_found'] > 0:
            # If task is to find/compare products, might need to extract
            if any(word in task_lower for word in ['find', 'compare', 'show', 'list']):
                options.append({
                    'action': 'extract',
                    'target': '',
                    'reason': f"Extract {state['products_found']} products found",
                    'priority': 8
                })
        
        # ===== OPTION 7: Scroll to load more =====
        if state['needs_scroll'] and state['visible_elements'] < 20:
            options.append({
                'action': 'scroll',
                'target': '',
                'reason': "Page has more content below, scroll to load",
                'priority': 5
            })
        
        # ===== OPTION 8: Task completion check =====
        # Check if task is likely complete
        if self._check_task_completion(state, task_lower):
            options.append({
                'action': 'done',
                'target': '',
                'reason': "Task appears complete based on current state",
                'priority': 7
            })
        
        # ===== OPTION 9: Intelligent element clicking =====
        # Find elements matching task keywords
        for elem in elements[:30]:  # Check top 30 elements
            if not elem.get('visible'):
                continue
            
            elem_text = (elem.get('text') or '').lower()
            
            # Check if element text matches task keywords
            matches = sum(1 for kw in keywords if kw in elem_text)
            
            if matches > 0:
                options.append({
                    'action': 'click',
                    'target': str(elem['id']),
                    'reason': f"Element matches {matches} keywords: '{elem['text'][:40]}'",
                    'priority': 5 + matches
                })
        
        # Sort by priority
        options.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return options[:10]  # Return top 10 options
    
    def _check_task_completion(self, state: Dict, task_lower: str) -> bool:
        """Check if task might be complete"""
        
        # If task was to find products and we found them
        if 'find' in task_lower and 'product' in task_lower:
            if state['products_found'] > 0:
                return True
        
        # If task was to search and we're on results page
        if 'search' in task_lower and state['page_type'] == 'product_listing':
            if state['products_found'] > 0:
                return True
        
        # If we've extracted data successfully
        if state['products_found'] > 5:
            return True
        
        return False
    
    # =========================================================================
    # DEEP THINKING WITH CLAUDE
    # =========================================================================
    
    def _deep_think_with_validation(self, task: str, state: Dict, options: List[Dict],
                                    screenshot_b64: str, elements: List[Dict],
                                    page_data: Dict, insights: Optional[Dict],
                                    problems: List[str]) -> Dict:
        """
        Deep thinking with Claude API and validation.
        This is where the AI reasoning happens.
        """
        
        # Build comprehensive prompt
        prompt = self._build_thinking_prompt(
            task, state, options, elements, page_data, insights, problems
        )
        
        # Prepare messages for Claude
        messages = self.conversation_history[-6:] + [{  # Keep last 6 messages for context
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_b64
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
        
        # Call Claude with extended thinking
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                temperature=0.2,  # Lower temperature for more focused thinking
                messages=messages,
                system=self._get_system_prompt()
            )
            
            answer = response.content[0].text
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": [{"type": "text", "text": f"Task: {task}\nState: {state['summary']}"}]
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })
            
            # Parse Claude's response
            decision = self._parse_claude_response(answer, elements)
            
            return decision
            
        except Exception as e:
            print(f"   ❌ Claude API error: {e}")
            
            # Fallback to rule-based decision
            return self._fallback_decision(options)
    
    def _build_thinking_prompt(self, task: str, state: Dict, options: List[Dict],
                               elements: List[Dict], page_data: Dict,
                               insights: Optional[Dict], problems: List[str]) -> str:
        """
        Build a comprehensive prompt for Claude.
        """
        
        # Get visible elements summary
        visible = [e for e in elements if e.get('visible', False)][:25]
        elem_desc = []
        for e in visible:
            desc = f"[{e['id']}] {e['tag']}"
            if e.get('type'):
                desc += f" type={e['type']}"
            if e.get('text'):
                desc += f" text=\"{e['text'][:50]}\""
            if e.get('learned_success'):
                desc += f" ✓(success_count={e.get('success_count', 0)})"
            elem_desc.append(desc)
        
        # Build options summary
        options_desc = []
        for opt in options[:5]:
            options_desc.append(
                f"• {opt['action'].upper()}: {opt['reason']} (priority: {opt.get('priority', 0)})"
            )
        
        # Build memory insights
        memory_desc = []
        if insights:
            if insights.get('domain_info'):
                info = insights['domain_info']
                memory_desc.append(f"• Domain visited {info.get('visits', 0)} times")
                memory_desc.append(f"• Success rate: {info.get('success_rate', 0)*100:.0f}%")
                if info.get('has_bot_detection'):
                    memory_desc.append(f"• ⚠️ Known to have bot detection")
            
            if insights.get('recent_failures'):
                memory_desc.append(f"• Recent failures: {len(insights['recent_failures'])}")
                for fail in insights['recent_failures'][:2]:
                    memory_desc.append(f"  - {fail['action']}: {fail['reason']}")
        
        # Build problems summary
        problems_desc = []
        if problems:
            for prob in problems:
                if prob == 'CAPTCHA_DETECTED':
                    problems_desc.append("⚠️ CAPTCHA detected - may need manual intervention")
                elif prob == 'STUCK_IN_LOOP':
                    problems_desc.append(f"⚠️ Stuck in loop: {state.get('stuck_reason', '')}")
                elif prob == 'MODAL_PRESENT':
                    problems_desc.append("⚠️ Modal/overlay may be blocking interaction")
                else:
                    problems_desc.append(f"⚠️ {prob}")
        
        prompt = f"""You are an autonomous web agent's cognitive system. You must analyze the situation deeply and make an intelligent decision.

🎯 TASK: {task}

📊 CURRENT STATE:
   • URL: {state['url']}
   • Domain: {state['domain']}
   • Page Type: {state['page_type']}
   • Visible Elements: {state['visible_elements']}
   • Products Found: {state['products_found']}
   • Task Keywords: {', '.join(state['task_keywords'])}

🔍 VISIBLE ELEMENTS (numbered boxes on screenshot):
{chr(10).join(elem_desc)}

💾 MEMORY INSIGHTS:
{chr(10).join(memory_desc) if memory_desc else '   • No prior experience with this domain'}

⚠️  DETECTED PROBLEMS:
{chr(10).join(problems_desc) if problems_desc else '   • No problems detected'}

💡 SUGGESTED OPTIONS (generated by rule engine):
{chr(10).join(options_desc) if options_desc else '   • No specific suggestions'}

📄 PAGE DATA:
   • {len(page_data.get('products', []))} products detected
   • {len(page_data.get('forms', []))} forms detected
   • Page has search: {state['has_search']}

═══════════════════════════════════════════════════════════════

🧠 YOUR THINKING PROCESS:

1️⃣ ANALYZE: What do I see on this screenshot? What's the current situation?

2️⃣ UNDERSTAND: What is the user trying to achieve? What's the next logical step?

3️⃣ VALIDATE: Consider each option carefully:
   - What could go wrong?
   - Have we tried this before?
   - Is this the most direct path to the goal?
   - What are the alternatives?

4️⃣ DECIDE: What's the BEST action to take right now?

5️⃣ CONFIDENCE: How sure am I? (0-10)
   - 9-10: Extremely confident, clear path
   - 7-8: Confident, good option
   - 5-6: Moderate confidence, some uncertainty
   - 3-4: Low confidence, risky
   - 0-2: Very uncertain, might fail

═══════════════════════════════════════════════════════════════

CRITICAL RULES:
• Look at the SCREENSHOT - the numbered boxes [1], [2], etc. show you what you can interact with
• Elements marked with ✓ have worked before - prefer these
• If stuck in a loop, try a DIFFERENT approach
• If CAPTCHA detected, you CANNOT proceed automatically
• Be CONSERVATIVE - only act when confident (5+)
• For clicking, use the element ID number from the screenshot
• For typing, provide the exact text to type
• Think step-by-step and validate your reasoning

═══════════════════════════════════════════════════════════════

RESPONSE FORMAT:

ANALYSIS:
[Deep analysis of what you see and the situation - 2-3 sentences]

VALIDATION:
[Consider the options, what could go wrong, what's the best path - 2-3 sentences]

REASONING:
[Why you chose this specific action - 2-3 sentences]

ACTION: [goto/type/click/scroll/extract/done/wait]

DETAILS: [Specific details for the action]
- For goto: provide URL (e.g., "amazon.com")
- For type: provide exact text to type (e.g., "wireless headphones")
- For click: provide element ID from screenshot (e.g., "23")
- For scroll: just "scroll"
- For extract: just "extract"
- For done: just "done"
- For wait: just "wait"

CONFIDENCE: [0-10]

ALTERNATIVE: [What would you do if this fails? - 1 sentence]
"""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for Claude"""
        return """You are the cognitive engine of an autonomous web agent. Your role is to:

1. Analyze screenshots with numbered element labels [1], [2], [3], etc.
2. Think deeply about the task and current state
3. Validate options before deciding
4. Make intelligent, cautious decisions
5. Provide clear reasoning for your choices

You must be:
• Thorough in analysis
• Conservative in confidence (only 8+ when very sure)
• Aware of past failures (learn from memory)
• Strategic in planning (multi-step thinking)
• Honest about uncertainty (low confidence when unsure)

Remember: Elements with ✓ symbols have worked before - prefer these when applicable."""
    
    def _parse_claude_response(self, response: str, elements: List[Dict]) -> Dict:
        """
        Parse Claude's structured response into a decision dict.
        """
        
        decision = {
            'analysis': '',
            'validation': '',
            'thinking': '',
            'action': 'wait',
            'details': '',
            'confidence': 5,
            'alternative': '',
            'raw_response': response
        }
        
        # Parse each section
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line_upper = line.strip().upper()
            
            if line_upper.startswith('ANALYSIS:'):
                current_section = 'analysis'
                decision['analysis'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_upper.startswith('VALIDATION:'):
                current_section = 'validation'
                decision['validation'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_upper.startswith('REASONING:'):
                current_section = 'thinking'
                decision['thinking'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_upper.startswith('ACTION:'):
                current_section = 'action'
                action_text = line.split(':', 1)[1].strip().lower() if ':' in line else ''
                decision['action'] = action_text
            elif line_upper.startswith('DETAILS:'):
                current_section = 'details'
                decision['details'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_upper.startswith('CONFIDENCE:'):
                current_section = 'confidence'
                try:
                    conf_text = line.split(':', 1)[1].strip() if ':' in line else '5'
                    decision['confidence'] = int(re.search(r'\d+', conf_text).group())
                except:
                    decision['confidence'] = 5
            elif line_upper.startswith('ALTERNATIVE:'):
                current_section = 'alternative'
                decision['alternative'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif current_section and line.strip():
                # Continue current section
                if current_section in ['analysis', 'validation', 'thinking', 'details', 'alternative']:
                    decision[current_section] += ' ' + line.strip()
        
        # Validate and clean up
        decision['analysis'] = decision['analysis'].strip()
        decision['validation'] = decision['validation'].strip()
        decision['thinking'] = decision['thinking'].strip()
        decision['details'] = decision['details'].strip()
        decision['alternative'] = decision['alternative'].strip()
        
        # Ensure confidence is in range
        decision['confidence'] = max(0, min(10, decision['confidence']))
        
        return decision
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def _validate_decision(self, decision: Dict, state: Dict, problems: List[str]) -> Dict:
        """
        Final validation of decision before execution.
        Can modify or reject decisions that seem problematic.
        """
        
        action = decision['action']
        confidence = decision['confidence']
        
        # Reduce confidence for certain scenarios
        if 'STUCK_IN_LOOP' in problems and action == 'click':
            if confidence > 6:
                decision['confidence'] = 6
                decision['thinking'] += " [Confidence reduced: stuck in loop]"
        
        # Require higher confidence for navigation
        if action == 'goto' and confidence < 6:
            decision['action'] = 'wait'
            decision['details'] = 'Low confidence for navigation'
            decision['thinking'] += " [Switched to wait: low confidence for goto]"
        
        # Don't click with very low confidence
        if action == 'click' and confidence < 4:
            decision['action'] = 'scroll'
            decision['details'] = 'scroll'
            decision['thinking'] += " [Switched to scroll: too risky to click]"
        
        # Don't allow action on CAPTCHA
        if 'CAPTCHA_DETECTED' in problems and action not in ['wait', 'done']:
            decision['action'] = 'wait'
            decision['confidence'] = 0
            decision['thinking'] = "CAPTCHA detected - cannot proceed automatically"
        
        return decision
    
    def _fallback_decision(self, options: List[Dict]) -> Dict:
        """
        Fallback decision if Claude API fails.
        Uses rule-based system.
        """
        
        if not options:
            return {
                'thinking': 'No options available, waiting',
                'action': 'wait',
                'details': '',
                'confidence': 2,
                'analysis': 'Fallback mode',
                'validation': 'Using rule-based decision',
                'alternative': 'Manual intervention'
            }
        
        # Pick highest priority option
        best = options[0]
        
        return {
            'thinking': best['reason'],
            'action': best['action'],
            'details': best.get('target', ''),
            'confidence': max(3, best.get('priority', 3)),
            'analysis': 'Fallback to rule-based decision',
            'validation': f"Selected based on priority: {best.get('priority', 0)}",
            'alternative': options[1]['reason'] if len(options) > 1 else 'None'
        }
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def reset_conversation(self):
        """Reset conversation history for new task"""
        self.conversation_history = []
    
    def set_validation(self, enabled: bool):
        """Enable/disable validation (for testing)"""
        self.validation_enabled = enabled
    
    def get_task_progress(self) -> str:
        """Get summary of task progress"""
        if not self.conversation_history:
            return "No progress yet"
        
        actions_taken = [msg for msg in self.conversation_history if msg['role'] == 'assistant']
        return f"{len(actions_taken)} decisions made"


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("🧠 Testing Cognitive Engine\n")
    
    from .memory import AgentMemory
    import os
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Set ANTHROPIC_API_KEY environment variable to test")
        exit(1)
    
    memory = AgentMemory("test_brain.db")
    cognition = CognitiveEngine(memory)
    
    # Simulate a simple decision scenario
    mock_state = {
        'url': 'https://amazon.com',
        'domain': 'amazon.com',
        'page_type': 'search',
        'task': 'find wireless headphones under $50',
        'task_keywords': ['wireless', 'headphones', '$50'],
        'visible_elements': 25,
        'total_elements': 120,
        'has_search': True,
        'has_products': False,
        'products_found': 0,
        'is_stuck': False,
        'stuck_reason': '',
        'summary': '25 interactive elements, search available'
    }
    
    mock_elements = [
        {'id': 1, 'tag': 'input', 'type': 'search', 'text': '', 'visible': True, 'x': 500, 'y': 100},
        {'id': 2, 'tag': 'button', 'type': 'submit', 'text': 'Search', 'visible': True, 'x': 600, 'y': 100}
    ]
    
    mock_options = [
        {'action': 'type', 'target': 'wireless headphones', 'reason': 'Search for products', 'priority': 9}
    ]
    
    print("Generating decision for mock scenario...")
    print(f"Task: {mock_state['task']}")
    print(f"State: {mock_state['summary']}\n")
    
    # Note: Would need screenshot for full test
    # decision = cognition.think(page, task, screenshot_b64, elements, page_data, page_analysis)
    
    print("✅ Cognitive engine initialized successfully!")
    print("\nNote: Full testing requires:")
    print("  • Live browser page")
    print("  • Screenshot capture")
    print("  • Anthropic API key")
    
    memory.close()
