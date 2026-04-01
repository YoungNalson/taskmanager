# import asyncio
import pytest
from httpx import AsyncClient
from httpx import ASGITransport

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# -------------------------
# EVENT LOOP (pytest-asyncio moderno)
# -------------------------

@pytest.fixture
def anyio_backend():
    return "asyncio"

# -------------------------
# CRIAR / DROPAR TABELAS
# -------------------------

@pytest.fixture
async def engine():
    engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,  # importante para evitar reuse de conexão
    )

    # garante isolamento entre testes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

# -------------------------
# SESSION POR TESTE
# -------------------------

@pytest.fixture
async def client(engine):
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()