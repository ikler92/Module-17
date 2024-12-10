from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from app.backend.db_depends import get_db
from app.models import *
from app.schemas import *
from slugify import slugify
from typing import List

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


# Получение всех пользователей
@router.get("/")
def all_users(db: Session = Depends(get_db)):
    query = select(User)
    result = db.execute(query).scalars().all()
    return result


# Получение пользователя по ID
@router.get("/{user_id}")
def user_by_id(user_id: int, db: Session = Depends(get_db)):
    query = select(User).where(User.id == user_id)
    result = db.execute(query).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return result


@router.get("/{user_id}/tasks", response_model=List[CreateTask])
def tasks_by_user_id(user_id: int, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    user_query = select(User).where(User.id == user_id)
    user = db.execute(user_query).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Получаем задачи пользователя
    query = select(Task).where(Task.user_id == user_id)
    tasks = db.execute(query).scalars().all()
    return tasks


# Создание нового пользователя
@router.post("/create")
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    slug = slugify(user.username)
    new_user = {
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "age": user.age,
        "slug": slug,
    }
    try:
        stmt = insert(User).values(**new_user)
        db.execute(stmt)
        db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")


# Обновление пользователя
@router.put("/update/{user_id}")
def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            firstname=user.firstname,
            lastname=user.lastname,
            age=user.age,
        )
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User was not found")
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}


# Удаление пользователя
@router.delete("/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Удаляем связанные задачи
    delete_tasks_stmt = delete(Task).where(Task.user_id == user_id)
    db.execute(delete_tasks_stmt)

    # Удаляем пользователя
    delete_user_stmt = delete(User).where(User.id == user_id)
    result = db.execute(delete_user_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User was not found")

    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User and related tasks deleted successfully"}

