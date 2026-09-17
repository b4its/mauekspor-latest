FROM python:3.13-slim

# libpq diperlukan untuk psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV MAUEKSPOR_DATABASE_URL=postgresql://mauekspor:mauekspor@localhost:5432/mauekspor

RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
