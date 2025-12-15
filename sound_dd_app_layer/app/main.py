from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware 
from contextlib import asynccontextmanager
from sqlalchemy import text
import asyncio
from strawberry.fastapi import GraphQLRouter
from .graphql.schema import schema
from .api import stream
from .core.throttling import TieredLimiter

from .api import routes
from .config import settings
from .database import engine
from .models.sql_models import MATERIALIZED_VIEW_SQL, REFRESH_VIEW_SQL

graphql_app = GraphQLRouter(schema)



# Background Task to Refresh View
async def periodic_view_refresh():
    while True:
        await asyncio.sleep(3600) # Refresh every 1 hour
        async with engine.begin() as conn:
            try:
                # REFRESH CONCURRENTLY requires unique index, 
                # falling back to standard refresh for safety in this snippet
                await conn.execute(text("REFRESH MATERIALIZED VIEW impact_stats_mv;"))
                print("🔄 Materialized View Refreshed")
            except Exception as e:
                print(f"❌ View Refresh Failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create Views
    async with engine.begin() as conn:
        await conn.execute(text(MATERIALIZED_VIEW_SQL))
    
    # Start Background Loop
    task = asyncio.create_task(periodic_view_refresh())
    
    yield
    
    # Shutdown
    task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="Enterprise-Optimized",
    lifespan=lifespan
)

# Compresses JSON responses > 1KB. Critical for Mobile users on 4G/5G.
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(graphql_app, prefix="/graphql")
app.include_router(stream.router, prefix="/stream")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix=settings.API_V1_STR)