import json
import gzip
import sys

def explore_amazon(filepath: str, n: int = 3):
    """Explores Amazon Reviews dataset structure."""
    print("\n=== AMAZON REVIEWS (Task A) ===")
    count = 0
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        for line in f:
            if count >= n:
                break
            record = json.loads(line)
            print(f"\nRecord {count + 1}:")
            for key, value in record.items():
                print(f"  {key}: {str(value)[:100]}")
            count += 1
    print(f"\n✅ Showed {count} records")


def explore_yelp(filepath: str, n: int = 3):
    """Explores Yelp Reviews dataset structure."""
    print("\n=== YELP REVIEWS (Task B) ===")
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if count >= n:
                break
            record = json.loads(line)
            print(f"\nRecord {count + 1}:")
            for key, value in record.items():
                print(f"  {key}: {str(value)[:100]}")
            count += 1
    print(f"\n✅ Showed {count} records")


if __name__ == "__main__":
    explore_amazon("task_a/data/Digital_Music_5.json.gz")
    explore_yelp("task_b/data/reviews_sample.jsonl")