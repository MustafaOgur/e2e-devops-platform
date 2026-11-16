# E2E DevOps Platform

[![Backend Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=mustafaogur_todo-backend&metric=alert_status&branch=main)](https://sonarcloud.io/dashboard?id=mustafaogur_todo-backend&branch=main)
[![Frontend Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=mustafaogur_todo-frontend&metric=alert_status&branch=main)](https://sonarcloud.io/dashboard?id=mustafaogur_todo-frontend&branch=main)

Bir web uygulamasının koddan production benzeri bir Kubernetes ortamına kadar olan yolunu uçtan uca kuran DevOps projesi. Uygulama bilerek basit tutuldu (todo listesi); odak noktası test, güvenlik taraması, paketleme, GitOps ile dağıtım, dış erişim, gözlemlenebilirlik ve dayanıklılık.

## Mimari

```mermaid
flowchart LR
    dev([Geliştirici]) -->|PR / merge| app[(app repo)]
    app --> jenkins[Jenkins CI]
    jenkins -->|image push| hub[(Docker Hub)]
    jenkins -->|image tag commit| gitops[(gitops repo)]

    subgraph cluster["k3s cluster · Vagrant VM'leri · Ansible ile kurulum (infra repo)"]
        argocd[ArgoCD]
        lb[MetalLB] --> traefik[Traefik<br/>Gateway API]
        traefik --> fe[frontend]
        traefik --> be[backend]
        be --> db[(PostgreSQL)]
        prom[Prometheus] --> grafana[Grafana]
        loki[Loki + Alloy] --> grafana
    end

    argocd -.->|izler| gitops
    argocd -->|uygular| fe & be
    hub -.->|image| fe & be
    user([Kullanıcı]) -->|todo.test| lb
```

1. Değişiklik PR ile gelir; Jenkins testleri, taramaları ve image build'ini çalıştırır.
2. `main`'e merge edilince image'lar Docker Hub'a gönderilir ve gitops reposundaki image tag'leri Jenkins tarafından güncellenir.
3. Cluster içindeki ArgoCD gitops reposunu izler ve değişikliği uygular. Jenkins cluster'a erişmez (pull modeli).
4. Kullanıcı trafiği MetalLB'nin verdiği IP üzerinden Traefik'e (Gateway API) gelir ve frontend ile backend'e yönlendirilir.
5. Metrikler Prometheus'ta, loglar Loki'de toplanır ve Grafana'da izlenir.

## Repolar

| Repo | İçerik |
|------|--------|
| **e2e-devops-platform** (bu repo) | Uygulama kodu, testler, Dockerfile'lar, Jenkins CI/CD hattı |
| [e2e-devops-platform-infra](https://github.com/MustafaOgur/e2e-devops-platform-infra) | Vagrant ile VM'ler, Ansible ile k3s (ve alternatif olarak kubeadm) cluster kurulumu |
| [e2e-devops-platform-gitops](https://github.com/MustafaOgur/e2e-devops-platform-gitops) | Cluster'ın istenen durumu: ArgoCD, uygulama manifest'leri, dış erişim, izleme, loglama |

## Ekran Görüntüleri

| | |
|---|---|
| ![ArgoCD uygulamaları](docs/images/argocd-applications.png) | ![ArgoCD app-of-apps](docs/images/argocd-app-of-apps.png) |
| ArgoCD: cluster'daki tüm uygulamalar Git ile senkron | App-of-apps: `root` uygulaması diğerlerini yönetir |
| ![Backend dashboard](docs/images/grafana-backend.png) | ![Traefik dashboard](docs/images/grafana-traefik.png) |
| Backend RED metrikleri (istek, hata, gecikme) | Giriş noktası trafiği ve başarısız istek logları |
| ![Loglar](docs/images/grafana-logs.png) | ![Uygulama](docs/images/todo-app.png) |
| Grafana Logs Drilldown: Loki'deki servis logları | `http://todo.test` üzerinden uygulama |

## Teknolojiler

| Alan | Araçlar |
|------|---------|
| Uygulama | React, Vite, Nginx, FastAPI, SQLAlchemy, Alembic, PostgreSQL |
| Test ve kod kalitesi | pytest, Vitest, React Testing Library, Ruff, ESLint, SonarCloud |
| Güvenlik taraması | Trivy, pip-audit, npm audit |
| CI | Jenkins (Docker üzerinde), Docker Hub |
| Altyapı | Vagrant, VirtualBox, Ansible, k3s |
| CD | ArgoCD (GitOps, app-of-apps), Helm, Sealed Secrets |
| Ağ ve dış erişim | MetalLB, Traefik, Gateway API |
| Gözlemlenebilirlik | Prometheus, Grafana, Loki, Grafana Alloy, alarm kuralları (PrometheusRule) |
| Dayanıklılık | HorizontalPodAutoscaler, PodDisruptionBudget |

## Uygulama

| Endpoint | Açıklama |
|----------|----------|
| `/api/todos` | Todo CRUD API'si (`GET`, `POST`, `GET/PATCH/DELETE /{id}`) |
| `/healthz` | Liveness: süreç ayakta mı |
| `/readyz` | Readiness: veritabanına bağlanılabiliyor mu (değilse `503`) |
| `/metrics` | Prometheus metrikleri |
| `/docs` | OpenAPI dokümanı |

### Yapılandırma

Backend ortam değişkenleriyle yapılandırılır (`app/backend/.env.example`):

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `DATABASE_URL` | – (zorunlu) | `postgresql+psycopg://kullanıcı:şifre@host:5432/veritabanı` |
| `CORS_ORIGINS` | `http://localhost:5173` | İzin verilen origin'ler, virgülle ayrılmış |
| `LOG_LEVEL` | `INFO` | Log seviyesi |

Frontend'in API adresi build'e gömülmez; çalışma anında `config.js` dosyasından okunur (`API_URL`). Kubernetes'te bu dosya ConfigMap'ten gelir.

### Gözlemlenebilirlik

- **Metrikler:** `http_requests_total` (method, path, status) ve `http_request_duration_seconds`. `path` rota şablonudur (`/api/todos/{todo_id}`).
- **Loglar:** stdout'a JSON (`timestamp`, `level`, `logger`, `message`, `trace_id`; istek loglarında `method`, `path`, `status`, `duration_ms`).
- **İstek takibi:** Her isteğe bir `trace_id` atanır; yanıtta `X-Trace-ID` başlığıyla döner ve isteğin tüm log satırlarında bulunur.
- `/healthz`, `/readyz` ve `/metrics` istekleri metriklere ve istek loglarına dahil edilmez.

## CI/CD Hattı

`main`'e giden her PR ve `main`'e yapılan her merge, Docker içinde çalışan Jenkins üzerinde şu hattan geçer. Backend ve frontend paralel ilerler:

```mermaid
flowchart LR
    pr[PR veya main] --> install[Install]
    install --> dep[Dependency Scan]
    dep --> lint[Lint]
    lint --> test[Unit Test]
    test --> cov[Code Coverage]
    cov --> fs[Trivy FS]
    fs --> sonar[SonarCloud]
    sonar --> build[Docker Build]
    build --> img[Trivy Image]
    img --> main{main mi?}
    main -->|Evet| hub[(Docker Hub)]
    hub --> gitops[Update GitOps]
    main -->|Hayır| stop[Push yok]
```

![Jenkins pipeline](docs/images/jenkins-pipeline.png)

- Image'lar kısa commit SHA ile etiketlenir, `latest` kullanılmaz: [todo-backend](https://hub.docker.com/r/mustafaoqr/todo-backend), [todo-frontend](https://hub.docker.com/r/mustafaoqr/todo-frontend).
- **Update GitOps** aşaması gitops reposundaki backend, migration Job'ı ve frontend image tag'lerini yeni SHA ile günceller ve `main`'e commit'ler. Dağıtımı ArgoCD yapar.
- Hattı durduran durumlar: lint hatası, başarısız test, %80'in altında coverage, npm audit'in bulduğu kritik açık, Trivy'nin bulduğu düzeltmesi yayınlanmış kritik açık veya secret, SonarCloud quality gate'inin geçmemesi. pip-audit bulguları build'i durdurmaz, `UNSTABLE` olarak işaretler.
- `main` korumalıdır; PR'lar `continuous-integration/jenkins/pr-head` kontrolü geçmeden merge edilemez.
- Test, coverage ve güvenlik raporları JUnit XML, Cobertura XML ve JSON olarak yayınlanır.

### Pipeline ne zaman çalışır?

Pipeline, Jenkins'te **Multibranch Pipeline** job'ı olarak tanımlıdır ve `ci/Jenkinsfile` dosyasını kullanır. Jenkins yerel makinede çalıştığı için GitHub webhook'u kullanılmaz; Jenkins repoyu 2 dakikada bir tarar ve yeni commit bulursa pipeline'ı kendisi başlatır.

| Olay | Pipeline | Image push | GitOps güncellemesi |
|------|----------|------------|---------------------|
| PR yokken feature branch'e push | Çalışmaz | Hayır | Hayır |
| PR açılması veya PR'a yeni commit | Çalışır | Hayır | Hayır |
| PR'ın `main`'e merge edilmesi | Çalışır | Evet | Evet |

Bunu job'daki `main PR-*` branch filtresi sağlar.

## Hızlı Başlangıç

Gereksinim: Docker

```bash
cd app
docker compose up --build
```

| Adres | İçerik |
|-------|--------|
| http://localhost:3000 | Uygulama |
| http://localhost:8000/docs | API dokümanı |

Durdurmak için `docker compose down`, veritabanını da silmek için `docker compose down -v`.

Kubernetes üzerinde çalıştırmak için önce [infra](https://github.com/MustafaOgur/e2e-devops-platform-infra), ardından [gitops](https://github.com/MustafaOgur/e2e-devops-platform-gitops) reposundaki adımları izleyin.

## Geliştirme

Gereksinimler: Python 3.13, Node.js 24, Docker

```bash
# Veritabanı
docker run --name todo-db -e POSTGRES_USER=todo -e POSTGRES_PASSWORD=todo \
  -e POSTGRES_DB=todo -p 5432:5432 -d postgres:18-alpine

# Backend
cd app/backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (ayrı terminalde)
cd app/frontend
npm install
npm run dev                    # http://localhost:5173
```

### Test ve lint

Unit testler veritabanı veya çalışan bir backend gerektirmez. Coverage %80'in altına düşerse komut hata verir.

```bash
# app/backend
ruff check .
pytest --cov

# app/frontend
npm run lint
npm run test:coverage
```

## Jenkins'i Çalıştırma

```bash
cd ci/jenkins
docker compose up --build -d
```

Jenkins http://localhost:8080 adresinde açılır. İlk kurulumdan sonra gereken ayarlar:

| Ayar | Değer |
|------|-------|
| Credential'lar | `github-credentials`, `dockerhub-credentials`, `sonar-token`, `gitops-credentials` |
| Job türü | Multibranch Pipeline |
| Branch source | GitHub, fork PR keşfi kapalı |
| Script Path | `ci/Jenkinsfile` |
| Tarama | Periodically if not otherwise run, 2 dakika |
| Filter by name | `main PR-*` |

`gitops-credentials`: sadece gitops reposuna erişimi olan, Contents yazma yetkili fine-grained GitHub token'ı.

## Repo Yapısı

```text
app/
├── backend/            FastAPI uygulaması, migration'lar, testler, Dockerfile
├── frontend/           React uygulaması, testler, Dockerfile, Nginx ayarı
└── docker-compose.yml  3 katmanı birlikte çalıştıran yerel ortam
ci/
├── Jenkinsfile         CI/CD hattı
└── jenkins/            Jenkins image'ı, plugin listesi, Compose dosyası
docs/
└── images/             README ekran görüntüleri
```
