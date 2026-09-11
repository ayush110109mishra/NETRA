/**
 * System Health and Diagnostics Contract
 */

export type ServiceHealthStatus = 'OPERATIONAL' | 'DEGRADED' | 'OUTAGE';

export type DatabaseConnectionStatus = 'CONNECTED' | 'DISCONNECTED' | 'NOT_CONFIGURED';

export interface SystemMemoryInfo {
  heapUsedMb: number;
  heapTotalMb: number;
  rssMb: number;
}

export interface HealthCheckData {
  status: ServiceHealthStatus;
  service: string;
  version: string;
  environment: string;
  uptimeSeconds: number;
  timestamp: string;
  database: DatabaseConnectionStatus;
  memory: SystemMemoryInfo;
}
