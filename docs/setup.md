# AquaTrust — Setup Guide

## Prerequisites

| Tool | Version | Required |
|------|---------|----------|
| Python | 3.14+ | Yes (backend) |
| Node.js | 18+ | Yes (frontend) |
| npm | 9+ | Yes (frontend) |
| PostgreSQL | 16 | Optional (production) |
| Docker | 24+ | Optional |

## Quick Start (5 minutes)

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd aquatrust
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

Verify:
```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"AquaTrust"}
```

### 3. Start the frontend

Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

### 4. Open the app

Go to `http://localhost:3000` in your browser.

Click **Load Scenarios** → select a scenario → click to run.

---

## Backend Setup Details

### Environment Variables

Create `backend/.env` (optional — has sensible defaults):

```env
DATABASE_URL=sqlite:///./aquatrust.db
API_V1_PREFIX=/api
PROJECT_NAME=AquaTrust
```

For PostgreSQL:
```env
DATABASE_URL=postgresql://aquatrust:aquatrust@localhost:5432/aquatrust
```

### Database

**SQLite (default)** — zero config, file created automatically at `backend/aquatrust.db`

**PostgreSQL** — set `DATABASE_URL` and ensure the database exists:
```bash
createdb aquatrust
```

### Run Tests

```bash
cd backend
pytest ../tests/ -v
```

Expected: **85 passed**

### API Documentation

Once backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Frontend Setup Details

### Install Dependencies

```bash
cd frontend
npm install
```

### Development Mode

```bash
npm run dev
```

Vite dev server with hot reload at `http://localhost:3000`

API calls are proxied to `http://localhost:8000` (configured in `vite.config.ts`).

### Production Build

```bash
npm run build
npm run preview
```

---

## Docker Setup (Optional)

```bash
docker-compose up
```

This starts:
- PostgreSQL on port 5432
- Backend on port 8000

---

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Must be 3.14+

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend won't start

```bash
# Check Node version
node --version  # Must be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port already in use

```bash
# Backend: use different port
uvicorn app.main:app --port 8001

# Frontend: use different port
npm run dev -- --port 3001
```

### Database locked (SQLite)

```bash
# Delete the database file (will be recreated)
rm backend/aquatrust.db
```

---

## Verification Checklist

After setup, verify everything works:

- [ ] Backend health check returns `{"status":"healthy"}`
- [ ] Frontend loads at `http://localhost:3000`
- [ ] "Load Scenarios" shows 4 scenarios
- [ ] Running "Agreement" scenario shows `SUPPORTED`
- [ ] Running "Citizen Conflict" shows `CONTRADICTED`
- [ ] All 85 tests pass
- [ ] Evaluation script shows 4/4 scenarios passing
