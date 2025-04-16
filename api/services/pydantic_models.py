from pydantic import BaseModel
from typing import Optional, Literal

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    model: Literal["gpt-4o", "gpt-4o-mini"]
    no_of_chunks: Optional[int] = 3

class ChatResponse(BaseModel):
    question: str
    refine_question: str
    response: str
    session_id: str
    debug_info: Optional[dict] = None