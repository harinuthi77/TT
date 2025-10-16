import requests
from typing import List, Dict
import time

class ResearchTool:
    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict]:
        try:
            import feedparser
            url = "http://export.arxiv.org/api/query?search_query=all:" + query + "&max_results=" + str(max_results)
            feed = feedparser.parse(url)
            
            papers = []
            for entry in feed.entries:
                papers.append({
                    'title': entry.title,
                    'authors': [a.name for a in entry.authors],
                    'summary': entry.summary[:500],
                    'url': entry.link,
                    'published': entry.published
                })
            return papers
        except:
            return []
    
    def search_web(self, query: str) -> List[Dict]:
        return [{'title': 'Result for ' + query, 'url': 'https://example.com'}]
