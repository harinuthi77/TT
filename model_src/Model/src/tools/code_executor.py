import sys
from io import StringIO
from typing import Dict

class CodeExecutor:
    def execute_python(self, code: str) -> Dict:
        try:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            exec(code, {'__builtins__': __builtins__})
            
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            return {'success': True, 'output': output}
        except Exception as e:
            sys.stdout = old_stdout
            return {'success': False, 'error': str(e)}
    
    def validate_code(self, code: str) -> bool:
        try:
            compile(code, '<string>', 'exec')
            return True
        except:
            return False
