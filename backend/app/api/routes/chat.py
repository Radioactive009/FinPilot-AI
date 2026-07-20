from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


@router.post("/")
def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Placeholder for invoking the LangGraph supervisor and agents
    return {
        "response": f"Echo: '{request.message}'. The LangGraph agents are configured but inactive for this phase.",
        "thread_id": request.thread_id
    }
