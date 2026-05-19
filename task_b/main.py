import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from src.agents.supervisor import process_message
from src.agents.user_modeling import get_sample_users
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Twinn Recommend API starting...")
    from src.dataset_loader import ensure_dataset_available
    ensure_dataset_available()
    yield


app = FastAPI(
    title="Twinn Recommend API",
    description="Task B: LLM-powered conversational recommendation agent",
    version="1.0.0",
    lifespan=lifespan
)


class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation: list[dict] = []
    session_id: str


class ChatResponse(BaseModel):
    response: str
    reasoning_trace: list[str] = []
    recommendations: list[dict] = []
    agent_used: str = ""
    profile: dict = {}


@app.get("/")
def root():
    return {"status": "Twinn Recommend API is live 🍽️", "version": "1.0.0"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = process_message(
            user_id=request.user_id,
            message=request.message,
            conversation=request.conversation,
            session_id=request.session_id
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sample-users")
def sample_users(n: int = 8):
    users = get_sample_users(n)
    return {"users": users}


@app.get("/user/{user_id}")
def get_user(user_id: str):
    from src.agents.user_modeling import get_or_build_profile
    profile = get_or_build_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
