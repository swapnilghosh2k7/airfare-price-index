"""
FastAPI Application Entry Point for APIx Platform
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.config import PROJECT_TITLE, VERSION, DATA_DIR
from backend.database import init_db, SessionLocal
from backend.api.index_routes import router as index_router
from backend.api.fare_routes import router as fare_router
from backend.api.route_routes import router as route_router
from backend.api.analytics_routes import router as analytics_router
from backend.api.backtest_routes import router as backtest_router
from backend.api.scraper_routes import router as scraper_router
from backend.api.governance_routes import router as governance_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas on startup
    init_db()
    
    # Auto-seed if database is brand new
    from backend.scripts.seed_database import seed_initial_platform_data
    db = SessionLocal()
    try:
        seed_initial_platform_data(db)
    finally:
        db.close()
        
    yield

app = FastAPI(
    title=PROJECT_TITLE,
    version=VERSION,
    description=(
        "Production-style API for the Real-time Airfare Price Index (APIx) for India. "
        "Augments the Consumer Price Index (CPI) Transport & Communication subgroup "
        "through automated high-frequency web scraping, statistical cleaning, and DGCA backtesting."
    ),
    lifespan=lifespan
)

# Enable CORS for local Vite/React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(index_router, prefix="/api")
app.include_router(fare_router, prefix="/api")
app.include_router(route_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(backtest_router, prefix="/api")
app.include_router(scraper_router, prefix="/api")
app.include_router(governance_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "APIx Platform Backend",
        "version": VERSION,
        "database": "connected"
    }

# If frontend is built, serve static files
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
