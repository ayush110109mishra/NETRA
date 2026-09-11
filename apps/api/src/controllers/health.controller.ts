import { Request, Response, NextFunction } from 'express';
import { HealthService } from '../services/health.service.js';
import { sendSuccess } from '../utils/response.js';

export class HealthController {
  public static async getHealth(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const healthData = await HealthService.getHealthStatus();
      sendSuccess(req, res, healthData, 200);
    } catch (err) {
      next(err);
    }
  }
}
