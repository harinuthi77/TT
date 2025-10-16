"""
Autonomous Web Agent - Main Entry Point
FIXED: Correct imports, proper error handling
"""

import os
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.intelligent_agent import IntelligentAgent


def main():
    """Smart entry point - agent decides its own mode"""
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🤖 AUTONOMOUS WEB AGENT - INTELLIGENT MODE        ║
║                                                           ║
║  The agent automatically decides how to help you best    ║
║                                                           ║
║  ✅ Automatic mode selection                             ║
║  ✅ Continuous learning and adaptation                   ║
║  ✅ Multi-step task execution                            ║
║  ✅ Visual element highlighting                          ║
║  ✅ Persistent memory across sessions                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not set\n")
        print("Set it with:")
        print("  export ANTHROPIC_API_KEY='your-key'  # Mac/Linux")
        print("  $env:ANTHROPIC_API_KEY='your-key'   # Windows\n")
        sys.exit(1)
    
    # Get task from user
    print("\n💬 What can I help you with?")
    print("━" * 60)
    print("\nExamples:")
    print("  • Find wireless headphones under $50 on Amazon")
    print("  • Search for laptops on Best Buy")
    print("  • Compare prices across multiple sites")
    print()
    
    task = input("Task: ").strip()
    
    if not task:
        print("❌ No task provided")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🧠 Analyzing your request...")
    print("="*60)
    
    # Create intelligent agent
    agent = IntelligentAgent(debug=True)
    
    try:
        # Execute task
        result = agent.execute(task)
        
        print("\n" + "="*60)
        print("✅ Task Complete!")
        print("="*60)
        
        if result.get('status') == 'success':
            print("\n✨ Successfully completed your task!")
        elif result.get('status') == 'failed':
            print("\n⚠️ Task incomplete - see results above")
        
        # Show data if available
        if result.get('data'):
            data = result['data']
            if data.get('products'):
                print(f"\n📦 Found {len(data['products'])} products")
        
    except KeyboardInterrupt:
        print("\n\n⏸️ Stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()
    
    print("\n✅ Thank you for using Autonomous Web Agent!\n")


if __name__ == "__main__":
    main()