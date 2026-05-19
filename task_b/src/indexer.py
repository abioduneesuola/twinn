import json
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config import (
    PINECONE_API_KEY, PINECONE_INDEX_NAME,
    YELP_DATASET_PATH
)

LOCAL_MODEL_PATH = r"C:\Users\USER\Desktop\HACKATHON\all-MiniLM-L6-v2"
EMBEDDINGS_CACHE = "task_b/data/business_embeddings.npy"
BUSINESSES_CACHE = "task_b/data/businesses.json"

model = SentenceTransformer(LOCAL_MODEL_PATH)
pc = Pinecone(api_key=PINECONE_API_KEY)


def get_index():
    return pc.Index(PINECONE_INDEX_NAME)


def load_businesses(filepath: str) -> dict:
    """Loads unique businesses from the dataset."""
    businesses = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            bid = record.get("business_id")
            if bid and bid not in businesses:
                businesses[bid] = {
                    "business_id": bid,
                    "name": record.get("name", ""),
                    "categories": record.get("categories", ""),
                    "city": record.get("city", ""),
                    "state": record.get("state", ""),
                    "price_range": record.get("price_range", ""),
                }
    print(f"✅ Loaded {len(businesses)} unique businesses")
    return businesses


def compute_and_save_embeddings(businesses: dict) -> tuple:
    """Computes embeddings locally and saves to disk."""
    items = list(businesses.values())
    texts = [
        f"{b['name']} {b['categories']} {b['city']} {b['state']} {b['price_range']}"
        for b in items
    ]

    print(f"🔢 Computing embeddings for {len(texts)} businesses...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    # Save to disk
    np.save(EMBEDDINGS_CACHE, embeddings)
    with open(BUSINESSES_CACHE, 'w') as f:
        json.dump(items, f)

    print(f"✅ Embeddings saved to {EMBEDDINGS_CACHE}")
    print(f"✅ Businesses saved to {BUSINESSES_CACHE}")
    return items, embeddings


def push_to_pinecone(items: list, embeddings: np.ndarray, batch_size: int = 50):
    """Pushes precomputed embeddings to Pinecone."""
    index = get_index()
    total = len(items)
    stored = 0

    for i in range(0, total, batch_size):
        batch_items = items[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        vectors = []

        for b, emb in zip(batch_items, batch_embeddings):
            vectors.append({
                "id": b["business_id"],
                "values": emb.tolist(),
                "metadata": {
                    "name": b["name"],
                    "categories": b["categories"],
                    "city": b["city"],
                    "state": b["state"],
                    "price_range": b["price_range"]
                }
            })

        index.upsert(vectors=vectors)
        stored += len(vectors)
        print(f"📦 Pushed {stored}/{total} to Pinecone")

    print(f"\n✅ Done. {stored} businesses indexed in Pinecone.")
    return stored


if __name__ == "__main__":
    # Step 1: Load businesses
    print("🔍 Loading businesses...")
    businesses = load_businesses(YELP_DATASET_PATH)

    # Step 2: Compute and save embeddings locally
    if os.path.exists(EMBEDDINGS_CACHE) and os.path.exists(BUSINESSES_CACHE):
        print("✅ Found cached embeddings — loading from disk...")
        embeddings = np.load(EMBEDDINGS_CACHE)
        with open(BUSINESSES_CACHE, 'r') as f:
            items = json.load(f)
    else:
        items, embeddings = compute_and_save_embeddings(businesses)

    # Step 3: Push to Pinecone
    print("\n📥 Pushing to Pinecone...")
    push_to_pinecone(items, embeddings)