"""Main FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.database.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="CloudCompliance Sentinel API",
    description="Compliance Engine API for multi-cloud configuration auditing (GDPR/HIPAA)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "message": "CloudCompliance Sentinel API is running successfully.",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
