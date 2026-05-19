import os
from dotenv import load_dotenv

load_dotenv()

# LLM Providers
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Vector DB
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "task-b-recommend")

# Database
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Datasets
YELP_DATASET_PATH = os.getenv("YELP_DATASET_PATH", "data/reviews_enriched_price.jsonl")
GOODREADS_DATASET_PATH = os.getenv("GOODREADS_DATASET_PATH", "data/goodreads_reviews.json")

HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET_REPO = os.getenv("HF_DATASET_REPO")
