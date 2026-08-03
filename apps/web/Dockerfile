# syntax=docker/dockerfile:1

# ---- dependencies -----------------------------------------------------------
FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# Cache mount keeps the npm cache out of the layer and off the critical path.
# --no-audit/--no-fund avoid the post-install network calls that make npm's
# "Exit handler never called" bug fire inside containers.
RUN --mount=type=cache,target=/root/.npm npm ci --no-audit --no-fund

# ---- development ------------------------------------------------------------
# Used by docker compose. Source arrives through Compose Watch rather than a
# bind mount, so the host can never shadow the container's node_modules.
FROM node:22-slim AS dev
ENV NODE_ENV=development
WORKDIR /app
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node . .
USER node
EXPOSE 5175
CMD ["npm", "run", "dev"]

# ---- production build -------------------------------------------------------
FROM deps AS build
COPY . .
RUN npm run build

# ---- production runtime -----------------------------------------------------
# Unprivileged nginx: uid 101, listens on 8080, no root at any point.
FROM nginxinc/nginx-unprivileged:1.27-alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
