# HomzDoctor - Infrastructure

Infrastructure as Code for the HomzDoctor AI Healthcare Platform.

## Components

### Docker

- **Dockerfile**: Application container definitions
- **docker-compose.yml**: Local development stack
- **docker-compose.prod.yml**: Production stack

### Kubernetes

- **Deployments**: Application deployments
- **Services**: Load balancers and internal services
- **Ingress**: Traffic routing and SSL
- **ConfigMaps**: Application configuration
- **Secrets**: Sensitive data management
- **PVC**: Persistent volume claims

### Terraform

 Infrastructure modules for cloud deployment.

## Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n homzdoctor
```

## Terraform

```bash
# Initialize
cd terraform
terraform init

# Plan
terraform plan

# Apply
terraform apply
```

## Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and alerts
- **Sentry**: Error tracking
