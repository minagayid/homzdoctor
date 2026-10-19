# Multi-cloud container deployment for HomzDoctor

This repository provides two OCI images: root Dockerfile for the FastAPI backend and frontend/Dockerfile for the Vite-built React UI served by NGINX. Root compose.yaml brings the complete app up on one long-lived Docker host. Dockerfile.vercel files plus vercel.json describe a multi-service Vercel deployment.

Safety boundary: HomzDoctor is a research/demo system, not a clinically validated or compliant health-record system. Doctor review views are system-wide and uploads are stored locally. Do not use real patient data until resource-level care-relationship authorization, private durable object storage, audit logs, retention/deletion, consent and legal/regulatory review are implemented.

## 1. Full-stack deployment on a Docker VM

Suitable for AWS EC2, Oracle Cloud Compute, OVHcloud Public Cloud instances, or any Linux VM running Docker Engine + Compose v2.

Copy .env.compose.example to .env. Generate new secrets by running openssl rand -hex 32 twice and pasting the values into POSTGRES_PASSWORD and SECRET_KEY. Set ALLOWED_ORIGINS to the actual HTTPS website origin. Put TLS in front of the web container using the cloud load balancer or a maintained reverse proxy. Never expose PostgreSQL, Redis or Qdrant publicly.

~~~sh
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs --tail=200 api web
~~~

Open the web service on WEB_PORT (3000 by default) during synthetic-data validation. Named Postgres, Qdrant and upload volumes persist on that host's Docker data disk; configure backups and test restore. This is a single-host deployment, not a clustered deployment. Protect the host and keep images updated.

## 2. Build portable images for managed container services

~~~sh
docker build -t homzdoctor-api:local .
docker build -t homzdoctor-web:local frontend
~~~

Push both images to a registry the target provider can read. Create a backend/API service and frontend service, configuring networking, health check, TLS/ingress, environment, secrets, and external dependencies in the platform. The API requires ENVIRONMENT=production, DEBUG=false, SEED_DEMO_DATA=false, DATABASE_URL using PostgreSQL + asyncpg, SECRET_KEY with at least 32 random characters, explicit HTTPS ALLOWED_ORIGINS, and protected durable upload storage if files must survive instance replacement. Optional integrations include QDRANT_URL/QDRANT_API_KEY, REDIS_URL, HF_TOKEN or a private local-LLM endpoint.

Do not set a platform-reserved PORT through CLI flags when the host injects it. The generic image defaults to 8080 and honors the runtime PORT. Secret values belong in provider secret storage, not Dockerfile ENV or source control.

### Google Cloud Run

Build both immutable images from the repository source root:

~~~sh
gcloud builds submit --region=us-central1 --config=cloudbuild.yaml .
gcloud builds submit --region=us-central1 --config=cloudbuild-frontend.yaml .
~~~

The frontend Cloud Build step changes into frontend/ and uses that directory as Docker context. Deploy both images as separate services using GOOGLE_CLOUD_DEPLOYMENT.md. Cloud Run storage is ephemeral: keep PostgreSQL managed and do not rely on local uploads for important records.

### AWS

Use the same API and frontend images with ECS/Fargate or App Runner where the service's container contract is met. Push to ECR or another reachable OCI registry. Configure secrets, PostgreSQL networking, optional Redis/Qdrant networking, and frontend upstream. For one EC2 host, Compose is the simplest persistent option. Serverless/managed services do not share Docker named volumes.

### Oracle Cloud and OVHcloud

Use the OCI-compatible images with Oracle Container Instances, OCI Kubernetes Engine, OVHcloud Managed Kubernetes, or cloud VMs. For Kubernetes, provision PersistentVolumeClaims where data must survive pod replacement and use managed DB/object services or secure persistence adapters. For one VM, use Compose with backups on a persistent disk.

### Vercel container services

Vercel supports Dockerfile.vercel entrypoints for container services and top-level rewrites in vercel.json. Configure the Vercel project framework to Services so its services block is active. /api/* and /health route to FastAPI; all other paths go to NGINX frontend. These images default to port 80, the Vercel container default.

Configure DATABASE_URL, SECRET_KEY and ALLOWED_ORIGINS as backend service secrets. Attach managed PostgreSQL and configure vector/AI integrations only if needed. Vercel Services are in beta; the project must be configured to use the Services framework.

Vercel container functions are stateless and do not provide Compose named volumes. The API currently writes uploads to local container filesystem, so this target is only suitable for synthetic-data validation until uploads move to private durable object storage and the clinical authorization gaps above are closed. An external database alone does not make local file uploads durable.

## 3. Verification

~~~sh
python -m unittest discover -s backend/tests -v
docker compose --env-file .env.compose.example config
docker build -t homzdoctor-api:smoke .
docker build -t homzdoctor-web:smoke frontend
~~~

CI verifies the API image and a production API/PostgreSQL smoke flow, builds the frontend and checks NGINX serving, builds Vercel container entrypoints, and validates Compose configuration. A green image build is not proof of live deployment. After provisioning a provider, verify health, registration/login, an authenticated /api/v1/auth/me, frontend/API routing, database connectivity and restore behavior.

Official provider docs: https://vercel.com/kb/guide/docker ; https://vercel.com/docs/services/routing ; https://docs.cloud.google.com/run/docs/container-contract
