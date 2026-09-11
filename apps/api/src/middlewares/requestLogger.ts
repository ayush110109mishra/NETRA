import { Request, Response, NextFunction } from 'express';

export function requestLoggerMiddleware(req: Request, res: Response, next: NextFunction): void {
  // Capture response finish
  res.on('finish', () => {
    const duration = req.startTime ? Date.now() - req.startTime : 0;
    const isoTimestamp = new Date().toISOString();
    const correlationId = req.correlationId || 'anonymous';
    const status = res.statusCode;

    // Tactical console logging format
    const statusColor =
      status >= 500
        ? '\x1b[31m' // Red
        : status >= 400
        ? '\x1b[33m' // Yellow
        : status >= 300
        ? '\x1b[36m' // Cyan
        : '\x1b[32m'; // Green
    const resetColor = '\x1b[0m';
    const dimColor = '\x1b[2m';

    console.log(
      `${dimColor}[${isoTimestamp}]${resetColor} ` +
      `[REQ:${correlationId.substring(0, 14)}...] ` +
      `${req.method.padEnd(6)} ${req.originalUrl} ` +
      `${statusColor}${status}${resetColor} ` +
      `${dimColor}(${duration}ms)${resetColor}`
    );
  });

  next();
}
