# Talent Promo

Application to help talent to best present themselves.

## Project Structure

```
talent-promo/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── packages/
│   └── shared/       # Shared types and utilities
└── temporal/         # Temporal workflows
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- pnpm

### Development

Install dependencies:

```bash
pnpm install
cd apps/api && pip install -r requirements.txt
```

Run development servers:

```bash
# Frontend
pnpm --filter web dev

# Backend
cd apps/api && uvicorn main:app --reload
```

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Backend**: FastAPI, Python
- **Workflows**: Temporal
- **AI**: OpenAI Agents SDK
