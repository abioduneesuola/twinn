import sys
sys.path.append("task_a")

from src.agents.user_modeling import (
    get_sample_users,
    load_user_reviews,
    get_or_build_profile
)

# Get sample users from dataset
print("🔍 Getting sample users from dataset...")
users = get_sample_users(5)
print(f"✅ Sample users: {users}")

# Pick first user
test_user = users[0]
print(f"\n👤 Testing with user: {test_user}")

# Load their reviews
reviews = load_user_reviews(test_user)
print(f"✅ Found {len(reviews)} reviews")
for r in reviews[:2]:
    print(f"  Rating: {r['rating']} | {r['review_text'][:80]}")

# Build profile
print(f"\n🧠 Building profile...")
profile = get_or_build_profile(test_user)
print(f"\n📊 Profile:")
for key, val in profile.items():
    print(f"  {key}: {val}")