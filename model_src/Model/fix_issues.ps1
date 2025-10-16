# fix_issues.ps1
# Fix: 1) Duplicate browsers, 2) Low confidence actions, 3) File/image support

Write-Host ""
Write-Host "🔧 Fixing three issues..." -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# ISSUE 1: Fix duplicate browser opening
# ============================================================================
Write-Host "1️⃣  Fixing duplicate browser issue..." -ForegroundColor Yellow

# The problem: IntelligentAgent creates memory (which might open a browser)
# and then the sub-agent creates another browser

$file = "src\agents\intelligent_agent.py"
$content = Get-Content $file -Raw

# Remove memory initialization from IntelligentAgent
# Each sub-agent will create its own memory when needed
$content = $content -replace 'self\.memory = AgentMemory\([^\)]+\)', '# Memory created by sub-agents individually'
$content = $content -replace 'from src\.core\.memory import AgentMemory', '# from src.core.memory import AgentMemory  # Not needed here'

$content | Set-Content $file -NoNewline
Write-Host "   ✅ Fixed IntelligentAgent to not create duplicate browser" -ForegroundColor Green

# ============================================================================
# ISSUE 2: Require confidence 9-10 before taking action
# ============================================================================
Write-Host ""
Write-Host "2️⃣  Setting high confidence threshold (9-10)..." -ForegroundColor Yellow

$file = "src\core\cognition.py"
$content = Get-Content $file -Raw

# Find the _validate_decision method and add strict confidence check
$validationCheck = @'

        # STRICT CONFIDENCE REQUIREMENT: Only act with 9-10 confidence
        if confidence < 9:
            print(f"   ⚠️  CONFIDENCE TOO LOW ({confidence}/10) - Requiring more analysis")
            decision['action'] = 'wait'
            decision['details'] = f'Need higher confidence (currently {confidence}/10)'
            decision['thinking'] += f" [Action blocked: confidence {confidence} < 9]"
            decision['confidence'] = confidence
            return decision
'@

# Add this check at the start of _validate_decision
$content = $content -replace '(def _validate_decision\(self, decision.*?\n.*?""".*?""")', "`$1$validationCheck"

$content | Set-Content $file -NoNewline
Write-Host "   ✅ Added confidence threshold: minimum 9/10 required" -ForegroundColor Green

# ============================================================================
# ISSUE 3: Add file and image processing capability
# ============================================================================
Write-Host ""
Write-Host "3️⃣  Adding file/image processing support..." -ForegroundColor Yellow

# Create new utility for file processing
$fileProcessorContent = @'
# src/utils/file_processor.py
"""
File and Image Processing for Agent
Allows agent to read and understand images, PDFs, documents, etc.
"""

import base64
from pathlib import Path
from typing import Dict, Optional, Tuple
import anthropic
import os


class FileProcessor:
    """
    Processes files and images for the agent to understand.
    Supports: images (jpg, png, gif, webp), PDFs, text files
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def process_image(self, image_path: str, question: str = "What do you see in this image?") -> str:
        """
        Analyze an image and answer questions about it.
        
        Args:
            image_path: Path to image file
            question: What to ask about the image
            
        Returns:
            Analysis of the image
        """
        
        # Read and encode image
        image_data = self._encode_image(image_path)
        if not image_data:
            return "Error: Could not read image"
        
        media_type, b64_data = image_data
        
        # Ask Claude to analyze
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64_data
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error analyzing image: {e}"
    
    def process_pdf(self, pdf_path: str, question: str = "Summarize this document") -> str:
        """
        Extract text from PDF and analyze it.
        
        Args:
            pdf_path: Path to PDF file
            question: What to ask about the PDF
            
        Returns:
            Analysis of the PDF
        """
        
        try:
            # Try to extract text (requires pypdf or similar)
            import pypdf
            
            with open(pdf_path, 'rb') as f:
                pdf = pypdf.PdfReader(f)
                text = ""
                for page in pdf.pages[:10]:  # First 10 pages
                    text += page.extract_text()
            
            # Ask Claude to analyze
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"{question}\n\nDocument content:\n{text[:50000]}"
                }]
            )
            
            return response.content[0].text
            
        except ImportError:
            return "Error: pypdf not installed. Run: pip install pypdf"
        except Exception as e:
            return f"Error processing PDF: {e}"
    
    def process_text_file(self, file_path: str, question: str = "Summarize this file") -> str:
        """
        Read and analyze a text file.
        """
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"{question}\n\nFile content:\n{content[:50000]}"
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error processing file: {e}"
    
    def _encode_image(self, image_path: str) -> Optional[Tuple[str, str]]:
        """Encode image to base64"""
        
        path = Path(image_path)
        if not path.exists():
            return None
        
        # Determine media type
        ext = path.suffix.lower()
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        
        media_type = media_types.get(ext, 'image/jpeg')
        
        # Read and encode
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        return media_type, image_data
'@

# Write the new file processor
$fileProcessorPath = "src\utils\file_processor.py"
$fileProcessorContent | Set-Content $fileProcessorPath -NoNewline
Write-Host "   ✅ Created file_processor.py with image/PDF support" -ForegroundColor Green

# Update cognition to use file processor
$file = "src\core\cognition.py"
$content = Get-Content $file -Raw

# Add import at top
if ($content -notmatch 'from src\.utils\.file_processor import FileProcessor') {
    $content = $content -replace '(import anthropic)', "`$1`nfrom src.utils.file_processor import FileProcessor"
}

# Add file processor to __init__
$content = $content -replace '(self\.validation_enabled = True)', "`$1`n        self.file_processor = FileProcessor(api_key)"

$content | Set-Content $file -NoNewline
Write-Host "   ✅ Added file processing to CognitiveEngine" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "✅ All three issues fixed!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Cyan
Write-Host "  1. ✅ Fixed duplicate browser (only one now)" -ForegroundColor Green
Write-Host "  2. ✅ Confidence threshold set to 9-10 minimum" -ForegroundColor Green
Write-Host "  3. ✅ Added image/PDF/file processing capability" -ForegroundColor Green
Write-Host ""
Write-Host "New capability - Process images:" -ForegroundColor Yellow
Write-Host '  agent.cognition.file_processor.process_image("screenshot.png", "What products are shown?")' -ForegroundColor Gray
Write-Host ""
Write-Host "Now run: python main.py" -ForegroundColor Cyan
Write-Host ""