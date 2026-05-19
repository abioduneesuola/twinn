import json
import os
import sys
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config import (
    PINECONE_API_KEY, PINECONE_INDEX_NAME,
    YELP_DATASET_PATH,
    YELP_REVIEW_PATH   # <-- ADD THIS in config
)

LOCAL_MODEL_PATH = r"C:\Users\USER\Desktop\HACKATHON\all-MiniLM-L6-v2"

model = SentenceTransformer(LOCAL_MODEL_PATH)
pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(PINECONE_INDEX_NAME)


# ---------------------------
# Load Businesses
# ---------------------------
def load_businesses(filepath):
    businesses = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            bid = r.get("business_id")

            if bid and bid not in businesses:
                businesses[bid] = {
                    "business_id": bid,
                    "name": r.get("name", ""),
                    "categories": r.get("categories", ""),
                    "city": r.get("city", ""),
                    "state": r.get("state", ""),
                    "price_range": r.get("price_range", "")
                }

    return businesses


# ---------------------------
# Load Reviews grouped by business
# ---------------------------
def load_reviews_grouped(filepath):
    reviews_by_business = defaultdict(list)

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)

            bid = r.get("business_id")
            text = r.get("text", "")
            stars = r.get("stars", 0)

            if bid and text:
                reviews_by_business[bid].append({
                    "text": text,
                    "stars": stars
                })

    return reviews_by_business


# ---------------------------
# Build weighted review summary
# ---------------------------
def build_weighted_review_text(reviews, top_k=30):
    """
    Converts reviews into weighted text summary.
    Higher star reviews contribute more.
    """

    if not reviews:
        return ""

    # sort by stars (high first)
    reviews_sorted = sorted(reviews, key=lambda x: x["stars"], reverse=True)

    selected = reviews_sorted[:top_k]

    weighted_text_parts = []

    for r in selected:
        weight = r["stars"] / 5.0  # normalize 0–1
        boosted_text = (r["text"] + " ") * int(max(1, weight * 2))

        weighted_text_parts.append(boosted_text)

    return " ".join(weighted_text_parts)


# ---------------------------
# Build embedding text per business
# ---------------------------
def build_business_text(b, review_text):
    return f"""
Name: {b['name']}
Categories: {b['categories']}
Location: {b['city']}, {b['state']}
Price: {b['price_range']}

Customer Reviews:
{review_text}
"""


# ---------------------------
# Embed + Push
# ---------------------------
def process_and_index(businesses, reviews_by_business):
    vectors = []

    for bid, b in businesses.items():

        review_text = build_weighted_review_text(
            reviews_by_business.get(bid, [])
        )

        final_text = build_business_text(b, review_text)

        emb = model.encode(final_text)

        vectors.append({
            "id": bid,
            "values": emb.tolist(),
            "metadata": {
                "name": b["name"],
                "categories": b["categories"],
                "city": b["city"],
                "state": b["state"],
                "price_range": b["price_range"]
            }
        })

    # batch upload
    batch_size = 50

    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors[i:i+batch_size])
        print(f"Pushed {min(i+batch_size, len(vectors))}/{len(vectors)}")

    print("Done.")


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":

    print("Loading data...")

    businesses = load_businesses(YELP_DATASET_PATH)
    reviews_by_business = load_reviews_grouped("your_review_dataset.json")

    print("Indexing with weighted reviews...")

    process_and_index(businesses, reviews_by_business)