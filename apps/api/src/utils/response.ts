import { Response, Request } from 'express';
import { ApiResponse, ApiErrorResponse, ApiErrorDetail } from '@netra/shared';

export function sendSuccess<T>(
  req: Request,
  res: Response,
  data: T,
  statusCode: number = 200
): Response {
  const latencyMs = req.startTime ? Date.now() - req.startTime : undefined;

  const responseBody: ApiResponse<T> = {
    success: true,
    data,
    meta: {
      requestId: req.correlationId || 'unknown',
      timestamp: new Date().toISOString(),
      latencyMs,
    },
  };

  return res.status(statusCode).json(responseBody);
}

export function sendError(
  req: Request,
  res: Response,
  options: {
    code: string;
    message: string;
    statusCode?: number;
    details?: ApiErrorDetail[];
  }
): Response {
  const { code, message, statusCode = 500, details } = options;
  const latencyMs = req.startTime ? Date.now() - req.startTime : undefined;

  const responseBody: ApiErrorResponse = {
    success: false,
    error: {
      code,
      message,
      details,
    },
    meta: {
      requestId: req.correlationId || 'unknown',
      timestamp: new Date().toISOString(),
      latencyMs,
    },
  };

  return res.status(statusCode).json(responseBody);
}
