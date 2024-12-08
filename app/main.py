from fastapi import FastAPI
from routers import task_router, user_router

app = FastAPI()

app.include_router(task_router)
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Taskmanager"}
