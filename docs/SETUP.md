# NETRA Platform Setup Guide

## Prerequisites

- **Node.js**: v20.x or v22.x or v24.x (Active LTS or Current)
- **npm**: v10.x or v11.x
- **PostgreSQL**: v14+ (Local instance or Docker container)

---

## 1. Environment Setup

Copy `.env.example` to `.env` in the root workspace:

```bash
cp .env.example .env
```

Update variables as appropriate:
- `DATABASE_URL`: PostgreSQL connection URI.
- `PORT`: Port for Express API (default: `5000`).
- `CORS_ORIGIN`: Allowed origins for API requests (default: `http://localhost:5173`).

---

## 2. Dependency Installation

From the repository root:

```bash
npm install
```

This installs dependencies across all workspaces (`apps/web`, `apps/api`, `packages/shared`).

---

## 3. Database Initialization (Prisma)

When PostgreSQL is available:

```bash
# Generate Prisma Client
npm run prisma:generate

# Apply migrations
npm run prisma:migrate
```

*Note*: The API core is designed to run gracefully even if the PostgreSQL instance is in standby, reporting database readiness via `/api/v1/health`.

---

## 4. Launching the Platform

### Development Mode (Both Frontend & Backend concurrently)

```bash
npm run dev
```

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:5000/api/v1`
- **Health Check**: `http://localhost:5000/api/v1/health`

### Launch Separately

```bash
# Start API only
npm run dev:api

# Start Web only
npm run dev:web
```

---

## 5. Verification Commands

```bash
# Run TypeScript compilation checks across all workspaces
npm run typecheck

# Build all packages and applications for production
npm run build
```
