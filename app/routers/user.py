from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from app.backend.db_depends import get_db
from app.models import User
from app.schemas import CreateUser, UpdateUser
from slugify import slugify

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
    stmt = delete(User).where(User.id == user_id)
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User was not found")
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User deletion is successful"}
