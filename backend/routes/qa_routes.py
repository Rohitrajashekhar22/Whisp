from fastapi import APIRouter, Depends
from pydantic import BaseModel

from security import get_current_user
from services.rag_service import ask_meeting_question

router = APIRouter()


class QuestionRequest(BaseModel):
    meeting_id: int
    question: str


@router.post("/ask")
def ask(
    request: QuestionRequest,
    current_user=Depends(get_current_user)
):

    answer = ask_meeting_question(
        meeting_id=request.meeting_id,
        user_id=current_user["id"],   # ✅ FIXED USAGE
        question=request.question
    )

    return {
        "answer": answer
    }