#!/usr/bin/env python3
# run_agent.py
# =============================================================================
# UNIVERSAL LAUNCHER - Works with both flat and organized structures
# All features preserved, just better organized
# =============================================================================

import os
import sys
from pathlib import Path

# Auto-detect structure and adjust imports
def setup_imports():
    """Auto-detect flat vs organized structure"""
    if Path("core/memory.py").exists():
        # Organized structure
        sys.path.insert(0, str(Path(__file__).parent))
        return "organized"
    elif Path("memory.py").exists():
        # Flat structure
        return "flat"
    else:
        print("❌ Error: Cannot find agent files")
        sys.exit(1)

structure = setup_imports()

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          🤖 AUTONOMOUS WEB AGENT - FULL FEATURED             ║
║                                                               ║
║  ✅ 3 Operating Modes                                        ║
║  ✅ Real-Time Learning & Adaptation                          ║
║  ✅ Post-Session Analysis                                    ║
║  ✅ Bot Detection Handling                                   ║
║  ✅ Visual Element Highlighting                              ║
║  ✅ Human Behavior Simulation                                ║
║  ✅ Persistent Memory System                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not set\n")
        print("Set it with:")
        print("  export ANTHROPIC_API_KEY='your-key'  # Mac/Linux")
        print("  $env:ANTHROPIC_API_KEY='your-key'   # Windows\n")
        sys.exit(1)
    
    # Create results directory
    Path("results").mkdir(exist_ok=True)
    
    print("Choose your mode:\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║ 1. 🎯 GUIDED MODE (Recommended)                          ║")
    print("║    • YOU control what happens next                        ║")
    print("║    • Agent provides AI suggestions                        ║")
    print("║    • Best for: Interactive exploration                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║ 2. 🔄 CONTINUOUS MODE                                     ║")
    print("║    • Agent decides next actions (asks approval)           ║")
    print("║    • Semi-autonomous operation                            ║")
    print("║    • Best for: Multi-step workflows                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║ 3. 🎲 SINGLE TASK MODE                                    ║")
    print("║    • Complete one specific task                           ║")
    print("║    • Simple and focused                                   ║")
    print("║    • Best for: Quick searches, testing                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║ 4. 🧪 TEST ELEMENT DETECTION                              ║")
    print("║    • Visual highlighting demo                             ║")
    print("║    • See what the agent sees                              ║")
    print("║    • Best for: Verification, debugging                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║ 5. 📊 VIEW LEARNING DATA                                  ║")
    print("║    • See what agent has learned                           ║")
    print("║    • Review adaptive improvements                         ║")
    print("║    • Check memory statistics                              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║ 6. ✅ VERIFY SETUP                                        ║")
    print("║    • Check installation                                   ║")
    print("║    • Validate dependencies                                ║")
    print("║    • Test all modules                                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    if choice == "1":
        run_guided()
    elif choice == "2":
        run_continuous()
    elif choice == "3":
        run_single_task()
    elif choice == "4":
        test_detection()
    elif choice == "5":
        view_learning()
    elif choice == "6":
        verify_setup()
    else:
        print("Invalid choice")

def run_guided():
    """Guided mode - user controls everything"""
    try:
        if structure == "organized":
            from agents.guided_agent import GuidedAgent
        else:
            from guided_agent import GuidedAgent
    except ImportError as e:
        print(f"❌ Error importing guided_agent: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎯 GUIDED MODE - You're in Control!")
    print("="*60)
    print("\nFeatures:")
    print("  ✅ Complete each task you assign")
    print("  ✅ Show results after each step")
    print("  ✅ AI suggests next actions")
    print("  ✅ You decide what happens")
    print("  ✅ Filter, sort, compare options")
    print("="*60)
    
    task = input("\n📋 Initial task: ").strip()
    if not task:
        print("❌ No task provided")
        return
    
    print("\n🚀 Starting guided agent with all features...\n")
    
    agent = GuidedAgent(debug=True)
    agent.run_guided(task)

def run_continuous():
    """Continuous mode - semi-autonomous"""
    try:
        if structure == "organized":
            from agents.continuous_agent import ContinuousAgent
        else:
            from continuous_agent import ContinuousAgent
    except ImportError as e:
        print(f"❌ Error importing continuous_agent: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🔄 CONTINUOUS MODE - Semi-Autonomous")
    print("="*60)
    print("\nFeatures:")
    print("  ✅ Completes initial task")
    print("  ✅ Analyzes results")
    print("  ✅ Suggests next actions")
    print("  ✅ Asks for your approval")
    print("  ✅ Chains multiple tasks")
    print("  ✅ Real-time learning")
    print("="*60)
    
    task = input("\n📋 Initial task: ").strip()
    if not task:
        print("❌ No task provided")
        return
    
    iterations = input("🔢 Max iterations [10]: ").strip()
    max_iter = int(iterations) if iterations else 10
    
    print("\n🚀 Starting continuous agent...\n")
    
    agent = ContinuousAgent(debug=True)
    agent.run_continuous(task, max_iterations=max_iter)

def run_single_task():
    """Single task mode - basic operation"""
    try:
        if structure == "organized":
            from agents.agent import Agent
        else:
            from agent import Agent
    except ImportError as e:
        print(f"❌ Error importing agent: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎲 SINGLE TASK MODE")
    print("="*60)
    print("\nFeatures:")
    print("  ✅ Complete one specific task")
    print("  ✅ Extract and display results")
    print("  ✅ Learn from the session")
    print("  ✅ Save to results folder")
    print("="*60)
    
    task = input("\n📋 Task: ").strip()
    if not task:
        print("❌ No task provided")
        return
    
    max_steps = input("🔢 Max steps [25]: ").strip()
    max_steps = int(max_steps) if max_steps else 25
    
    print("\n🚀 Starting agent...\n")
    
    agent = Agent(debug=True)
    success, data = agent.run(task, max_steps=max_steps)
    
    if success:
        print("\n✅ Task completed!")
        if data and 'products' in data:
            print(f"\n📊 Found {len(data['products'])} products")
            for i, p in enumerate(data['products'][:5], 1):
                print(f"{i}. {p.get('title', 'Unknown')[:60]}")
                print(f"   💰 ${p.get('price', 'N/A')}")
    else:
        print("\n⚠️  Task incomplete - check results folder")
    
    agent.close()

def test_detection():
    """Test element detection with visual feedback"""
    try:
        if structure == "organized":
            from core.memory import AgentMemory
            from utils.vision_fixed import Vision
        else:
            from memory import AgentMemory
            try:
                from vision_fixed import Vision
            except ImportError:
                from vision import Vision
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        sys.exit(1)
    
    from playwright.sync_api import sync_playwright
    
    print("\n" + "="*60)
    print("🧪 ELEMENT DETECTION TEST")
    print("="*60)
    print("\nFeatures:")
    print("  ✅ Visual highlighting (green boxes)")
    print("  ✅ Numbered element IDs")
    print("  ✅ Real-time detection")
    print("  ✅ Screenshot saved")
    print("="*60)
    
    url = input("\n🌐 URL to test [amazon.com]: ").strip() or "amazon.com"
    if not url.startswith('http'):
        url = 'https://' + url
    
    print(f"\n🚀 Opening {url}...")
    print("Watch for green boxes with element IDs!\n")
    
    memory = AgentMemory("results/agent_brain.db")
    vision = Vision(memory, debug=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto(url)
        page.wait_for_load_state('domcontentloaded')
        
        print("\n🔍 Detecting elements...")
        elements = vision.detect_all_elements(page)
        
        visible = len([e for e in elements if e.get('visible')])
        print(f"\n✅ Found {len(elements)} elements")
        print(f"   📍 Visible: {visible}")
        print(f"   📦 Total: {len(elements)}")
        
        print("\n📸 Creating labeled screenshot...")
        vision.create_labeled_screenshot(page, elements)
        
        print("\n✅ Visual highlighting active!")
        print("   🟢 Green boxes = detected elements")
        print("   🔢 Numbers = element IDs for clicking")
        print("   📁 Screenshot saved to results/screenshots/")
        
        input("\n👀 Press Enter to close...")
        browser.close()
    
    memory.close()

def view_learning():
    """View what the agent has learned"""
    try:
        if structure == "organized":
            from core.memory import AgentMemory
        else:
            from memory import AgentMemory
    except ImportError as e:
        print(f"❌ Error importing memory: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("📊 AGENT LEARNING DATA")
    print("="*60)
    
    if not Path("results/agent_brain.db").exists():
        print("\n⚠️  No learning data yet - run agent first")
        return
    
    memory = AgentMemory("results/agent_brain.db")
    stats = memory.get_stats()
    
    print("\n📈 Overall Statistics:")
    print(f"   • Patterns Learned: {stats.get('patterns_learned', 0)}")
    print(f"   • Failures Recorded: {stats.get('failures_recorded', 0)}")
    print(f"   • Tasks Completed: {stats.get('tasks_completed', 0)}")
    print(f"   • Success Rate: {stats.get('success_rate', 0)*100:.1f}%")
    print(f"   • Domains Visited: {stats.get('domains_visited', 0)}")
    
    # Show adaptive learning files
    adaptive_dir = Path("results/adaptive_learning")
    if adaptive_dir.exists():
        sessions = list(adaptive_dir.glob("session_*.json"))
        print(f"\n📁 Adaptive Learning Sessions: {len(sessions)}")
        
        if sessions:
            print("\n   Recent sessions:")
            for session in sorted(sessions)[-5:]:
                print(f"   • {session.name}")
    
    memory.close()
    print("\n" + "="*60)

def verify_setup():
    """Run setup verification"""
    try:
        if structure == "organized":
            from utils.verify_setup import main as verify_main
        else:
            import verify_setup
            verify_main = verify_setup.main if hasattr(verify_setup, 'main') else None
    except ImportError:
        print("⚠️  verify_setup.py not found, running basic checks...\n")
        basic_verify()
        return
    
    if verify_main:
        verify_main()
    else:
        # Run the verify_setup script directly
        import subprocess
        script = "utils/verify_setup.py" if structure == "organized" else "verify_setup.py"
        subprocess.run([sys.executable, script])

def basic_verify():
    """Basic verification if verify_setup.py not available"""
    print("📝 Basic Setup Check\n")
    
    errors = []
    
    # Check Python version
    print("1️⃣  Python version...")
    if sys.version_info >= (3, 8):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print(f"   ❌ Need Python 3.8+")
        errors.append("Python version")
    
    # Check packages
    print("\n2️⃣  Required packages...")
    for package in ['playwright', 'anthropic', 'PIL']:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            errors.append(package)
    
    # Check API key
    print("\n3️⃣  API key...")
    if os.getenv('ANTHROPIC_API_KEY'):
        print("   ✅ ANTHROPIC_API_KEY set")
    else:
        print("   ❌ ANTHROPIC_API_KEY not set")
        errors.append("API key")
    
    if errors:
        print(f"\n❌ {len(errors)} issues found")
    else:
        print("\n✅ Basic setup looks good!")

if __name__ == "__main__":
    main()