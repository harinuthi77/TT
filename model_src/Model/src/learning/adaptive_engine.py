# adaptive_engine.py
# =============================================================================
# REAL-TIME ADAPTIVE LEARNING ENGINE
# Learns from every action, adapts behavior, handles bot detection
# =============================================================================

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter, deque
from pathlib import Path

from src.core.memory import AgentMemory, extract_domain


class AdaptiveEngine:
    """
    Real-time learning engine that:
    - Learns from every single action
    - Detects patterns in failures
    - Adapts behavior dynamically
    - Handles bot detection intelligently
    """
    
    def __init__(self, memory: AgentMemory):
        self.memory = memory
        self.session_failures = deque(maxlen=20)
        self.session_successes = deque(maxlen=20)
        self.bot_detection_count = {}
        self.adaptation_log = []
        
        self.results_dir = Path("results/adaptive_learning")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def record_action_result(self, domain: str, action: str, 
                            success: bool, details: Dict):
        """
        Record EVERY action and learn from it in real-time
        """
        
        timestamp = datetime.now()
        
        record = {
            'timestamp': timestamp.isoformat(),
            'domain': domain,
            'action': action,
            'success': success,
            'details': details
        }
        
        if success:
            self.session_successes.append(record)
            print(f"   âœ… LEARNED: {action} works on {domain}")
        else:
            self.session_failures.append(record)
            print(f"   âŒ LEARNED: {action} failed on {domain} - {details.get('reason', 'unknown')}")
            
            # Immediate adaptation
            self._adapt_to_failure(domain, action, details)
    
    def _adapt_to_failure(self, domain: str, action: str, details: Dict):
        """
        Immediately adapt behavior when failure detected
        """
        
        reason = details.get('reason', '')
        
        # Bot detection
        if any(keyword in reason.lower() for keyword in ['captcha', 'bot', 'verify', 'unusual traffic']):
            self.bot_detection_count[domain] = self.bot_detection_count.get(domain, 0) + 1
            
            if self.bot_detection_count[domain] >= 2:
                adaptation = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'BOT_DETECTION_ADAPTATION',
                    'domain': domain,
                    'action': 'Increase delays, add random mouse movements',
                    'severity': 'HIGH'
                }
                
                self.adaptation_log.append(adaptation)
                
                print(f"\n   ðŸš¨ ADAPTIVE RESPONSE:")
                print(f"   Domain: {domain}")
                print(f"   Issue: Bot detection triggered {self.bot_detection_count[domain]} times")
                print(f"   Adaptation: Switching to STEALTH MODE")
                print(f"   - Delays: 3-8 seconds between actions")
                print(f"   - Mouse movements: Random natural patterns")
                print(f"   - Reading time: Simulated eye tracking\n")
                
                # Update memory
                self.memory.update_domain_insight(domain, 0, False, has_bot_detection=True)
                
                return {
                    'stealth_mode': True,
                    'min_delay': 3.0,
                    'max_delay': 8.0,
                    'mouse_movements': True
                }
        
        # Element not found - try alternative selectors
        if 'not found' in reason.lower() or 'no element' in reason.lower():
            adaptation = {
                'timestamp': datetime.now().isoformat(),
                'type': 'ELEMENT_DETECTION_ADAPTATION',
                'domain': domain,
                'action': 'Expand element detection selectors',
                'severity': 'MEDIUM'
            }
            
            self.adaptation_log.append(adaptation)
            
            print(f"\n   ðŸ”§ ADAPTIVE RESPONSE:")
            print(f"   Issue: Element not found")
            print(f"   Adaptation: Expanding detection scope")
            print(f"   - Will re-scan with broader selectors")
            print(f"   - Will try alternative interaction methods\n")
        
        # Page load timeout
        if 'timeout' in reason.lower():
            adaptation = {
                'timestamp': datetime.now().isoformat(),
                'type': 'TIMEOUT_ADAPTATION',
                'domain': domain,
                'action': 'Increase timeout limits',
                'severity': 'MEDIUM'
            }
            
            self.adaptation_log.append(adaptation)
            
            print(f"\n   â° ADAPTIVE RESPONSE:")
            print(f"   Issue: Page load timeout")
            print(f"   Adaptation: Increasing timeout thresholds\n")
    
    def get_domain_strategy(self, domain: str) -> Dict:
        """
        Get adapted strategy for domain based on learning
        """
        
        strategy = {
            'stealth_mode': False,
            'min_delay': 0.8,
            'max_delay': 2.5,
            'timeout': 30,
            'retry_count': 2
        }
        
        # Check if domain has bot detection
        if self.bot_detection_count.get(domain, 0) > 0:
            strategy['stealth_mode'] = True
            strategy['min_delay'] = 3.0
            strategy['max_delay'] = 8.0
            strategy['timeout'] = 60
            strategy['retry_count'] = 1
        
        # Check memory
        insight = self.memory.get_domain_insight(domain)
        if insight:
            if insight.get('has_bot_detection'):
                strategy['stealth_mode'] = True
                strategy['min_delay'] = 4.0
                strategy['max_delay'] = 10.0
            
            if insight.get('success_rate', 1.0) < 0.5:
                # Low success rate - be more careful
                strategy['timeout'] = 45
                strategy['retry_count'] = 3
        
        return strategy
    
    def analyze_session(self) -> Dict:
        """
        Analyze current session performance
        """
        
        total_actions = len(self.session_successes) + len(self.session_failures)
        
        if total_actions == 0:
            return {'message': 'No actions yet'}
        
        success_rate = len(self.session_successes) / total_actions
        
        # Analyze failure patterns
        failure_reasons = Counter(
            f['details'].get('reason', 'unknown') 
            for f in self.session_failures
        )
        
        # Analyze action patterns
        failed_actions = Counter(f['action'] for f in self.session_failures)
        success_actions = Counter(s['action'] for s in self.session_successes)
        
        analysis = {
            'total_actions': total_actions,
            'successes': len(self.session_successes),
            'failures': len(self.session_failures),
            'success_rate': success_rate,
            'failure_patterns': dict(failure_reasons.most_common(5)),
            'failed_actions': dict(failed_actions.most_common(5)),
            'successful_actions': dict(success_actions.most_common(5)),
            'adaptations_made': len(self.adaptation_log),
            'bot_detections': sum(self.bot_detection_count.values())
        }
        
        return analysis
    
    def print_learning_summary(self):
        """
        Print what the agent has learned this session
        """
        
        analysis = self.analyze_session()
        
        print(f"\n{'='*80}")
        print(f"ðŸ“Š ADAPTIVE LEARNING SUMMARY")
        print(f"{'='*80}")
        
        print(f"\nðŸ“ˆ Performance:")
        print(f"   Total Actions: {analysis['total_actions']}")
        print(f"   Successes: {analysis['successes']} âœ…")
        print(f"   Failures: {analysis['failures']} âŒ")
        print(f"   Success Rate: {analysis['success_rate']*100:.1f}%")
        
        if analysis['failure_patterns']:
            print(f"\nðŸ” Failure Patterns:")
            for reason, count in analysis['failure_patterns'].items():
                print(f"   - {reason}: {count} times")
        
        if analysis['adaptations_made'] > 0:
            print(f"\nðŸ”§ Adaptations Made: {analysis['adaptations_made']}")
            for adapt in self.adaptation_log[-5:]:
                print(f"   - {adapt['type']}: {adapt['action']}")
        
        if analysis['bot_detections'] > 0:
            print(f"\nðŸš¨ Bot Detections: {analysis['bot_detections']}")
            print(f"   Stealth mode activated for affected domains")
        
        print(f"\n{'='*80}")
        
        # Save to file
        filename = self.results_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'analysis': analysis,
                'adaptations': self.adaptation_log,
                'recent_failures': list(self.session_failures),
                'recent_successes': list(self.session_successes)
            }, f, indent=2)
        
        print(f"ðŸ’¾ Learning data saved: {filename}\n")
    
    def should_abort_task(self, domain: str) -> bool:
        """
        Decide if task should be aborted based on learning
        """
        
        # If bot detection triggered multiple times, suggest abort
        if self.bot_detection_count.get(domain, 0) >= 3:
            print(f"\nâš ï¸ RECOMMENDATION: Abort task on {domain}")
            print(f"   Reason: Bot detection triggered {self.bot_detection_count[domain]} times")
            print(f"   Suggestion: Try alternative site or manual verification")
            return True
        
        # If too many consecutive failures
        recent_failures = list(self.session_failures)[-5:]
        if len(recent_failures) >= 5:
            same_domain = all(f['domain'] == domain for f in recent_failures)
            if same_domain:
                print(f"\nâš ï¸ RECOMMENDATION: Consider alternative approach")
                print(f"   Reason: 5 consecutive failures on {domain}")
                return True
        
        return False


# =============================================================================
# INTEGRATION EXAMPLE
# =============================================================================

if __name__ == "__main__":
    from src.core.memory import AgentMemory
    
    memory = AgentMemory("results/agent_brain.db")
    adaptive = AdaptiveEngine(memory)
    
    # Simulate some actions
    print("ðŸ§ª Testing Adaptive Engine\n")
    
    # Success
    adaptive.record_action_result(
        'amazon.com', 'click', True,
        {'selector': 'button.search', 'confidence': 8}
    )
    
    # Failure - bot detection
    adaptive.record_action_result(
        'walmart.com', 'goto', False,
        {'reason': 'CAPTCHA detected - bot verification required'}
    )
    
    # Another bot detection
    adaptive.record_action_result(
        'walmart.com', 'click', False,
        {'reason': 'Unusual traffic detected'}
    )
    
    # Get adapted strategy
    print("\nðŸŽ¯ Getting adapted strategy for walmart.com:")
    strategy = adaptive.get_domain_strategy('walmart.com')
    print(json.dumps(strategy, indent=2))
    
    # Print summary
    adaptive.print_learning_summary()
    
    memory.close()