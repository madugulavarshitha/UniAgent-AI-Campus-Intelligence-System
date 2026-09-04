# UniAgent – AI Campus Intelligence System

UniAgent is a multi-agent AI campus platform designed for colleges. It provides academic profiling, warning systems, skill gap analytics, job vacancy matching, and vector-based regulations search.

---

## Technical Stack Overview

### Frontend
- **Framework**: React (Vite, TypeScript)
- **Styling**: Tailwind CSS & Shadcn/UI
- **Icons**: Lucide Icons
- **Visuals**: Recharts (for academic performance tracking and vacancy matched scores)

### Backend
- **Core API**: FastAPI (Python 3.10+)
- **ORM & DB**: SQLAlchemy, sqlite3 / PostgreSQL driver
- **AI Agent Graph**: LangGraph
- **Vector DB / RAG**: local FAISS vector indexer & PyPDF2 parser
- **Predictive Analytics**: Scikit-Learn (Logistic Regression risk classifier), Pandas, NumPy

---

## Folder Structure

```
College_Multi_Agent/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/         # Reusable layouts, buttons, charts
│   │   ├── pages/              # Portal panels
│   │   ├── layouts/            # Navigation layout shell
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # Backend API clients
│   │   └── types/              # TypeScript declarations
├── backend/                    # Python API server
│   ├── app/
│   │   ├── api/                # FastAPI Routers (Auth, Student, Docs, Analytics)
│   │   ├── database/           # SQLite / Postgres connections
│   │   ├── security/           # Hashing (PBKDF2) and JWT token creation
│   │   ├── models/             # SQLAlchemy Table entities
│   │   └── services/           # AI (Gemini), RAG (FAISS), and Analytics (Scikit-Learn)
│   ├── requirements.txt
│   └── test_backend.py         # Unit tests suite
```

---

## Local Development Setup

### 1. Backend Server Setup
Navigate to the `backend/` directory:
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate environment
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install packages
pip install -r requirements.txt

# 4. Seed demo data
python app/core/seed.py

# 5. Run tests to verify
python test_backend.py

# 6. Run FastAPI
python -m uvicorn app.main:app --reload
```
Once started, the backend exposes:
- **API Server URL**: http://127.0.0.1:8000
- **Health Check**: http://127.0.0.1:8000/health
- **Swagger Documentation**: http://127.0.0.1:8000/docs

---

## 2. Frontend client setup
Navigate to the `frontend/` directory:
```bash
# 1. Install NPM packages
npm install

# 2. Start Vite development server
npm run dev
```
Once started, the client runs on:
- **Client URL**: http://localhost:5173
- The UI automatically checks connection status with the backend at startup and renders responsive, animated dashboards.
