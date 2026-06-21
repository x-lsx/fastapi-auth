from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from redis.exceptions import ConnectionError

from .postgres import engine
from .redis import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("Запуск приложения")
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключен успешно")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    try:
        await redis_client.ping()
        print("✅ Redis подключен успешно")
    except ConnectionError:
        print("❌ Ошибка подключения к Redis!")

    yield  

    print("Завершение работы приложения")
    
    await redis_client.aclose()
    
    await engine.dispose()
    
    print("Все соединения закрыты")