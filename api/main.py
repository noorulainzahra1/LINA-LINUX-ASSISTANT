"""
LINA FastAPI Application
Main entry point for the REST API
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from env file
try:
    from dotenv import load_dotenv
    # Try both .env and env files
    env_file = PROJECT_ROOT / "env"
    if env_file.exists():
        load_dotenv(env_file)
    elif (PROJECT_ROOT / ".env").exists():
        load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    # If dotenv not available, manually load env file
    env_file = PROJECT_ROOT / "env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Import routers
from api.routers import session, request, command, tools, stream, hash, files

# Import services (initialize them)
from api.services.session_service import SessionService

# Initialize FastAPI app
app = FastAPI(
    title="LINA API",
    description="AI-Powered Cybersecurity Assistant API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(session.router)
app.include_router(request.router)
app.include_router(command.router)
app.include_router(tools.router)
app.include_router(stream.router)
app.include_router(hash.router)
app.include_router(files.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "LINA API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LINA API"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with CORS headers"""
    import traceback
    from utils.logger import log as logger
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    response = JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred"
        }
    )
    # Add CORS headers even for errors
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

