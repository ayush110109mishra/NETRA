import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

declare global {
  namespace Express {
    interface Request {
      correlationId: string;
      startTime: number;
    }
  }
}

export function correlationIdMiddleware(req: Request, res: Response, next: NextFunction): void {
  const existingId = req.header('x-correlation-id') || req.header('x-request-id');
  const correlationId = existingId || `netra-${uuidv4()}`;

  req.correlationId = correlationId;
  req.startTime = Date.now();

  res.setHeader('X-Correlation-ID', correlationId);
  res.setHeader('X-Request-ID', correlationId);

  next();
}
