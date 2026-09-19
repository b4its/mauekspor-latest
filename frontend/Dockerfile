FROM node:22-alpine AS build
WORKDIR /app

# Create .npmrc with correct pnpm settings
RUN echo "fetch-retries=5" >> .npmrc && \
    echo "fetchretry-interval=20000" >> .npmrc && \
    echo "fetch-retry-max-timeout=120000" >> .npmrc

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
ENV PNPM_CONFIGURE_WEBPACK=false
RUN corepack enable && \
    export PNPM_HOME=/pnpm && \
    export PATH=$PNPM_HOME:$PATH && \
    (pnpm install --frozen-lockfile || pnpm install --no-frozen-lockfile --config.fetch-retries=5 --config.fetchRetryInterval=20000)

COPY . .
ARG VITE_API_BASE_URL=http://localhost:8015/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN pnpm build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOST=0.0.0.0
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "build/index.js"]
