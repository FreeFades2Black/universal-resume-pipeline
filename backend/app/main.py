"""
FastAPI Server Entry Point
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .api.routes import router as api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Universal Resume Extraction and Injection Engine API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration for Browser Extension and Web Dropzone
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows browser extension and any local host origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.api_prefix)

# Mount web dropzone UI if folder exists
web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "web")
if os.path.exists(web_dir):
    app.mount("/app", StaticFiles(directory=web_dir, html=True), name="web")


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
        "schema": f"{settings.api_prefix}/schema",
        "web_ui": "/app/"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
