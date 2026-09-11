import { Router } from 'express';
import { IntelligenceController } from '../../controllers/intelligence.controller.js';
import { authMiddleware } from '../../middlewares/auth.js';

export const intelligenceRouter = Router();

// Apply auth middleware foundation to intelligence routes
intelligenceRouter.use(authMiddleware);

// System Status & KPIs
intelligenceRouter.get('/system', IntelligenceController.getSystemStatus);
intelligenceRouter.get('/kpis', IntelligenceController.getKpis);

// Intelligence Domain Endpoints
intelligenceRouter.get('/assessment', IntelligenceController.getAssessment);
intelligenceRouter.get('/entities', IntelligenceController.getEntities);
intelligenceRouter.get('/entities/:id', IntelligenceController.getEntityById);
intelligenceRouter.get('/alerts', IntelligenceController.getAlerts);
intelligenceRouter.get('/events', IntelligenceController.getEvents);
intelligenceRouter.get('/evidence', IntelligenceController.getEvidence);
intelligenceRouter.get('/feed', IntelligenceController.getFeed);

// Interactive Query (Ask NETRA)
intelligenceRouter.post('/ask', IntelligenceController.askNetra);
