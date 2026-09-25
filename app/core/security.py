from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import pbkdf2_sha256

from app.api.schemas.user import UserRead
from app.core.config import settings
from app.core.exceptions import ForbiddenError
from app.utils.unitofwork import IUnitOfWork, UnitOfWork
from app.core.role_levels import RoleLevel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")


def get_hash(password: str):
    return pbkdf2_sha256.hash(password)


def compare_hash(password: str, hashed_password: str):
    return pbkdf2_sha256.verify(password, hashed_password)


def create_jwt_token(data: Dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_user_from_token(
    token: str = Depends(oauth2_scheme), uow: IUnitOfWork = Depends(UnitOfWork)
):
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")

    except jwt.ExpiredSignatureError:
        raise unauthorized

    except jwt.InvalidTokenError:
        raise unauthorized

    if user_id is None:
        raise unauthorized

    async with uow:
        user = await uow.user.find_one("id", int(user_id))

        if user is None:
            raise unauthorized

        return UserRead.model_validate(user)


def require_role(min_role: RoleLevel):
    async def dependency(user: UserRead = Depends(get_user_from_token)) -> UserRead:
        current_role_level = RoleLevel[user.role.upper()]

        if current_role_level < min_role:
            raise ForbiddenError("You do not have needed role permission")
        
        return user
    
    return dependency