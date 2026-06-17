"""FastAPI main application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    auth, binding, children, questions, plans, progress, review, reports,
    ai_questions, teacher, insights, admin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="親子學習互動平台 API",
    description="Parent-Child Learning Companion API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting on auth endpoints
app.add_middleware(RateLimitMiddleware, max_requests=10, window_seconds=60)

# Routes
app.include_router(auth.router)
app.include_router(binding.router)
app.include_router(children.router)
app.include_router(questions.router)
app.include_router(plans.router)
app.include_router(progress.router)
app.include_router(review.router)
app.include_router(reports.router)
app.include_router(ai_questions.router)
app.include_router(teacher.router)
app.include_router(insights.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "3.0.0"}
