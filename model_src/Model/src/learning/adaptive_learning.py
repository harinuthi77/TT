# adaptive_learning.py
# =============================================================================
# ADAPTIVE LEARNING & SELF-IMPROVEMENT SYSTEM
# Analyzes failures, identifies patterns, and recommends code improvements
# =============================================================================

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import Counter
import anthropic

from src.core.memory import AgentMemory, extract_domain


class AdaptiveLearning:
    """
    Self-improving system that analyzes agent performance and generates
    recommendations for code improvements.
    
    Capabilities:
    - Analyzes session failures
    - Identifies recurring patterns
    - Generates code improvement suggestions
    - Auto-tunes parameters
    - Creates domain-specific strategies
    """
    
    def __init__(self, memory: AgentMemory, api_key: str = None):
        """
        Initialize adaptive learning system.
        
        Args:
            memory: AgentMemory instance for accessing historical data
            api_key: Anthropic API key for generating recommendations
        """
        self.memory = memory
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.recommendations_file = "adaptive_recommendations.json"
        self.strategies_file = "domain_strategies.json"
        
    # =========================================================================
    # SESSION ANALYSIS
    # =========================================================================
    
    def analyze_session(self, task: str, domain: str, success: bool, 
                        steps_taken: int, final_url: str,
                        stuck_count: int, bot_detected: bool) -> Dict:
        """
        Analyze a completed session and generate insights.
        
        Returns:
            Analysis dict with problems, patterns, and recommendations
        """
        
        print("\n" + "=" * 80)
        print("ðŸ” ADAPTIVE LEARNING - SESSION ANALYSIS")
        print("=" * 80)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'domain': domain,
            'success': success,
            'steps_taken': steps_taken,
            'stuck_count': stuck_count,
            'bot_detected': bot_detected,
            'problems_identified': [],
            'patterns_found': [],
            'recommendations': []
        }
        
        # Get domain insights from memory
        domain_insight = self.memory.get_domain_insight(domain)
        recent_failures = self.memory.get_recent_failures(domain, limit=10)
        
        # ===== PROBLEM IDENTIFICATION =====
        print("\n1ï¸âƒ£ IDENTIFYING PROBLEMS:")
        
        problems = []
        
        if bot_detected:
            problems.append({
                'type': 'BOT_DETECTION',
                'severity': 'CRITICAL',
                'description': f'{domain} has aggressive bot detection',
                'frequency': 'high' if domain_insight and domain_insight.get('has_bot_detection') else 'first_time'
            })
            print(f"   âš ï¸  CRITICAL: Bot detection on {domain}")
        
        if stuck_count > 2:
            problems.append({
                'type': 'STUCK_IN_LOOP',
                'severity': 'HIGH',
                'description': f'Agent got stuck {stuck_count} times',
                'actions': self._analyze_stuck_actions(recent_failures)
            })
            print(f"   âš ï¸  HIGH: Stuck in loop {stuck_count} times")
        
        if steps_taken >= 20 and not success:
            problems.append({
                'type': 'INEFFICIENT_NAVIGATION',
                'severity': 'MEDIUM',
                'description': f'Took {steps_taken} steps without completing task',
                'efficiency': f"{(steps_taken / 25) * 100:.0f}% of max steps used"
            })
            print(f"   âš ï¸  MEDIUM: Used {steps_taken}/25 steps without success")
        
        if not success and steps_taken < 10:
            problems.append({
                'type': 'EARLY_FAILURE',
                'severity': 'HIGH',
                'description': 'Failed early, likely fundamental issue',
                'possible_causes': ['Wrong website', 'Missing features', 'Access blocked']
            })
            print(f"   âš ï¸  HIGH: Failed after only {steps_taken} steps")
        
        # Check failure patterns
        failure_types = Counter(f['reason'] for f in recent_failures)
        for failure_reason, count in failure_types.most_common(3):
            if count >= 3:
                problems.append({
                    'type': 'RECURRING_FAILURE',
                    'severity': 'HIGH',
                    'description': f'Same failure repeated {count} times: {failure_reason}',
                    'action_type': recent_failures[0]['action']
                })
                print(f"   âš ï¸  HIGH: Recurring failure - {failure_reason} ({count}x)")
        
        analysis['problems_identified'] = problems
        
        # ===== PATTERN RECOGNITION =====
        print("\n2ï¸âƒ£ ANALYZING PATTERNS:")
        
        patterns = self._identify_patterns(domain, recent_failures, domain_insight)
        analysis['patterns_found'] = patterns
        
        for pattern in patterns:
            print(f"   ðŸ“Š {pattern['type']}: {pattern['description']}")
        
        # ===== GENERATE RECOMMENDATIONS =====
        print("\n3ï¸âƒ£ GENERATING RECOMMENDATIONS:")
        
        recommendations = self._generate_recommendations(problems, patterns, domain)
        analysis['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. [{rec['priority']}] {rec['title']}")
            print(f"      {rec['description'][:80]}...")
        
        # Save analysis
        self._save_analysis(analysis)
        
        return analysis
    
    def _analyze_stuck_actions(self, failures: List[Dict]) -> List[str]:
        """Analyze which actions caused stuck loops"""
        action_counts = Counter(f['action'] for f in failures)
        return [f"{action} ({count}x)" for action, count in action_counts.most_common(3)]
    
    def _identify_patterns(self, domain: str, failures: List[Dict], 
                          domain_insight: Optional[Dict]) -> List[Dict]:
        """Identify recurring patterns in failures"""
        
        patterns = []
        
        # Pattern 1: Always fails on specific action
        action_failures = Counter(f['action'] for f in failures)
        for action, count in action_failures.items():
            if count >= 3:
                patterns.append({
                    'type': 'ACTION_FAILURE_PATTERN',
                    'description': f'{action} action fails frequently ({count} times)',
                    'action': action,
                    'frequency': count
                })
        
        # Pattern 2: Bot detection domain
        if domain_insight and domain_insight.get('has_bot_detection'):
            patterns.append({
                'type': 'BOT_DETECTION_DOMAIN',
                'description': f'{domain} consistently triggers bot detection',
                'success_rate': domain_insight.get('success_rate', 0)
            })
        
        # Pattern 3: Low success rate on domain
        if domain_insight and domain_insight.get('success_rate', 1.0) < 0.3:
            patterns.append({
                'type': 'LOW_SUCCESS_DOMAIN',
                'description': f'{domain} has very low success rate ({domain_insight["success_rate"]*100:.0f}%)',
                'visits': domain_insight.get('visits', 0)
            })
        
        return patterns
    
    # =========================================================================
    # RECOMMENDATION GENERATION
    # =========================================================================
    
    def _generate_recommendations(self, problems: List[Dict], 
                                  patterns: List[Dict], domain: str) -> List[Dict]:
        """
        Generate actionable recommendations for improvements.
        """
        
        recommendations = []
        
        # ===== BOT DETECTION RECOMMENDATIONS =====
        if any(p['type'] == 'BOT_DETECTION' for p in problems):
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'ANTI_BOT',
                'title': f'Enhance bot detection handling for {domain}',
                'description': 'Current anti-bot measures insufficient. Need stronger evasion.',
                'suggested_changes': [
                    'Increase delays: min_sec=3.0, max_sec=8.0',
                    'Add random mouse movements between actions',
                    'Implement page idle time (10-20s) before interaction',
                    'Use residential proxy rotation',
                    'Consider using undetected-chromedriver'
                ],
                'code_location': 'executor.py â†’ _handle_goto()',
                'auto_applicable': True,
                'parameter_updates': {
                    'executor.py': {
                        'HumanBehavior.delay': {'min_sec': 3.0, 'max_sec': 8.0},
                        'goto_bot_detection_wait': {'min': 10.0, 'max': 20.0}
                    }
                }
            })
            
            recommendations.append({
                'priority': 'HIGH',
                'category': 'STRATEGY',
                'title': f'Create domain-specific strategy for {domain}',
                'description': f'{domain} requires special handling due to bot detection',
                'suggested_changes': [
                    f'Add {domain} to high-security domains list',
                    'Use slower action timing for this domain',
                    'Implement CAPTCHA solver integration',
                    'Consider alternative data sources'
                ],
                'code_location': 'cognition.py â†’ _generate_action_options()',
                'auto_applicable': False
            })
        
        # ===== STUCK LOOP RECOMMENDATIONS =====
        if any(p['type'] == 'STUCK_IN_LOOP' for p in problems):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'LOGIC',
                'title': 'Improve stuck detection and recovery',
                'description': 'Agent repeatedly getting stuck in action loops',
                'suggested_changes': [
                    'Reduce stuck threshold from 5 to 3 actions',
                    'Add "try different domain" option when stuck',
                    'Implement backtracking mechanism',
                    'Force extract action after 3 stuck detections'
                ],
                'code_location': 'memory.py â†’ is_stuck()',
                'auto_applicable': True,
                'parameter_updates': {
                    'memory.py': {
                        'stuck_threshold': 3,
                        'stuck_action_limit': 2
                    }
                }
            })
        
        # ===== PRODUCT EXTRACTION RECOMMENDATIONS =====
        if any(p['type'] == 'INEFFICIENT_NAVIGATION' for p in problems):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'VISION',
                'title': 'Enhance product detection for car listings',
                'description': 'Product extraction failed - need better selectors',
                'suggested_changes': [
                    f'Add {domain}-specific product selectors',
                    'Include price range patterns (e.g., "$30,000-$35,000")',
                    'Detect vehicle-specific attributes (mileage, year)',
                    'Add fallback extraction using AI vision'
                ],
                'code_location': 'vision.py â†’ extract_page_content()',
                'auto_applicable': True,
                'code_snippet': f'''
# Add to vision.py product selectors for {domain}:
if '{domain}' in url:
    product_selectors.extend([
        '[class*="vehicle-card"]',
        '[data-qa*="vehicle"]',
        'article[class*="listing"]'
    ])
'''
            })
        
        # ===== NAVIGATION EFFICIENCY =====
        if any(p['type'] == 'INEFFICIENT_NAVIGATION' for p in problems):
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'STRATEGY',
                'title': 'Optimize navigation strategy',
                'description': 'Too many steps for simple tasks - need better planning',
                'suggested_changes': [
                    'Implement direct URL construction for known sites',
                    'Skip UI interaction, go straight to results URL',
                    'Use site-specific URL parameters from memory',
                    'Pre-validate URLs before navigating'
                ],
                'code_location': 'cognition.py â†’ _generate_action_options()',
                'auto_applicable': False
            })
        
        # ===== GENERAL IMPROVEMENTS =====
        recommendations.append({
            'priority': 'LOW',
            'category': 'ENHANCEMENT',
            'title': 'Add alternative data sources',
            'description': f'Consider using API or different site when {domain} fails',
            'suggested_changes': [
                'Implement fallback to alternative car sites (AutoTrader, CarGurus)',
                'Add API integration for structured data',
                'Create site preference ranking based on success rate'
            ],
            'code_location': 'agent.py â†’ run()',
            'auto_applicable': False
        })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        recommendations.sort(key=lambda x: priority_order[x['priority']])
        
        return recommendations
    
    # =========================================================================
    # AUTO-IMPROVEMENT
    # =========================================================================
    
    def auto_apply_improvements(self, recommendations: List[Dict]) -> List[str]:
        """
        Automatically apply safe parameter updates.
        
        Returns:
            List of applied changes
        """
        
        print("\n" + "=" * 80)
        print("ðŸ”§ AUTO-APPLYING SAFE IMPROVEMENTS")
        print("=" * 80)
        
        applied = []
        
        for rec in recommendations:
            if not rec.get('auto_applicable', False):
                continue
            
            if 'parameter_updates' in rec:
                print(f"\nðŸ“ Applying: {rec['title']}")
                
                for file, params in rec['parameter_updates'].items():
                    print(f"   File: {file}")
                    
                    # Save to strategies file for runtime loading
                    self._save_parameter_update(file, params)
                    
                    for param, value in params.items():
                        print(f"   âœ“ {param} = {value}")
                        applied.append(f"{file}::{param} = {value}")
        
        if applied:
            print(f"\nâœ… Applied {len(applied)} automatic improvements")
            print("   These will take effect on next run")
        else:
            print("\n   No auto-applicable improvements found")
        
        return applied
    
    def _save_parameter_update(self, file: str, params: Dict):
        """Save parameter updates to strategies file"""
        
        strategies = {}
        if os.path.exists(self.strategies_file):
            with open(self.strategies_file, 'r') as f:
                strategies = json.load(f)
        
        if file not in strategies:
            strategies[file] = {}
        
        strategies[file].update(params)
        strategies['last_updated'] = datetime.now().isoformat()
        
        with open(self.strategies_file, 'w') as f:
            json.dump(strategies, f, indent=2)
    
    def get_domain_strategy(self, domain: str) -> Optional[Dict]:
        """Get custom strategy for a domain"""
        
        if not os.path.exists(self.strategies_file):
            return None
        
        with open(self.strategies_file, 'r') as f:
            strategies = json.load(f)
        
        return strategies.get(domain)
    
    # =========================================================================
    # AI-POWERED CODE IMPROVEMENT SUGGESTIONS
    # =========================================================================
    
    def generate_code_improvements(self, analysis: Dict) -> List[Dict]:
        """
        Use Claude to analyze failures and suggest actual code changes.
        """
        
        if not self.client:
            return []
        
        print("\n" + "=" * 80)
        print("ðŸ¤– AI-POWERED CODE IMPROVEMENT GENERATION")
        print("=" * 80)
        
        # Build analysis context
        context = f"""
Task: {analysis['task']}
Domain: {analysis['domain']}
Success: {analysis['success']}
Steps: {analysis['steps_taken']}
Bot Detected: {analysis['bot_detected']}

Problems Identified:
{json.dumps(analysis['problems_identified'], indent=2)}

Patterns Found:
{json.dumps(analysis['patterns_found'], indent=2)}
"""
        
        prompt = f"""You are an expert Python developer analyzing a web automation agent's failure.

CONTEXT:
{context}

The agent is built with these modules:
- memory.py: Learning & persistence
- vision.py: Element detection & screenshots
- cognition.py: Decision making
- executor.py: Action execution
- agent.py: Main orchestrator

ANALYSIS REQUEST:
1. Identify the ROOT CAUSE of the failure
2. Suggest SPECIFIC code changes (with exact code snippets)
3. Prioritize changes by impact
4. Consider bot detection, stuck loops, and extraction failures

Provide your response in JSON format:
{{
    "root_cause": "Clear explanation of why it failed",
    "code_changes": [
        {{
            "file": "filename.py",
            "function": "function_name",
            "change_type": "modify/add/remove",
            "description": "What to change",
            "code_snippet": "Exact Python code to add/modify",
            "reasoning": "Why this will help"
        }}
    ],
    "strategic_recommendations": [
        "High-level strategy change 1",
        "High-level strategy change 2"
    ]
}}

Focus on ACTIONABLE, SPECIFIC changes, not general advice."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = response.content[0].text
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', answer, re.DOTALL)
            if json_match:
                improvements = json.loads(json_match.group())
                
                print(f"\nðŸŽ¯ ROOT CAUSE:")
                print(f"   {improvements.get('root_cause', 'Unknown')}")
                
                print(f"\nðŸ’¡ SUGGESTED CODE CHANGES:")
                for i, change in enumerate(improvements.get('code_changes', [])[:3], 1):
                    print(f"\n   {i}. {change['file']} â†’ {change['function']}()")
                    print(f"      {change['description']}")
                    print(f"      Reasoning: {change['reasoning']}")
                
                # Save for review
                self._save_ai_improvements(improvements)
                
                return improvements
            
        except Exception as e:
            print(f"   âŒ AI improvement generation failed: {e}")
        
        return {}
    
    # =========================================================================
    # PERSISTENCE
    # =========================================================================
    
    def _save_analysis(self, analysis: Dict):
        """Save analysis to file"""
        
        analyses = []
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                analyses = json.load(f)
        
        analyses.append(analysis)
        
        # Keep last 50 analyses
        analyses = analyses[-50:]
        
        with open(self.recommendations_file, 'w') as f:
            json.dump(analyses, f, indent=2)
    
    def _save_ai_improvements(self, improvements: Dict):
        """Save AI-generated improvements"""
        
        filename = f"ai_improvements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(improvements, f, indent=2)
        
        print(f"\nðŸ’¾ AI improvements saved to: {filename}")
    
    def get_improvement_summary(self) -> str:
        """Get summary of all recommendations"""
        
        if not os.path.exists(self.recommendations_file):
            return "No recommendations yet"
        
        with open(self.recommendations_file, 'r') as f:
            analyses = json.load(f)
        
        total_sessions = len(analyses)
        successful = sum(1 for a in analyses if a['success'])
        total_recommendations = sum(len(a.get('recommendations', [])) for a in analyses)
        
        return f"""
ðŸ“Š IMPROVEMENT SUMMARY
{'=' * 60}
Total Sessions Analyzed: {total_sessions}
Successful: {successful} ({successful/total_sessions*100:.1f}%)
Failed: {total_sessions - successful}
Total Recommendations Generated: {total_recommendations}

Recent Improvements:
{self._format_recent_improvements(analyses[-5:])}
"""
    
    def _format_recent_improvements(self, recent: List[Dict]) -> str:
        """Format recent improvements for display"""
        
        lines = []
        for analysis in recent:
            status = "âœ…" if analysis['success'] else "âŒ"
            lines.append(
                f"{status} {analysis['domain']}: "
                f"{len(analysis.get('recommendations', []))} recommendations"
            )
        
        return '\n'.join(lines) if lines else "None"


# =============================================================================
# INTEGRATION WITH MAIN AGENT
# =============================================================================

def analyze_and_improve(memory: AgentMemory, task: str, domain: str, 
                        success: bool, steps_taken: int, final_url: str,
                        stuck_count: int = 0, bot_detected: bool = False) -> Dict:
    """
    Main entry point for post-session analysis and improvement.
    
    Call this after agent.run() completes.
    """
    
    adaptive = AdaptiveLearning(memory)
    
    # Analyze session
    analysis = adaptive.analyze_session(
        task, domain, success, steps_taken, 
        final_url, stuck_count, bot_detected
    )
    
    # Auto-apply safe improvements
    applied = adaptive.auto_apply_improvements(analysis['recommendations'])
    
    # Generate AI-powered improvements (if API key available)
    if os.getenv('ANTHROPIC_API_KEY'):
        ai_improvements = adaptive.generate_code_improvements(analysis)
        analysis['ai_improvements'] = ai_improvements
    
    # Print summary
    print("\n" + "=" * 80)
    print("ðŸ“ˆ IMPROVEMENT SUMMARY")
    print("=" * 80)
    print(f"Problems Identified: {len(analysis['problems_identified'])}")
    print(f"Patterns Found: {len(analysis['patterns_found'])}")
    print(f"Recommendations: {len(analysis['recommendations'])}")
    print(f"Auto-Applied: {len(applied)}")
    print("=" * 80)
    
    return analysis


# =============================================================================
# CLI FOR REVIEWING IMPROVEMENTS
# =============================================================================

if __name__ == "__main__":
    import sys
    
    print("\nðŸ” ADAPTIVE LEARNING SYSTEM - REVIEW MODE")
    print("=" * 60)
    
    # Check for memory database
    if not os.path.exists("agent_brain.db"):
        print("âŒ No agent_brain.db found. Run agent first.")
        sys.exit(1)
    
    memory = AgentMemory()
    adaptive = AdaptiveLearning(memory)
    
    # Show summary
    print(adaptive.get_improvement_summary())
    
    # Load latest analysis
    if os.path.exists(adaptive.recommendations_file):
        with open(adaptive.recommendations_file, 'r') as f:
            analyses = json.load(f)
        
        if analyses:
            latest = analyses[-1]
            
            print(f"\nðŸ“‹ LATEST SESSION ANALYSIS")
            print("=" * 60)
            print(f"Task: {latest['task'][:80]}...")
            print(f"Domain: {latest['domain']}")
            print(f"Success: {latest['success']}")
            print(f"Steps: {latest['steps_taken']}")
            
            print(f"\nðŸ”§ TOP RECOMMENDATIONS:")
            for i, rec in enumerate(latest.get('recommendations', [])[:5], 1):
                print(f"\n{i}. [{rec['priority']}] {rec['title']}")
                print(f"   {rec['description']}")
                if rec.get('auto_applicable'):
                    print(f"   âœ“ Can be auto-applied")
    
    print("\n" + "=" * 60)
    memory.close()