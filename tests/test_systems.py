import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import DDL

import src.entities as entities
from src.database import SCHEMA_NAME, engine
from src.main import app
from src.models import CreatePlanet, Planet, CreateSystem, System


@pytest.fixture(scope="session", autouse=True)
async def session_cleanup():
    yield

    async with engine.begin() as conn:
        await conn.execute(
            DDL(
                'TRUNCATE "%(schema)s"."%(table)s" CASCADE',
                {"schema": SCHEMA_NAME, "table": entities.System.__tablename__},
            )
        )


async def test_system_creation():
    request = CreateSystem(name="test", supreme_commander="anas@gmail.com", supreme_commander_name="Sincere@april.biz")

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/systems?email=Sincere%40april.biz",
            content=request.model_dump_json(),
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 200, response.text

    system = System.model_validate_json(response.content)
    assert system.name == request.name
    assert system.supreme_commander == request.supreme_commander
    assert system.supreme_commander_name == request.supreme_commander_name
    assert system.id is not None
