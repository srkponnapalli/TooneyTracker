# TooneyTracker 🍁

> A Canadian personal finance tracker that connects to multiple bank accounts via Plaid API, centralizes transactions, and gives you a clean dashboard to track spending — built because no existing app does this reliably for Canadians.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## Why I Built This

Managing multiple Canadian bank accounts (TD, RBC, Scotiabank etc.) with no single reliable view is painful. Existing apps like Wealthica have reliability issues, and most mainstream apps (Mint, Copilot) are US-first with poor Canadian bank support.

TooneyTracker solves this by connecting directly to Canadian banks via Plaid, pulling all transactions into a centralized Postgres database, and presenting them in a clean Streamlit dashboard.

This is also a personal learning project — built to develop full-stack product engineering skills alongside a professional background in data engineering and distributed systems (Databricks).

---

## Features

- 🏦 **Multi-bank support** — connect TD, RBC, BMO, Scotiabank, CIBC and more via Plaid
- 🔄 **Automatic transaction sync** — cursor-based incremental sync, no duplicates
- 📊 **Monthly spending dashboard** — visual spend summaries by month
- 💳 **Account balances** — real-time balance across all connected accounts
- 🗂️ **Transaction history** — filterable by account, searchable
- 🔒 **Secure token storage** — access tokens stored in DB (encryption TODO for production)

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Backend** | Python 3.11, FastAPI | Fast to build, async-ready, auto-generates API docs |
| **Database** | PostgreSQL 15 | Reliable relational DB, strong support for financial data |
| **Bank Integration** | Plaid API | Best Canadian bank coverage, battle-tested |
| **Frontend** | Streamlit | Python-native, fast to build, no frontend experience needed |
| **Infrastructure** | Docker, docker-compose | Portable local dev, easy to deploy |
| **ORM** | SQLAlchemy | Clean DB abstraction, session management |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Streamlit UI                   │
│         (Dashboard, Balances, Transactions)      │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│                  FastAPI Backend                  │
│   /plaid/create-link-token                       │
│   /plaid/exchange-token                          │
│   /plaid/sync-accounts                           │
│   /plaid/sync-transactions                       │
└──────────┬──────────────────────┬───────────────┘
           │                      │
┌──────────▼──────────┐  ┌───────▼───────────────┐
│     Plaid API        │  │    PostgreSQL DB        │
│  (Bank Integration)  │  │  users, institutions,  │
│                      │  │  accounts, transactions │
└──────────────────────┘  └───────────────────────┘
```

---

## Database Schema

```
users
  └── institutions (banks connected via Plaid)
        └── accounts (chequing, savings, credit cards)
              └── transactions (every expense/credit)

categories  ← linked to transactions
budgets     ← linked to users + categories
```

Key design decisions:
- `autocommit=False` — financial data requires atomic writes
- `cursor` on institutions — Plaid cursor-based sync for efficient incremental updates
- `raw_name` + `merchant_name` — both stored, raw for debugging, clean for display
- `pending` flag — pending transactions handled separately from posted

---

## Project Structure

```
TooneyTracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── db/
│   │   │   ├── schema.sql       # Full DB schema
│   │   │   └── connection.py    # SQLAlchemy engine + session
│   │   ├── routers/
│   │   │   └── plaid.py         # All Plaid API endpoints
│   │   └── services/
│   │       └── plaid_service.py # Plaid client configuration
│   ├── requirements.txt
│   └── .env                     # Never commit this
├── frontend/
│   └── app.py                   # Streamlit dashboard
├── docker-compose.yml           # Postgres container
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11
- Docker Desktop
- Plaid developer account (free) — [Sign up here](https://dashboard.plaid.com/signup)

### 1. Clone the repo

```bash
git clone https://github.com/srkponnapalli/TooneyTracker.git
cd TooneyTracker
```

### 2. Set up environment variables

Create `backend/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tooneytracker
DB_USER=tooney
DB_PASSWORD=tooney123

PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_sandbox_secret
PLAID_ENV=Sandbox
```

### 3. Start the database

```bash
docker-compose up -d
```

### 4. Apply the schema

```bash
Get-Content backend/app/db/schema.sql | docker exec -i tooneytracker_db psql -U tooney -d tooneytracker
```

### 5. Set up Python environment

```bash
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Run the backend

```bash
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

### 7. Connect a bank (sandbox)

1. `POST /plaid/sandbox/create-public-token` — get a test token
2. `POST /plaid/exchange-token` — exchange for access token
3. `POST /plaid/sync-accounts` — sync accounts
4. `POST /plaid/sync-transactions` — sync transactions

### 8. Run the dashboard

```bash
cd frontend
python -m streamlit run app.py
```

Dashboard available at: `http://localhost:8501`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | API health check |
| GET | `/db-health` | Database connection check |
| POST | `/plaid/create-link-token` | Create Plaid Link token |
| POST | `/plaid/exchange-token` | Exchange public token for access token |
| POST | `/plaid/sync-accounts` | Sync bank accounts to DB |
| POST | `/plaid/sync-transactions` | Sync transactions to DB |
| POST | `/plaid/sandbox/create-public-token` | Sandbox testing only |

---

## Roadmap

- [ ] Budget tracking with monthly limits per category
- [ ] Spending alerts when approaching budget
- [ ] Category management (custom categories)
- [ ] Multi-user support
- [ ] Encrypt access tokens at rest
- [ ] Cloud deployment (Railway + Streamlit Cloud)
- [ ] Real bank connection (Plaid production)
- [ ] React frontend migration

---

## What I Learned

- Full-stack ownership from DB schema to frontend
- REST API design with FastAPI
- Plaid API integration — Link flow, token exchange, cursor-based sync
- PostgreSQL schema design for financial data
- Docker for local development
- Why `autocommit=False` matters in financial applications
- Python app architecture vs distributed systems thinking

---

## Author

**Siva Ponnapalli** — Senior Data Engineer  
[GitHub](https://github.com/srkponnapalli) · [LinkedIn](https://linkedin.com/in/ponnasivark)

---

*Built with 🍁 in Toronto*