from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from models.schemas import QueryRequest, QueryResponse, PaperUploadResponse, HealthResponse
from models.chat_schemas import MessageCreate, ConversationList, ConversationDetail, ConversationSummary
from services.document_processor import document_processor
from services.vector_store import vector_store_service
from services.llm_service import llm_service
from services.chat_history import chat_history_service, Message, Conversation
from services.export_service import export_service
from agents.orchestrator import agent_orchestrator
from typing import List
from datetime import datetime
import uuid

app = FastAPI(title="ScholarAgent API", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ScholarAgent API v3.1 - Phase 3: Chat History + Export"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        vector_db=vector_store_service.test_connection(),
        llm=llm_service.test_connection()
    )

@app.post("/upload", response_model=PaperUploadResponse)
async def upload_paper(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    try:
        print(f"[UPLOAD] Starting upload for: {file.filename}")
        
        content = await file.read()
        print(f"[UPLOAD] File read, size: {len(content)} bytes")
        
        file_path = document_processor.save_paper(content, file.filename)
        print(f"[UPLOAD] File saved to: {file_path}")
        
        print(f"[UPLOAD] Processing paper...")
        paper_id, nodes = document_processor.process_paper(file_path)
        print(f"[UPLOAD] Paper processed. ID: {paper_id}, Nodes: {len(nodes)}")
        
        print(f"[UPLOAD] Creating index...")
        vector_store_service.create_index(nodes, paper_id=paper_id)
        print(f"[UPLOAD] Index created successfully")
        
        agent_orchestrator.index = None
        agent_orchestrator.tools = None
        
        return PaperUploadResponse(
            filename=file.filename,
            status="success",
            message=f"Paper processed successfully (ID: {paper_id})",
            num_chunks=len(nodes)
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[UPLOAD ERROR] {error_details}")
        raise HTTPException(500, f"Error processing paper: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_papers(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(400, "Query cannot be empty")
    
    try:
        result = await agent_orchestrator.query(request.query)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            reasoning=result["reasoning"]
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error processing query: {str(e)}")

@app.get("/papers")
async def list_papers():
    try:
        papers = document_processor.get_all_papers()
        indexed_ids = vector_store_service.get_papers_list()
        
        for paper in papers:
            paper["indexed"] = paper["paper_id"] in indexed_ids
        
        return {
            "papers": papers,
            "total": len(papers)
        }
    except Exception as e:
        raise HTTPException(500, f"Error listing papers: {str(e)}")

@app.delete("/papers/{filename}")
async def delete_paper(filename: str):
    try:
        paper_id = document_processor.generate_paper_id(filename)
        
        try:
            vector_store_service.delete_paper(paper_id)
        except Exception as e:
            print(f"Warning: Could not delete from vector store: {e}")
        
        deleted = document_processor.delete_paper_file(filename)
        
        if not deleted:
            raise HTTPException(404, "Paper not found")
        
        agent_orchestrator.index = None
        agent_orchestrator.tools = None
        
        return {
            "message": f"Paper '{filename}' deleted successfully",
            "paper_id": paper_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(500, f"Error deleting paper: {str(e)}")

@app.get("/papers/compare")
async def compare_papers_endpoint(query: str):
    try:
        agent_orchestrator.initialize_agent()
        result = await agent_orchestrator._execute_comparison(query)
        return result
    except Exception as e:
        raise HTTPException(500, f"Comparison error: {str(e)}")

# ==================== CHAT HISTORY ENDPOINTS ====================

@app.get("/conversations", response_model=ConversationList)
async def list_conversations():
    """Get all conversations"""
    conversations = chat_history_service.list_conversations()
    return ConversationList(
        conversations=[ConversationSummary(**conv) for conv in conversations],
        total=len(conversations)
    )

@app.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    """Load a specific conversation"""
    conversation = chat_history_service.load_conversation(conversation_id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    return conversation

@app.post("/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, message: MessageCreate):
    """Add a message to conversation"""
    try:  
        msg = Message(
            role=message.role,
            content=message.content,
            timestamp=datetime.utcnow().isoformat(),
            sources=message.sources,
            reasoning=message.reasoning
        )
        
        success = chat_history_service.add_message(conversation_id, msg)
        if not success:
            raise HTTPException(500, "Failed to save message")
        
        return {"status": "success", "conversation_id": conversation_id}
    except Exception as e:
        import traceback
        print(f"[ADD_MESSAGE ERROR] {traceback.format_exc()}")
        raise HTTPException(422, f"Message validation error: {str(e)}")

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    success = chat_history_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(404, "Conversation not found")
    
    return {"message": "Conversation deleted", "conversation_id": conversation_id}

# ==================== EXPORT ENDPOINTS ====================

@app.get("/conversations/{conversation_id}/export/markdown")
async def export_markdown(conversation_id: str):
    """Export conversation as Markdown"""
    try:
        md_content = export_service.export_markdown(conversation_id)
        
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=conversation_{conversation_id}.md"
            }
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Export error: {str(e)}")

@app.get("/conversations/{conversation_id}/export/bibtex")
async def export_bibtex(conversation_id: str):
    """Export papers as BibTeX"""
    try:
        papers = document_processor.get_all_papers()
        bibtex_content = export_service.export_bibtex(conversation_id, papers)
        
        return Response(
            content=bibtex_content,
            media_type="application/x-bibtex",
            headers={
                "Content-Disposition": f"attachment; filename=references_{conversation_id}.bib"
            }
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Export error: {str(e)}")

@app.get("/conversations/{conversation_id}/export/pdf")  # NEW: PDF export endpoint
async def export_pdf(conversation_id: str):
    """Export conversation as PDF"""
    try:
        pdf_content = export_service.export_pdf(conversation_id)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=conversation_{conversation_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Export error: {str(e)}")