import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from groq import Groq
from supabase import create_client
from config import GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY, YELP_DATASET_PATH

client = Groq(api_key=GROQ_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def load_user_reviews(user_id: str) -> list[dict]:
    """Loads all reviews for a user from the dataset."""
    reviews = []
    try:
        with open(YELP_DATASET_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if record.get("user_id") == user_id:
                    reviews.append({
                        "business_id": record.get("business_id"),
                        "name": record.get("name", ""),
                        "rating": record.get("user_rating"),
                        "text": record.get("text", ""),
                        "categories": record.get("categories", ""),
                        "city": record.get("city", ""),
                        "state": record.get("state", ""),
                        "price_range": record.get("price_range", "")
                    })
    except Exception as e:
        print(f"❌ Error loading reviews: {e}")
    return reviews


def get_sample_users(n: int = 8) -> list[str]:
    """Gets random quality users from the dataset."""
    import random
    user_counts = {}
    try:
        with open(YELP_DATASET_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                uid = record.get("user_id")
                text = record.get("text", "")
                if uid and len(text) >= 50:
                    user_counts[uid] = user_counts.get(uid, 0) + 1
        quality_users = [uid for uid, count in user_counts.items() if count >= 3]
        sample = random.sample(quality_users, min(n, len(quality_users)))
        print(f"✅ {len(quality_users)} quality users available, returning {len(sample)}")
        return sample
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return []


def build_user_profile(user_id: str, reviews: list[dict]) -> dict:
    """Extracts user preferences from review history using LLM."""
    if not reviews:
        return {}

    reviews_text = "\n".join([
        f"Business: {r['name']} | Categories: {r['categories']} | "
        f"City: {r['city']} | Price: {r['price_range']} | "
        f"Rating: {r['rating']}/5 | Review: {r['text'][:150]}"
        for r in reviews[:20]
    ])

    avg_rating = sum(r['rating'] for r in reviews if r.get('rating')) / max(len(reviews), 1)

    prompt = f"""
Analyze these Yelp reviews written by the same user and extract their preferences.

Reviews:
{reviews_text}

Respond in exact JSON format with no extra text:
{{
    "favorite_categories": "comma separated list of business types they love",
    "disliked_categories": "comma separated list of business types they rate poorly",
    "price_preference": "one of: budget, moderate, expensive, luxury",
    "preferred_cities": "comma separated list of cities they visit most",
    "dining_style": "one of: casual, fine dining, fast food, mixed",
    "avg_rating_given": {round(avg_rating, 1)},
    "personality": "2 sentence description of this reviewer's taste and style",
    "search_query": "a natural language search query representing what this user would enjoy next"
}}
"""

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip().replace("```", "").strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end != 0:
            content = content[start:end]
        profile = json.loads(content)
        profile["user_id"] = user_id
        profile["review_count"] = len(reviews)
        return profile
    except Exception as e:
        print(f"❌ Profile building error: {e}")
        return {}


def build_cold_start_profile(conversation: list[dict]) -> dict:
    """Builds a profile from conversation for cold-start users."""
    convo_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation
    ])

    prompt = f"""
Extract user preferences from this conversation to build a recommendation profile.

Conversation:
{convo_text}

Respond in exact JSON format with no extra text:
{{
    "favorite_categories": "what they want",
    "price_preference": "one of: budget, moderate, expensive, luxury",
    "preferred_cities": "location if mentioned",
    "dining_style": "one of: casual, fine dining, fast food, mixed",
    "personality": "brief description of what they're looking for",
    "search_query": "natural language search query for Pinecone"
}}
"""

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip().replace("```", "").strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end != 0:
            content = content[start:end]
        return json.loads(content)
    except Exception as e:
        print(f"❌ Cold start profile error: {e}")
        return {}


def save_user_profile(profile: dict) -> bool:
    """Saves user profile to Supabase."""
    try:
        supabase.table("task_b_users").upsert({
            "id": profile.get("user_id"),
            "interaction_count": profile.get("review_count", 0),
            "preferred_categories": profile.get("favorite_categories", ""),
            "price_preference": profile.get("price_preference", ""),
            "location": profile.get("preferred_cities", ""),
            "domain": "yelp"
        }).execute()
        print(f"✅ Profile saved for: {profile.get('user_id')}")
        return True
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False


def get_or_build_profile(user_id: str) -> dict:
    """Gets existing profile or builds from dataset."""
    result = supabase.table("task_b_users").select("*").eq("id", user_id).execute()
    if result.data:
        print(f"✅ Found existing profile for: {user_id}")
        return result.data[0]

    print(f"🔍 Building profile for: {user_id}")
    reviews = load_user_reviews(user_id)
    if not reviews:
        print(f"⚠️ No reviews found — cold start mode")
        return {"user_id": user_id, "cold_start": True}

    profile = build_user_profile(user_id, reviews)
    if profile:
        save_user_profile(profile)
    return profile
