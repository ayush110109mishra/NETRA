import express, { Express } from 'express';
import cors from 'cors';
import { env } from './config/env.js';
import { correlationIdMiddleware } from './middlewares/correlationId.js';
import { requestLoggerMiddleware } from './middlewares/requestLogger.js';
import { errorHandlerMiddleware } from './middlewares/errorHandler.js';
import { sendError } from './utils/response.js';
import { v1Router } from './routes/v1/index.js';

export function createApp(): Express {
  const app = express();

  // Basic security and parsing middlewares
  app.disable('x-powered-by');
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true, limit: '10mb' }));

  // CORS Configuration
  app.use(
    cors({
      origin: (origin, callback) => {
        // Allow requests with no origin (like mobile apps, curl, server-to-server)
        if (!origin) return callback(null, true);
        if (env.corsOrigins.includes('*') || env.corsOrigins.includes(origin)) {
          return callback(null, true);
        }
        return callback(new Error(`CORS policy violation: Origin ${origin} not allowed`));
      },
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Correlation-ID', 'X-Request-ID'],
      exposedHeaders: ['X-Correlation-ID', 'X-Request-ID'],
    })
  );

  // Tactical Tracing & Logging Middleware
  app.use(correlationIdMiddleware);
  app.use(requestLoggerMiddleware);

  // Mount API Versioned Routes
  app.use(env.API_PREFIX, v1Router);

  // Fallback 404 Handler for undefined routes
  app.use((req, res) => {
    sendError(req, res, {
      code: 'ROUTE_NOT_FOUND',
      message: `Cannot ${req.method} ${req.originalUrl}`,
      statusCode: 404,
    });
  });

  // Centralized Error Handling Middleware
  app.use(errorHandlerMiddleware);

  return app;
}
