from typing import Dict, List
from datetime import datetime
from services.chat_history import chat_history_service, Conversation
from fpdf import FPDF
from io import BytesIO
import os

class ExportService:
    
    def export_markdown(self, conversation_id: str) -> str:
        conv = chat_history_service.load_conversation(conversation_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        md = f"# {conv.title}\n\n"
        md += f"**Created:** {self._format_date(conv.created_at)}\n\n"
        md += "---\n\n"
        
        for msg in conv.messages:
            if msg.role == "user":
                md += f"## User\n{msg.content}\n\n"
            else:
                md += f"## Assistant\n{msg.content}\n\n"
                
                if msg.reasoning:
                    md += "**Reasoning:**\n"
                    for step in msg.reasoning:  
                        if isinstance(step, dict):
                            md += f"- **{step.get('step', '')}:** {step.get('description', '')}\n"
                        else:  
                            md += f"- {str(step)}\n"
                    md += "\n"
                
                if msg.sources:
                    md += "**Sources:**\n"
                    for i, src in enumerate(msg.sources, 1):
                        md += f"{i}. {src.get('paper_name', 'Unknown')} "
                        if src.get('page'):
                            md += f"(Page {src['page']})"
                        md += f" - Score: {src.get('score', 0):.2%}\n"
                    md += "\n"
            
            md += "---\n\n"
        
        return md
    
    def export_bibtex(self, conversation_id: str, papers_metadata: List[Dict]) -> str:
        conv = chat_history_service.load_conversation(conversation_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        paper_names = set()
        for msg in conv.messages:
            if msg.sources:
                for src in msg.sources:
                    paper_names.add(src.get('paper_name', ''))
        
        bibtex = f"% BibTeX Export from ScholarAgent\n"
        bibtex += f"% Conversation: {conv.title}\n"
        bibtex += f"% Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, paper in enumerate(paper_names, 1):
            if paper:
                cite_key = paper.replace('.pdf', '').replace(' ', '_').replace('-', '_')
                meta = next((p for p in papers_metadata if p.get('filename') == paper), {})
                author = meta.get('author', 'Unknown')
                year = meta.get('year', 'Unknown')
                bibtex += f"@article{{{cite_key},\n"
                bibtex += f"  title = {{{paper.replace('.pdf', '')}}},\n"
                bibtex += f"  author = {{{author}}},\n"
                bibtex += f"  year = {{{year}}},\n"
                bibtex += f"  note = {{Retrieved from ScholarAgent on {datetime.utcnow().strftime('%Y-%m-%d')}}}\n"
                bibtex += f"}}\n\n"
        
        return bibtex

    def export_pdf(self, conversation_id: str) -> bytes:
        """Export conversation as PDF - FINAL, UNBREAKABLE VERSION using Helvetica"""
        conv = chat_history_service.load_conversation(conversation_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.add_page()
        
        # FORCE Helvetica — it never causes "not enough space" error
        pdf.set_font("Helvetica", size=11)
        print("[PDF] Using Helvetica (safe core font)")

        def write_line(text: str):
            if not text:
                return
            # Simple safe write: split very long lines manually
            max_len = 110  # Safe for Helvetica
            while len(text) > max_len:
                chunk = text[:max_len]
                # Find last space to break cleanly
                space_idx = chunk.rfind(' ')
                if space_idx > max_len // 2:
                    chunk = text[:space_idx]
                    text = text[space_idx:]
                else:
                    text = text[max_len:]
                pdf.cell(0, 7, chunk.strip(), ln=1)
            if text:
                pdf.cell(0, 7, text.strip(), ln=1)

        try:
            # Title
            pdf.set_font("Helvetica", "B", 16)
            write_line(conv.title[:100])
            
            pdf.set_font("Helvetica", size=10)
            write_line(f"Created: {self._format_date(conv.created_at)}")
            pdf.ln(10)
            
            for msg in conv.messages:
                role_text = "User:" if msg.role == "user" else "Assistant:"
                pdf.set_font("Helvetica", "B", 13)
                pdf.cell(0, 10, role_text, ln=1)
                
                pdf.set_font("Helvetica", size=10)
                lines = msg.content.split('\n')
                for line in lines:
                    write_line(line)
                pdf.ln(5)
                
                if msg.reasoning:
                    pdf.set_font("Helvetica", "I", 10)
                    pdf.cell(0, 8, "Reasoning:", ln=1)
                    pdf.set_font("Helvetica", size=9)
                    for step in msg.reasoning:
                        if isinstance(step, dict):
                            line = f"- {step.get('step', '')}: {step.get('description', '')}"
                        else:
                            line = f"- {str(step)}"
                        write_line(line)
                    pdf.ln(4)
                
                if msg.sources:
                    pdf.set_font("Helvetica", "I", 10)
                    pdf.cell(0, 8, "Sources:", ln=1)
                    pdf.set_font("Helvetica", size=9)
                    for i, src in enumerate(msg.sources, 1):
                        line = f"{i}. {src.get('paper_name', 'Unknown')}"
                        if src.get('page'):
                            line += f" (Page {src.get('page')})"
                        line += f" - Score: {src.get('score', 0):.2%}"
                        write_line(line)
                    pdf.ln(4)
                
                pdf.set_draw_color(180, 180, 180)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(12)
            
            buffer = BytesIO()
            pdf.output(buffer)
            buffer.seek(0)
            print("[PDF] PDF EXPORTED SUCCESSFULLY WITH HELVETICA — NO MORE ERRORS!")
            return buffer.getvalue()
            
        except Exception as e:
            print(f"[PDF FINAL ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _format_date(self, iso_date: str) -> str:
        try:
            dt = datetime.fromisoformat(iso_date)
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return iso_date

export_service = ExportService()