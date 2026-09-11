import { Request, Response, NextFunction } from 'express';
import { UserRole, UserSession } from '@netra/shared';
import { sendError } from '../utils/response.js';

declare global {
  namespace Express {
    interface Request {
      user?: UserSession;
    }
  }
}

/**
 * Phase 1 Authentication Middleware Foundation
 * Populates request user context from header or assigns default simulated operator session
 */
export function authMiddleware(req: Request, _res: Response, next: NextFunction): void {
  // Check for operator identification header or bearer token
  const authHeader = req.header('authorization');
  const callsignHeader = req.header('x-operator-callsign');

  if (authHeader && authHeader.startsWith('Bearer ')) {
    // Session token structure ready for Phase 2 JWT / session verification
    req.user = {
      user_id: 'usr-analyst-01',
      callsign: callsignHeader || 'VIPER-01',
      role: 'ANALYST',
      clearance_level: 'SECRET',
      station_id: 'STN-ALPHA-C2',
    };
  } else {
    // Default simulated operational session for Phase 1 MVP
    req.user = {
      user_id: 'usr-operator-demo',
      callsign: callsignHeader || 'NETRA-OPERATOR',
      role: 'OPERATOR',
      clearance_level: 'CONFIDENTIAL',
      station_id: 'STN-DEMO-01',
    };
  }

  next();
}

/**
 * Role-based authorization guard foundation
 */
export function requireRole(allowedRoles: UserRole[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (!req.user || !allowedRoles.includes(req.user.role)) {
      sendError(req, res, {
        code: 'FORBIDDEN',
        message: 'Insufficient clearance level or unauthorized operational role',
        statusCode: 403,
      });
      return;
    }
    next();
  };
}
