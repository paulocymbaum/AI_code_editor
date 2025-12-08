"""
Memory Management System
Handles multi-tier memory (Redis, ChromaDB, PostgreSQL)
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class MemoryEntry:
    """Single memory entry"""
    key: str
    content: str
    metadata: Dict[str, Any]
    timestamp: float
    ttl: Optional[int] = None


class ShortTermMemory:
    """Redis-based short-term memory"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.local_cache = {}  # Fallback if Redis not available
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Store value with TTL"""
        if self.redis:
            await self.redis.setex(key, ttl, json.dumps(value))
        else:
            self.local_cache[key] = value
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value"""
        if self.redis:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        else:
            return self.local_cache.get(key)
    
    async def delete(self, key: str):
        """Delete value"""
        if self.redis:
            await self.redis.delete(key)
        else:
            self.local_cache.pop(key, None)


class VectorMemory:
    """ChromaDB-based vector memory for semantic search"""
    
    def __init__(self, chroma_client=None, collection_name: str = "code_memory"):
        self.client = chroma_client
        self.collection_name = collection_name
        self.collection = None
        
        if self.client:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Code embeddings for semantic search"}
            )
    
    async def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to vector store"""
        if not self.collection:
            return
        
        # Generate IDs
        ids = [hashlib.md5(doc.encode()).hexdigest() for doc in documents]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Semantic search"""
        if not self.collection:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        return [
            {
                "document": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]


class LongTermMemory:
    """PostgreSQL-based long-term storage"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
    
    async def store_session(self, session_id: str, data: Dict[str, Any]):
        """Store session data"""
        if not self.db:
            return
        
        # Simplified - would use SQLAlchemy models in production
        query = """
        INSERT INTO sessions (session_id, data, created_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (session_id) DO UPDATE SET data = $2, updated_at = NOW()
        """
        await self.db.execute(query, session_id, json.dumps(data))
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        if not self.db:
            return None
        
        query = "SELECT data FROM sessions WHERE session_id = $1"
        result = await self.db.fetchrow(query, session_id)
        
        return json.loads(result['data']) if result else None


class MemoryManager:
    """Unified memory management"""
    
    def __init__(
        self,
        redis_client=None,
        chroma_client=None,
        db_connection=None
    ):
        self.short_term = ShortTermMemory(redis_client)
        self.vector = VectorMemory(chroma_client)
        self.long_term = LongTermMemory(db_connection)
    
    async def store_conversation(
        self,
        session_id: str,
        messages: List[Dict[str, Any]],
        ttl: int = 86400  # 24 hours
    ):
        """Store conversation in short-term memory"""
        await self.short_term.set(f"conversation:{session_id}", messages, ttl)
    
    async def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation"""
        return await self.short_term.get(f"conversation:{session_id}") or []
    
    async def index_code(self, file_path: str, content: str, metadata: Dict[str, Any]):
        """Index code for semantic search"""
        await self.vector.add_documents(
            documents=[content],
            metadatas=[{**metadata, "file_path": file_path}]
        )
    
    async def search_code(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search code semantically"""
        return await self.vector.search(query, top_k)
    
    async def save_session(self, session_id: str, data: Dict[str, Any]):
        """Save session to long-term storage"""
        await self.long_term.store_session(session_id, data)
    
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session from long-term storage"""
        return await self.long_term.get_session(session_id)
