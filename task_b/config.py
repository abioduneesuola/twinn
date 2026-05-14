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
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "twinn-recommend")

# Database
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Datasets
YELP_DATASET_PATH = os.getenv("YELP_DATASET_PATH", "data/yelp_reviews.json")
GOODREADS_DATASET_PATH = os.getenv("GOODREADS_DATASET_PATH", "data/goodreads_reviews.json")