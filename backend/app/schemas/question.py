"""Question schemas."""
from pydantic import BaseModel


class QuestionOut(BaseModel):
    id: int
    subject: str
    grade: int
    difficulty: int
    type: str
    content: str
    options: list
    answer: str
    explanation: str
    tags: list
    avg_time_sec: float
    correct_rate: float

    class Config:
        from_attributes = True


class QuestionBrief(BaseModel):
    """Without answer/explanation — sent to child before answering."""
    id: int
    subject: str
    grade: int
    difficulty: int
    type: str
    content: str
    options: list
    tags: list

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    child_id: int
    question_id: int
    is_correct: bool
    time_taken_sec: float = 0.0
    selected_answer: str | None = None


class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    reward: str | None = None
    new_sticker: str | None = None


class NextQuestionRequest(BaseModel):
    child_id: int
    subject: str | None = None
