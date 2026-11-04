# DevOps Platform Lab

> 🚧 Proje aktif olarak geliştiriliyor. README, eklenen her adımla birlikte güncellenir.

Production standartlarına yakın, uçtan uca bir DevOps platformu kurma projesi. Uygulama bilerek basit tutuldu; asıl odak CI/CD, Kubernetes, GitOps, gözlemlenebilirlik ve güvenlik.

## Şu An Neler Var

3 katmanlı bir Todo uygulaması:

| Katman | Teknoloji |
|--------|-----------|
| Frontend | React (Vite) |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Veritabanı | PostgreSQL |

Backend, sonraki adımlara hazır olacak şekilde şunları içerir:

- `/healthz` ve `/readyz` sağlık kontrolleri
- Environment variable ile konfigürasyon

## Yerelde Çalıştırma

### Docker Compose ile

Gereksinim: Docker

```bash
cd app
docker compose up --build
```

- Uygulama: http://localhost:3000
- API dokümanı: http://localhost:8000/docs

Durdurmak için `docker compose down`. Veritabanını da silmek için `docker compose down -v`.

### Geliştirme için (container'sız)

Gereksinimler: Python 3.13, Node.js 24, Docker

```bash
# 1. Veritabanı
docker run --name todo-db -e POSTGRES_USER=todo -e POSTGRES_PASSWORD=todo \
  -e POSTGRES_DB=todo -p 5432:5432 -d postgres:18-alpine

# 2. Backend
cd app/backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Frontend (ayrı terminalde)
cd app/frontend
npm install
npm run dev
```

- Uygulama: http://localhost:5173
- API dokümanı: http://localhost:8000/docs

## Test ve Lint

Unit testler veritabanı veya çalışan bir backend gerektirmez. Coverage %80'in altına düşerse komut hata verir.

```bash
# Backend: pytest (bellek içi SQLite ile) + Ruff
cd app/backend
pip install -r requirements-dev.txt
ruff check .
pytest --cov

# Frontend: Vitest + React Testing Library + ESLint
cd app/frontend
npm install
npm run lint
npm run test:coverage
```

## Repo Yapısı

```
app/backend/          FastAPI uygulaması, veritabanı migration'ları, testler ve Dockerfile
app/frontend/         React uygulaması, testler, Dockerfile ve Nginx ayarı
app/docker-compose.yml  3 katmanı birlikte çalıştıran yerel ortam
```

## Lisans

MIT
