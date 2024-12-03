from typing import Dict, List, Any, Optional
import numpy as np
from openai import OpenAI
import json
import faiss
from dataclasses import dataclass
from pathlib import Path
import logging
import pickle
import shutil
import os
from datetime import datetime

@dataclass
class EmbeddingDocument:
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

class RAGHandler:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.index: Optional[faiss.IndexFlatL2] = None
        self.documents: List[EmbeddingDocument] = []
        self.embedding_dim = 1536
        self.logger = logging.getLogger(__name__)
        self.storage_dir = Path("rag_processing/storage")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.active_index: Optional[str] = None
        
        # Try to load last active index
        self._load_last_active()
    
    def _get_storage_path(self, name: str) -> Path:
        """Get storage path for a given index name"""
        return self.storage_dir / name
    
    def _save_index(self, name: str) -> None:
        """Save current index and documents"""
        if not self.index or not self.documents:
            raise ValueError("No index or documents to save")
            
        storage_path = self._get_storage_path(name)
        storage_path.mkdir(exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(storage_path / "index.faiss"))
        
        # Save documents without embeddings
        docs_for_storage = []
        for doc in self.documents:
            doc_dict = {
                'text': doc.text,
                'metadata': doc.metadata
            }
            docs_for_storage.append(doc_dict)
            
        with open(storage_path / "documents.pkl", "wb") as f:
            pickle.dump(docs_for_storage, f)
            
        # Save metadata
        metadata = {
            'created_at': datetime.now().isoformat(),
            'document_count': len(self.documents),
            'embedding_dim': self.embedding_dim
        }
        with open(storage_path / "metadata.json", "w") as f:
            json.dump(metadata, f)
            
        # Mark as last active
        self._mark_as_active(name)
    
    def _load_index(self, name: str) -> None:
        """Load index and documents from storage"""
        storage_path = self._get_storage_path(name)
        
        if not storage_path.exists():
            raise ValueError(f"No index found with name: {name}")
            
        # Load FAISS index
        self.index = faiss.read_index(str(storage_path / "index.faiss"))
        
        # Load documents
        with open(storage_path / "documents.pkl", "rb") as f:
            docs_data = pickle.load(f)
            
        self.documents = []
        for doc_dict in docs_data:
            doc = EmbeddingDocument(
                text=doc_dict['text'],
                metadata=doc_dict['metadata']
            )
            self.documents.append(doc)
            
        self._mark_as_active(name)
    
    def _mark_as_active(self, name: str) -> None:
        """Mark an index as the last active one"""
        with open(self.storage_dir / "last_active.txt", "w") as f:
            f.write(name)
        self.active_index = name
    
    def _load_last_active(self) -> None:
        """Load the last active index if it exists"""
        try:
            with open(self.storage_dir / "last_active.txt", "r") as f:
                last_active = f.read().strip()
            if last_active:
                self._load_index(last_active)
        except FileNotFoundError:
            pass
    
    def get_available_indices(self) -> List[Dict[str, Any]]:
        """Get list of available indices with metadata"""
        indices = []
        for path in self.storage_dir.iterdir():
            if path.is_dir():
                try:
                    with open(path / "metadata.json", "r") as f:
                        metadata = json.load(f)
                    indices.append({
                        'name': path.name,
                        'created_at': metadata['created_at'],
                        'document_count': metadata['document_count']
                    })
                except Exception as e:
                    self.logger.error(f"Error loading metadata for {path.name}: {e}")
        return indices
    
    def delete_index(self, name: str) -> None:
        """Delete an index from storage"""
        storage_path = self._get_storage_path(name)
        if storage_path.exists():
            shutil.rmtree(storage_path)
            
        # If this was the active index, clear current state
        if self.active_index == name:
            self.index = None
            self.documents = []
            self.active_index = None
            
            # Remove last_active marker if it exists
            try:
                os.remove(self.storage_dir / "last_active.txt")
            except FileNotFoundError:
                pass
    
    async def process_jsonl_file(self, file_path: str, index_name: str) -> None:
        """Process JSONL file and create embeddings"""
        documents = []
        
        with open(file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                messages = data.get('messages', [])
                
                user_msg = next((msg['content'] for msg in messages 
                               if msg['role'] == 'user'), '')
                assistant_msg = next((msg['content'] for msg in messages 
                                   if msg['role'] == 'assistant'), '')
                
                doc = EmbeddingDocument(
                    text=f"Question: {user_msg}\nAnswer: {assistant_msg}",
                    metadata={
                        'question': user_msg,
                        'answer': assistant_msg,
                        'source': data.get('source', ''),
                        'category': data.get('category', '')
                    }
                )
                documents.append(doc)
        
        await self._create_embeddings(documents)
        self._save_index(index_name)
    
    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            self.logger.error(f"Error getting embedding: {str(e)}", exc_info=True)
            raise
    
    async def _create_embeddings(self, documents: List[EmbeddingDocument]) -> None:
        """Create embeddings for documents using OpenAI API"""
        if not documents:
            self.logger.warning("No documents to process")
            return
            
        embeddings = []
        
        for doc in documents:
            doc.embedding = await self._get_embedding(doc.text)
            embeddings.append(doc.embedding)
            
        # Stack embeddings into a single numpy array
        embeddings_array = np.vstack(embeddings)
        
        # Create or update FAISS index
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            
        # Add vectors to the index
        self.index.add(embeddings_array)
        self.documents.extend(documents)
    
    async def get_relevant_docs(self, query: str, top_k: int = 5):
        """Get relevant documents for a query"""
        try:
            self.logger.info(f"Getting relevant documents for query: {query}")
            if not self.index:
                self.logger.warning("No index loaded")
                return []
            
            # Get document embeddings
            query_embedding = await self._get_embedding(query)
            
            # Search for similar documents using FAISS
            distances, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
            
            # Get the documents
            docs = [self.documents[i] for i in indices[0]]
            self.logger.info(f"Found {len(docs)} relevant documents")
            return docs
            
        except Exception as e:
            self.logger.error(f"Error getting relevant documents: {str(e)}", exc_info=True)
            return []
    
    async def get_relevant_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Alias for get_relevant_docs with dict formatting"""
        try:
            docs = await self.get_relevant_docs(query, top_k)
            return [
                {
                    "metadata": doc.metadata,
                    "content": doc.text
                }
                for doc in docs
            ]
        except Exception as e:
            self.logger.error(f"Error getting relevant context: {str(e)}", exc_info=True)
            return []
    
    def get_active_index(self) -> Optional[str]:
        """Get the name of the currently active index"""
        try:
            with open(self.storage_dir / "last_active.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None