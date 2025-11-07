from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal

class KeyEntities(BaseModel):
    people: List[str] = []
    organizations: List[str] = []
    locations: List[str] = []

class QuizItem(BaseModel):
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    answer: str
    difficulty: Literal["easy", "medium", "hard"]
    explanation: str

class QuizOutput(BaseModel):
    id: int | None = None
    url: str
    title: str
    summary: str
    key_entities: KeyEntities
    sections: List[str]
    quiz: List[QuizItem] = Field(..., min_items=5, max_items=10)
    related_topics: List[str] = Field(..., min_items=3)

class GenerateRequest(BaseModel):
    url: HttpUrl
    force_refresh: bool = False

class HistoryItem(BaseModel):
    id: int
    url: str
    title: str
    date_generated: str

class HistoryResponse(BaseModel):
    items: List[HistoryItem]
