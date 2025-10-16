"""
Centralized Configuration - FIXED
All tunable parameters in one place
"""
import os

# ============================================================================
# API CONFIGURATION - CRITICAL FIX
# ============================================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# FIXED: Use correct model name (NOT "claude-3-5-sonnet-latest")
# Valid options: "claude-sonnet-4-5-20250929", "claude-3-5-sonnet-20241022", etc.
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
ANTHROPIC_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000"))

# Validate model name
VALID_MODELS = [
    "claude-sonnet-4-5-20250929",
    "claude-3-5-sonnet-20241022", 
    "claude-3-opus-20240229",
    "claude-3-haiku-20240307"
]

if ANTHROPIC_MODEL not in VALID_MODELS:
    print(f"⚠️  WARNING: Model '{ANTHROPIC_MODEL}' may be invalid")
    print(f"   Valid models: {', '.join(VALID_MODELS[:2])}")
    print(f"   Defaulting to: {VALID_MODELS[0]}")
    ANTHROPIC_MODEL = VALID_MODELS[0]

# ============================================================================
# EXECUTION THRESHOLDS
# ============================================================================
MIN_CONFIDENCE_TO_ACT = 7  # Lowered from 9 for better action rate
MAX_CONSECUTIVE_REJECTIONS = 3
MAX_STEPS_PER_TASK = 50
MAX_COGNITION_FAILURES = 3  # NEW: Switch to fallback after 3 API failures

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
# STARTUP BEHAVIOR - NEW
# ============================================================================
DEFAULT_START_URL = "https://www.google.com"  # Start here if no URL
ENABLE_STARTUP_NAVIGATION = True  # Auto-navigate to search engine

# ============================================================================
# STEALTH MODE
# ============================================================================
ENABLE_STEALTH_MODE = os.getenv("ENABLE_STEALTH_MODE", "false").lower() == "true"
STEALTH_MIN_DELAY = 3.0
STEALTH_MAX_DELAY = 8.0

# ============================================================================
# FALLBACK STRATEGY - NEW
# ============================================================================
ENABLE_RULE_BASED_FALLBACK = True  # Use heuristics if LLM fails
FALLBACK_SEARCH_ENGINE = "https://www.google.com/search?q="

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
VERBOSE_LOGGING = True  # Print detailed logs