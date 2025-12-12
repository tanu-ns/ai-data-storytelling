# AI Data Storytelling SaaS

An open-source platform that acts as an "AI Data Analyst". Upload your CSV, get instant insights, visualizations, and a coherent data story (executive report) written by AI.

## 🚀 Features
- **Instant EDA**: Automatically infers schema, calculates statistics, and visualizes distributions.
- **AI Insights**: Uses LLMs (vLLM or Mock) to find hidden patterns and correlations.
- **Data Storytelling**: Synthesizes findings into a professional Markdown report.
- **Local First**: Runs entirely on your machine without Docker (via SQLite & Local Storage).

## 🛠 Tech Stack
- **Backend**: FastAPI (Python), Pandas, SQLAlchemy, Pydantic.
- **Frontend**: Next.js (TypeScript), Tailwind CSS, Recharts.
- **Database**: SQLite (Local) or PostgreSQL (Production).
- **AI**: Local Mock (Default) or OpenAI-compatible API (vLLM/TGI).

## ⚡ Quick Start (Local Mode)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Backend Setup
```bash
cd api
pip install -r requirements.txt
# Seed the database (creates demo tenant/user)
python -m api.seed
# Run the Server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
Open a new terminal:
```bash
cd web
npm install
npm run dev
```

### 4. Usage
- Go to `http://localhost:3000/login`
- Login with: `analyst@example.com` (No password needed for local dev)
- Upload a CSV file (e.g. Titanic or Iris)
- Click "Generate Insights" -> "Write Story"

## 🐳 Docker Setup (Optional)
If you have Docker running, you can spin up the full infrastructure (Postgres, MinIO, Keycloak):
```bash
cd infra
docker compose up -d
```
*Note: Set `USE_SQLITE=False` in `.env` to use the Docker services.*

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
