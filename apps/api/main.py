from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import research  # type: ignore[import-untyped]

app = FastAPI(
    title="Talent Promo API",
    description="API for helping talent present themselves",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Talent Promo API"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
