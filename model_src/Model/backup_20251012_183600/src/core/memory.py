# memory.py
# =============================================================================
# AGENT MEMORY & LEARNING SYSTEM
# Persistent database for tracking successes, failures, and patterns
# =============================================================================

import sqlite3
from datetime import datetime
from collections import deque
from typing import List, Tuple, Optional, Dict
import json


class AgentMemory:
    """
    Persistent memory system that learns from experiences.
    Tracks successful patterns, failures, and detects when stuck.
    """
    
    def __init__(self, db_path: str = "agent_brain.db"):
        """
        Initialize memory system with SQLite database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_database()
        
        # Short-term memory for stuck detection
        self.recent_actions = deque(maxlen=10)
        self.session_start = datetime.now()
        
    def _init_database(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Success patterns - what worked before
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS success_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                action_type TEXT NOT NULL,
                selector TEXT NOT NULL,
                context TEXT,
                success_count INTEGER DEFAULT 1,
                last_used TEXT,
                avg_confidence REAL DEFAULT 5.0,
                UNIQUE(domain, action_type, selector, context)
            )
        ''')
        
        # Failure tracking - what to avoid
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                action_type TEXT NOT NULL,
                selector TEXT,
                reason TEXT,
                timestamp TEXT,
                page_url TEXT
            )
        ''')
        
        # Task history - completed missions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                success INTEGER NOT NULL,
                steps_taken INTEGER,
                duration REAL,
                timestamp TEXT,
                final_url TEXT,
                data_collected TEXT
            )
        ''')
        
        # Domain-specific insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domain_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL UNIQUE,
                total_visits INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                avg_steps REAL DEFAULT 0.0,
                has_bot_detection INTEGER DEFAULT 0,
                best_strategy TEXT,
                last_visit TEXT
            )
        ''')
        
        self.conn.commit()
        
    # =========================================================================
    # SUCCESS TRACKING
    # =========================================================================
    
    def record_success(self, domain: str, action_type: str, selector: str, 
                      context: str = "", confidence: float = 5.0):
        """
        Record a successful action for future reference.
        
        Args:
            domain: Website domain (e.g., 'amazon.com')
            action_type: Type of action ('click', 'type', 'scroll', etc.)
            selector: Element selector that worked
            context: Optional context (e.g., 'search_box', 'product_link')
            confidence: How confident the action was (0-10)
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        try:
            # Try to update existing pattern
            cursor.execute('''
                UPDATE success_patterns 
                SET success_count = success_count + 1,
                    last_used = ?,
                    avg_confidence = (avg_confidence + ?) / 2.0
                WHERE domain = ? AND action_type = ? AND selector = ? AND context = ?
            ''', (timestamp, confidence, domain, action_type, selector, context))
            
            # If no rows updated, insert new pattern
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO success_patterns 
                    (domain, action_type, selector, context, success_count, last_used, avg_confidence)
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                ''', (domain, action_type, selector, context, timestamp, confidence))
            
            self.conn.commit()
            print(f"   💾 Learned: {action_type} on {selector}")
            
        except Exception as e:
            print(f"   ⚠️  Memory error: {e}")
            
    def get_best_selectors(self, domain: str, action_type: str, 
                          context: str = "", limit: int = 5) -> List[Dict]:
        """
        Retrieve proven selectors for a domain and action type.
        
        Returns:
            List of dicts with selector, success_count, and confidence
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                SELECT selector, success_count, avg_confidence, last_used
                FROM success_patterns
                WHERE domain = ? AND action_type = ? AND context LIKE ?
                ORDER BY success_count DESC, avg_confidence DESC, last_used DESC
                LIMIT ?
            ''', (domain, action_type, f"%{context}%", limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'selector': row[0],
                    'success_count': row[1],
                    'confidence': row[2],
                    'last_used': row[3]
                })
            
            return results
            
        except Exception as e:
            print(f"   ⚠️  Memory retrieval error: {e}")
            return []
    
    # =========================================================================
    # FAILURE TRACKING
    # =========================================================================
    
    def record_failure(self, domain: str, action_type: str, reason: str,
                      selector: str = "", page_url: str = ""):
        """
        Record a failed action to avoid repeating mistakes.
        
        Args:
            domain: Website domain
            action_type: Type of action that failed
            reason: Why it failed
            selector: Element selector (if applicable)
            page_url: Full page URL
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO failures (domain, action_type, selector, reason, timestamp, page_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (domain, action_type, selector, reason, timestamp, page_url))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"   ⚠️  Failed to record failure: {e}")
    
    def get_recent_failures(self, domain: str, action_type: str = "", 
                           limit: int = 5) -> List[Dict]:
        """Get recent failures for a domain/action"""
        cursor = self.conn.cursor()
        
        try:
            if action_type:
                cursor.execute('''
                    SELECT action_type, selector, reason, timestamp
                    FROM failures
                    WHERE domain = ? AND action_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (domain, action_type, limit))
            else:
                cursor.execute('''
                    SELECT action_type, selector, reason, timestamp
                    FROM failures
                    WHERE domain = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (domain, limit))
            
            return [
                {
                    'action': row[0],
                    'selector': row[1],
                    'reason': row[2],
                    'timestamp': row[3]
                }
                for row in cursor.fetchall()
            ]
            
        except:
            return []
    
    # =========================================================================
    # STUCK DETECTION
    # =========================================================================
    
    def record_action(self, action: str):
        """Record an action to short-term memory"""
        self.recent_actions.append(action)
    
    def is_stuck(self) -> Tuple[bool, str]:
        """
        Detect if agent is stuck in a loop.
        
        Returns:
            (is_stuck, reason)
        """
        if len(self.recent_actions) < 5:
            return False, ""
        
        recent = list(self.recent_actions)[-5:]
        unique_actions = len(set(recent))
        
        # Too many repeated actions
        if unique_actions <= 2:
            return True, f"Repeating only {unique_actions} actions: {set(recent)}"
        
        # Same action 3+ times in a row
        last_three = recent[-3:]
        if len(set(last_three)) == 1:
            return True, f"Same action 3x: {last_three[0]}"
        
        return False, ""
    
    def clear_recent_actions(self):
        """Reset short-term memory"""
        self.recent_actions.clear()
    
    # =========================================================================
    # DOMAIN INSIGHTS
    # =========================================================================
    
    def update_domain_insight(self, domain: str, steps_taken: int, 
                             success: bool, has_bot_detection: bool = False):
        """Update domain statistics"""
        cursor = self.conn.cursor()
        
        try:
            # Get existing stats
            cursor.execute('''
                SELECT total_visits, success_rate, avg_steps
                FROM domain_insights
                WHERE domain = ?
            ''', (domain,))
            
            row = cursor.fetchone()
            
            if row:
                total_visits = row[0] + 1
                old_success_rate = row[1]
                old_avg_steps = row[2]
                
                # Update success rate
                new_success_rate = (old_success_rate * (total_visits - 1) + (1 if success else 0)) / total_visits
                new_avg_steps = (old_avg_steps * (total_visits - 1) + steps_taken) / total_visits
                
                cursor.execute('''
                    UPDATE domain_insights
                    SET total_visits = ?,
                        success_rate = ?,
                        avg_steps = ?,
                        has_bot_detection = ?,
                        last_visit = ?
                    WHERE domain = ?
                ''', (total_visits, new_success_rate, new_avg_steps, 
                     int(has_bot_detection), datetime.now().isoformat(), domain))
            else:
                # Insert new domain
                cursor.execute('''
                    INSERT INTO domain_insights
                    (domain, total_visits, success_rate, avg_steps, has_bot_detection, last_visit)
                    VALUES (?, 1, ?, ?, ?, ?)
                ''', (domain, 1.0 if success else 0.0, steps_taken, 
                     int(has_bot_detection), datetime.now().isoformat()))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"   ⚠️  Domain insight error: {e}")
    
    def get_domain_insight(self, domain: str) -> Optional[Dict]:
        """Get statistics for a domain"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                SELECT total_visits, success_rate, avg_steps, has_bot_detection, best_strategy
                FROM domain_insights
                WHERE domain = ?
            ''', (domain,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'visits': row[0],
                    'success_rate': row[1],
                    'avg_steps': row[2],
                    'has_bot_detection': bool(row[3]),
                    'strategy': row[4]
                }
            return None
            
        except:
            return None
    
    # =========================================================================
    # TASK HISTORY
    # =========================================================================
    
    def save_task(self, task: str, success: bool, steps_taken: int,
                 duration: float, final_url: str, data_collected: Dict = None):
        """Save completed task to history"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO task_history
                (task, success, steps_taken, duration, timestamp, final_url, data_collected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task, int(success), steps_taken, duration, timestamp, 
                 final_url, json.dumps(data_collected) if data_collected else None))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"   ⚠️  Task save error: {e}")
    
    # =========================================================================
    # STATS & UTILITIES
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Get overall memory statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        try:
            # Total success patterns learned
            cursor.execute('SELECT COUNT(*) FROM success_patterns')
            stats['patterns_learned'] = cursor.fetchone()[0]
            
            # Total failures recorded
            cursor.execute('SELECT COUNT(*) FROM failures')
            stats['failures_recorded'] = cursor.fetchone()[0]
            
            # Total tasks completed
            cursor.execute('SELECT COUNT(*) FROM task_history')
            stats['tasks_completed'] = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute('SELECT AVG(success) FROM task_history')
            result = cursor.fetchone()[0]
            stats['success_rate'] = result if result else 0.0
            
            # Domains visited
            cursor.execute('SELECT COUNT(*) FROM domain_insights')
            stats['domains_visited'] = cursor.fetchone()[0]
            
        except:
            pass
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Ensure connection is closed"""
        self.close()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    if '://' in url:
        domain = url.split('/')[2]
    else:
        domain = url.split('/')[0]
    
    # Remove www.
    if domain.startswith('www.'):
        domain = domain[4:]
    
    return domain


if __name__ == "__main__":
    # Test the memory system
    print("🧠 Testing Agent Memory System\n")
    
    memory = AgentMemory("test_brain.db")
    
    # Record some successes
    memory.record_success("amazon.com", "click", "button.search", "search_button", 8.5)
    memory.record_success("amazon.com", "click", "button.search", "search_button", 9.0)
    memory.record_success("amazon.com", "type", "input#search", "search_box", 7.5)
    
    # Record a failure
    memory.record_failure("amazon.com", "click", "Element not found", "button.invalid")
    
    # Get best selectors
    print("Best selectors for clicking on amazon.com:")
    selectors = memory.get_best_selectors("amazon.com", "click")
    for s in selectors:
        print(f"  • {s['selector']} (used {s['success_count']}x, confidence: {s['confidence']:.1f})")
    
    # Test stuck detection
    for _ in range(6):
        memory.record_action("click")
    
    stuck, reason = memory.is_stuck()
    print(f"\nStuck? {stuck} - {reason}")
    
    # Get stats
    stats = memory.get_stats()
    print(f"\n📊 Stats: {stats}")
    
    memory.close()
    print("\n✅ Memory system test complete!")