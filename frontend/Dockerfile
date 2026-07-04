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

# Opt-in flag required by the base image's 15-local-resolvers.envsh: without
# it, that script no-ops and NGINX_LOCAL_RESOLVERS is never exported, so
# envsubst leaves "${NGINX_LOCAL_RESOLVERS}" un-substituted in nginx.conf.
ENV NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
