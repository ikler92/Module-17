from fastapi import FastAPI
from app.backend.db import Base, engine
from app.routers import user, task  # Импорт моделей

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to Taskmanager"}


app.include_router(task.router)
app.include_router(user.router)
