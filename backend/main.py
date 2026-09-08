import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.database.session import init_db
from backend.app.api.endpoints import (
    health, routes, carriers, fares, index, analytics, quality, collection
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    init_db()
    yield

app = FastAPI(
    title=settings.name,
    version=settings.version,
    description="Real-Time Airfare Price Index Platform for India (APIx) for Augmentation of the Consumer Price Index (CPI).",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, prefix="/api", tags=["System Health"])
app.include_router(routes.router, prefix="/api", tags=["Routes"])
app.include_router(carriers.router, prefix="/api", tags=["Carriers"])
app.include_router(fares.router, prefix="/api", tags=["Fares"])
app.include_router(index.router, prefix="/api", tags=["Index Engine"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(quality.router, prefix="/api", tags=["Data Quality"])
app.include_router(collection.router, prefix="/api", tags=["Collection Management"])

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
