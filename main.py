import uvicorn
from fastapi import FastAPI

from app.api.endpoints.tasks import task_router
from app.api.endpoints.users import user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(task_router)

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "oddddtestk"}

if __name__ == "__main__":
    uvicorn.run(app="main:app")
# @app.get("/")
# def read_root():
#     return {"message": "Hello, taskmanager World!"}
