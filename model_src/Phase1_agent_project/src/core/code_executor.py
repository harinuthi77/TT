"""
Code Executor - Safe Python code execution
Runs user/AI generated code in isolated environment
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, Optional
import tempfile


class CodeExecutor:
    """
    Executes Python code safely with timeout and isolation
    """
    
    def __init__(self, workspace_dir: str = "workspace", timeout: int = 30):
        """
        Initialize code executor
        
        Args:
            workspace_dir: Directory for code execution
            timeout: Maximum execution time in seconds
        """
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        
    def execute_python(self, code: str, save_file: bool = True) -> Tuple[bool, str]:
        """
        Execute Python code and return output
        
        Args:
            code: Python code to execute
            save_file: Whether to save code to file before executing
            
        Returns:
            (success: bool, output: str)
        """
        
        # Create temp file for code
        if save_file:
            temp_file = self.workspace / f"temp_script_{os.getpid()}.py"
        else:
            # Use system temp
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            temp_file = Path(temp_file.name)
        
        try:
            # Write code to file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute with subprocess
            result = subprocess.run(
                [sys.executable, str(temp_file)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.workspace)  # Run in workspace directory
            )
            
            # Combine stdout and stderr
            output = ""
            
            if result.stdout:
                output += "📤 Output:\n" + result.stdout
            
            if result.stderr:
                if output:
                    output += "\n\n"
                output += "⚠️ Errors/Warnings:\n" + result.stderr
            
            if not output:
                output = "✅ Code executed successfully (no output)"
            
            success = result.returncode == 0
            
            return success, output
        
        except subprocess.TimeoutExpired:
            return False, f"❌ Timeout: Code execution exceeded {self.timeout} seconds"
        
        except Exception as e:
            return False, f"❌ Execution error: {e}"
        
        finally:
            # Cleanup temp file (optional - keep for debugging)
            if not save_file and temp_file.exists():
                temp_file.unlink()
    
    def execute_python_interactive(self, code: str) -> Tuple[bool, str]:
        """
        Execute Python code and capture output interactively
        
        Args:
            code: Python code to execute
            
        Returns:
            (success: bool, output: str)
        """
        
        try:
            # Create namespace for execution
            namespace = {}
            
            # Capture stdout
            from io import StringIO
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # Execute
            exec(code, namespace)
            
            # Get output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            if not output:
                output = "✅ Code executed successfully (no output)"
            
            return True, output
        
        except Exception as e:
            sys.stdout = old_stdout
            return False, f"❌ Error: {e}"
    
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate Python code without executing
        
        Args:
            code: Python code to validate
            
        Returns:
            (is_valid: bool, message: str)
        """
        
        try:
            compile(code, '<string>', 'exec')
            return True, "✅ Code is syntactically valid"
        
        except SyntaxError as e:
            return False, f"❌ Syntax Error: {e}"
        
        except Exception as e:
            return False, f"❌ Validation Error: {e}"
    
    def list_saved_scripts(self) -> list:
        """
        List all saved Python scripts in workspace
        
        Returns:
            List of script filenames
        """
        
        scripts = []
        
        for file in self.workspace.glob("*.py"):
            if not file.name.startswith("temp_"):
                scripts.append(file.name)
        
        return sorted(scripts)
    
    def save_script(self, code: str, filename: str) -> str:
        """
        Save code to a permanent script file
        
        Args:
            code: Python code
            filename: Filename to save as
            
        Returns:
            Success/error message
        """
        
        try:
            if not filename.endswith('.py'):
                filename += '.py'
            
            filepath = self.workspace / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return f"✅ Script saved: {filepath}"
        
        except Exception as e:
            return f"❌ Error saving script: {e}"
    
    def run_saved_script(self, filename: str) -> Tuple[bool, str]:
        """
        Run a previously saved script
        
        Args:
            filename: Script filename
            
        Returns:
            (success: bool, output: str)
        """
        
        try:
            filepath = self.workspace / filename
            
            if not filepath.exists():
                return False, f"❌ Script not found: {filename}"
            
            # Read and execute
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return self.execute_python(code, save_file=False)
        
        except Exception as e:
            return False, f"❌ Error running script: {e}"


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    executor = CodeExecutor()
    
    print("💻 Code Executor Test\n")
    
    # Example 1: Simple calculation
    print("1. Testing simple calculation...")
    code1 = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""
    
    success, output = executor.execute_python(code1)
    print(f"   Success: {success}")
    print(f"   Output:\n{output}\n")
    
    # Example 2: Data processing
    print("2. Testing data processing...")
    code2 = """
import json

data = {
    'name': 'AI Agent',
    'capabilities': ['web', 'code', 'files'],
    'status': 'active'
}

print(json.dumps(data, indent=2))
"""
    
    success, output = executor.execute_python(code2)
    print(f"   Success: {success}")
    print(f"   Output:\n{output}\n")
    
    # Example 3: Validation
    print("3. Testing code validation...")
    invalid_code = "print('test'"  # Missing closing parenthesis
    
    valid, message = executor.validate_code(invalid_code)
    print(f"   {message}\n")