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

#### Backend Setup (Python)

1. Create virtual environment:

```bash
cd apps/api
python3 -m venv venv
```

2. Activate virtual environment:

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Install dependencies (in the `apps/api` directory):

```bash
pip install -r requirements.txt
```

4. Set environment variables:

```bash
export OPENAI_API_KEY=sk-your-key-here
```

5. Run the API server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

To deactivate the virtual environment when done:

```bash
deactivate
```

#### Frontend Setup (Node.js)

```bash
pnpm install
pnpm --filter web dev
```

The web app will be available at `http://localhost:3000`

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Backend**: FastAPI, Python
- **Workflows**: Temporal
- **AI**: OpenAI Agents SDK
