from services.vector_store import vector_store_service
from services.llm_service import llm_service
from agents.tools import rag_tools

class AgentOrchestrator:
    def __init__(self):
        self.index = None
        self.reasoning_steps = []
        self.tools = None
    
    def initialize_agent(self):
        self.index = vector_store_service.get_index()
        if self.index is None or not hasattr(self.index, '_docstore') or len(self.index.docstore.docs) == 0:
            raise ValueError("No tools available. Upload papers first.")
        self.tools = rag_tools.create_tools()
    
    async def query(self, question: str) -> dict:
        if not self.index:
            self.initialize_agent()
        
        self.reasoning_steps = []
        
        # Step 1: Analyze query type
        query_lower = question.lower()
        self.reasoning_steps.append({
            "step": "Query Analysis",
            "description": f"Analyzing: '{question}'"
        })
        
        # Step 2: Select tool (now includes new tools)
        tool_type = self._select_tool(query_lower)
        self.reasoning_steps.append({
            "step": "Tool Selection",
            "description": f"Selected '{tool_type}' based on query patterns"
        })
        
        # Step 3: Execute with appropriate tool
        if tool_type == "compare_papers":
            response = await self._execute_comparison(question)
        elif tool_type == "hybrid_search":
            response = await self._execute_hybrid(question)
        else:
            response = await self._execute_standard(question, tool_type)
        
        # Step 4: Synthesis
        self.reasoning_steps.append({
            "step": "Answer Synthesis",
            "description": f"Generated answer using '{tool_type}' tool"
        })
        
        return {
            "answer": str(response.get("answer", response)),
            "sources": response.get("sources", []),
            "reasoning": self.reasoning_steps
        }
    
    def _select_tool(self, query: str) -> str:
        """Enhanced tool selection with Phase 2 tools"""
        # Multi-paper comparison keywords
        comparison_kw = ["compare", "across papers", "different papers", "all papers", 
                         "similarities", "differences", "between papers"]
        
        # Hybrid search keywords (exact terms)
        hybrid_kw = ["find mentions", "all equations", "references to", "citations of",
                     "show all", "list all", "search for term"]
        
        # Original keywords
        summary_kw = ["summarize", "summary", "overview", "main", "contribution", "about"]
        detailed_kw = ["explain", "how does", "analyze", "discuss", "describe", "why"]
        
        if any(kw in query for kw in comparison_kw):
            return "compare_papers"
        elif any(kw in query for kw in hybrid_kw):
            return "hybrid_search"
        elif any(kw in query for kw in summary_kw):
            return "summary"
        elif any(kw in query for kw in detailed_kw):
            return "detailed"
        else:
            return "vector_search"
    
    async def _execute_comparison(self, question: str) -> dict:
        """Execute multi-paper comparison"""
        try:
            tool = next((t for t in self.tools if t.metadata.name == "compare_papers"), None)
            if tool:
                result = tool.fn(question)
                return {"answer": result, "sources": []}
            else:
                # Fallback
                return await self._execute_standard(question, "vector_search")
        except Exception as e:
            return {"answer": f"Comparison failed: {str(e)}", "sources": []}
    
    async def _execute_hybrid(self, question: str) -> dict:
        """Execute hybrid search"""
        try:
            tool = next((t for t in self.tools if t.metadata.name == "hybrid_search"), None)
            if tool:
                result = tool.fn(question)
                return {"answer": result, "sources": []}
            else:
                return await self._execute_standard(question, "vector_search")
        except Exception as e:
            return {"answer": f"Hybrid search failed: {str(e)}", "sources": []}
    
    async def _execute_standard(self, question: str, tool_type: str) -> dict:
        """Execute standard query tools"""
        if tool_type == "summary":
            query_engine = self.index.as_query_engine(
                response_mode="tree_summarize",
                similarity_top_k=10
            )
        elif tool_type == "detailed":
            query_engine = self.index.as_query_engine(
                response_mode="compact",
                similarity_top_k=7
            )
        else:  # vector search
            query_engine = self.index.as_query_engine(similarity_top_k=5)
        
        response = await query_engine.aquery(question)
        
        return {
            "answer": str(response),
            "sources": self._extract_sources(response)
        }
    
    def _extract_sources(self, response) -> list:
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                sources.append({
                    "paper_name": node.metadata.get("filename", "Unknown"),
                    "page": node.metadata.get("page", None),
                    "content": node.text[:300],
                    "score": node.score if hasattr(node, 'score') else None,
                    "paper_id": node.metadata.get("paper_id", "unknown")
                })
        return sources

agent_orchestrator = AgentOrchestrator()