import { Router } from 'express';
import { HealthController } from '../../controllers/health.controller.js';

export const healthRouter = Router();

// GET /api/v1/health
healthRouter.get('/health', HealthController.getHealth);
