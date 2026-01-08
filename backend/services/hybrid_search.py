from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearchService:
    def __init__(self):
        self.bm25_index: Dict[str, BM25Okapi] = {}
        self.doc_texts: Dict[str, List[str]] = {}
    
    def index_documents(self, paper_id: str, texts: List[str]):
        """Index documents for BM25 keyword search"""
        # Filter out empty/whitespace-only texts
        texts = [t for t in texts if t and t.strip()]
        
        if not texts or len(texts) == 0:
            print(f"[HYBRID] Skipping {paper_id} - no valid texts")
            return
        
        tokenized = [text.lower().split() for text in texts]
        
        # Filter out empty token lists
        tokenized = [t for t in tokenized if len(t) > 0]
        
        if not tokenized or len(tokenized) == 0:
            print(f"[HYBRID] Skipping {paper_id} - no valid tokens")
            return
        
        try:
            self.bm25_index[paper_id] = BM25Okapi(tokenized)
            self.doc_texts[paper_id] = texts
            print(f"[HYBRID] Indexed {len(texts)} docs for {paper_id}")
        except Exception as e:
            print(f"[HYBRID] Error indexing {paper_id}: {e}")
    
    def keyword_search(self, paper_id: str, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """BM25 keyword search"""
        if paper_id not in self.bm25_index:
            return []
        
        tokenized_query = query.lower().split()
        scores = self.bm25_index[paper_id].get_scores(tokenized_query)
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        return [
            {
                "text": self.doc_texts[paper_id][i],
                "score": float(scores[i]),
                "index": int(i)
            }
            for i in top_indices if scores[i] > 0
        ]
    
    def merge_results(
        self, 
        semantic_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]],
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Merge and re-rank semantic + keyword results
        
        Args:
            alpha: Weight for semantic (1-alpha for keyword)
        """
        result_map = {}
        
        # Normalize and combine scores
        sem_scores = [r.get("score", 0) for r in semantic_results]
        kw_scores = [r.get("score", 0) for r in keyword_results]
        
        sem_max = max(sem_scores) if sem_scores else 1
        kw_max = max(kw_scores) if kw_scores else 1
        
        for r in semantic_results:
            key = r.get("text", "")[:100]
            result_map[key] = {
                **r,
                "hybrid_score": alpha * (r.get("score", 0) / sem_max)
            }
        
        for r in keyword_results:
            key = r.get("text", "")[:100]
            if key in result_map:
                result_map[key]["hybrid_score"] += (1 - alpha) * (r.get("score", 0) / kw_max)
            else:
                result_map[key] = {
                    **r,
                    "hybrid_score": (1 - alpha) * (r.get("score", 0) / kw_max)
                }
        
        # Sort by hybrid score
        results = sorted(result_map.values(), key=lambda x: x["hybrid_score"], reverse=True)
        return results

hybrid_search_service = HybridSearchService()