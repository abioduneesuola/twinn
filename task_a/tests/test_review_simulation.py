import sys
sys.path.append("task_a")

from src.agents.user_modeling import get_sample_users, get_or_build_profile
from src.agents.review_simulation import get_unseen_products, simulate_multiple_reviews

# Get a test user
print("🔍 Getting test user...")
users = get_sample_users(3)
test_user = users[0]
print(f"✅ Test user: {test_user}")

# Get their profile
print(f"\n🧠 Loading profile...")
profile = get_or_build_profile(test_user)
print(f"✅ Profile loaded: {profile.get('tone')} | {profile.get('rating_pattern')}")

# Get unseen products
print(f"\n🛍️ Getting unseen products...")
products = get_unseen_products(test_user, n=3)
print(f"✅ Found {len(products)} unseen products")

# Simulate reviews
print(f"\n✍️ Simulating reviews...")
results = simulate_multiple_reviews(profile, products)

# Display results
print("\n--- SIMULATED REVIEWS ---")
for r in results:
    print(f"\nProduct: {r.get('product_id')}")
    print(f"Simulated Rating: {r.get('simulated_rating')} | Actual Rating: {r.get('actual_rating')}")
    print(f"Simulated Review: {r.get('simulated_review')[:150]}")
    print(f"Actual Review: {r.get('actual_review')[:150]}")
    print(f"Confidence: {r.get('confidence')}")