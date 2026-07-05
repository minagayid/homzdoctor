# HomzDoctor - Deployment Guide

This guide provides comprehensive instructions for deploying HomzDoctor across different environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Deployment](#local-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [GitHub Actions CI/CD](#github-actions-cicd)
7. [Deployment Checklist](#deployment-checklist)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2)
- **CPU**: Minimum 2 cores, recommended 4+
- **RAM**: Minimum 4GB, recommended 8GB+
- **Disk**: Minimum 20GB for development, 50GB+ for production

### Required Tools

- Docker & Docker Compose (for containerized deployment)
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- kubectl (for Kubernetes deployment)
- Helm (optional, for K8s package management)

### Accounts & Credentials

- GitHub account with access to the repository
- Container registry (Docker Hub, GitHub Container Registry, or private registry)
- Cloud provider account (AWS, GCP, Azure) for production deployment
- Environment-specific API keys (Gemini, OpenAI, etc.)

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/minagayid/homzdoctor.git
cd homzdoctor
```

### 2. Create Environment Files

#### Backend (.env)

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:

```env
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database
DATABASE_URL=postgresql://homzdoctor:password@localhost:5432/homzdoctor
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# AI/ML
MEDGEMMA_MODEL_PATH=./ml/models/medgemma
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key

# Email (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

#### Frontend (.env)

```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENV=development
VITE_LOG_LEVEL=debug
```

## Local Deployment

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed database (optional)
python scripts/seed_db.py

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redis Admin: http://localhost:8081

## Docker Deployment

### Build Docker Images

```bash
# Build backend image
docker build -f infra/docker/Dockerfile.backend -t homzdoctor-backend:latest .

# Build frontend image
docker build -f infra/docker/Dockerfile.frontend -t homzdoctor-frontend:latest .
```

### Run with Docker Compose

```bash
cd infra/docker
docker-compose up -d
```

This starts:
- Backend (port 8000)
- Frontend (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Redis Admin UI (port 8081)

### Check Container Status

```bash
docker-compose ps
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Containers

```bash
docker-compose down
docker-compose down -v  # Also remove volumes
```

## Railway Deployment

### Backend (`homzdoctor` service)

- Root Directory must be set to `backend` and Builder must be `Dockerfile` (pinned explicitly in `backend/railway.json` — do not rely on Railpack auto-detection, which only scans the service's Root Directory for `main.py`/`app.py` and will fail with "No start command detected" if Root Directory is left at the repo root).
- The repo root must **not** contain a stray `requirements.txt` — Railpack treats its presence as "this is a Python project root" and then fails to find an entrypoint, since the real app lives in `backend/`.

### Frontend (`loyal-vitality` service)

`frontend/nginx.conf.template` proxies `/api` and `/ws` to the backend via `BACKEND_HOST`/`BACKEND_PORT` env vars (substituted at container start by nginx's built-in `envsubst-on-templates` entrypoint script). Set these on the `loyal-vitality` service:

- `BACKEND_HOST` = `${{homzdoctor.RAILWAY_PRIVATE_DOMAIN}}` (Railway reference variable to the backend's private networking domain)
- `BACKEND_PORT` = `${{homzdoctor.PORT}}`

Do not hardcode a static hostname (e.g. the docker-compose service name `api`) — nginx resolves `proxy_pass` hosts once at config load, and an unresolvable static host causes a hard crash (`host not found in upstream`) that crash-loops the container. The config instead resolves the backend at request time via `resolver ${NGINX_LOCAL_RESOLVERS}` + a `set`-based `proxy_pass`, so nginx starts and serves the static frontend even if the backend is briefly unavailable.

### ⚠️ Required services & environment variables (why the deploy "wasn't working")

The app runs on Railway even with nothing configured, but it silently degrades:
logins vanish and the AI returns canned answers. Fix all three below, then open
`https://<backend-domain>/api/v1/status` — every subsystem should read
`available: true` / `connected: true`.

**1. Persistent database (fixes disappearing logins).**
Without a database, the backend falls back to **SQLite on the container's
ephemeral disk**, which Railway wipes on every redeploy — so every registered
account is lost and login fails. Provision a real DB:

- In your Railway project: **New → Database → Add PostgreSQL**.
- On the `homzdoctor` backend service, add a reference variable:
  `DATABASE_URL = ${{Postgres.DATABASE_URL}}`
- That is all — the backend auto-rewrites `postgres://` → `postgresql+asyncpg://`,
  strips libpq-only params (`sslmode`, `channel_binding`) that the async driver
  rejects, and enables TLS for the managed host. See
  `backend/core/config.py:normalize_database_url`.

**2. AI models (fixes "no photo processing / no interactive LLM").**
The VLM (medical image reading) and LLM (chat) agents use the Hugging Face
Inference API. Without `HF_TOKEN` they return deterministic fallback text. Set on
the backend service:

- `HF_TOKEN` = a token from <https://huggingface.co/settings/tokens> (Read scope).
- `HF_MODEL` = `meta-llama/Llama-3.1-8B-Instruct` (or another chat model you can access).
- `HF_VLM_MODEL` = `Qwen/Qwen2.5-VL-7B-Instruct` (for a medical-tuned VLM, request
  access to `google/medgemma-4b-it` on its model page, then use it here).

  > Some models require an inference **provider**. If image analysis 404s, set
  > `HF_VLM_PROVIDER` (e.g. `hf-inference`, `nebius`, `together`).

**3. Vector DB / RAG (optional but recommended).**
Qdrant grounds the assistant in a curated knowledge base + the patient's own
records. Without it, chat still works but without retrieval.

- **Managed:** create a free cluster at <https://cloud.qdrant.io>, then set on the
  backend service: `QDRANT_URL = https://<cluster>.qdrant.io:6333` and
  `QDRANT_API_KEY = <key>`.
- **Self-hosted on Railway:** **New → Empty Service → Deploy from Docker image**
  `qdrant/qdrant:latest`, attach a Volume at `/qdrant/storage`, then set
  `QDRANT_URL = http://${{Qdrant.RAILWAY_PRIVATE_DOMAIN}}:6333` on the backend.
- Embeddings use the same `HF_TOKEN` (model `EMBEDDING_MODEL`, default MiniLM /
  `EMBEDDING_DIM=384`). The knowledge base is seeded automatically on startup.

**Also set** `SECRET_KEY` (any 32+ char random string) so JWTs are stable across
restarts.

#### Quick reference — backend service variables

| Variable | Required | Value |
|----------|----------|-------|
| `DATABASE_URL` | ✅ | `${{Postgres.DATABASE_URL}}` |
| `SECRET_KEY` | ✅ | random 32+ chars |
| `HF_TOKEN` | ✅ for AI | HF read token |
| `HF_MODEL` | ✅ for AI | `meta-llama/Llama-3.1-8B-Instruct` |
| `HF_VLM_MODEL` | ✅ for AI | `Qwen/Qwen2.5-VL-7B-Instruct` |
| `QDRANT_URL` | ⬜ for RAG | Qdrant Cloud URL or private domain |
| `QDRANT_API_KEY` | ⬜ for RAG | Qdrant Cloud key |
| `ALLOWED_ORIGINS` | recommended | your frontend domain |

After setting these, redeploy and verify: `curl https://<backend>/api/v1/status`.

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm (optional)

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace homzdoctor

# Create secrets
kubectl create secret generic homzdoctor-secrets \
  --from-literal=db-password=your-password \
  --from-literal=secret-key=your-secret \
  --from-literal=api-keys=your-api-keys \
  -n homzdoctor

# Apply Kubernetes manifests
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/postgres.yaml
kubectl apply -f infra/k8s/redis.yaml
kubectl apply -f infra/k8s/backend.yaml
kubectl apply -f infra/k8s/frontend.yaml
kubectl apply -f infra/k8s/ingress.yaml

# Verify deployment
kubectl get pods -n homzdoctor
kubectl get svc -n homzdoctor
```

### Port Forwarding (for local testing)

```bash
# Backend
kubectl port-forward -n homzdoctor svc/backend 8000:8000

# Frontend
kubectl port-forward -n homzdoctor svc/frontend 3000:80
```

### Scaling

```bash
# Scale backend replicas
kubectl scale deployment backend --replicas=3 -n homzdoctor

# Monitor scaling
kubectl watch deployment -n homzdoctor
```

## GitHub Actions CI/CD

### Available Workflows

The repository includes automated CI/CD workflows:

1. **Test** - Runs on every push to any branch
   - Backend tests (pytest)
   - Frontend tests (npm test)
   - Code linting

2. **Build** - Runs on every push
   - Build Docker images
   - Push to registry

3. **Deploy to Staging** - Runs on push to `develop` branch
   - Deploy to staging environment
   - Run smoke tests

4. **Deploy to Production** - Runs on release or manual trigger
   - Deploy to production
   - Run health checks

### Trigger Deployments

#### Via GitHub UI

1. Go to **Actions** tab
2. Select workflow: "Deploy to Production"
3. Click **Run workflow**
4. Choose target environment
5. Click **Run workflow**

#### Via Git Commands

```bash
# Trigger staging deployment
git push origin develop

# Trigger production deployment (via git tags)
git tag v1.0.0
git push origin v1.0.0
```

#### Via Workflow Dispatch

```bash
# Using GitHub CLI
gh workflow run deploy.yml -f environment=staging
```

### Configure GitHub Secrets

Required secrets for CI/CD:

```bash
# Container Registry
REGISTRY_USERNAME
REGISTRY_PASSWORD
REGISTRY_URL

# Database
DB_HOST
DB_USERNAME
DB_PASSWORD
DB_NAME

# API Keys
GEMINI_API_KEY
OPENAI_API_KEY

# Cloud Provider (AWS/GCP/Azure)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION

# Deployment
KUBECONFIG
DOCKER_REGISTRY_SECRET
```

Set these in repository Settings → Secrets and variables → Actions.

### Manual Deployment Steps

For full control, contributors can deploy manually:

```bash
# 1. Build images
docker build -t homzdoctor-backend:v1.0.0 -f infra/docker/Dockerfile.backend .
docker build -t homzdoctor-frontend:v1.0.0 -f infra/docker/Dockerfile.frontend .

# 2. Tag and push
docker tag homzdoctor-backend:v1.0.0 your-registry/homzdoctor-backend:v1.0.0
docker push your-registry/homzdoctor-backend:v1.0.0
docker push your-registry/homzdoctor-frontend:v1.0.0

# 3. Update manifests
sed -i 's/v[0-9.]*$/v1.0.0/g' infra/k8s/backend.yaml
sed -i 's/v[0-9.]*$/v1.0.0/g' infra/k8s/frontend.yaml

# 4. Deploy
kubectl apply -f infra/k8s/

# 5. Verify
kubectl rollout status deployment/backend -n homzdoctor
kubectl rollout status deployment/frontend -n homzdoctor
```

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code review completed
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] Secrets configured in CI/CD
- [ ] Container images built and pushed
- [ ] Backup created (for production)

### During Deployment

- [ ] Monitor logs for errors
- [ ] Verify health checks pass
- [ ] Test critical user flows
- [ ] Monitor resource usage (CPU, memory)
- [ ] Check database connections

### Post-Deployment

- [ ] Run smoke tests
- [ ] Verify API endpoints
- [ ] Check frontend loads
- [ ] Monitor error rates
- [ ] Verify authentication works
- [ ] Test file uploads
- [ ] Check email notifications

### Rollback Plan

```bash
# Kubernetes rollback
kubectl rollout undo deployment/backend -n homzdoctor
kubectl rollout undo deployment/frontend -n homzdoctor

# Check rollout history
kubectl rollout history deployment/backend -n homzdoctor
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
psql -h localhost -U homzdoctor -d homzdoctor

# Check connection string in .env
echo $DATABASE_URL
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -h localhost ping

# Check Redis URL in .env
echo $REDIS_URL
```

### Port Conflicts

```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Docker Image Build Failures

```bash
# Check Docker logs
docker build --verbose -f infra/docker/Dockerfile.backend .

# Prune unused images
docker system prune -a

# Build without cache
docker build --no-cache -f infra/docker/Dockerfile.backend .
```

### Kubernetes Pod Issues

```bash
# Check pod status
kubectl get pods -n homzdoctor

# Describe pod for events
kubectl describe pod <pod-name> -n homzdoctor

# Check pod logs
kubectl logs <pod-name> -n homzdoctor

# Interactive shell
kubectl exec -it <pod-name> -n homzdoctor -- /bin/bash
```

### Health Check Failures

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend health check
curl http://localhost:3000/health
```

## Support & Resources

- **Documentation**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Contributing**: See [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Issues**: https://github.com/minagayid/homzdoctor/issues
- **Discussions**: https://github.com/minagayid/homzdoctor/discussions

---

**Last Updated**: 2026-06-16
**Maintainer**: HomzDoctor Team
