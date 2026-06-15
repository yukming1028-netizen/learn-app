FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python3 -c 'from app.database import init_db; init_db()' && python3 -m app.seed.run_seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
