import pytest

@pytest.mark.anyio
async def test_create_task(client):
    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test task",
            "description": "Testing",
            "priority": "low",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Test task"
    assert data["description"] == "Testing"
    assert data["priority"] == "low"
    assert data["completed"] is False
    assert "id" in data


@pytest.mark.anyio
async def test_create_task_without_title(client):
    response = await client.post(
        "/api/v1/tasks",
        json={
            "description": "Testing",
            "priority": "low",
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_list_tasks(client):
    # cria uma task
    await client.post(
        "/api/v1/tasks",
        json={
            "title": "Task 1",
            "description": "Testing",
            "priority": "low",
        },
    )

    response = await client.get("/api/v1/tasks")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"