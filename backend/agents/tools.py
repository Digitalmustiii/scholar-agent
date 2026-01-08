from llama_index.core.tools import QueryEngineTool, FunctionTool
from services.vector_store import vector_store_service
from services.hybrid_search import hybrid_search_service
from services.llm_service import llm_service
from typing import List, Dict, Any
import json

class RAGTools:
    def __init__(self):
        self.tools = []
    
    def create_tools(self):
        try:
            index = vector_store_service.get_index()
            
            if index is None or not hasattr(index, '_docstore') or len(index.docstore.docs) == 0:
                return []
            
            # Tool 1: Vector Search (Specific Q&A)
            vector_tool = QueryEngineTool.from_defaults(
                query_engine=index.as_query_engine(similarity_top_k=5),
                name="vector_search",
                description=(
                    "Use this for answering SPECIFIC questions about research papers. "
                    "Best for: methodologies, datasets, results, technical details, "
                    "comparisons between specific concepts. "
                    "Example queries: 'What dataset was used?', 'How does X compare to Y?', "
                    "'What were the accuracy results?'"
                )
            )
            
            # Tool 2: Summary (Overview & Broad Questions)
            summary_tool = QueryEngineTool.from_defaults(
                query_engine=index.as_query_engine(
                    response_mode="tree_summarize",
                    similarity_top_k=10
                ),
                name="summarize",
                description=(
                    "Use this for COMPREHENSIVE summaries and overviews. "
                    "Best for: paper summaries, main contributions, broad understanding, "
                    "research objectives, conclusions. "
                    "Example queries: 'Summarize the paper', 'What is the main contribution?', "
                    "'Give me an overview'"
                )
            )
            
            # Tool 3: Detailed Analysis (Multi-aspect queries)
            analysis_tool = QueryEngineTool.from_defaults(
                query_engine=index.as_query_engine(
                    response_mode="compact",
                    similarity_top_k=7
                ),
                name="detailed_analysis",
                description=(
                    "Use this for DETAILED ANALYSIS requiring multiple aspects. "
                    "Best for: explaining complex concepts, analyzing approaches, "
                    "discussing limitations, exploring implications. "
                    "Example queries: 'Explain how X works', 'Analyze the approach', "
                    "'What are the limitations?'"
                )
            )
            
            # Tool 4: Multi-Paper Comparison (NEW)
            comparison_tool = FunctionTool.from_defaults(
                fn=self._compare_papers,
                name="compare_papers",
                description=(
                    "Use this to COMPARE concepts across MULTIPLE papers. "
                    "Best for: comparative analysis, finding differences/similarities, "
                    "tracking evolution of ideas across papers. "
                    "Example queries: 'Compare approach X across all papers', "
                    "'How do different papers handle Y?', 'What are common themes?'"
                )
            )
            
            # Tool 5: Hybrid Search (NEW)
            hybrid_tool = FunctionTool.from_defaults(
                fn=self._hybrid_search,
                name="hybrid_search",
                description=(
                    "Use this for queries requiring EXACT term matching + semantic understanding. "
                    "Best for: finding specific equations, algorithms, technical terms, "
                    "author names, citations. "
                    "Example queries: 'Find mentions of BERT', 'Show all equations', "
                    "'References to ResNet'"
                )
            )
            
            self.tools = [vector_tool, summary_tool, analysis_tool, comparison_tool, hybrid_tool]
            return self.tools
        except Exception as e:
            print(f"Error creating tools: {e}")
            return []
    
    def _compare_papers(self, query: str) -> str:
        """Compare information across multiple papers"""
        try:
            # Get all papers
            paper_ids = vector_store_service.get_papers_list()
            
            if len(paper_ids) < 2:
                return "Need at least 2 papers for comparison. Please upload more papers."
            
            # Get embeddings for query
            from services.llm_service import llm_service
            query_embedding = llm_service.get_embeddings([query])[0]
            
            # Search each paper
            results_by_paper = {}
            for paper_id in paper_ids:
                results = vector_store_service.search_by_paper(
                    query_vector=query_embedding,
                    paper_ids=[paper_id],
                    top_k=3
                )
                if results:
                    results_by_paper[paper_id] = results
            
            # Format comparison
            comparison_text = f"Cross-paper analysis for: {query}\n\n"
            for paper_id, results in results_by_paper.items():
                comparison_text += f"Paper: {paper_id}\n"
                comparison_text += f"Key findings:\n"
                for i, r in enumerate(results[:2], 1):
                    comparison_text += f"{i}. {r['text'][:200]}...\n"
                comparison_text += "\n"
            
            # Generate synthesis
            synthesis_prompt = f"""Based on these findings from multiple papers:

{comparison_text}

Provide a comparative analysis that:
1. Highlights key similarities
2. Points out important differences
3. Synthesizes insights across papers

Keep it concise (3-4 paragraphs)."""

            synthesis = llm_service.generate_response(synthesis_prompt)
            
            return f"{comparison_text}\n=== SYNTHESIS ===\n{synthesis}"
            
        except Exception as e:
            return f"Comparison error: {str(e)}"
    
    def _hybrid_search(self, query: str) -> str:
        """Perform hybrid semantic + keyword search"""
        try:
            # Get semantic results
            from services.llm_service import llm_service
            query_embedding = llm_service.get_embeddings([query])[0]
            semantic_results = vector_store_service.search_all_papers(
                query_vector=query_embedding,
                top_k=10
            )
            
            # Get keyword results (if papers indexed)
            paper_ids = vector_store_service.get_papers_list()
            keyword_results = []
            for paper_id in paper_ids:
                kw_res = hybrid_search_service.keyword_search(
                    paper_id=paper_id,
                    query=query,
                    top_k=5
                )
                keyword_results.extend(kw_res)
            
            # Merge results
            merged = hybrid_search_service.merge_results(
                semantic_results=semantic_results,
                keyword_results=keyword_results,
                alpha=0.6  # 60% semantic, 40% keyword
            )
            
            # Format results
            output = f"Hybrid search results for: {query}\n\n"
            for i, r in enumerate(merged[:5], 1):
                output += f"{i}. [Score: {r.get('hybrid_score', 0):.3f}]\n"
                output += f"{r.get('text', '')[:300]}...\n\n"
            
            return output
            
        except Exception as e:
            return f"Hybrid search error: {str(e)}"

rag_tools = RAGTools()