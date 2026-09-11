# NETRA API Contract Specification (Phase 1)

**Platform**: NETRA (AI-Powered Defence Intelligence Workspace)  
**Company**: Astraveda Defence  
**Architectural Boundary**: Ayush (TypeScript / Full-Stack Interface) ⟷ Atul (Python AI / ML Intelligence Core)

---

## 1. Ownership & Boundary Principle

```text
ATUL (Python Intelligence Core)
AI/ML, Anomaly Detection, Event Correlation, Risk Scoring, Entity Intelligence, AI Query Engine
                              │
                              ▼ API CONTRACT
AYUSH (Full-Stack Operational Interface)
Frontend (React/TS), Backend API Gateway (Node/Express), Database, WebSockets, Dashboard, Map UI
```

> **Strict Rule**:
> - Ayush's Node.js API Gateway serves as the operational gateway.
> - For Phase 1, all intelligence endpoints return clearly marked **synthetic/demo data** (`simulation: true`).
> - No AI/ML algorithms or logic are duplicated in JavaScript/TypeScript.
> - When Atul's Python service is integrated, the data shapes defined in this contract will be retained.

---

## 2. Shared Domain Contracts

### 2.1 Event
```typescript
interface Event {
  event_id: string;             // Unique event identifier (e.g., "EVT-2026-0819")
  timestamp: string;            // ISO 8601 UTC timestamp
  type: string;                 // Event category (e.g., "RADAR_ANOMALY", "RF_INTERCEPT")
  severity: SeverityLevel;      // 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
  confidence: number;           // 0 to 100
  risk_score: number;           // 0 to 100
  entities: string[];           // Associated Entity IDs
  location: {
    latitude: number;
    longitude: number;
    sector: string;
    elevationMeters?: number;
  };
  assessment: string;           // Tactical narrative summary
  evidence: string[];           // Associated Evidence IDs
  simulation: true;             // Always true in Phase 1
}
```

### 2.2 Entity
```typescript
interface Entity {
  entity_id: string;            // e.g., "ENT-SIG-042"
  name: string;                 // Operational designation
  type: string;                 // "UAV", "RADAR_EMITTER", "SURFACE_VESSEL", "GROUND_NODE"
  status: EntityStatus;         // 'ACTIVE' | 'SURVEILLANCE' | 'STANDBY' | 'HOSTILE' | 'NEUTRAL' | 'UNKNOWN'
  risk_score: number;           // 0 to 100
  anomaly_score: number;        // 0 to 100
  confidence: number;           // 0 to 100
  observations: number;         // Count of sensor detections
  related_events: string[];     // IDs of linked events
  related_entities: string[];   // IDs of linked entities
  assessment: string;           // Entity operational context
  evidence_count: number;
  location?: LocationCoordinate;
  simulation: true;
}
```

### 2.3 Alert
```typescript
interface Alert {
  alert_id: string;             // e.g., "ALT-701"
  severity: SeverityLevel;      // 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
  timestamp: string;            // ISO 8601 UTC timestamp
  confidence: number;           // 0 to 100
  risk_score: number;           // 0 to 100
  title: string;
  description: string;
  entity_id?: string;
  event_id?: string;
  status: 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'RESOLVED';
  simulation: true;
}
```

### 2.4 Assessment
```typescript
interface Assessment {
  assessment_id: string;
  title: string;
  answer: string;               // Current tactical situation summary
  confidence: number;           // e.g., 86%
  risk_score: number;           // e.g., 72%
  priority: SeverityLevel;
  evidence_count: number;       // e.g., 12
  sources_count: number;        // e.g., 8
  contradictions_count: number; // e.g., 2
  evidence: string[];
  related_events: string[];
  related_entities: string[];
  timestamp: string;
  simulation: true;
}
```

### 2.5 System Status
```typescript
interface SystemStatus {
  system: 'OPERATIONAL' | 'DEGRADED' | 'CRITICAL';
  backend: 'ONLINE' | 'OFFLINE';
  database: 'ONLINE' | 'STANDBY' | 'DISCONNECTED';
  ai_core: 'SIMULATION';        // Explicit state for Atul AI service
  data_stream: 'CONNECTED' | 'DISCONNECTED' | 'STANDBY';
  websocket: 'READY' | 'CONNECTED' | 'DISCONNECTED';
  timestamp: string;
  uptime_seconds: number;
  simulation: true;
}
```

---

## 3. Endpoints Specification (REST API v1)

All responses follow the standard NETRA envelope:
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "requestId": "netra-...",
    "timestamp": "2026-09-12T00:36:00.000Z",
    "latencyMs": 4
  }
}
```

### `GET /api/v1/system`
Returns real-time subsystem readiness states:
- `system`: Overall platform health
- `backend`: Express API status
- `database`: PostgreSQL connection state
- `ai_core`: `"SIMULATION"`
- `data_stream`: Ingestion link state
- `websocket`: Realtime bridge state

### `GET /api/v1/kpis`
Returns aggregated command layer KPIs:
- `alerts`: 7
- `events`: 186
- `entities`: 73
- `anomalies`: 8
- `risk`: 72%
- `confidence`: 86%

### `GET /api/v1/events`
Returns chronological array of tactical events.
- Query params: `severity`, `type`, `limit`.

### `GET /api/v1/entities`
Returns tracked tactical entity intelligence records.
- Query params: `status`, `type`, `minRisk`.

### `GET /api/v1/alerts`
Returns active alerts sorted by severity.
- Query params: `status`, `severity`.

### `GET /api/v1/assessment`
Returns the current NETRA AI assessment summary with evidence indicators.

### `GET /api/v1/evidence`
Returns correlated evidence records supporting events and assessments.

### `POST /api/v1/ask`
Simulated natural language query processor for Ask NETRA.
- Request: `{ "query": string, "context_sector"?: string }`
- Response: `AskNetraResponse` with advisory response and guardrail notice.
