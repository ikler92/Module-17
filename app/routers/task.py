from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from app.backend.db_depends import get_db
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from typing import List

router = APIRouter(
    prefix="/task",
    tags=["task"]
)


# Получение всех заданий
@router.get("/", response_model=List[CreateTask])
def all_tasks(db: Session = Depends(get_db)):
    query = select(Task)
    result = db.execute(query).scalars().all()
    return result


# Получение задания по ID
@router.get("/{task_id}", response_model=CreateTask)
def task_by_id(task_id: int, db: Session = Depends(get_db)):
    query = select(Task).where(Task.id == task_id)
    result = db.execute(query).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Task was not found")
    return result


# Создание нового задания
@router.post("/create")
def create_task(task: CreateTask, user_id: int, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    user_query = select(User).where(User.id == user_id)
    user = db.execute(user_query).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    new_task = {
        "title": task.title,
        "content": task.content,
        "priority": task.priority,
        "user_id": user_id,  # Привязываем задачу к конкретному пользователю
    }
    try:
        stmt = insert(Task).values(**new_task)
        db.execute(stmt)
        db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create task")


# Обновление задания
@router.put("/update/{task_id}")
def update_task(task_id: int, task: UpdateTask, db: Session = Depends(get_db)):
    stmt = (
        update(Task)
        .where(Task.id == task_id)
        .values(
            title=task.title,
            content=task.content,
            priority=task.priority,
        )
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task was not found")
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Task update is successful!"}


# Удаление задания
@router.delete("/delete/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    stmt = delete(Task).where(Task.id == task_id)
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task was not found")
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Task deletion is successful"}
