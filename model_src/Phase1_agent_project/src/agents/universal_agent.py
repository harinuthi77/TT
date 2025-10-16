"""
Universal Agent - Handles ANY task type
Routes to appropriate subsystem: web, file, or code
"""

import os
from typing import Dict
from pathlib import Path

from src.core.config import ANTHROPIC_API_KEY
from src.core.file_handler import FileHandler
from src.core.code_executor import CodeExecutor


class UniversalAgent:
    """
    Universal agent that intelligently routes tasks to appropriate handlers
    """
    
    def __init__(self, api_key: str = None, debug: bool = False):
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.debug = debug
        
        # Initialize handlers
        self.file_handler = FileHandler()
        self.code_executor = CodeExecutor()
        
        if self.debug:
            print("✅ Universal Agent initialized")
            print("   📁 File handler ready")
            print("   💻 Code executor ready")
            print("   🌐 Web automation ready\n")
    
    def execute(self, task: str) -> Dict:
        """
        Execute any task by routing to appropriate subsystem
        
        Args:
            task: User's task description
            
        Returns:
            Result dictionary with status, mode, and data
        """
        
        if self.debug:
            print(f"🎯 Task: {task}\n")
        
        # Detect task type
        task_type = self._detect_task_type(task)
        
        if self.debug:
            print(f"🔍 Detected type: {task_type}\n")
        
        # Route to appropriate handler
        if task_type == 'file':
            return self._handle_file_task(task)
        
        elif task_type == 'code':
            return self._handle_code_task(task)
        
        elif task_type == 'web':
            return self._handle_web_task(task)
        
        else:
            # Default to web automation for general tasks
            return self._handle_web_task(task)
    
    def _detect_task_type(self, task: str) -> str:
        """Detect what type of task this is"""
        
        task_lower = task.lower()
        
        # File operations
        file_keywords = ['file', 'read', 'write', 'save', 'load', 'open', 
                        'create file', 'delete file', 'list files', 'directory',
                        'json', 'csv', 'txt', 'document']
        
        if any(keyword in task_lower for keyword in file_keywords):
            # But not if it's about web files
            if not any(web in task_lower for web in ['website', 'download', 'fetch', 'scrape']):
                return 'file'
        
        # Code execution
        code_keywords = ['python script', 'write code', 'run code', 'execute code',
                        'create script', 'program', 'function', 'calculate',
                        'write a script', 'python program']
        
        if any(keyword in task_lower for keyword in code_keywords):
            return 'code'
        
        # Web automation (default for most tasks)
        web_keywords = ['website', 'web', 'search', 'browse', 'goto', 'go to',
                       'find', 'amazon', 'google', 'github', 'wikipedia',
                       'extract', 'scrape', 'navigate', 'click', 'url']
        
        if any(keyword in task_lower for keyword in web_keywords):
            return 'web'
        
        # Default to web for ambiguous tasks
        return 'web'
    
    def _handle_file_task(self, task: str) -> Dict:
        """Handle file operations"""
        
        if self.debug:
            print("📁 MODE: File Operations\n")
        
        task_lower = task.lower()
        
        try:
            # Read file
            if 'read' in task_lower or 'show' in task_lower or 'open' in task_lower:
                # Extract filename
                words = task.split()
                filename = None
                
                for word in words:
                    if '.' in word and not word.startswith('http'):
                        filename = word.strip('.,;')
                        break
                
                if not filename:
                    return {
                        'status': 'error',
                        'mode': 'file',
                        'output': 'Could not determine filename. Please specify a file.'
                    }
                
                content = self.file_handler.read_file(filename)
                
                return {
                    'status': 'success',
                    'mode': 'file',
                    'output': content,
                    'file': filename
                }
            
            # Write file
            elif 'write' in task_lower or 'create' in task_lower or 'save' in task_lower:
                return {
                    'status': 'info',
                    'mode': 'file',
                    'output': 'File writing requires content. Use: write_file(filename, content)'
                }
            
            # List files
            elif 'list' in task_lower:
                files = self.file_handler.list_files()
                
                return {
                    'status': 'success',
                    'mode': 'file',
                    'output': '\n'.join(files),
                    'data': files
                }
            
            else:
                return {
                    'status': 'error',
                    'mode': 'file',
                    'output': 'Unclear file operation. Supported: read, write, list'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'mode': 'file',
                'output': f'File operation failed: {e}'
            }
    
    def _handle_code_task(self, task: str) -> Dict:
        """Handle code execution"""
        
        if self.debug:
            print("💻 MODE: Code Execution\n")
        
        # Use Claude to generate the code
        from src.core.cognition import CognitiveEngine
        from src.core.memory import AgentMemory
        
        memory = AgentMemory()
        cognition = CognitiveEngine(memory, self.api_key)
        
        prompt = f"""Generate Python code for this task: {task}

Requirements:
1. Write complete, runnable Python code
2. Include all necessary imports
3. Add comments explaining the logic
4. Make it production-ready
5. Output results with print statements

Respond with ONLY the Python code, no explanations."""
        
        try:
            response = cognition.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            code = response.content[0].text
            
            # Extract code block if present
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
            
            print(f"📝 Generated code:\n")
            print("─" * 60)
            print(code)
            print("─" * 60 + "\n")
            
            # Ask user if they want to execute
            execute = input("Execute this code? [Y/n]: ").strip().lower()
            
            if execute in ['', 'y', 'yes']:
                print("\n⚡ Executing...\n")
                success, output = self.code_executor.execute_python(code)
                
                return {
                    'status': 'success' if success else 'error',
                    'mode': 'code',
                    'code': code,
                    'output': output,
                    'executed': True
                }
            else:
                return {
                    'status': 'success',
                    'mode': 'code',
                    'code': code,
                    'output': 'Code generated but not executed',
                    'executed': False
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'mode': 'code',
                'output': f'Code generation failed: {e}'
            }
        finally:
            memory.close()
    
    def _handle_web_task(self, task: str) -> Dict:
        """Handle web automation"""
        
        if self.debug:
            print("🌐 MODE: Web Automation\n")
        
        from src.agents.continuous_agent import ContinuousAgent
        
        agent = ContinuousAgent(api_key=self.api_key, debug=self.debug)
        
        try:
            success, data = agent.run_continuous(task, max_iterations=1)
            
            return {
                'status': 'success' if success else 'incomplete',
                'mode': 'web',
                'data': data
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'mode': 'web',
                'output': f'Web automation failed: {e}'
            }
        finally:
            agent.close()
    
    def close(self):
        """Cleanup resources"""
        pass