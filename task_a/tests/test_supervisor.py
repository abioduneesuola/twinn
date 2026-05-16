import sys
sys.path.append("task_a")

from src.agents.user_modeling import get_sample_users
from src.agents.supervisor import run_task_a

# Get a sample user
users = get_sample_users(3)
test_user = users[0]
print(f"🧪 Testing with user: {test_user}")

# Run full Task A pipeline
result = run_task_a(test_user, n_products=3)

# Display
print("\n=== FINAL OUTPUT ===")
for i, review in enumerate(result.get("presented_reviews", []), 1):
    print(f"\n--- Review {i} ---")
    print(review)

print(f"\n📈 Metrics: {result.get('metrics')}")