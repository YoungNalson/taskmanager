import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine
from app.db.base import Base


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    # cria tabelas antes dos testes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # opcional: limpar depois
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac