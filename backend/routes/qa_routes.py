from fastapi import APIRouter
from pydantic import BaseModel

from services.rag_service import (
    ask_meeting_question
)

router = APIRouter()


class QuestionRequest(BaseModel):
    meeting_id: int
    question: str


@router.post("/ask")
def ask(request: QuestionRequest):

    answer = ask_meeting_question(
        request.meeting_id,
        request.question
    )

    return {
        "answer": answer
    }