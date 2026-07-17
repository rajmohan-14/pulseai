# PulseAI — AI-Integrated Event-Driven Backend Platform

> A production-grade backend system built with FastAPI, Apache Kafka, Docker, PostgreSQL, Redis, Celery, and an AI layer powered by Groq LLM and FAISS vector search.

🚀 **Live API:** `coming soon`  
📁 **GitHub:** [github.com/rajmohan-14/pulseai](https://github.com/rajmohan-14/pulseai)

---

## What is PulseAI?

PulseAI is a real-time, event-driven backend platform that demonstrates production-grade backend engineering. Every user action (registration, login) is published as a Kafka event, consumed by AI workers that classify and store events in a vector database, and queryable via a natural language RAG pipeline.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                               │
│              (REST API via /docs or curl)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ JWT Auth
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (Port 8000)                       │
│         Auth · Users · AI Routes · Prometheus /metrics      │
└──────────┬──────────────────────────────────────────────────┘
           │ Publishes events
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Apache Kafka (Port 9092)                   │
│                   Topic: user-events                         │
└──────────┬──────────────────────────────────────────────────┘
           │ Consumed by
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Kafka Consumer Worker                      │
│                                                             │
│   ┌─────────────────┐      ┌──────────────────────────┐    │
│   │  Groq LLM       │      │   FAISS Vector Store     │    │
│   │  Classifies     │      │   Stores embeddings      │    │
│   │  event severity │      │   for RAG search         │    │
│   └─────────────────┘      └──────────────────────────┘    │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              Celery Workers (via Redis)              │  │
│   │   send_welcome_email · notify_admin · hourly_summary │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│   PostgreSQL (users)  ·  Redis (task queue, cache)          │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Observability                             │
│        Prometheus (metrics)  ·  Grafana (dashboards)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI (async) |
| Authentication | JWT (access + refresh tokens), RBAC |
| Message Broker | Apache Kafka |
| Task Queue | Celery + Redis |
| Database | PostgreSQL (async via SQLAlchemy 2.0) |
| Cache | Redis |
| AI Classification | Groq LLM (Llama 3) |
| Vector Database | FAISS |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| RAG Pipeline | FAISS + Groq LLM |
| Containerization | Docker + Docker Compose |
| Metrics | Prometheus |
| Dashboards | Grafana |

---

## Features

### Authentication & Authorization
- JWT access + refresh token rotation
- Role-Based Access Control (RBAC) — user vs admin
- bcrypt password hashing
- Protected routes via FastAPI dependency injection

### Event-Driven Architecture
- Every user action published to Kafka `user-events` topic
- Multiple independent consumers processing events in parallel
- Non-blocking API — events processed asynchronously

### AI Layer
- **Event Classification** — Groq LLM classifies each event as `critical`, `warning`, or `info` in real time
- **Vector Storage** — Events embedded using SentenceTransformers and stored in FAISS
- **RAG Pipeline** — Natural language Q&A over system events using retrieval-augmented generation
- **Hourly Summaries** — Celery Beat generates AI-powered plain-English summaries every hour
- **Abstracted LLM Client** — Swappable between Groq, OpenAI, and Ollama

### Background Workers
- Welcome email on user registration (with retry logic)
- Admin notifications for new users
- Scheduled hourly event digest via Celery Beat

### Observability
- Prometheus metrics at `/metrics`
- Grafana dashboard for API request rates and response times
- Structured logging across all services

---

## Project Structure

```
pulseai/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py        # register, login, refresh, /me
│   │       ├── users.py       # admin user management
│   │       └── ai.py          # RAG Q&A, AI stats
│   ├── consumers/
│   │   └── event_consumer.py  # Kafka consumer + AI processing
│   ├── core/
│   │   ├── config.py          # settings from .env
│   │   ├── database.py        # async SQLAlchemy setup
│   │   ├── security.py        # JWT + bcrypt
│   │   ├── dependencies.py    # FastAPI dependencies (auth guards)
│   │   ├── kafka.py           # Kafka producer
│   │   ├── ai_client.py       # Groq LLM client (classify, answer, summarize)
│   │   ├── vector_store.py    # FAISS vector database
│   │   └── celery_app.py      # Celery + Beat configuration
│   ├── models/
│   │   └── user.py            # SQLAlchemy User model
│   ├── schemas/
│   │   └── user.py            # Pydantic request/response schemas
│   ├── services/
│   │   └── auth_service.py    # auth business logic
│   ├── tasks/
│   │   └── notification_tasks.py  # Celery tasks
│   └── main.py                # FastAPI app entry point
├── docker-compose.yml         # all services
├── prometheus.yml             # Prometheus scrape config
├── requirements.txt
└── .env.example
```

---

## Quick Start

### Prerequisites
- Python 3.12
- Docker Desktop
- Groq API key (free at console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/rajmohan-14/pulseai.git
cd pulseai
```

### 2. Create virtual environment
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your values
```

Required values in `.env`:
```
DATABASE_URL=postgresql+asyncpg://raj:password@localhost:5433/pulseai
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key-here
```

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Start all services
```bash
docker compose up -d
```

Wait 45 seconds for Kafka to fully start.

### 5. Run the FastAPI server
```bash
uvicorn app.main:app --reload
```

### 6. Run the Kafka consumer (new terminal)
```bash
source venv/bin/activate
python -m app.consumers.event_consumer
```

### 7. Run the Celery worker (new terminal)
```bash
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/` | Health check | None |
| GET | `/health` | Health status | None |
| GET | `/metrics` | Prometheus metrics | None |
| POST | `/api/v1/auth/register` | Register user | None |
| POST | `/api/v1/auth/login` | Login + get tokens | None |
| POST | `/api/v1/auth/refresh` | Refresh access token | None |
| GET | `/api/v1/auth/me` | Get current user | JWT |
| GET | `/api/v1/users/` | List all users | JWT + Admin |
| GET | `/api/v1/users/{id}` | Get user by ID | JWT + Admin |
| POST | `/api/v1/ai/ask` | Ask AI about events (RAG) | JWT |
| GET | `/api/v1/ai/stats` | Vector DB stats | JWT |

Full interactive docs: `http://localhost:8000/docs`

---

## Testing the AI

Once the system is running and you've registered a few users:

1. Login and get your access token
2. Authorize in `/docs`
3. Hit `POST /api/v1/ai/ask` with:

```json
{
  "question": "what users registered today?"
}
```

The AI will search the vector database and return a natural language answer based on real system events.

---

## Monitoring

| Service | URL | Credentials |
|---|---|---|
| API Docs | http://localhost:8000/docs | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin |

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `ALGORITHM` | JWT algorithm (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL |
| `GROQ_API_KEY` | Groq API key for LLM |
| `GROQ_MODEL` | Groq model (llama3-8b-8192) |
| `APP_NAME` | Application name |
| `DEBUG` | Debug mode |

---

## What I Learned Building This

- Designing event-driven systems with Kafka producer/consumer patterns
- Implementing production-grade JWT authentication with token rotation
- Building a RAG pipeline from scratch — embeddings, vector search, LLM prompting
- Managing async Python with FastAPI and SQLAlchemy 2.0
- Containerizing multi-service architectures with Docker Compose
- Setting up real-time observability with Prometheus and Grafana
- Abstracting external dependencies (LLM client) for maintainability

---

## Author

**Raj Mohan**  
Final-year CSE student | Backend Developer  
[GitHub](https://github.com/rajmohan-14)
