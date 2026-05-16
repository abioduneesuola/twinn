import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from src.agents.supervisor import run_task_a
from src.agents.user_modeling import get_sample_users
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Twinn Review API starting...")
    yield


app = FastAPI(
    title="Twinn Review API",
    description="Task A: LLM-powered review simulation agent",
    version="1.0.0",
    lifespan=lifespan
)


class ReviewRequest(BaseModel):
    user_id: str
    n_products: int = 3


class ReviewResponse(BaseModel):
    user_id: str
    profile: dict = {}
    simulated_reviews: list[dict] = []
    presented_reviews: list[str] = []
    metrics: dict = {}


@app.get("/")
def root():
    return {"status": "Twinn Review API is live 🎵", "version": "1.0.0"}


@app.post("/simulate", response_model=ReviewResponse)
def simulate_reviews(request: ReviewRequest):
    try:
        result = run_task_a(
            user_id=request.user_id,
            n_products=request.n_products
        )
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return ReviewResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sample-users")
def sample_users(n: int = 5):
    """Returns sample user IDs from the dataset for testing."""
    users = get_sample_users(n)
    return {"users": users}


@app.get("/user/{user_id}")
def get_user_profile(user_id: str):
    from src.agents.user_modeling import get_or_build_profile
    profile = get_or_build_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)