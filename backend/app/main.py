import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.core.security import sanitize_log_message
from app.db.session import engine
from app.db.metadata import Base
from app.api.v1.router import router as api_v1_router
try:
    from scripts.seed_company_data import seed_database
except ImportError:
    seed_database = None

app = FastAPI(
    title="CompanyLens API Gateway",
    description="Production-grade Indian company intelligence, identification, and verification platform.",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (permitting all origin during local development/demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Sanitization & Logging Middleware
@app.middleware("http")
async def sanitize_and_log_middleware(request: Request, call_next):
    # Enforce no raw PAN in request query or URL path logging
    safe_url = sanitize_log_message(str(request.url))
    logger.info(f"[Request] {request.method} {safe_url}")
    
    response = await call_next(request)
    
    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# Mount CompanyLens API v1
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CompanyLens Platform",
        "version": "1.0.0"
    }

# Mount Frontend SPA Build (All-in-One Deployment on Port 8000)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static_assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Allow FastAPI API and Swagger docs to handle their own routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path == "health":
            return Response(status_code=404)
        target_file = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing CompanyLens database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

