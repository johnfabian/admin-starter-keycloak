FROM node:22-alpine AS dependencies
WORKDIR /repo
RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY web/package.json web/package.json
RUN pnpm install --frozen-lockfile --filter @admin-starter/web...

FROM node:22-alpine AS build
WORKDIR /repo
RUN corepack enable
COPY --from=dependencies /repo/node_modules ./node_modules
COPY --from=dependencies /repo/web/node_modules ./web/node_modules
COPY . .
WORKDIR /repo/web
RUN pnpm build

FROM node:22-alpine
WORKDIR /repo
RUN corepack enable
ENV NODE_ENV=production
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY web/package.json web/package.json
RUN pnpm install --frozen-lockfile --prod --filter @admin-starter/web...
COPY --from=build /repo/web/build /repo/web/build
WORKDIR /repo/web
CMD ["pnpm", "start"]
