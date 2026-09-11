import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { sendError } from '../utils/response.js';

export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly isOperational: boolean;

  constructor(message: string, statusCode: number = 500, code: string = 'INTERNAL_ERROR') {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export function errorHandlerMiddleware(
  err: Error,
  req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _next: NextFunction
): void {
  // Handle Zod Schema Validation Errors
  if (err instanceof ZodError) {
    const details = err.issues.map((issue) => ({
      field: issue.path.join('.'),
      message: issue.message,
      code: issue.code,
    }));

    sendError(req, res, {
      code: 'VALIDATION_ERROR',
      message: 'Request payload validation failed',
      statusCode: 400,
      details,
    });
    return;
  }

  // Handle Known Application Operational Errors
  if (err instanceof AppError) {
    sendError(req, res, {
      code: err.code,
      message: err.message,
      statusCode: err.statusCode,
    });
    return;
  }

  // Unhandled / Internal Server Errors
  console.error(`💥 [ERROR] Unhandled Exception [REQ:${req.correlationId}]:`, err);

  sendError(req, res, {
    code: 'INTERNAL_SERVER_ERROR',
    message: process.env.NODE_ENV === 'production' ? 'An unexpected server error occurred' : err.message,
    statusCode: 500,
  });
}
