/**
 * Platform Tactical & Operational System Contracts (Phase 1)
 */

export type SubsystemHealthState = 'OPERATIONAL' | 'ONLINE' | 'STANDBY' | 'DEGRADED' | 'OFFLINE' | 'SIMULATION' | 'CONNECTED' | 'READY';

/**
 * System Status Contract (Section 7 Specification)
 */
export interface SystemStatus {
  system: 'OPERATIONAL' | 'DEGRADED' | 'CRITICAL';
  backend: 'ONLINE' | 'OFFLINE';
  database: 'ONLINE' | 'STANDBY' | 'DISCONNECTED';
  ai_core: 'SIMULATION'; // Stated explicitly: Atul AI service is in simulation mode
  data_stream: 'CONNECTED' | 'DISCONNECTED' | 'STANDBY';
  websocket: 'READY' | 'CONNECTED' | 'DISCONNECTED';
  timestamp: string;
  uptime_seconds: number;
  simulation: true;
}

export type ThreatPostureLevel = 'DEFCON 5' | 'DEFCON 4' | 'DEFCON 3' | 'DEFCON 2' | 'DEFCON 1';

export type OperationalWatchStatus = 'NOMINAL' | 'ELEVATED' | 'CRITICAL' | 'STANDBY';

export type UserRole = 'ADMIN' | 'ANALYST' | 'OPERATOR' | 'VIEWER';

export interface UserSession {
  user_id: string;
  callsign: string;
  role: UserRole;
  clearance_level: string;
  station_id: string;
}

export interface SectorSummary {
  id: string;
  name: string;
  code: string;
  posture: OperationalWatchStatus;
}
