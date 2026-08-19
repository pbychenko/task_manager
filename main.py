import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.endpoints.tasks import task_router
from app.api.endpoints.users import user_router

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exceptions import NotFoundError, InvalidCredentialsError, ForbiddenError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI()

@app.exception_handler(ForbiddenError)
async def forbidden_error_handler(_: Request, exc: ForbiddenError):
    logger.exception("Forbidden error")

    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})

@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, exc: IntegrityError):
    logger.exception("Database integrity error")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Operation conflicts with existing data"},
    )

@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_error_handler(_: Request, exc: InvalidCredentialsError):
    logger.info("Invalid credentials error")

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


@app.exception_handler(SQLAlchemyError)
async def db_error_handler(_: Request, exc: SQLAlchemyError):
    logger.exception("Database error")          
    return JSONResponse(
        status_code=503,                        
        content={"detail": "Service temporarily unavailable"},
    )

@app.exception_handler(NotFoundError)
async def not_found_error_handler(_: Request, exc: NotFoundError):
    logger.exception("Not found error")

    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})



app.include_router(user_router)
app.include_router(task_router)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app")