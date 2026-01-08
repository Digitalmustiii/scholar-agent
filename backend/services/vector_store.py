from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List, Dict, Any, Optional
from config import settings
import uuid

class VectorStoreService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=180  # 3 minutes timeout for large uploads
        )
        self._ensure_collection()
        self.vector_store = SimpleVectorStore()
        self.index = None
        
        # Set embedding model globally
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def _ensure_collection(self):
        from qdrant_client.models import PayloadSchemaType
        
        collections = [c.name for c in self.client.get_collections().collections]
        
        if settings.collection_name not in collections:
            self.client.create_collection(
                collection_name=settings.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"[QDRANT] Created new collection: {settings.collection_name}")
        
        try:
            self.client.create_payload_index(
                collection_name=settings.collection_name,
                field_name="paper_id",
                field_schema=PayloadSchemaType.KEYWORD
            )
            print(f"[QDRANT] Created paper_id index")
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"[QDRANT] Note: {e}")
    
    def create_index(self, nodes, paper_id: Optional[str] = None):
        """Create index and store with paper_id for multi-paper support"""
        from llama_index.core import Settings
        
        print(f"[INDEX] Generating embeddings for {len(nodes)} nodes...")
        for node in nodes:
            if not hasattr(node, 'embedding') or node.embedding is None:
                node.embedding = Settings.embed_model.get_text_embedding(node.get_content())
        
        print(f"[INDEX] Embeddings generated, creating index...")
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        self.index = VectorStoreIndex(nodes, storage_context=storage_context)
        
        # Push nodes with embeddings to Qdrant in batches
        self._push_to_qdrant(nodes, paper_id)
        
        return self.index
    
    def _push_to_qdrant(self, nodes, paper_id: Optional[str] = None):
        """Upload to Qdrant in batches to avoid timeout"""
        BATCH_SIZE = 20  # Upload 20 nodes at a time
        
        all_points = []
        for node in nodes:
            if hasattr(node, 'embedding') and node.embedding:
                payload = {
                    "text": node.text,
                    "metadata": node.metadata
                }
                if paper_id:
                    payload["paper_id"] = paper_id
                
                all_points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=node.embedding,
                    payload=payload
                ))
        
        if not all_points:
            print(f"[QDRANT] WARNING: No points to upsert")
            return
        
        # Upload in batches
        total = len(all_points)
        for i in range(0, total, BATCH_SIZE):
            batch = all_points[i:i + BATCH_SIZE]
            print(f"[QDRANT] Upserting batch {i//BATCH_SIZE + 1}/{(total + BATCH_SIZE - 1)//BATCH_SIZE} ({len(batch)} points)")
            
            self.client.upsert(
                collection_name=settings.collection_name,
                points=batch
            )
        
        print(f"[QDRANT] Successfully upserted {total} points for paper_id: {paper_id}")
    
    def search_by_paper(
        self, 
        query_vector: List[float], 
        paper_ids: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search within specific papers"""
        from qdrant_client.models import FieldCondition, Filter, MatchAny
        
        filter_conditions = Filter(
            must=[
                FieldCondition(
                    key="paper_id",
                    match=MatchAny(any=paper_ids)
                )
            ]
        )
        
        results = self.client.query_points(
            collection_name=settings.collection_name,
            query=query_vector,
            query_filter=filter_conditions,
            limit=top_k
        ).points
        
        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "paper_id": r.payload.get("paper_id", ""),
                "metadata": r.payload.get("metadata", {})
            }
            for r in results
        ]
    
    def search_all_papers(
        self, 
        query_vector: List[float], 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search across all papers"""
        results = self.client.query_points(
            collection_name=settings.collection_name,
            query=query_vector,
            limit=top_k
        ).points
        
        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "paper_id": r.payload.get("paper_id", "unknown"),
                "metadata": r.payload.get("metadata", {})
            }
            for r in results
        ]
    
    def get_papers_list(self) -> List[str]:
        """Get list of all indexed paper IDs"""
        results = self.client.scroll(
            collection_name=settings.collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )[0]
        
        paper_ids = set()
        for point in results:
            if "paper_id" in point.payload:
                paper_ids.add(point.payload["paper_id"])
        
        return list(paper_ids)
    
    def delete_paper(self, paper_id: str):
        """Delete all chunks for a specific paper"""
        self.client.delete(
            collection_name=settings.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(key="paper_id", match=MatchValue(value=paper_id))
                ]
            )
        )
    
    def get_index(self):
        if self.index is None:
            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            self.index = VectorStoreIndex([], storage_context=storage_context)
        return self.index
    
    def test_connection(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except:
            return False

vector_store_service = VectorStoreService()