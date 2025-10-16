"""
Centralized Configuration
All tunable parameters in one place
"""
import os

# ============================================================================
# API CONFIGURATION
# ============================================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
ANTHROPIC_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "3000"))

# ============================================================================
# EXECUTION THRESHOLDS
# ============================================================================
MIN_CONFIDENCE_TO_ACT = 7  # Was 9 - now more lenient
MAX_CONSECUTIVE_REJECTIONS = 3  # Stop infinite loops
MAX_STEPS_PER_TASK = 50

# ============================================================================
# TIMING & DELAYS (seconds)
# ============================================================================
MIN_ACTION_DELAY = 0.8
MAX_ACTION_DELAY = 2.5
PAGE_LOAD_TIMEOUT = 30000  # milliseconds
NETWORK_IDLE_TIMEOUT = 5000  # milliseconds
ELEMENT_WAIT_TIMEOUT = 4000  # milliseconds

# ============================================================================
# BROWSER CONFIGURATION
# ============================================================================
HEADLESS = False
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ============================================================================
# STEALTH MODE (disabled by default for stability)
# ============================================================================
ENABLE_STEALTH_MODE = os.getenv("ENABLE_STEALTH_MODE", "false").lower() == "true"
STEALTH_MIN_DELAY = 3.0
STEALTH_MAX_DELAY = 8.0

# ============================================================================
# PATHS
# ============================================================================
RESULTS_DIR = "results"
SCREENSHOTS_DIR = f"{RESULTS_DIR}/screenshots"
MEMORY_DB_PATH = f"{RESULTS_DIR}/agent_brain.db"

# ============================================================================
# DEBUGGING
# ============================================================================
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
SAVE_SCREENSHOTS = True