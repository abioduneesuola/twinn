import json
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

PRESENTATION_PROMPT = """
You are Twinn Review, an AI that presents simulated user reviews in a clean, 
professional, and easy to understand way.

Present the following review simulation result clearly.
Highlight the rating, the simulated review, and briefly note the confidence level.
Keep it concise and professional — this is a demo interface, not a chat.
Do not add unnecessary commentary.
"""


def present_simulation_result(result: dict) -> str:
    """Wraps simulation result in a clean presentation."""
    content = f"""
Review Simulation Result:
- Product ID: {result.get('product_id')}
- Simulated Rating: {result.get('simulated_rating')}/5
- Simulated Review: {result.get('simulated_review')}
- Confidence: {result.get('confidence')}
- Actual Rating (ground truth): {result.get('actual_rating')}/5
- Rating Difference: {abs(result.get('simulated_rating', 0) - result.get('actual_rating', 0)):.2f}
"""
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {"role": "system", "content": PRESENTATION_PROMPT},
                {"role": "user", "content": content}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Presentation error: {e}")
        return content


def present_multiple_results(results: list[dict]) -> list[str]:
    """Presents multiple simulation results."""
    presented = []
    for result in results:
        presented.append(present_simulation_result(result))
    return presented


def compute_metrics(results: list[dict]) -> dict:
    """Computes basic evaluation metrics."""
    if not results:
        return {}

    rating_errors = [
        abs(r.get("simulated_rating", 0) - r.get("actual_rating", 0))
        for r in results
        if r.get("simulated_rating") and r.get("actual_rating")
    ]

    rmse = (sum(e**2 for e in rating_errors) / len(rating_errors)) ** 0.5 if rating_errors else 0

    return {
        "total_reviews": len(results),
        "avg_rating_error": round(sum(rating_errors) / len(rating_errors), 3) if rating_errors else 0,
        "rmse": round(rmse, 3),
        "high_confidence": sum(1 for r in results if r.get("confidence") == "high")
    }
