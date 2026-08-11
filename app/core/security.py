from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt

# import datetime
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import pbkdf2_sha256

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")


def get_hash(password: str):
    return pbkdf2_sha256.hash(password)


def compare_hash(password: str, hashed_password: str):
    return pbkdf2_sha256.verify(password, hashed_password)


# Функция для создания JWT токена с заданным временем жизни
def create_jwt_token(data: Dict):
    """
    Функция для создания JWT токена. Мы копируем входные данные, добавляем время истечения и кодируем токен.
    """
    to_encode = data.copy()  # Копируем данные, чтобы не изменить исходный словарь Задаем время истечения токена
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )  # Задаем время истечения токена

    to_encode.update({"exp": expire})  # Добавляем время истечения в данные токена
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )  # Кодируем токен с использованием секретного ключа и алгоритма


# Функция для получения пользователя из токена
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    """
    Функция для извлечения информации о пользователе из токена. Проверяем токен и извлекаем утверждение о пользователе.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )  # Декодируем токен с помощью секретного ключа
        return payload.get("sub")  # Возвращаем утверждение о пользователе (subject) из полезной нагрузки
    except jwt.ExpiredSignatureError:
        pass  # Обработка ошибки истечения срока действия токена
    except jwt.InvalidTokenError:
        pass  # Обработка ошибки недействительного токена
