import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.endpoints.tasks import task_router
from app.api.endpoints.users import user_router

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exceptions import NotFoundError


app = FastAPI()

@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, exc: IntegrityError):
    # logger.exception("Database integrity error")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Operation conflicts with existing data"},
    )

@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request, exc: SQLAlchemyError):
    # logger.exception("Database error")          # логируем полный traceback у себя
    return JSONResponse(
        status_code=503,                        # "сервис временно недоступен", не 500
        content={"detail": "Service temporarily unavailable"},
    )

@app.exception_handler(NotFoundError)
async def user_not_found_error_handler(_: Request, exc: NotFoundError):
    # logger.exception("User not found error")

    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(NotFoundError)
async def task_not_found_error_handler(_: Request, exc: NotFoundError):
    # logger.exception("Task not found error")

    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(PermissionError)
async def permission_error_handler(_: Request, exc: PermissionError):
    # logger.exception("Permission error")

    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})


app.include_router(user_router)
app.include_router(task_router)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app")