# BI Platform — каркас enterprise-платформы

Широкий production-ready каркас BI-платформы (аналог Tableau/Power BI/Metabase):
FastAPI + Clean Architecture на бэкенде, React + TypeScript на фронтенде,
визуальный стиль — по мотивам айдентики «Сбер» (см. `docs/DESIGN_SYSTEM.md`).

## Структура репозитория

```
backend/            FastAPI-приложение (Clean Architecture, async, Alembic)
  src/
    core/            конфиг, логирование, security, БД, кэш, метрики — общий фундамент
    shared/          Entity/AggregateRoot база, репозиторий-протоколы
    modules/
      auth/          пользователи, JWT, RBAC (роли/права)
      datasources/   подключение внешних БД/хранилищ (Postgres/ClickHouse), шифрование секретов
      dashboards/    дашборды, виджеты, исполнение запросов + Redis-кэш
  alembic/           миграции (async, autogenerate-ready)
  tests/             юнит-тесты (пример для use case)
frontend/            React 18 + TypeScript + Vite
  src/
    theme/           дизайн-токены (см. docs/DESIGN_SYSTEM.md)
    components/ui/   Card, Button, Badge, KpiTile, AppShell
    charts/          Line/Bar/Donut на Recharts, палитра по dataviz-методике
    pages/           демо-страница дашборда
deploy/
  k8s/               Deployment/Service/HPA для API и воркера
  prometheus.yml     пример scrape-конфига
docs/
  ARCHITECTURE.md    архитектура, ER-диаграмма, стратегия масштабирования
  DESIGN_SYSTEM.md   цвета/шрифты/палитра графиков (Sber-style, расчётная валидация)
docker-compose.yml   локальный dev-стек: postgres, pgbouncer, redis, minio, api, worker, frontend
```

## Быстрый старт (локально)

```bash
cp backend/.env.example backend/.env   # и отредактируйте секреты
docker compose up --build
# API:      http://localhost:8000/docs
# Frontend: http://localhost:5173
```

Применить миграции вручную (контейнер `api` уже делает это на старте):

```bash
cd backend && alembic upgrade head
```

## Тесты и линт (backend)

```bash
cd backend
pip install -e ".[dev]"
pytest
ruff check src
mypy src
```

## Ключевые архитектурные решения

См. `docs/ARCHITECTURE.md`: слоистая структура каждого модуля
(domain → application → infrastructure → presentation), ER-диаграмма,
поток исполнения виджета (кэш → коннектор → безопасная компиляция запроса),
и стратегия масштабирования до 10+ ТБ / 1000+ одновременных пользователей.

## Дизайн-система

См. `docs/DESIGN_SYSTEM.md`: бренд-токены, типографика (Golos Text —
открытый аналог фирменного SB Sans), и расчётная (CVD-валидированная через
`validate_palette.js`) палитра для графиков.
