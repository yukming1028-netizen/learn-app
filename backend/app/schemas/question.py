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
    avg_time_sec: float = 30.0

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    question_id: int
    selected_answer: str
    time_taken_sec: float = 0.0
    is_correct: bool | None = None  # If omitted, server determines from selected_answer


class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    reward: str | None = None
    new_sticker: str | None = None


class NextQuestionRequest(BaseModel):
    subject: str | None = None
    language: str | None = None  # zh-TW, zh-CN, en-US
