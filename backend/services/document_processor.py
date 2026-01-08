from pathlib import Path
from pypdf import PdfReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from config import settings
import hashlib
from typing import Tuple, List

class DocumentProcessor:
    def __init__(self):
        self.splitter = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        self.papers_dir = Path("data/papers")
        self.papers_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_paper_id(self, filename: str) -> str:
        """Generate unique paper ID from filename"""
        return hashlib.md5(filename.encode()).hexdigest()[:12]
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        reader = PdfReader(pdf_path)
        return "\n\n".join(page.extract_text() for page in reader.pages)
    
    def process_paper(self, pdf_path: Path) -> Tuple[str, List]:
        """Process paper and return (paper_id, nodes)"""
        paper_id = self.generate_paper_id(pdf_path.name)
        text = self.extract_text_from_pdf(pdf_path)
        
        document = Document(
            text=text,
            metadata={
                "filename": pdf_path.name,
                "paper_id": paper_id
            }
        )
        
        nodes = self.splitter.get_nodes_from_documents([document])
        
        # Add paper_id to each node's metadata
        for node in nodes:
            node.metadata["paper_id"] = paper_id
        
        # Index for hybrid search
        from services.hybrid_search import hybrid_search_service
        texts = [node.text for node in nodes]
        hybrid_search_service.index_documents(paper_id, texts)
        
        return paper_id, nodes
    
    def save_paper(self, file_content: bytes, filename: str) -> Path:
        file_path = self.papers_dir / filename
        file_path.write_bytes(file_content)
        return file_path
    
    def get_all_papers(self) -> List[dict]:
        """List all papers in directory"""
        papers = []
        for pdf_file in self.papers_dir.glob("*.pdf"):
            papers.append({
                "filename": pdf_file.name,
                "paper_id": self.generate_paper_id(pdf_file.name),
                "size_mb": pdf_file.stat().st_size / (1024 * 1024)
            })
        return papers
    
    def delete_paper_file(self, filename: str) -> bool:
        """Delete paper file from disk"""
        try:
            file_path = self.papers_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

document_processor = DocumentProcessor()