from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    paper_ids: Optional[List[str]] = None  # For specific paper queries

class SourceNode(BaseModel):
    paper_name: str
    page: Optional[int] = None
    content: str
    score: Optional[float] = None
    paper_id: str = "unknown"  # NEW: Track which paper

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceNode]
    reasoning: Optional[List[dict]] = None

class PaperUploadResponse(BaseModel):
    filename: str
    status: str
    message: str
    num_chunks: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    vector_db: bool
    llm: bool

class PaperInfo(BaseModel):
    filename: str
    paper_id: str
    size_mb: float
    indexed: bool = False

class PaperListResponse(BaseModel):
    papers: List[PaperInfo]
    total: int

class DeletePaperResponse(BaseModel):
    message: str
    paper_id: str

class ComparisonResponse(BaseModel):
    query: str
    papers_compared: int
    synthesis: str
    details: List[dict]