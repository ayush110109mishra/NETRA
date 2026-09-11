/**
 * NETRA Intelligence Domain Types & API Contracts (Phase 1)
 * Boundary between Ayush (Full-Stack/Operational) and Atul (Python AI Core)
 */

export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type EntityStatus = 'ACTIVE' | 'SURVEILLANCE' | 'STANDBY' | 'HOSTILE' | 'NEUTRAL' | 'UNKNOWN';

export interface LocationCoordinate {
  latitude: number;
  longitude: number;
  sector: string;
  elevationMeters?: number;
}

/**
 * Event Contract
 */
export interface Event {
  event_id: string;
  timestamp: string;
  type: string;
  severity: SeverityLevel;
  confidence: number; // 0 to 100
  risk_score: number; // 0 to 100
  entities: string[]; // Associated Entity IDs
  location: LocationCoordinate;
  assessment: string;
  evidence: string[]; // Associated Evidence IDs
  simulation: true;
}

/**
 * Entity Contract
 */
export interface Entity {
  entity_id: string;
  name: string;
  type: string;
  status: EntityStatus;
  risk_score: number; // 0 to 100
  anomaly_score: number; // 0 to 100
  confidence: number; // 0 to 100
  observations: number;
  related_events: string[];
  related_entities: string[];
  assessment: string;
  evidence_count: number;
  location?: LocationCoordinate;
  simulation: true;
}

/**
 * Alert Contract
 */
export interface Alert {
  alert_id: string;
  severity: SeverityLevel;
  timestamp: string;
  confidence: number; // 0 to 100
  risk_score: number; // 0 to 100
  title: string;
  description: string;
  entity_id?: string;
  event_id?: string;
  status: 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'RESOLVED';
  simulation: true;
}

/**
 * Assessment Contract
 */
export interface Assessment {
  assessment_id: string;
  title: string;
  answer: string;
  confidence: number; // e.g. 86%
  risk_score: number; // e.g. 72%
  priority: SeverityLevel;
  evidence_count: number;
  sources_count: number;
  contradictions_count: number;
  evidence: string[];
  related_events: string[];
  related_entities: string[];
  timestamp: string;
  simulation: true;
}

/**
 * Evidence Contract
 */
export interface Evidence {
  evidence_id: string;
  source: string;
  type: string;
  timestamp: string;
  relationship: string;
  confidence: number;
  reliability: 'CONFIRMED' | 'PROBABLE' | 'DOUBTFUL' | 'CANNOT_JUDGE';
  summary: string;
  related_entity_id?: string;
  related_event_id?: string;
  simulation: true;
}

/**
 * KPI Command Layer Contract
 */
export interface CommandKpis {
  alerts: number;
  events: number;
  entities: number;
  anomalies: number;
  risk: number; // Percentage, e.g. 72
  confidence: number; // Percentage, e.g. 86
  simulation: true;
}

/**
 * Intelligence Feed Item
 */
export interface IntelligenceFeedItem {
  id: string;
  timestamp: string;
  category: 'EVENT' | 'ENTITY' | 'ALERT' | 'ASSESSMENT' | 'SYSTEM';
  title: string;
  detail: string;
  severity?: SeverityLevel;
  simulation: true;
}

/**
 * Ask NETRA Contract
 */
export interface AskNetraQuery {
  query: string;
  context_sector?: string;
  include_evidence?: boolean;
}

export interface AskNetraResponse {
  query_id: string;
  query: string;
  response: string;
  confidence: number;
  sources_used: string[];
  recommended_actions: string[];
  guardrail_note: string;
  timestamp: string;
  simulation: true;
}
