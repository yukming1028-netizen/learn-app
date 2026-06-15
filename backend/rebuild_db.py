"""Rebuild DB with seed data."""
import sys
sys.path.insert(0, '.')
from app.database import engine, Base, SessionLocal
from app.models import *
from app.seed.seed_data import get_seed_questions
from app.models.question import Question

Base.metadata.create_all(bind=engine)
db = SessionLocal()
questions = get_seed_questions()
for q in questions:
    db.add(q)
db.commit()
print(f"Seeded {db.query(Question).count()} questions")
db.close()
