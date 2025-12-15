from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager

from .api import routes
from .database import engine, Base
from .config import settings

# OPTIMIZATION: Lifespan manager for Async Redis connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Redis for Rate Limiting
    # (Assuming Redis URL is in settings, defaulting to localhost for now)
    redis_url = "redis://localhost:6379" 
    r = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    
    # Create DB Tables (Async requires run_sync)
    async with engine.begin() as conn:
        # Note: In Prod, use Alembic. This is for dev bootstrapping.
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
    # Shutdown
    await r.close()

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0-enterprise",
    lifespan=lifespan,
    docs_url="/api/docs"
)

# Enterprise Security: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Modules
app.include_router(routes.router, prefix=settings.API_V1_STR, tags=["Ingestion"])

# Enterprise Observability: Prometheus Metrics
Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health_check():
    return {"status": "operational", "metrics": "/metrics"}