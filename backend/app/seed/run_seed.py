"""Run seed script: populate the database with sample questions."""
from app.database import SessionLocal, init_db
from app.models.question import Question
from app.seed.seed_data import QUESTIONS


def run_seed():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(Question).count()
        if existing > 0:
            print(f"⚠️ Database already has {existing} questions. Skipping seed.")
            return

        for q_data in QUESTIONS:
            q = Question(**q_data)
            db.add(q)

        db.commit()
        print(f"✅ Seeded {len(QUESTIONS)} questions successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
