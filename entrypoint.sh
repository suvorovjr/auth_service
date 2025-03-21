#!/bin/bash

echo "Ожидание PostgreSQL..."
echo данные - $SQL_HOST $SQL_PORT
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 5
done
echo "PostgreSQL готов!"

echo "Ожидание Redis..."
echo $REDIS_HOST $REDIS_PORT
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done
echo "Redis готов!"

echo "Применение миграций Alembic..."
alembic upgrade head

echo "Запуск приложения..."

uvicorn src.main:app --host 0.0.0.0 --port 8001