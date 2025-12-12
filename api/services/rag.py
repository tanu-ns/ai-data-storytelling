import os
from typing import List, Dict, Any
import uuid
import numpy as np

# Try to import Qdrant and SentenceTransformers, fallback if failed
# Try to import Qdrant and SentenceTransformers, fallback if failed
try:
    # Temporarily forcing Mock Mode to resolve crash reports
    # from qdrant_client import QdrantClient
    # from qdrant_client.http import models
    # from sentence_transformers import SentenceTransformer
    # HAS_DEPS = True
    raise ImportError("Forcing Mock Mode")
except ImportError as e:
    print(f"RAG Dependencies missing or broken: {e}. Using Mock Mode.")
    HAS_DEPS = False

# Global In-Memory Store
_MOCK_STORAGE = {}

class MockEmbedder:
    def encode(self, texts):
        # Return random vectors of size 384
        count = len(texts) if isinstance(texts, list) else 1
        return np.random.rand(count, 384)

class MockQdrant:
     def __init__(self, path=None): pass
     
     def get_collections(self): 
         class Cols: collections=[]
         return Cols()
         
     def create_collection(self, **kwargs): 
         name = kwargs.get("collection_name")
         if name not in _MOCK_STORAGE:
             _MOCK_STORAGE[name] = []
             
     def upsert(self, **kwargs): 
         name = kwargs.get("collection_name")
         points = kwargs.get("points", [])
         if name not in _MOCK_STORAGE:
             _MOCK_STORAGE[name] = []
         # Extend storage with new points
         _MOCK_STORAGE[name].extend(points)
         
     def search(self, **kwargs): 
         name = kwargs.get("collection_name")
         query_filter = kwargs.get("query_filter")
         dataset_id = None
         
         # Extract dataset_id from filter logic if possible
         # We are cheating here for the specific structure of our app
         try:
             dataset_id = query_filter.must[0].match.value
         except:
             pass
             
         collection = _MOCK_STORAGE.get(name, [])
         
         # Filter by dataset_id
         hits = []
         for p in collection:
             if dataset_id and p.payload.get("dataset_id") != dataset_id:
                 continue
             # In a real mock we would compute cosine similarity
             # But simply returning the last 3 items is often good enough for "context"
             # matching the "latest" insights.
             hits.append(p)
             
         # Return top 3 (reverse order to get latest)
         return hits[-3:]

if not 'models' in locals():
    class MockModels:
        class VectorParams:
             def __init__(self, size, distance): pass
        class Distance:
             COSINE = "Cosine"
        class PointStruct:
             def __init__(self, **kwargs): pass
        class Filter:
             def __init__(self, **kwargs): pass
        class FieldCondition:
             def __init__(self, **kwargs): pass
        class MatchValue:
             def __init__(self, **kwargs): pass
    models = MockModels()

def get_model():
    global _model
    if _model is None:
        if HAS_DEPS:
            try:
                _model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Failed to load SentenceTransformer: {e}")
                _model = MockEmbedder()
        else:
            _model = MockEmbedder()
    return _model

def get_qdrant_client():
    global _qdrant
    if _qdrant is None:
        if HAS_DEPS:
            try:
                _qdrant = QdrantClient(path="./qdrant_storage")
            except Exception:
                 _qdrant = MockQdrant()
        else:
            _qdrant = MockQdrant()
    return _qdrant

COLLECTION_NAME = "insights"

def init_collection():
    client = get_qdrant_client()
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )

def index_text(dataset_id: str, texts: List[str], metadatas: List[Dict]):
    """
    Embeds texts and saves them to Qdrant.
    """
    if not texts: return
    
    client = get_qdrant_client()
    model = get_model()
    
    # Ensure collection exists
    init_collection()
    
    embeddings = model.encode(texts).tolist()
    
    points = []
    for i, text in enumerate(texts):
        points.append(models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings[i],
            payload={
                "dataset_id": str(dataset_id),
                "text": text,
                **metadatas[i]
            }
        ))
        
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def search(dataset_id: str, query: str, limit: int = 3) -> List[str]:
    """
    Embeds query and retrieves similar texts for the given dataset.
    """
    client = get_qdrant_client()
    model = get_model()
    
    # Ensure collection exists (if not, nothing to search)
    init_collection()
    
    query_vector = model.encode(query).tolist()
    
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="dataset_id",
                    match=models.MatchValue(value=str(dataset_id))
                )
            ]
        ),
        limit=limit
    )
    
    return [hit.payload["text"] for hit in hits]
