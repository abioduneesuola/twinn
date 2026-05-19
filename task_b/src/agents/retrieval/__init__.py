import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)

_model = None


def get_model():
    """Lazily loads the embedding model only when needed."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("📥 Loading embedding model...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("✅ Embedding model loaded")
    return _model


def get_index():
    return pc.Index(PINECONE_INDEX_NAME)


def embed_query(text: str) -> list[float]:
    """Embeds a search query using the same model as indexing."""
    return get_model().encode(text).tolist()


def retrieve_candidates(
    search_query: str,
    top_k: int = 20,
    filters: dict = None
) -> list[dict]:
    """
    Retrieves candidate businesses from Pinecone
    using semantic search on user's profile query.
    """
    try:
        query_embedding = embed_query(search_query)
        index = get_index()

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filters
        )

        candidates = []
        for match in results.matches:
            candidate = match.metadata.copy()
            candidate["score"] = round(match.score, 4)
            candidate["business_id"] = match.id
            candidates.append(candidate)

        print(f"✅ Retrieved {len(candidates)} candidates from Pinecone")
        return candidates

    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return []


def retrieve_for_user(profile: dict, top_k: int = 20) -> tuple[list[dict], str]:
    """
    Retrieves candidates based on user profile.
    Returns candidates and the reasoning behind the query.
    """
    search_query = profile.get("search_query", "")

    if not search_query:
        parts = []
        if profile.get("favorite_categories"):
            parts.append(profile["favorite_categories"])
        if profile.get("preferred_cities"):
            parts.append(profile["preferred_cities"])
        if profile.get("price_preference"):
            parts.append(profile["price_preference"])
        search_query = " ".join(parts) if parts else "popular local restaurants"

    reasoning = f"Searching for: '{search_query}' based on user's history of preferring {profile.get('favorite_categories', 'various categories')} in {profile.get('preferred_cities', 'their area')} at {profile.get('price_preference', 'moderate')} price range."

    print(f"🔍 Query: {search_query}")
    candidates = retrieve_candidates(search_query, top_k=top_k)
    return candidates, reasoning


# NOTE: This agent handles semantic search against the Pinecone business
# index. It converts the user's profile into a search query, embeds it
# using the same model used during indexing, and retrieves the most
# semantically similar businesses as candidates for ranking.
