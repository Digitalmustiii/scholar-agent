# backend/services/llm_service.py
# Updated with lazy loading for embed_model

from groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq as GroqLLM
from llama_index.core import Settings
from config import settings
from typing import List

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self._embed_model = None  # Lazy load
        
        # Set global LLM to Groq (prevents OpenAI lookup)
        Settings.llm = GroqLLM(
            model=settings.llm_model,
            api_key=settings.groq_api_key
        )
    
    @property
    def embed_model(self):
        if self._embed_model is None:
            print("[LLM] Lazy loading embedding model...")
            self._embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        return self._embed_model
    
    def generate_response(self, prompt: str) -> str:
        """Generate text response using Groq"""
        try:
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text list"""
        try:
            embeddings = []
            for text in texts:
                embedding = self.embed_model.get_text_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            print(f"Embedding error: {e}")
            return [[0.0] * 384 for _ in texts]  # Return zero vectors on error
    
    def test_connection(self) -> bool:
        """Test if Groq API is accessible"""
        try:
            self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except:
            return False

# Do NOT instantiate globally - we'll handle in main.py