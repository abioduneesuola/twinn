import gzip
import json
import pandas as pd

def load_amazon_to_df(filepath: str, max_records: int = 10000) -> pd.DataFrame:
    """Loads Amazon reviews dataset into a pandas DataFrame."""
    records = []
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= max_records:
                break
            records.append(json.loads(line))
    df = pd.DataFrame(records)
    return df


def inspect_df(df: pd.DataFrame):
    """Prints useful stats about the dataset."""
    print(f"📦 Total records: {len(df)}")
    print(f"\n📋 Columns: {list(df.columns)}")
    print(f"\n📊 Data types:\n{df.dtypes}")
    print(f"\n🔢 Null counts:\n{df.isnull().sum()}")
    print(f"\n⭐ Rating distribution:\n{df['overall'].value_counts().sort_index()}")
    print(f"\n👤 Unique users: {df['reviewerID'].nunique()}")
    print(f"\n🛍️ Unique products: {df['asin'].nunique()}")
    print(f"\n📝 Avg review length: {df['reviewText'].dropna().str.len().mean():.0f} chars")
    print(f"\n👥 Reviews per user:\n{df.groupby('reviewerID').size().describe()}")


def filter_quality_users(df: pd.DataFrame, min_reviews: int = 5, min_review_length: int = 50) -> pd.DataFrame:
    """Filters out low-signal users."""
    # Filter short reviews
    df = df[df['reviewText'].str.len() >= min_review_length]
    
    # Filter users with too few reviews
    user_counts = df.groupby('reviewerID').size()
    valid_users = user_counts[user_counts >= min_reviews].index
    df = df[df['reviewerID'].isin(valid_users)]
    
    print(f"✅ Quality users: {df['reviewerID'].nunique()}")
    print(f"✅ Quality reviews: {len(df)}")
    return df


if __name__ == "__main__":
    filepath = "task_a/data/Digital_Music_5.json.gz"
    
    print("🔍 Loading dataset...")
    df = load_amazon_to_df(filepath)
    
    print("\n=== RAW DATASET ===")
    inspect_df(df)
    
    print("\n=== AFTER QUALITY FILTER ===")
    df_filtered = filter_quality_users(df, min_reviews=5, min_review_length=50)
    inspect_df(df_filtered)
    
    print("\n📋 Sample rows:")
    print(df_filtered[['reviewerID', 'asin', 'overall', 'reviewText']].head(3).to_string())