from typing import Dict, List

class Visualizer:
    def create_mermaid(self, diagram_type: str, data: Dict) -> str:
        if diagram_type == 'flowchart':
            nodes = data.get('nodes', [])
            edges = data.get('edges', [])
            
            mermaid = "flowchart TD\n"
            for node in nodes:
                mermaid += "    " + node['id'] + "[" + node['label'] + "]\n"
            for edge in edges:
                mermaid += "    " + edge['from'] + " --> " + edge['to'] + "\n"
            return mermaid
        
        return "graph TD\n    A[Start]"
    
    def create_table(self, items: List[Dict]) -> str:
        if not items:
            return ""
        
        headers = list(items[0].keys())
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(['---'] * len(headers)) + " |\n"
        
        for item in items:
            values = [str(item.get(h, '')) for h in headers]
            row = "| " + " | ".join(values) + " |\n"
            table += row
        
        return table
