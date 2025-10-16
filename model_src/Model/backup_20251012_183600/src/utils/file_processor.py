"""
File and Image Processing for Agent
"""
import base64
from pathlib import Path
from typing import Optional, Tuple
import anthropic
import os


class FileProcessor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def process_image(self, image_path: str, question: str = "What do you see?") -> str:
        """Analyze an image"""
        image_data = self._encode_image(image_path)
        if not image_data:
            return "Error: Could not read image"
        
        media_type, b64_data = image_data
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64_data}},
                        {"type": "text", "text": question}
                    ]
                }]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {e}"
    
    def _encode_image(self, image_path: str) -> Optional[Tuple[str, str]]:
        path = Path(image_path)
        if not path.exists():
            return None
        
        ext = path.suffix.lower()
        media_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'}
        media_type = media_types.get(ext, 'image/jpeg')
        
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        return media_type, image_data