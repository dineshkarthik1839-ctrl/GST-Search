import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.db.metadata import Base
from app.core.middlewares import RequestIDMiddleware, RequestLoggingMiddleware
from app.core.exceptions import AppException, app_exception_handler, global_exception_handler
from app.api import health

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

from app.core.middleware import SecurityHeadersMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.academic.router import router as academic_router
from app.modules.content.router import router as content_router
from app.modules.assessment.router import router as assessment_router

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(health.router)
app.include_router(auth_router, prefix=settings.api_v1_str)
app.include_router(academic_router, prefix=settings.api_v1_str)
app.include_router(content_router, prefix=settings.api_v1_str)
app.include_router(assessment_router, prefix=settings.api_v1_str)


@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

