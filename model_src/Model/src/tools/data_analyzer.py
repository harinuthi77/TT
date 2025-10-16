import pandas as pd
from typing import Dict, List

class DataAnalyzer:
    def analyze_csv(self, filepath: str) -> Dict:
        try:
            df = pd.read_csv(filepath)
            return {
                'rows': len(df),
                'columns': list(df.columns),
                'summary': df.describe().to_dict(),
                'head': df.head(10).to_dict()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def compare_prices(self, products: List[Dict]) -> Dict:
        if not products:
            return {}
        
        prices = [p.get('price', 0) for p in products if p.get('price')]
        if not prices:
            return {}
        
        return {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices),
            'count': len(prices)
        }
