FROM node:22-alpine AS build
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml* ./
COPY apps/web/package.json apps/web/package.json
COPY packages/cop-types/package.json packages/cop-types/package.json
RUN pnpm install --filter @cop-studio/web... --no-frozen-lockfile
COPY apps/web apps/web
COPY packages/cop-types packages/cop-types
RUN pnpm --filter @cop-studio/web build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/apps/web/.next/standalone ./
COPY --from=build /app/apps/web/.next/static ./apps/web/.next/static
EXPOSE 3000
CMD ["node", "apps/web/server.js"]

