#!/usr/bin/env python3
"""
Universal AI Agent - Main Entry Point
Handles ANY task: web automation, file operations, code execution, research
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.universal_agent import UniversalAgent


def main():
    """Main entry point"""
    
    print("\n" + "=" * 80)
    print("🤖 UNIVERSAL AI AGENT")
    print("=" * 80)
    print("Capabilities:")
    print("  🌐 Web Automation    - Browse, search, extract data from any website")
    print("  📁 File Operations   - Read, write, analyze local files")
    print("  💻 Code Execution    - Write and run Python code")
    print("  🔍 Research          - Gather and synthesize information")
    print("  🛒 E-commerce        - Shopping, cart management, price comparison")
    print("=" * 80 + "\n")
    
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY not set")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='your-key'  # Mac/Linux")
        print("  $env:ANTHROPIC_API_KEY='your-key'   # Windows PowerShell")
        sys.exit(1)
    
    # Get task from user
    print("💬 What should the agent do?")
    print("\nExamples:")
    print("  • Go to GitHub and find trending Python repos")
    print("  • Search Wikipedia for quantum computing and summarize")
    print("  • Read config.json and show me the settings")
    print("  • Write a Python script to calculate prime numbers")
    print("  • Go to Amazon and find wireless headphones under $50")
    print("  • Visit Hacker News and extract top 10 stories")
    print()
    
    task = input("📋 Your task: ").strip()
    
    if not task:
        print("❌ No task provided")
        sys.exit(1)
    
    # Create and run agent
    print()
    agent = UniversalAgent(debug=True)
    
    try:
        result = agent.execute(task)
        
        print(f"\n{'=' * 80}")
        print("📊 FINAL RESULT")
        print(f"{'=' * 80}")
        print(f"Status: {result['status']}")
        print(f"Mode: {result['mode']}")
        
        if result.get('data'):
            print(f"\nData collected: {len(result['data'])} items")
        
        if result.get('output'):
            print(f"\nOutput:\n{result['output']}")
        
        print(f"{'=' * 80}\n")
        
    except KeyboardInterrupt:
        print("\n\n⏸️ Stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()


if __name__ == "__main__":
    main()