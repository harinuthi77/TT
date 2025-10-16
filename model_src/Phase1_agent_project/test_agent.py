#!/usr/bin/env python3
"""
Quick test script to verify agent components
"""

import os
import sys

print("\n" + "=" * 60)
print("🧪 TESTING UNIVERSAL AI AGENT")
print("=" * 60)

errors = []
warnings = []

# Test 1: Python version
print("\n1️⃣  Testing Python version...")
if sys.version_info >= (3, 8):
    print("   ✅ Python 3.8+")
else:
    errors.append("Python 3.8+ required")
    print("   ❌ Python version too old")

# Test 2: Required packages
print("\n2️⃣  Testing packages...")
packages = ['playwright', 'anthropic', 'PIL']

for package in packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        errors.append(f"Missing package: {package}")
        print(f"   ❌ {package} - not installed")

# Test 3: API key
print("\n3️⃣  Testing API key...")
if os.getenv('ANTHROPIC_API_KEY'):
    key = os.getenv('ANTHROPIC_API_KEY')
    print(f"   ✅ API key set ({key[:8]}...{key[-4:]})")
else:
    warnings.append("ANTHROPIC_API_KEY not set")
    print("   ⚠️  API key not set")

# Test 4: Import agent modules
print("\n4️⃣  Testing agent modules...")

try:
    from src.core.memory import AgentMemory
    print("   ✅ memory.py")
except Exception as e:
    errors.append(f"memory.py: {e}")
    print(f"   ❌ memory.py: {e}")

try:
    from src.core.vision import Vision
    print("   ✅ vision.py")
except Exception as e:
    errors.append(f"vision.py: {e}")
    print(f"   ❌ vision.py: {e}")

try:
    from src.core.cognition import CognitiveEngine
    print("   ✅ cognition.py")
except Exception as e:
    errors.append(f"cognition.py: {e}")
    print(f"   ❌ cognition.py: {e}")

try:
    from src.core.executor import ActionExecutor
    print("   ✅ executor.py")
except Exception as e:
    errors.append(f"executor.py: {e}")
    print(f"   ❌ executor.py: {e}")

try:
    from src.core.file_handler import FileHandler
    print("   ✅ file_handler.py")
except Exception as e:
    errors.append(f"file_handler.py: {e}")
    print(f"   ❌ file_handler.py: {e}")

try:
    from src.core.code_executor import CodeExecutor
    print("   ✅ code_executor.py")
except Exception as e:
    errors.append(f"code_executor.py: {e}")
    print(f"   ❌ code_executor.py: {e}")

try:
    from src.agents.universal_agent import UniversalAgent
    print("   ✅ universal_agent.py")
except Exception as e:
    errors.append(f"universal_agent.py: {e}")
    print(f"   ❌ universal_agent.py: {e}")

try:
    from src.agents.continuous_agent import ContinuousAgent
    print("   ✅ continuous_agent.py")
except Exception as e:
    errors.append(f"continuous_agent.py: {e}")
    print(f"   ❌ continuous_agent.py: {e}")

# Test 5: File handler
print("\n5️⃣  Testing file handler...")
try:
    from src.core.file_handler import FileHandler
    handler = FileHandler()
    
    # Write test
    result = handler.write_file("test.txt", "Hello from AI Agent!")
    
    # Read test
    content = handler.read_file("test.txt")
    
    if "Hello from AI Agent!" in content:
        print("   ✅ File read/write works")
    else:
        warnings.append("File handler test incomplete")
        print("   ⚠️  File handler test incomplete")
        
except Exception as e:
    errors.append(f"File handler test: {e}")
    print(f"   ❌ File handler: {e}")

# Test 6: Code executor
print("\n6️⃣  Testing code executor...")
try:
    from src.core.code_executor import CodeExecutor
    executor = CodeExecutor()
    
    # Validate code
    valid, msg = executor.validate_code("print('test')")
    
    if valid:
        print("   ✅ Code executor works")
    else:
        warnings.append("Code executor validation failed")
        print("   ⚠️  Code executor validation failed")
        
except Exception as e:
    errors.append(f"Code executor test: {e}")
    print(f"   ❌ Code executor: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)

if not errors and not warnings:
    print("\n✅ ALL TESTS PASSED!")
    print("\nYour agent is ready to use:")
    print("   python main.py")
elif errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNING(S):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    print("\n🔧 FIX ERRORS BEFORE RUNNING")
else:
    print(f"\n✅ No critical errors")
    print(f"\n⚠️  {len(warnings)} WARNING(S):")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    
    print("\nYou can proceed, but some features may not work.")

print("\n" + "=" * 60)

sys.exit(1 if errors else 0)