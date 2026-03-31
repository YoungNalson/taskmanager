import os
from typing import Union

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import task as task_crud
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import PriorityEnum

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter()

PRIORITY_LABELS = {
    "high": "Alta",
    "medium": "Média",
    "low": "Baixa",
}

@router.get("/", response_class=HTMLResponse)
async def ui_home(
    request: Request,
    priority: Union[PriorityEnum, str] = "",
    completed: str = "",
    edit_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    if not priority:
        priority = None
    
    if completed == "":
        converted_completed = None
    else:
        converted_completed = completed.lower() == "true"

    tasks = await task_crud.get_tasks(db, priority, converted_completed)

    return templates.TemplateResponse(
        name="index.html",
        context={
            "tasks": tasks,
            "priority": priority,
            "completed": completed,
            "edit_id": edit_id,
            "priority_labels": PRIORITY_LABELS,
        },
        request=request,
    )


@router.post("/tasks/{task_id}/edit")
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

    return RedirectResponse(url="/", status_code=303)


@router.post("/tasks")
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

    return RedirectResponse(url="/", status_code=303)


@router.post("/tasks/{task_id}/complete")
async def complete_task_ui(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task(db, task_id)

    if task:
        await task_crud.update_task(
            db,
            task,
            TaskUpdate(completed=not task.completed),
        )

    return RedirectResponse(url="/", status_code=303)


@router.post("/tasks/{task_id}/delete")
async def delete_task_ui(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task(db, task_id)

    if task:
        await task_crud.delete_task(db, task)

    return RedirectResponse(url="/", status_code=303)