from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ModelName(str, Enum):
    O4_MINI = "o4-mini"
    GPT4_O_MINI = "gpt-4o-mini"

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.GPT4_O_MINI)

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName

class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_timestamp: datetime

class DeleteFileRequest(BaseModel):
    file_id: str