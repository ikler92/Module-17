from fastapi import FastAPI
from app.backend.db import Base, engine
from app.models import user, task  # Импорт моделей

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to Taskmanager"}
