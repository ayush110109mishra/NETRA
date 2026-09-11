import { HealthCheckData } from '@netra/shared';
import { env } from '../config/env.js';
import { checkDatabaseConnection } from '../db/prisma.js';

export class HealthService {
  public static async getHealthStatus(): Promise<HealthCheckData> {
    const memory = process.memoryUsage();
    const dbStatus = await checkDatabaseConnection();

    // System is operational if core services run; degraded if db is configured but unreachable
    const status = dbStatus === 'DISCONNECTED' ? 'DEGRADED' : 'OPERATIONAL';

    return {
      status,
      service: 'NETRA Command Core API',
      version: '1.0.0-alpha',
      environment: env.NODE_ENV,
      uptimeSeconds: Math.floor(process.uptime()),
      timestamp: new Date().toISOString(),
      database: dbStatus,
      memory: {
        heapUsedMb: Math.round((memory.heapUsed / 1024 / 1024) * 100) / 100,
        heapTotalMb: Math.round((memory.heapTotal / 1024 / 1024) * 100) / 100,
        rssMb: Math.round((memory.rss / 1024 / 1024) * 100) / 100,
      },
    };
  }
}
