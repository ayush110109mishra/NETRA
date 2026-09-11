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
├── ai-core/                    # Python Intelligence Core (FastAPI, Pydantic v2, Phases 1-6) [ATUL]
│   ├── anomaly/                # Phase 4 Anomaly & Risk attribution engine
│   ├── api/                    # FastAPI routes (/health, /intelligence, /anomalies, /fusion, /predictions)
│   ├── entities/               # Phase 3 Entity Intelligence & Focus Mode
│   ├── events/                 # Phase 2 Multi-event correlation & clustering
│   ├── fusion/                 # Phase 5 Multi-source sensor fusion & evidence ledger
│   ├── intelligence/           # Master domain orchestrators
│   ├── models/                 # Pydantic v2 domain schemas
│   ├── prediction/             # Phase 6 Predictive Intelligence & forecasting
│   ├── simulation/             # Operational synthetic scenarios
│   └── tests/                  # 248 unit & integration tests (100% passing)
├── apps/
│   ├── web/                    # React 18, Vite, Tailwind CSS, TanStack Query [AYUSH]
│   └── api/                    # Express.js, TypeScript, Correlation ID, Zod Env [AYUSH]
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
