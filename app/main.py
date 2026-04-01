from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine

from app.api.v1 import api_router
from app.ui import routes as ui_routes

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

# UI (root)
app.include_router(ui_routes.router)

# API versionada
app.include_router(api_router, prefix="/api/v1")