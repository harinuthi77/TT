"""
File Handler - Local file operations
Read, write, analyze files in workspace
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional


class FileHandler:
    """
    Handles all file operations for the agent
    """
    
    def __init__(self, workspace_dir: str = "workspace"):
        """
        Initialize file handler
        
        Args:
            workspace_dir: Directory for agent's file operations
        """
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
    def read_file(self, filepath: str) -> str:
        """
        Read file content
        
        Args:
            filepath: Path to file (relative or absolute)
            
        Returns:
            File content as string
        """
        try:
            path = Path(filepath)
            
            # Check if file exists
            if not path.exists():
                # Try in workspace
                path = self.workspace / filepath
            
            if not path.exists():
                return f"❌ File not found: {filepath}"
            
            # Read based on file type
            if path.suffix.lower() == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
            elif path.suffix.lower() == '.csv':
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    return '\n'.join([', '.join(row) for row in rows[:20]])
            
            else:
                # Plain text
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Limit very large files
                    if len(content) > 10000:
                        return content[:10000] + f"\n\n... (showing first 10,000 chars of {len(content)} total)"
                    
                    return content
        
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    def write_file(self, filepath: str, content: str, mode: str = 'w') -> str:
        """
        Write content to file
        
        Args:
            filepath: Path to file
            content: Content to write
            mode: Write mode ('w' = overwrite, 'a' = append)
            
        Returns:
            Success message
        """
        try:
            path = Path(filepath)
            
            # If relative path, put in workspace
            if not path.is_absolute():
                path = self.workspace / filepath
            
            # Create parent directories
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ File written: {path} ({len(content)} chars)"
        
        except Exception as e:
            return f"❌ Error writing file: {e}"
    
    def list_files(self, directory: str = ".", pattern: str = "*") -> List[str]:
        """
        List files in directory
        
        Args:
            directory: Directory to list
            pattern: File pattern (e.g., "*.py", "*.json")
            
        Returns:
            List of file paths
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                path = self.workspace / directory
            
            if not path.exists():
                return [f"❌ Directory not found: {directory}"]
            
            # Get files matching pattern
            files = []
            for item in path.rglob(pattern):
                if item.is_file():
                    files.append(str(item.relative_to(path)))
            
            return sorted(files)
        
        except Exception as e:
            return [f"❌ Error listing files: {e}"]
    
    def analyze_file(self, filepath: str) -> Dict:
        """
        Analyze file and return metadata
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            path = Path(filepath)
            
            if not path.exists():
                path = self.workspace / filepath
            
            if not path.exists():
                return {'error': f'File not found: {filepath}'}
            
            stat = path.stat()
            
            return {
                'name': path.name,
                'path': str(path),
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'extension': path.suffix,
                'modified': stat.st_mtime,
                'is_text': path.suffix.lower() in ['.txt', '.py', '.json', '.csv', '.md', '.yml', '.yaml']
            }
        
        except Exception as e:
            return {'error': f'Error analyzing file: {e}'}
    
    def delete_file(self, filepath: str) -> str:
        """
        Delete a file
        
        Args:
            filepath: Path to file
            
        Returns:
            Success/error message
        """
        try:
            path = Path(filepath)
            
            if not path.exists():
                path = self.workspace / filepath
            
            if not path.exists():
                return f"❌ File not found: {filepath}"
            
            path.unlink()
            return f"✅ Deleted: {filepath}"
        
        except Exception as e:
            return f"❌ Error deleting file: {e}"
    
    def create_directory(self, directory: str) -> str:
        """
        Create a directory
        
        Args:
            directory: Directory path
            
        Returns:
            Success/error message
        """
        try:
            path = Path(directory)
            
            if not path.is_absolute():
                path = self.workspace / directory
            
            path.mkdir(parents=True, exist_ok=True)
            
            return f"✅ Directory created: {path}"
        
        except Exception as e:
            return f"❌ Error creating directory: {e}"


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    handler = FileHandler()
    
    print("📁 File Handler Test\n")
    
    # Create test file
    print("1. Writing test file...")
    result = handler.write_file("test.txt", "Hello from AI Agent!\nThis is a test file.")
    print(f"   {result}")
    
    # Read file
    print("\n2. Reading test file...")
    content = handler.read_file("test.txt")
    print(f"   {content}")
    
    # Analyze file
    print("\n3. Analyzing file...")
    info = handler.analyze_file("test.txt")
    print(f"   {json.dumps(info, indent=2)}")
    
    # List files
    print("\n4. Listing files...")
    files = handler.list_files()
    print(f"   {files}")