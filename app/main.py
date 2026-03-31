import os
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, engine
from app.db.base import Base
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud import task as task_crud
from app.models.task import PriorityEnum
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Task Manager API"}


@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task_crud.create_task(db, task)


@app.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    priority: PriorityEnum | None = Query(None),
    completed: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await task_crud.get_tasks(db, priority, completed)


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return await task_crud.update_task(db, task, updates)


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await task_crud.delete_task(db, task)

    return {"message": "Task deleted successfully"}


########
@app.get("/ui", response_class=HTMLResponse)
async def ui_home(
    request: Request,
    priority: PriorityEnum | None = None,
    completed: str = "",
    edit_id: int | None = None,  # 👈 novo
    db: AsyncSession = Depends(get_db),
):
    # conversão manual
    if completed == "":
        converted_completed = None
    elif completed is not None:
        converted_completed = completed.lower() == "true"
    
    tasks = await task_crud.get_tasks(db, priority, converted_completed)

    return templates.TemplateResponse(
        name="index.html",
        context={
            "tasks": tasks,
            "priority": priority,
            "completed": completed,
            "edit_id": edit_id,  # 👈 manda pro template
        },
        request = request,
    )


@app.post("/ui/tasks/{task_id}/edit")
async def edit_task_ui(
    task_id: int,
    title: str = Form(...),
    description: str = Form(None),
    priority: PriorityEnum = Form(...),
    completed: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await task_crud.update_task(
        db,
        task,
        TaskUpdate(
            title=title,
            description=description,
            priority=priority,
            completed=(completed == "on"),
        ),
    )

    return RedirectResponse(url="/ui", status_code=303)


@app.post("/ui/tasks")
async def create_task_ui(
    title: str = Form(...),
    description: str = Form(None),
    priority: PriorityEnum = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await task_crud.create_task(
        db,
        TaskCreate(
            title=title,
            description=description,
            priority=priority,
        ),
    )

    return RedirectResponse(url="/ui", status_code=303)


@app.post("/ui/tasks/{task_id}/complete")
async def complete_task_ui(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task(db, task_id)

    if task:
        await task_crud.update_task(
            db,
            task,
            TaskUpdate(completed=not task.completed),
        )

    return RedirectResponse(url="/ui", status_code=303)


@app.post("/ui/tasks/{task_id}/delete")
async def delete_task_ui(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task(db, task_id)

    if task:
        await task_crud.delete_task(db, task)

    return RedirectResponse(url="/ui", status_code=303)
########