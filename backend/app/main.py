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
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CloudCompliance Sentinel API</title>
        <meta charset="utf-8">
        <style>
            body {
                background-color: #020617;
                color: #f8fafc;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .card {
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid #1e293b;
                border-radius: 12px;
                padding: 2.5rem;
                max-width: 450px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                text-align: center;
            }
            h1 {
                color: #38bdf8;
                margin-top: 0;
                margin-bottom: 0.75rem;
                font-size: 1.85rem;
                font-weight: 800;
            }
            p {
                color: #94a3b8;
                font-size: 0.95rem;
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                color: #10b981;
                padding: 0.4rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                margin-bottom: 1.5rem;
            }
            .dot {
                height: 8px;
                width: 8px;
                background-color: #10b981;
                border-radius: 50%;
                display: inline-block;
                box-shadow: 0 0 8px #10b981;
            }
            .btn-group {
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
            .btn {
                background: #38bdf8;
                color: #020617;
                padding: 0.65rem 1.25rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 700;
                font-size: 0.875rem;
                transition: opacity 0.2s;
            }
            .btn:hover {
                opacity: 0.9;
            }
            .btn-outline {
                background: transparent;
                color: #f8fafc;
                border: 1px solid #334155;
            }
            .btn-outline:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>CloudCompliance Sentinel</h1>
            <p>REST API Engine supporting automated GDPR & HIPAA configuration drift auditing and reporting across AWS and GCP environments.</p>
            <div class="status-badge">
                <span class="dot"></span>
                API Engine Online
            </div>
            <div class="btn-group">
                <a href="/docs" class="btn">Interactive Docs</a>
                <a href="/health" class="btn btn-outline">Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
