# Decision Engine

A distributed decision-making system that evaluates financial applications using a scoring algorithm. Built with FastAPI, Redis, and PostgreSQL.

## Architecture
[Client] -> POST /decision -> [FastAPI] -> [Redis Queue] -> [Worker] -> [PostgreSQL]
|
|
[Client] <- GET /decisions <- [FastAPI] <- [PostgreSQL]

## Stack

- **FastAPI** — REST API
- **Redis** — job queue with guaranteed delivery
- **PostgreSQL** — persistent storage for decisions
- **SQLAlchemy** — ORM
- **Docker** — containerized infrastructure

## How It Works

1. Client sends a `POST /decision` request with income, age, and debt
2. API pushes the job to a Redis queue and returns immediately
3. Worker picks up the job, calculates a weighted score, and saves the decision to PostgreSQL
4. Client can query decisions via `GET /decisions` or `GET /decisions/{id}`

### Scoring Formula
score = income * 0.5 - debt * 0.3 + age * 2
score > 2000 → APPROVED
score ≤ 2000 → REJECTED

## Running Locally

### Prerequisites
- Docker
- Python 3.11+

### 1. Start infrastructure

```bash
docker run --name decision-engine-postgres \
  -e POSTGRES_USER=decision_user \
  -e POSTGRES_PASSWORD=decision_pass \
  -e POSTGRES_DB=decision_db \
  -p 5432:5432 -d postgres:15

docker run --name decision-engine-redis \
  -p 6379:6379 -d redis
```

### 2. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure environment

```bash

cp .env.example .env  
```

### 4. Initialize database

```bash
python init_db.py
```

### 5. Start the worker

```bash
python worker.py
```

### 6. Start the API

```bash
uvicorn api:app --reload
```

API docs available at `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|

| POST | `/decision` | Queue a new decision job |
| GET | `/decisions` | List all decisions |
| GET | `/decisions/{id}` | Get a specific decision |

## Roadmap

- [ ] Deploy API on AWS Lambda + API Gateway
- [ ] Add pytest test suite for scoring logic and API endpoints
- [ ] Add retry logic with dead letter queue for failed jobs
