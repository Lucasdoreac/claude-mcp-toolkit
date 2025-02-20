# Setup Guide

This guide will help you set up the Claude MCP Toolkit development environment.

## Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure PostgreSQL:
- Create a new database
- Update connection string in `src/api/database.py`

3. Run database migrations:
```bash
alembic upgrade head
```

4. Configure Redis:
- Install Redis server
- Update Redis configuration in `src/api/cache.py`

5. Start the API server:
```bash
uvicorn src.api.main:app --reload
```

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd src/frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Configure environment:
- Copy `.env.example` to `.env.local`
- Update API URL if needed

4. Start development server:
```bash
npm run dev
```

## Development Flow

1. Backend changes:
- Add/update models in `src/api/models/`
- Create migrations with `alembic revision --autogenerate -m "description"`
- Apply migrations with `alembic upgrade head`

2. Frontend changes:
- Add/update services in `src/frontend/api/services/`
- Use `useApi` hook for data fetching
- Follow component structure in docs/architecture.md