# Twinn

**AI agents that learn how your customers think — then act on it.**

- Twinn1: [mytwinn01.streamlit.app](https://mytwinn01.streamlit.app)
- Twinn2: [mytwinn02.streamlit.app](https://mytwinn02.streamlit.app)

---

## Overview

Twinn is a pair of LLM-powered agentic systems for modeling user behavior and generating personalized recommendations and content. Both systems are built in Python without relying on pre-built agent orchestration frameworks — every agent decision, tool call, and coordination step is written and controlled deliberately, giving full visibility into how each output is produced.

At its core, Twinn answers one question for any business with user data: **"What would this specific customer do, say, or want next?"**

---

## Why This Matters for Businesses

Most personalization tools rely on shallow rules (e.g. "users who bought X also bought Y"). Twinn instead builds a behavioral profile of each user — tone, preferences, rating patterns, price sensitivity, location habits — and uses that profile to drive two kinds of decisions:

- **Predict how a customer will react** to a new product, message, or experience before it's launched
- **Recommend the right thing** to a customer, including for brand-new users with no history

Practical applications include:

- **Pre-launch testing** — simulate customer reviews/ratings for a new product before it ships, to catch issues early
- **Personalized recommendations** — power a "for you" experience using semantic search instead of rigid categories
- **Cold-start onboarding** — generate useful recommendations for new users through a short conversation instead of waiting for purchase history
- **Customer voice modeling** — understand how different customer segments talk about and rate your products
- **Localized engagement** — tailor responses to a specific market's tone and language (the reference implementation uses Nigerian Pidgin as an example)

---

## Module A — Behavior Simulation Agent

### What it does

Given a user ID and a product (or description), the system:

1. Loads that user's review history
2. Builds a behavioral profile (tone, vocabulary, rating patterns)
3. Simulates what that user would write about an unseen product
4. Returns a predicted rating + written review in the user's own voice

### Architecture

```
User ID + Product Details
        ↓
Supervisor Agent
        ↓
User Modeling Agent → builds behavioral profile from review history
        ↓
Review Simulation Agent → generates review in user's voice
        ↓
Engagement Agent → presents results + computes accuracy metrics
        ↓
Output: Simulated Rating + Review
```

### Reference Dataset

- Amazon Digital Music Reviews (5-core subset)
- Source: [UCSD Recommender Systems Datasets](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/)

### Running Locally

```bash
cd task_a
pip install -r requirements.txt

# Set environment variables in .env
# Required: GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY, PINECONE_API_KEY
# Dataset: place Digital_Music_5.json.gz in task_a/data/

uvicorn main:app --host 0.0.0.0 --port 8001
streamlit run app.py
```

### API Endpoints

- `POST /simulate` — simulate a review for a user
- `GET /sample-users` — get random quality user IDs
- `GET /search-product?description=` — find a product by text description
- `GET /user/{user_id}` — get a user's behavioral profile

---

## Module B — Recommendation Agent

### What it does

Given a user ID (including cold-start users with no history), the system:

1. Loads the user's review/interaction history
2. Builds a preference profile (categories, price, location, style)
3. Conducts a multi-turn conversation to refine context
4. Semantically searches a vector index of 33,000+ businesses/products
5. Re-ranks candidates using LLM reasoning
6. Returns the top 5 recommendations with personalized explanations

### Architecture

```
User ID + Conversation
        ↓
Supervisor Agent
        ↓
User Modeling Agent → builds preference profile
        ↓
Retrieval Agent → semantic search via Pinecone (sentence-transformers)
        ↓
Ranking Agent → LLM re-ranks with explicit reasoning trace
        ↓
Engagement Agent → localized conversational response
        ↓
Output: Ranked Recommendations + Reasoning Trace
```

### Key Features

- **Cold-start handling** — builds a profile from conversation when no history exists
- **Multi-turn** — refines recommendations based on follow-up messages
- **Reasoning trace** — the agent's thinking is visible in the UI, not a black box
- **Localized tone** — responses adapted to a target market's voice (reference implementation: Nigerian Pidgin)
- **Conversational UI** — chat interface with live profile and recommendation panels

### Reference Dataset

- Yelp Reviews (enriched with price range metadata, 60,000 records)
- 33,395 unique businesses indexed in Pinecone

### Running Locally

```bash
cd task_b
pip install -r requirements.txt

# Set environment variables in .env
# Required: GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY, PINECONE_API_KEY
# Embedding model: sentence-transformers/all-MiniLM-L6-v2 (auto-downloads)
# Dataset: place reviews_enriched_price.jsonl in task_b/data/

uvicorn main:app --host 0.0.0.0 --port 8002
streamlit run app.py
```

### API Endpoints

- `POST /chat` — send a message and get recommendations
- `GET /sample-users` — get random quality user IDs
- `GET /user/{user_id}` — get a user's preference profile

---

## Tech Stack

| Component        | Technology                             |
| ----------------- | --------------------------------------- |
| LLM Inference     | Groq (llama-3.3-70b-versatile)          |
| Embeddings        | sentence-transformers/all-MiniLM-L6-v2  |
| Vector Search     | Pinecone                                |
| Database          | Supabase                                |
| Backend           | FastAPI                                 |
| Frontend          | Streamlit                               |
| Deployment        | Render (API) + Streamlit Cloud (UI)     |
| Containerization  | Docker                                  |

---

## Project Structure

```
twinn/
├── task_a/                    # Module A: Behavior Simulation
│   ├── src/
│   │   ├── agents/
│   │   │   ├── supervisor/    # Orchestrates pipeline
│   │   │   ├── user_modeling/ # Builds behavioral profiles
│   │   │   ├── review_simulation/ # Generates reviews
│   │   │   └── engagement/    # Presents results + metrics
│   │   └── dataset_loader.py  # Dataset download
│   ├── main.py                # FastAPI backend
│   ├── app.py                 # Streamlit frontend
│   ├── config.py              # Environment configuration
│   └── Dockerfile
├── task_b/                    # Module B: Recommendation
│   ├── src/
│   │   ├── agents/
│   │   │   ├── supervisor/    # Orchestrates pipeline
│   │   │   ├── user_modeling/ # Builds preference profiles
│   │   │   ├── retrieval/     # Semantic search via Pinecone
│   │   │   ├── ranking/       # LLM re-ranking with reasoning
│   │   │   └── engagement/    # Localized conversational responses
│   │   ├── indexer.py         # Indexes businesses into Pinecone
│   │   └── dataset_loader.py  # Dataset download
│   ├── main.py                # FastAPI backend
│   ├── app.py                 # Streamlit frontend
│   ├── config.py              # Environment configuration
│   └── Dockerfile
├── shared/
│   └── utils/                 # Shared utilities
└── docs/                      # Solution paper
```

---

## Environment Variables

Create `.env` files in both `task_a/` and `task_b/` with:

```
GROQ_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
SUPABASE_URL=
SUPABASE_KEY=
HF_TOKEN=
HF_DATASET_REPO=
```

---

## Docker

```bash
# Module A
cd task_a
docker build -t twinn-behavior .
docker run -p 8001:8001 --env-file .env twinn-behavior

# Module B
cd task_b
docker build -t twinn-recommend .
docker run -p 8002:8002 --env-file .env twinn-recommend
```

---

## Models Used

- **LLM:** `llama-3.3-70b-versatile` via Groq API
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
- **Framework:** Custom Python agents (no LangChain/LangGraph)

---

## Disclosure

- Public pre-trained models used: Groq LLaMA 3.3, sentence-transformers
- Reference dataset used: Amazon Digital Music Reviews (5-core)
- All datasets used with appropriate licensing
