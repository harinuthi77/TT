# verify_setup.py
# =============================================================================
# SETUP VERIFICATION SCRIPT
# Checks if everything is installed and configured correctly
# =============================================================================

import sys
import os

print("🔍 Autonomous Agent - Setup Verification")
print("=" * 60)

errors = []
warnings = []

# =============================================================================
# 1. CHECK PYTHON VERSION
# =============================================================================
print("\n1️⃣  Checking Python version...")
if sys.version_info < (3, 8):
    errors.append("Python 3.8+ required")
    print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.8+)")
else:
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

# =============================================================================
# 2. CHECK REQUIRED MODULES
# =============================================================================
print("\n2️⃣  Checking required packages...")

required_modules = {
    'playwright': 'playwright',
    'anthropic': 'anthropic',
    'PIL': 'pillow'
}

for module_name, package_name in required_modules.items():
    try:
        __import__(module_name)
        print(f"   ✅ {package_name}")
    except ImportError:
        errors.append(f"Missing: {package_name}")
        print(f"   ❌ {package_name} - install with: pip install {package_name}")

# =============================================================================
# 3. CHECK PROJECT FILES
# =============================================================================
print("\n3️⃣  Checking project files...")

required_files = [
    'memory.py',
    'vision.py',
    'cognition.py',
    'executor.py',
    'agent.py'
]

for filename in required_files:
    if os.path.exists(filename):
        # Check if file is not empty
        size = os.path.getsize(filename)
        if size > 1000:  # Should be at least 1KB
            print(f"   ✅ {filename} ({size:,} bytes)")
        else:
            warnings.append(f"{filename} seems too small")
            print(f"   ⚠️  {filename} ({size} bytes - seems incomplete)")
    else:
        errors.append(f"Missing file: {filename}")
        print(f"   ❌ {filename} - file not found")

# =============================================================================
# 4. CHECK API KEY
# =============================================================================
print("\n4️⃣  Checking API key...")

api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    masked_key = api_key[:8] + "..." + api_key[-4:]
    print(f"   ✅ ANTHROPIC_API_KEY set ({masked_key})")
else:
    errors.append("ANTHROPIC_API_KEY not set")
    print(f"   ❌ ANTHROPIC_API_KEY not set")
    print(f"      Set it with:")
    print(f"      export ANTHROPIC_API_KEY='your-key'  # Mac/Linux")
    print(f"      $env:ANTHROPIC_API_KEY='your-key'   # Windows")

# =============================================================================
# 5. CHECK PLAYWRIGHT BROWSERS
# =============================================================================
print("\n5️⃣  Checking Playwright browsers...")

try:
    from playwright.sync_api import sync_playwright
    
    # Try to get browser path
    try:
        with sync_playwright() as p:
            # This will fail if browsers not installed, but that's ok
            browser_path = p.chromium.executable_path
            if browser_path and os.path.exists(browser_path):
                print(f"   ✅ Chromium installed at {browser_path}")
            else:
                warnings.append("Chromium may not be installed")
                print(f"   ⚠️  Chromium path not found")
                print(f"      Install with: playwright install chromium")
    except Exception as e:
        warnings.append("Playwright browsers may not be installed")
        print(f"   ⚠️  Browsers not detected: {str(e)[:50]}")
        print(f"      Install with: playwright install chromium")
        
except ImportError:
    errors.append("Playwright not installed")
    print(f"   ❌ Cannot check browsers (playwright not installed)")

# =============================================================================
# 6. TEST MODULE IMPORTS
# =============================================================================
print("\n6️⃣  Testing module imports...")

if os.path.exists('memory.py'):
    try:
        from memory import AgentMemory
        print(f"   ✅ memory.py imports successfully")
    except Exception as e:
        errors.append(f"memory.py import error: {e}")
        print(f"   ❌ memory.py: {str(e)[:60]}")

if os.path.exists('vision.py'):
    try:
        from vision import Vision
        print(f"   ✅ vision.py imports successfully")
    except Exception as e:
        errors.append(f"vision.py import error: {e}")
        print(f"   ❌ vision.py: {str(e)[:60]}")

if os.path.exists('cognition.py'):
    try:
        from cognition import CognitiveEngine
        print(f"   ✅ cognition.py imports successfully")
    except Exception as e:
        errors.append(f"cognition.py import error: {e}")
        print(f"   ❌ cognition.py: {str(e)[:60]}")

if os.path.exists('executor.py'):
    try:
        from executor import ActionExecutor
        print(f"   ✅ executor.py imports successfully")
    except Exception as e:
        errors.append(f"executor.py import error: {e}")
        print(f"   ❌ executor.py: {str(e)[:60]}")

if os.path.exists('agent.py'):
    try:
        from agent import Agent
        print(f"   ✅ agent.py imports successfully")
    except Exception as e:
        errors.append(f"agent.py import error: {e}")
        print(f"   ❌ agent.py: {str(e)[:60]}")

# =============================================================================
# 7. TEST MEMORY SYSTEM
# =============================================================================
print("\n7️⃣  Testing memory system...")

if not errors:  # Only test if no errors so far
    try:
        from memory import AgentMemory
        
        # Create test database
        test_db = "test_verify.db"
        memory = AgentMemory(test_db)
        
        # Test basic operations
        memory.record_success("test.com", "click", "button.test", confidence=8.0)
        best = memory.get_best_selectors("test.com", "click")
        
        if best and len(best) > 0:
            print(f"   ✅ Memory system working")
        else:
            warnings.append("Memory system test incomplete")
            print(f"   ⚠️  Memory system test incomplete")
        
        memory.close()
        
        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)
            
    except Exception as e:
        errors.append(f"Memory system test failed: {e}")
        print(f"   ❌ Memory test: {str(e)[:60]}")

# =============================================================================
# FINAL REPORT
# =============================================================================
print("\n" + "=" * 60)
print("📊 VERIFICATION SUMMARY")
print("=" * 60)

if not errors and not warnings:
    print("\n✅ ALL CHECKS PASSED!")
    print("\nYour setup is complete and ready to use.")
    print("\nTo run the agent:")
    print("   python agent.py")
    print("\nOr programmatically:")
    print("   from agent import Agent")
    print("   agent = Agent()")
    print("   agent.run('your task here')")
    
elif errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNING(S):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    print("\n🔧 FIX ERRORS BEFORE RUNNING")
    print("\nCommon fixes:")
    print("   pip install playwright anthropic pillow")
    print("   playwright install chromium")
    print("   export ANTHROPIC_API_KEY='your-key'")
    
else:
    print(f"\n✅ No critical errors, but {len(warnings)} warning(s):")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    
    print("\n⚠️  You can proceed, but some features may not work")

print("\n" + "=" * 60)

# Exit with appropriate code
sys.exit(1 if errors else 0)