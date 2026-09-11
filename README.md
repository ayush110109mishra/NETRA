<div align="center">
  <img src="apps/web/public/assets/netra-logo.png" alt="NETRA - Next-Generation Evidence & Tactical Reasoning Assistant" width="220" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="apps/web/public/assets/astraveda-logo.jpg" alt="Astraveda Defence" width="220" />

  # NETRA // Astraveda Defence

  **Next-Generation Evidence & Tactical Reasoning Assistant**  
  *Advanced Systems for Technological Research, Artificial Vision, Engineering & Deep-tech AI*

  > **"See. Understand. Respond."**  
  > AI-powered interactive defence intelligence and situational-awareness command platform.
</div>

---

## Foundation Phase Overview

NETRA is engineered as a high-density, mission-critical command-and-control platform. This initial foundation phase establishes the monorepo architecture, Express API infrastructure, tactical React client shell, and Prisma database configuration.

### Operational Guardrails
- **Human-in-the-loop**: AI services remain purely advisory.
- **Autonomous Weapon Prohibitions**: Weapon firing, autonomous attacks, and targeting routines are strictly disallowed by system doctrine.
- **Strict Separation of Concerns**: Clean Controller → Service → Data Access layering.

---

## Monorepo Architecture

```
NETRA/
├── apps/
│   ├── web/                    # React 18, Vite, TypeScript, Tailwind CSS, TanStack Query
│   └── api/                    # Express.js, TypeScript, Zod, Structured Logger, Correlation ID
├── packages/
│   └── shared/                 # Common TypeScript contracts, API envelopes, constants
├── prisma/
│   └── schema.prisma           # PostgreSQL database schema and migration baseline
├── docs/                       # Architecture & Setup documentation
├── .env.example                # Environment variables template
└── package.json                # Root workspaces configuration
```

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router, Lucide React, Recharts, Framer Motion |
| **Backend** | Node.js, Express.js, TypeScript, Zod, UUID, CORS |
| **Database** | PostgreSQL, Prisma ORM |
| **Architecture** | Monorepo with npm workspaces, Controller-Service-Repository pattern |

---

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Setup
```bash
# Copy template to .env
cp .env.example .env
```

### 3. Start Development Servers
```bash
npm run dev
```

- **Frontend Command Display**: [http://localhost:5173](http://localhost:5173)
- **Backend API Root**: [http://localhost:5000/api/v1](http://localhost:5000/api/v1)
- **Machine-Readable Health Endpoint**: [http://localhost:5000/api/v1/health](http://localhost:5000/api/v1/health)

---

## Quality & Verification

```bash
# Run strict TypeScript type checks across all workspaces
npm run typecheck

# Run production build across all workspaces
npm run build
```

---

## Licensing & Compliance
Proprietary software developed by Astraveda Defence. All rights reserved.
