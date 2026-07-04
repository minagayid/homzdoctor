# Frontend Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Defaults match the docker-compose service name/port for local dev.
# On Railway, override BACKEND_HOST/BACKEND_PORT with the homzdoctor
# service's private networking values (see DEPLOYMENT.md).
ENV BACKEND_HOST=api
ENV BACKEND_PORT=8000

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
