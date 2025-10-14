from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import review

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
app.include_router(review.router)


@app.get("/")
async def root():
    return {"message": "Talent Promo API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
