"""
Main FastAPI application with CORS middleware and error handlers.

[Task]: T006, T021-T023, T041-T043, T065, T079, T096, T109
[From]: specs/001-fullstack-web-app/plan.md, quickstart.md
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.routes import auth, tasks
from app.middleware.error_handler import (
    validation_exception_handler,
    integrity_error_handler,
    generic_exception_handler
)

# Create FastAPI application
app = FastAPI(
    title="Todo Application API",
    description="RESTful API for Phase II Todo Full-Stack Web Application",
    version="1.0.0"
)

# Configure CORS middleware
origins = settings.CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Todo API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
