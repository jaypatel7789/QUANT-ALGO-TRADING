"""
Rerank Skill - Semantic Document & Code Snippet Re-ranking
Powered by OpenRouter's nvidia/llama-nemotron-rerank-vl-1b-v2:free model.
Allows agents to semantically rank code files, snippets, and documentation.
"""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

# Ensure .env is loaded
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class RerankSkill:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("RERANK_MODEL", "nvidia/llama-nemotron-rerank-vl-1b-v2:free")
        self.url = "https://openrouter.ai/api/v1/rerank"

    def rerank_texts(self, query: str, texts: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks a list of text snippets, code snippets, or documents based on relevance to query.
        Returns sorted results with relevance scores.
        """
        if not self.api_key:
            return [{"error": "Missing OpenRouter API Key"}]

        documents = [{"text": t} for t in texts if t.strip()]
        if not documents:
            return []

        payload = {
            "model": self.model,
            "query": query,
            "documents": documents,
            "top_n": min(top_n, len(documents))
        }

        try:
            response = requests.post(
                url=self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )

            if response.status_code != 200:
                return [{"error": f"OpenRouter API returned HTTP {response.status_code}: {response.text}"}]

            data = response.json()
            results = []
            for item in data.get("results", []):
                doc_text = item.get("document", {}).get("text", "")
                results.append({
                    "index": item.get("index"),
                    "relevance_score": round(item.get("relevance_score", 0.0), 4),
                    "snippet": doc_text[:200] + ("..." if len(doc_text) > 200 else "")
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]
