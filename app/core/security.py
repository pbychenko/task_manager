import jwt
# import datetime
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from datetime import datetime, timezone, timedelta
from passlib.hash import pbkdf2_sha256


# OAuth2PasswordBearer извлекает токен из заголовка "Authorization: Bearer <token>"
# Параметр tokenUrl указывает маршрут, по которому клиенты смогут получить токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "mysecretkey"  # В реальной практике генерируйте ключ, например, с помощью 'openssl rand -hex 32', и храните его в безопасности
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Время жизни токена

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Задаем время истечения токена

    to_encode.update({"exp": expire})  # Добавляем время истечения в данные токена
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Кодируем токен с использованием секретного ключа и алгоритма

# Функция для получения пользователя из токена
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    """
    Функция для извлечения информации о пользователе из токена. Проверяем токен и извлекаем утверждение о пользователе.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Декодируем токен с помощью секретного ключа
        return payload.get("sub")  # Возвращаем утверждение о пользователе (subject) из полезной нагрузки
    except jwt.ExpiredSignatureError:
        pass  # Обработка ошибки истечения срока действия токена
    except jwt.InvalidTokenError:
        pass  # Обработка ошибки недействительного токена