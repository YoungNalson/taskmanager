from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine

from app.api.v1 import api_router
from app.ui import routes as ui_routes

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# UI (root)
app.include_router(ui_routes.router)

# API versionada
app.include_router(api_router, prefix="/api/v1")