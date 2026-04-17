# ──────────────────────────────────────────────────────────
# Nullify Web — Next.js 16
# Multi-stage: deps → build → runtime
# ──────────────────────────────────────────────────────────

# Stage 1 — Install dependencies
FROM node:20-alpine AS deps

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# Stage 2 — Build
FROM node:20-alpine AS builder

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Generate Prisma client
RUN pnpm exec prisma generate

# Build Next.js
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# Stage 3 — Production runtime
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy built output
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy Prisma schema (needed at runtime for migrations)
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/lib/generated ./lib/generated

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
