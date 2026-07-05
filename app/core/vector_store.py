
import json
import logging
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


_model: SentenceTransformer = None


_index: faiss.IndexFlatL2 = None


_events: list = []

EMBEDDING_DIM = 384  
def get_model() -> SentenceTransformer:

    global _model
    if _model is None:
        logger.info("⏳ Loading embedding model (first time only)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("✅ Embedding model loaded")
    return _model


def get_index() -> faiss.IndexFlatL2:
    """Get or create the FAISS index."""
    global _index
    if _index is None:
      
        _index = faiss.IndexFlatL2(EMBEDDING_DIM)
        logger.info("✅ FAISS index created")
    return _index


def event_to_text(event: dict) -> str:
   
    return (
        f"Event type: {event.get('type', 'unknown')}. "
        f"User: {event.get('email', 'system')}. "
        f"Role: {event.get('role', 'unknown')}. "
        f"Classification: {event.get('classification', 'info')}."
    )


async def store_event(event: dict):

    try:
        model = get_model()
        index = get_index()

      
        event["timestamp"] = event.get(
            "timestamp",
            datetime.now(timezone.utc).isoformat()
        )

  
        text = event_to_text(event)
        embedding = model.encode([text]) 

      
        embedding = np.array(embedding, dtype=np.float32)


        index.add(embedding)

        _events.append(event)

        logger.info(f"✅ Event stored in vector DB (total: {len(_events)})")

    except Exception as e:
        logger.error(f"Failed to store event in vector DB: {e}")


async def search_events(query: str, top_k: int = 5) -> list:

    try:
        model = get_model()
        index = get_index()

        if index.ntotal == 0:
            logger.warning("Vector DB is empty — no events stored yet")
            return []

     
        query_embedding = model.encode([query])
        query_embedding = np.array(query_embedding, dtype=np.float32)

        k = min(top_k, index.ntotal) 
        distances, indices = index.search(query_embedding, k)

        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(_events):
                results.append(_events[idx])

        logger.info(f"🔍 Found {len(results)} relevant events for query: '{query}'")
        return results

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []