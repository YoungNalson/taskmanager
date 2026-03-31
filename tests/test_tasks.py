import pytest

@pytest.mark.asyncio
async def test_create_task(client):
    response = await client.post("/api/v1/tasks", json={
        "title": "Test task",
        "description": "Testing",
        "priority": "low"
    })

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Test task"
    assert data["completed"] is False