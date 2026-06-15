#!/bin/bash
cd "$(dirname "$0")"
pip install -r requirements.txt -q
python -c "from app.database import init_db; init_db()"
python -m app.seed.run_seed
echo "✅ Setup complete! Run: uvicorn app.main:app --reload --port 8000"
