
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.core.vector_store import search_events
from app.core.ai_client import generate_answer
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str
    events_found: int
    source_events: list


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    data: QuestionRequest,
    current_user: User = Depends(get_current_user),  # must be logged in
):
   
    if not data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    relevant_events = await search_events(data.question, top_k=5)

    if not relevant_events:
        return QuestionResponse(
            question=data.question,
            answer="No events found in the system yet. Try registering some users first.",
            events_found=0,
            source_events=[],
        )
    answer = await generate_answer(data.question, relevant_events)

    return QuestionResponse(
        question=data.question,
        answer=answer,
        events_found=len(relevant_events),
        source_events=relevant_events,
    )


@router.get("/stats")
async def ai_stats(current_user: User = Depends(get_current_user)):
  
    from app.core.vector_store import _index, _events
    total = len(_events)
    return {
        "total_events_in_vector_db": total,
        "message": f"AI has memory of {total} events"
    }