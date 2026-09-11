# NETRA Architecture Document

**Platform**: NETRA (AI-Powered Defence Intelligence & Situational Awareness Platform)  
**Company**: Astraveda Defence  
**Vision**: *"See. Understand. Respond."*  
**Core Guardrail**: AI is strictly advisory and human-controlled. Autonomous weapons or attacks are prohibited.

---

## 1. System Topology

```
                  OPERATOR WORKSTATION
                  (Browser / Command Shell)
                            │
                            ▼
                    ┌─────────────────┐
                    │  React + Vite   │
                    │  Tailwind CSS   │
                    │ TanStack Query  │
                    └────────┬────────┘
                             │
                      REST API (v1) / WebSocket
                             │
                             ▼
                    ┌─────────────────┐
                    │   Express API   │
                    │   TypeScript    │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │  Controller   │ │  Correlation  │ │  Centralized  │
   │     Layer     │ │  Middleware   │ │ Error Handler │
   └───────┬───────┘ └───────────────┘ └───────────────┘
           │
           ▼
   ┌───────────────┐
   │ Service Layer │
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐
   │  Data Access  │
   │  (Prisma ORM) │
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐
   │  PostgreSQL   │
   └───────────────┘
```

---

## 2. Monorepo Organization

```
NETRA/
├── apps/
│   ├── web/                    # React 18, Vite, Tailwind CSS, TanStack Query
│   └── api/                    # Express.js, TypeScript, Correlation ID, Zod Env
├── packages/
│   └── shared/                 # Common interfaces, API response envelopes, constants
├── prisma/
│   └── schema.prisma           # PostgreSQL schema definition and migrations
├── docs/                       # Architecture and Setup documentation
├── scripts/                    # Platform scripts
├── .env.example                # Environment variable template
└── package.json                # Monorepo workspaces root
```

---

## 3. Realtime Telemetry Architecture (Upcoming Phase)

```
[ Hardware Sensors / UAVs / Simulators ]
                   │
                   ▼
      [ Telemetry Gateway Layer ]
                   │ (Ingestion / Validation)
                   ▼
      [ NETRA Command Backend ]
                   │ (Broadcast)
                   ▼
    [ Socket.IO / WebSocket Stream ]
                   │
                   ▼
  [ Frontend Situational Awareness Display ]
```

---

## 4. AI Service Abstraction Architecture (Upcoming Phase)

The platform enforces a strict provider-agnostic abstraction layer:

```
[ NETRA Intelligence Controller ]
                   │
                   ▼
     [ IAIService Contract Interface ]
                   │
     ┌─────────────┴─────────────┐
     ▼                           ▼
[ Provider Adapter A ]    [ Provider Adapter B ]
(e.g., Local LLM / Ollama)  (e.g., Gemini / Vertex AI)
```

**Guardrail Policy**:
All AI analysis is flagged as **ADVISORY**. No state-altering or engagement command can be triggered without explicit human operator confirmation.
