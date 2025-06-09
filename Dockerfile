FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev

RUN pip install --no-cache-dir poetry

COPY . .

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

EXPOSE 2456

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2456"]
