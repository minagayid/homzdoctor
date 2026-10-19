# Google Cloud deployment: HomzDoctor

This guide builds separate Cloud Run services for the FastAPI API and the static React/NGINX frontend. The images now honor Cloud Run's injected `PORT`; the API image defaults to production mode, requires PostgreSQL and a non-placeholder secret, and does not package or seed demo accounts/medical records.

> **Prototype safety boundary:** HomzDoctor remains a research/demo system, not a clinically validated or compliant production health-record system. Doctor review and adherence views are currently system-wide and there is no doctor-to-patient/care-relationship assignment model. Local upload files are stored on the container filesystem. Do not put real patient data or medical images on Cloud Run until care-relationship authorization, audit/logging, retention/deletion, consent, regulatory, threat-model, and durable object-storage requirements have been independently implemented and reviewed.

## 1. Build and push the images

Set your Google Cloud project and create an Artifact Registry repository once:

```sh
gcloud config set project YOUR_PROJECT_ID
gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create homzdoctor --repository-format=docker --location=us-central1
```

Build/push immutable images from the repository root:

```sh
gcloud builds submit --region=us-central1 --config=cloudbuild.yaml .
gcloud builds submit --region=us-central1 --config=cloudbuild-frontend.yaml frontend
```

Image names will be:
- `us-central1-docker.pkg.dev/YOUR_PROJECT_ID/homzdoctor/homzdoctor-api:BUILD_ID`
- `us-central1-docker.pkg.dev/YOUR_PROJECT_ID/homzdoctor/homzdoctor-web:BUILD_ID`

The root `Dockerfile` builds only the API, while `frontend/Dockerfile` builds the static web client. The build contexts exclude local .env files, SQLite databases, patient uploads, test fixtures and `backend/core/seed.py`. The source/demo seeding module remains in Git for isolated local development; it is not included in production container images.

## 2. Configure PostgreSQL and secrets

Create a managed PostgreSQL database (Cloud SQL is one option) and a strong application signing secret. Store credentials in Secret Manager; don't put real secrets into Dockerfiles, YAML, images or Git.

Example secrets (input values interactively or through your approved secret-management process):

```sh
printf '%s' 'REPLACE_WITH_URL_ENCODED_POSTGRES_PASSWORD' | gcloud secrets create homzdoctor-db-password --data-file=-
openssl rand -base64 48 | tr -d '\n' | gcloud secrets create homzdoctor-secret-key --data-file=-
```

Create `homzdoctor-database-url` as a Secret Manager secret containing a PostgreSQL SQLAlchemy URL, for example for a Cloud SQL Unix socket:

```text
postgresql+asyncpg://DB_USER:URL_ENCODED_PASSWORD@/DB_NAME?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

Ensure Cloud Build's service account has `roles/artifactregistry.writer` on the `homzdoctor` Artifact Registry repository. Grant the Cloud Run API service identity `roles/cloudsql.client` and `roles/secretmanager.secretAccessor`; enable the Cloud SQL instance connection on the API service. For Unix-socket connections, set `DATABASE_SSL=off`; use TLS when connecting to PostgreSQL over TCP. Use URL-encoded credentials. `DATABASE_URL` must resolve to PostgreSQL via asyncpg; production rejects SQLite.

The API's production settings also require:
- `ENVIRONMENT=production` and `DEBUG=false`
- `SEED_DEMO_DATA=false`
- `SECRET_KEY` with at least 32 random characters and not a documented/example value
- `ALLOWED_ORIGINS` containing explicit bare HTTPS origins only (no wildcard)

Create the `homzdoctor-database-url` secret with the complete URL as its value. Create `homzdoctor-secret-key` with a new secret value. Do not use the sample strings from `backend/.env.example`.

## 3. Deploy the API first

The app is still a prototype, so use only synthetic/test data while validating this workflow. A temporary valid HTTPS origin can be used for bootstrap, then replace it after the web service has its URL. Set `MAX_FILE_SIZE=25165824` (24 MiB) because Cloud Run's HTTP/1 request size limit is 32 MiB; the app adds multipart overhead to this configured file limit.

```sh
gcloud run deploy homzdoctor-api \
  --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/homzdoctor/homzdoctor-api:BUILD_ID \
  --region=us-central1 --port=8080 --cpu=2 --memory=2Gi --timeout=300 \
  --add-cloudsql-instances=PROJECT_ID:REGION:INSTANCE_NAME \
  --set-env-vars=ENVIRONMENT=production,DEBUG=false,HOST=0.0.0.0,SEED_DEMO_DATA=false,DATABASE_SSL=off,ALLOWED_ORIGINS=https://bootstrap.invalid,MAX_FILE_SIZE=25165824 \
  --set-secrets=DATABASE_URL=homzdoctor-database-url:latest,SECRET_KEY=homzdoctor-secret-key:latest \
  --allow-unauthenticated
```

Copy the returned API URL, and set `BACKEND_HOST` to its hostname only (no `https://` and no path). The API service accepts unauthenticated network traffic so the NGINX frontend can proxy it; user-level API routes still require app-issued bearer tokens. Do not interpret public service reachability as public access to medical records.

## 4. Deploy the frontend

The NGINX image now listens on `PORT` (Cloud Run defaults to 8080) and supports a backend service over HTTPS with SNI and certificate verification. Deploy using the API hostname returned in the previous step:

```sh
gcloud run deploy homzdoctor-web \
  --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/homzdoctor/homzdoctor-web:BUILD_ID \
  --region=us-central1 --port=8080 --cpu=1 --memory=512Mi \
  --set-env-vars=BACKEND_HOST=YOUR_API_HOSTNAME,BACKEND_PORT=443,BACKEND_SCHEME=https,MAX_REQUEST_BODY_SIZE=25m \
  --allow-unauthenticated
```

NGINX routes `/api/*` and `/ws` to the API host. The frontend uses relative `/api/v1` paths by default, so the browser does not need to know or expose the API hostname. The API hostname must be the hostname only, e.g. `homzdoctor-api-xxxx-uc.a.run.app`.

After the web service deploys, copy its HTTPS URL and update the API CORS allowlist:

```sh
gcloud run services update homzdoctor-api --region=us-central1 --update-env-vars=ALLOWED_ORIGINS=https://YOUR_FRONTEND_SERVICE_URL_HOST
```

Replace `YOUR_FRONTEND_SERVICE_URL_HOST` with the actual frontend origin hostname only after `https://`, e.g. `homzdoctor-web-xxxx-uc.a.run.app`. Do not leave the bootstrap placeholder configured.

## 5. Local container checks

The regular local workflow remains unchanged. To run the frontend via Docker Compose, NGINX now listens on container port 8080 and local port mapping exposes it on 3000:

```sh
docker compose -f infra/docker/docker-compose.yml config
docker compose -f infra/docker/docker-compose.yml up --build
```

From the repository root, the cloud API image can be checked locally after supplying valid PostgreSQL/secret/origin environment variables:

```sh
docker build -t homzdoctor-api:local .
docker run --rm -p 8080:8080 --env PORT=8080 --env ENVIRONMENT=production --env DEBUG=false --env SEED_DEMO_DATA=false --env DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB' --env SECRET_KEY='REPLACE_WITH_A_LONG_RANDOM_SECRET_VALUE' --env ALLOWED_ORIGINS='https://your-test-web.example' homzdoctor-api:local
```

A database and secret are required for the production image to start; Docker build success alone does not validate database networking, migrations, or authentication end-to-end.

## 6. Persistence and medical-data warning

The API writes uploaded files under `UPLOAD_DIR`, which defaults to local storage. Cloud Run container files are ephemeral and each instance has its own filesystem, so files may disappear when an instance stops and may be unavailable from another instance. Moving only the database to Cloud SQL is **not** enough to make uploads durable. Before real patient data, implement and test a private Cloud Storage adapter with per-object authorization, lifecycle/deletion policies, retention rules, audit logging and approved data-processing/consent controls. Keep the local SQLite and generated upload files out of all production images.

The current doctor-review workflow is system-wide; it does not ensure a clinician is assigned to the patient. Do not use this deployment for real-world care until that authorization model is implemented, tested with cross-patient isolation tests, and reviewed for the relevant legal/regulatory requirements.

Official runtime references:
- [Cloud Run container contract](https://docs.cloud.google.com/run/docs/container-contract) — listen on `0.0.0.0` at the injected `PORT`.
- [Cloud Run quotas and limits](https://docs.cloud.google.com/run/quotas) — HTTP/1 requests are limited to 32 MiB.
