import { PrismaClient } from '@prisma/client';
import { env } from '../config/env.js';

let prismaInstance: PrismaClient | null = null;

export function getPrismaClient(): PrismaClient {
  if (!prismaInstance) {
    prismaInstance = new PrismaClient({
      log: env.NODE_ENV === 'development' ? ['error', 'warn'] : ['error'],
    });
  }
  return prismaInstance;
}

export async function checkDatabaseConnection(): Promise<'CONNECTED' | 'DISCONNECTED' | 'NOT_CONFIGURED'> {
  if (!env.DATABASE_URL || env.DATABASE_URL.includes('placeholder')) {
    return 'NOT_CONFIGURED';
  }

  try {
    const client = getPrismaClient();
    // Test simple query with short timeout
    await client.$queryRaw`SELECT 1`;
    return 'CONNECTED';
  } catch {
    return 'DISCONNECTED';
  }
}
