import json
import sys
sys.path.append("task_a")

from src.agents.user_modeling import get_or_build_profile, load_user_reviews
from src.agents.review_simulation import get_unseen_products, simulate_multiple_reviews
from src.agents.engagement import present_multiple_results, compute_metrics


def run_task_a(user_id: str, n_products: int = 3) -> dict:
    """
    Main Task A pipeline.
    Takes a user ID, simulates reviews for unseen products.
    Returns simulated reviews + metrics.
    """
    print(f"\n🚀 Starting Task A pipeline for user: {user_id}")

    # Step 1: Build user profile
    print("\n📊 Step 1: Building user profile...")
    profile = get_or_build_profile(user_id)
    if not profile:
        return {"error": f"The reviews written by user: {user_id} are not rich enough in context, please select another user"}
    print(f"✅ Profile: {profile.get('tone')} | {profile.get('rating_pattern')}")

    # Step 2: Get unseen products
    print("\n🛍️ Step 2: Getting unseen products...")
    products = get_unseen_products(user_id, n=n_products)
    if not products:
        return {"error": "No unseen products found"}
    print(f"✅ Found {len(products)} unseen products")

    # Step 3: Simulate reviews
    print("\n✍️ Step 3: Simulating reviews...")
    results = simulate_multiple_reviews(profile, products)
    if not results:
        return {"error": "Review simulation failed"}

    # Step 4: Present results
    print("\n🎨 Step 4: Presenting results...")
    presented = present_multiple_results(results)

    # Step 5: Compute metrics
    metrics = compute_metrics(results)
    print(f"\n📈 Metrics: {metrics}")

    return {
        "user_id": user_id,
        "profile": profile,
        "simulated_reviews": results,
        "presented_reviews": presented,
        "metrics": metrics
    }


if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "A2TYZ821XXK2YZ"
    result = run_task_a(user_id)
    print("\n=== FINAL OUTPUT ===")
    for i, review in enumerate(result.get("presented_reviews", []), 1):
        print(f"\n--- Review {i} ---")
        print(review)
    print(f"\n📈 Final Metrics: {result.get('metrics')}")
