import { createApp } from './app.js';
import { env } from './config/env.js';
import { getPrismaClient } from './db/prisma.js';
import { TacticalWebSocketServer } from './websocket/server.js';

const app = createApp();

const server = app.listen(env.PORT, () => {
  console.log(`\n======================================================`);
  console.log(`📡 NETRA Core Command API Online`);
  console.log(`Company: Astraveda Defence`);
  console.log(`Environment: ${env.NODE_ENV}`);
  console.log(`Listening: http://localhost:${env.PORT}${env.API_PREFIX}`);
  console.log(`Health Check: http://localhost:${env.PORT}${env.API_PREFIX}/health`);
  console.log(`WebSocket: ws://localhost:${env.PORT}/ws/telemetry`);
  console.log(`======================================================\n`);
});

// Initialize WebSocket server on HTTP listener
TacticalWebSocketServer.initialize(server);

// Graceful shutdown handling
const gracefulShutdown = async (signal: string) => {
  console.log(`\n⚠️  Received ${signal}. Terminating NETRA Core Command API gracefully...`);

  TacticalWebSocketServer.shutdown();

  server.close(async () => {
    try {
      const prisma = getPrismaClient();
      await prisma.$disconnect();
    } catch {
      // Ignore disconnect error during shutdown
    }
    console.log('✅ NETRA API server shutdown complete.');
    process.exit(0);
  });

  // Force close if graceful shutdown takes longer than 10 seconds
  setTimeout(() => {
    console.error('❌ Forcefully terminating NETRA API server (timeout).');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
