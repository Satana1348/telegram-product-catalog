# Telegram Product Catalog

Решение тестового задания: Telegram-бот, Telegram Mini App, Next.js App Router, FastAPI, PostgreSQL и MinIO.

## Архитектура

- Бот принимает у администратора фото с названием в `caption`.
- API валидирует входные данные, кладёт изображение в MinIO, метаданные - в PostgreSQL.
- Next.js выводит каталог и работает как обычная страница или внутри Telegram.
- Сервисы stateless: все данные лежат в PostgreSQL и MinIO, не в памяти контейнера.

## Запуск

1. Скопируйте `.env.example` в `.env`.
2. Укажите `BOT_TOKEN`, `ADMIN_TELEGRAM_ID`, публичный HTTPS `WEB_APP_URL` и секретный `INTERNAL_API_TOKEN`.
3. Запустите `docker compose up --build`.
4. Откройте `http://localhost:3000`.

MinIO Console: `http://localhost:9001`. Для Mini App используйте публичный HTTPS URL (при разработке - tunnel) как `WEB_APP_URL`.

## Проверка

```powershell
docker compose config
docker compose up --build
```

В Telegram выполните `/start`, затем от имени `ADMIN_TELEGRAM_ID` отправьте фото с названием товара в подписи.

## Безопасность

`.env` не коммитится. `INTERNAL_API_TOKEN` закрывает внутренний маршрут создания товара. В production замените открытый CORS на домен фронтенда.
