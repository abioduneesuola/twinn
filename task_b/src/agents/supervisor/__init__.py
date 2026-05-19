import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from groq import Groq
from supabase import create_client
from config import GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY
from src.agents.user_modeling import get_or_build_profile, build_cold_start_profile
from src.agents.retrieval import retrieve_for_user
from src.agents.ranking import rank_with_context
from src.agents.engagement import (
    generate_conversation_response,
    format_recommendations,
    should_recommend
)

client = Groq(api_key=GROQ_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def log_recommendation(user_id: str, recommendations: list[dict], session_id: str):
    """Logs recommendations to Supabase."""
    try:
        for rec in recommendations:
            supabase.table("task_b_recommendations").insert({
                "user_id": user_id,
                "item_id": rec.get("business_id", ""),
                "item_name": rec.get("name", ""),
                "rank": rec.get("rank", 0),
                "score": rec.get("score", 0),
                "reason": rec.get("reason", ""),
                "domain": "yelp",
                "is_cold_start": False
            }).execute()
    except Exception as e:
        print(f"❌ Logging error: {e}")


def process_message(
    user_id: str,
    message: str,
    conversation: list[dict],
    session_id: str
) -> dict:
    """
    Main Task B supervisor pipeline.
    Handles conversation, retrieval, ranking, and response generation.
    """
    print(f"\n💬 Processing message for user: {user_id}")

    # Add user message to conversation
    conversation.append({"role": "user", "content": message})

    # Get or build user profile
    profile = get_or_build_profile(user_id)
    is_cold_start = profile.get("cold_start", False)

    reasoning_trace = []

    # Decide whether to recommend or converse
    if should_recommend(conversation) or len(conversation) >= 4:

        reasoning_trace.append("🔍 Analyzing user preferences...")

        # For cold start, build profile from conversation
        if is_cold_start:
            reasoning_trace.append("❄️ Cold start detected — building profile from conversation...")
            profile = build_cold_start_profile(conversation)

        reasoning_trace.append(f"👤 Profile: {profile.get('favorite_categories', 'unknown')} | {profile.get('price_preference', 'moderate')}")

        # Retrieve candidates
        reasoning_trace.append("🔎 Searching knowledge base...")
        candidates, retrieval_reasoning = retrieve_for_user(profile, top_k=15)
        reasoning_trace.append(f"📦 Found {len(candidates)} candidates")
        reasoning_trace.append(f"💭 {retrieval_reasoning}")

        if not candidates:
            response = "I couldn't find matches right now — my search timed out. Please try again!"
            return {
                "response": response,
                "reasoning_trace": reasoning_trace,
                "recommendations": [],
                "agent_used": "retrieval_failed"
            }

        # Rank candidates
        reasoning_trace.append("🧠 Reasoning about best matches...")
        ranking_result = rank_with_context(profile, candidates, conversation)
        recommendations = ranking_result.get("recommendations", [])
        reasoning_trace.append(f"💡 Agent reasoning: {ranking_result.get('reasoning', '')}")

        # Format response
        response = format_recommendations(recommendations)

        # Log to Supabase
        log_recommendation(user_id, recommendations, session_id)

        return {
            "response": response,
            "reasoning_trace": reasoning_trace,
            "recommendations": recommendations,
            "agent_used": "full_pipeline",
            "profile": profile
        }

    else:
        # Continue conversation
        reasoning_trace.append("💬 Gathering more context through conversation...")
        response = generate_conversation_response(profile, conversation, is_cold_start)

        return {
            "response": response,
            "reasoning_trace": reasoning_trace,
            "recommendations": [],
            "agent_used": "conversation",
            "profile": profile
        }


# NOTE: This is the central coordinator for Task B. It receives every
# user message, decides whether to converse or recommend, orchestrates
# the retrieval and ranking pipeline, maintains reasoning traces for
# display, and logs all recommendations to Supabase. It also handles cold-start users by building profiles from conversation.