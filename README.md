# MultiModus

MultiModus — платформа для построения и эксплуатации рекомендательных систем для бизнеса с использованием табличных и текстовых данных.

## Особенности
- Мультибизнес-архитектура: каждый бизнес может загружать свои данные, обучать и использовать собственную модель.
- Поддержка табличных и текстовых признаков.
- Веб-интерфейс для управления бизнесами, загрузки данных, обучения моделей, получения рекомендаций и метрик.
- REST API для интеграции.
- Docker-окружение для быстрого запуска.

## Архитектура
- **Backend:** FastAPI, scikit-learn, SQLAlchemy, SQLite
- **Frontend:** React, Material UI
- **Данные:** JSONL (gzip), пример — openfoodfacts-products.jsonl.gz

## Быстрый старт
```bash
git clone <repo_url>
cd multimodal-recsys
docker-compose up --build
```
Frontend: http://localhost:3000  
Backend API: http://localhost:8000/docs

## Основные сценарии
1. Создать бизнес через UI или POST /businesses
2. Загрузить данные (jsonl.gz) через UI или POST /businesses/{id}/upload-data
3. Обучить модель (выбор признаков) через UI или POST /businesses/{id}/train
4. Получить рекомендации через UI или GET /businesses/{id}/recommend/{item_idx}
5. Посмотреть метрики через UI или GET /businesses/{id}/metrics

## Пример структуры данных
- projects/{business_id}/data.jsonl.gz — данные
- projects/{business_id}/model.pkl — обученная модель
- projects/{business_id}/logs.txt — логи обучения

## Зависимости
- Backend: FastAPI, scikit-learn, pandas, SQLAlchemy, uvicorn
- Frontend: React, Material UI, axios

