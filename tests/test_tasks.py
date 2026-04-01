import pytest

# ============================================================================
# POST /api/v1/tasks - CREATE TASK
# ============================================================================

@pytest.mark.anyio
async def test_create_task(client):
    """Test creating a task with all fields."""
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
async def test_create_task_minimal(client):
    """Test creating a task with only required fields."""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Minimal task",
            "priority": "medium",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Minimal task"
    assert data["description"] is None
    assert data["priority"] == "medium"
    assert data["completed"] is False


@pytest.mark.anyio
async def test_create_task_all_priorities(client):
    """Test creating tasks with all priority levels."""
    for priority in ["high", "medium", "low"]:
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": f"Task with {priority} priority",
                "priority": priority,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == priority


@pytest.mark.anyio
async def test_create_task_without_title(client):
    """Test creating a task without required title field returns 422."""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "description": "Testing",
            "priority": "low",
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_task_without_priority(client):
    """Test creating a task without required priority field returns 422."""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "No priority task",
            "description": "Testing",
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_task_invalid_priority(client):
    """Test creating a task with invalid priority returns 422."""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Invalid priority task",
            "priority": "invalid_priority",
        },
    )

    assert response.status_code == 422


# ============================================================================
# GET /api/v1/tasks - LIST TASKS
# ============================================================================

@pytest.mark.anyio
async def test_list_tasks(client):
    """Test listing tasks when one task exists."""
    # Create a task
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


@pytest.mark.anyio
async def test_list_tasks_empty(client):
    """Test listing tasks when no tasks exist."""
    response = await client.get("/api/v1/tasks")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.anyio
async def test_list_tasks_multiple(client):
    """Test listing multiple tasks."""
    # Create multiple tasks
    for i in range(3):
        await client.post(
            "/api/v1/tasks",
            json={
                "title": f"Task {i + 1}",
                "priority": "low",
            },
        )

    response = await client.get("/api/v1/tasks")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert all(isinstance(task, dict) for task in data)
    assert all("id" in task for task in data)


@pytest.mark.anyio
async def test_list_tasks_filter_by_priority(client):
    """Test listing tasks filtered by priority."""
    # Create tasks with different priorities
    await client.post(
        "/api/v1/tasks",
        json={"title": "High priority", "priority": "high"},
    )
    await client.post(
        "/api/v1/tasks",
        json={"title": "Low priority 1", "priority": "low"},
    )
    await client.post(
        "/api/v1/tasks",
        json={"title": "Low priority 2", "priority": "low"},
    )

    # Filter by high priority
    response = await client.get("/api/v1/tasks?priority=high")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "high"

    # Filter by low priority
    response = await client.get("/api/v1/tasks?priority=low")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["priority"] == "low" for task in data)


@pytest.mark.anyio
async def test_list_tasks_filter_by_completed(client):
    """Test listing tasks filtered by completion status."""
    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={"title": "Task to complete", "priority": "high"},
    )
    task_id = create_response.json()["id"]

    # Get incomplete tasks
    response = await client.get("/api/v1/tasks?completed=false")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] is False

    # Mark task as completed
    await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"completed": True},
    )

    # Get completed tasks
    response = await client.get("/api/v1/tasks?completed=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] is True

    # Get incomplete tasks (should be empty now)
    response = await client.get("/api/v1/tasks?completed=false")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.anyio
async def test_list_tasks_filter_by_priority_and_completed(client):
    """Test listing tasks filtered by both priority and completion status."""
    # Create multiple tasks
    create_resp_1 = await client.post(
        "/api/v1/tasks",
        json={"title": "High priority incomplete", "priority": "high"},
    )
    task_id_1 = create_resp_1.json()["id"]

    create_resp_2 = await client.post(
        "/api/v1/tasks",
        json={"title": "High priority complete", "priority": "high"},
    )
    task_id_2 = create_resp_2.json()["id"]

    await client.post(
        "/api/v1/tasks",
        json={"title": "Low priority incomplete", "priority": "low"},
    )

    # Mark second task as completed
    await client.put(f"/api/v1/tasks/{task_id_2}", json={"completed": True})

    # Filter by high priority and incomplete
    response = await client.get("/api/v1/tasks?priority=high&completed=false")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High priority incomplete"
    assert data[0]["priority"] == "high"
    assert data[0]["completed"] is False


# ============================================================================
# GET /api/v1/tasks/{task_id} - GET SINGLE TASK
# ============================================================================

@pytest.mark.anyio
async def test_get_task(client):
    """Test retrieving a single task by ID."""
    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Get this task",
            "description": "Task description",
            "priority": "medium",
        },
    )

    task_id = create_response.json()["id"]

    # Retrieve the task
    response = await client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Get this task"
    assert data["description"] == "Task description"
    assert data["priority"] == "medium"
    assert data["completed"] is False


@pytest.mark.anyio
async def test_get_task_not_found(client):
    """Test retrieving a non-existent task returns 404."""
    response = await client.get("/api/v1/tasks/9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_get_completed_task(client):
    """Test retrieving a completed task."""
    # Create and complete a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={"title": "Task to complete", "priority": "low"},
    )

    task_id = create_response.json()["id"]

    await client.put(f"/api/v1/tasks/{task_id}", json={"completed": True})

    # Get the task
    response = await client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["completed"] is True


# ============================================================================
# PUT /api/v1/tasks/{task_id} - UPDATE TASK
# ============================================================================

@pytest.mark.anyio
async def test_update_task_all_fields(client):
    """Test updating all fields of a task."""
    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Original title",
            "description": "Original description",
            "priority": "low",
        },
    )

    task_id = create_response.json()["id"]

    # Update all fields
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "high",
            "completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Updated title"
    assert data["description"] == "Updated description"
    assert data["priority"] == "high"
    assert data["completed"] is True


@pytest.mark.anyio
async def test_update_task_partial_title(client):
    """Test updating only the title field."""
    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Original title",
            "description": "Original description",
            "priority": "low",
        },
    )

    task_id = create_response.json()["id"]

    # Update only title
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "New title"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New title"
    assert data["description"] == "Original description"
    assert data["priority"] == "low"


@pytest.mark.anyio
async def test_update_task_partial_priority(client):
    """Test updating only the priority field."""
    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Task",
            "priority": "low",
        },
    )

    task_id = create_response.json()["id"]

    # Update only priority
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"priority": "high"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Task"
    assert data["priority"] == "high"


@pytest.mark.anyio
async def test_update_task_toggle_completed(client):
    """Test toggling the completed status."""
    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={"title": "Task", "priority": "medium"},
    )

    task_id = create_response.json()["id"]

    # Mark as completed
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"completed": True},
    )

    assert response.json()["completed"] is True

    # Mark as incomplete
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"completed": False},
    )

    assert response.json()["completed"] is False


@pytest.mark.anyio
async def test_update_task_not_found(client):
    """Test updating a non-existent task returns 404."""
    response = await client.put(
        "/api/v1/tasks/9999",
        json={"title": "New title"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_update_task_clear_description(client):
    """Test clearing the description field."""
    # Create a task with description
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Task",
            "description": "Has description",
            "priority": "low",
        },
    )

    task_id = create_response.json()["id"]

    # Clear description by setting to None
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"description": None},
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


# ============================================================================
# DELETE /api/v1/tasks/{task_id} - DELETE TASK
# ============================================================================

@pytest.mark.anyio
async def test_delete_task(client):
    """Test deleting a task."""
    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={"title": "Task to delete", "priority": "low"},
    )

    task_id = create_response.json()["id"]

    # Delete the task
    response = await client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()

    # Verify task is deleted
    get_response = await client.get(f"/api/v1/tasks/{task_id}")

    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_delete_task_not_found(client):
    """Test deleting a non-existent task returns 404."""
    response = await client.delete("/api/v1/tasks/9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_delete_task_removed_from_list(client):
    """Test that deleted task is removed from task list."""
    # Create two tasks
    create_resp_1 = await client.post(
        "/api/v1/tasks",
        json={"title": "Task 1", "priority": "low"},
    )
    task_id_1 = create_resp_1.json()["id"]

    await client.post(
        "/api/v1/tasks",
        json={"title": "Task 2", "priority": "low"},
    )

    # Delete first task
    await client.delete(f"/api/v1/tasks/{task_id_1}")

    # List should only have one task
    response = await client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 2"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.anyio
async def test_full_task_lifecycle(client):
    """Test complete task lifecycle: create, read, update, delete."""
    # Create
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Lifecycle task",
            "description": "Testing full lifecycle",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    # Read
    get_response = await client.get(f"/api/v1/tasks/{task_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Lifecycle task"

    # Update
    update_response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": "Updated lifecycle task",
            "completed": True,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated lifecycle task"
    assert update_response.json()["completed"] is True

    # Delete
    delete_response = await client.delete(f"/api/v1/tasks/{task_id}")

    assert delete_response.status_code == 200

    # Verify deletion
    final_get = await client.get(f"/api/v1/tasks/{task_id}")

    assert final_get.status_code == 404


@pytest.mark.anyio
async def test_multiple_tasks_operations(client):
    """Test multiple concurrent operations on different tasks."""
    # Create multiple tasks
    task_ids = []
    for i in range(5):
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": f"Task {i + 1}",
                "priority": ["high", "medium", "low"][i % 3],
            },
        )
        task_ids.append(response.json()["id"])

    # Verify all were created
    list_response = await client.get("/api/v1/tasks")

    assert len(list_response.json()) == 5

    # Update some
    await client.put(f"/api/v1/tasks/{task_ids[0]}", json={"completed": True})
    await client.put(f"/api/v1/tasks/{task_ids[2]}", json={"completed": True})

    # Verify filter by completed
    completed_response = await client.get("/api/v1/tasks?completed=true")

    assert len(completed_response.json()) == 2

    # Delete one
    await client.delete(f"/api/v1/tasks/{task_ids[4]}")

    # Verify count
    final_list = await client.get("/api/v1/tasks")

    assert len(final_list.json()) == 4