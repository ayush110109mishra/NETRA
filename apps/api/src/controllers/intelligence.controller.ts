import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { SyntheticDataStore } from '../synthetic/store.js';
import { sendSuccess, sendError } from '../utils/response.js';

const askQuerySchema = z.object({
  query: z.string().min(1, 'Query cannot be empty').max(500),
  context_sector: z.string().optional(),
  include_evidence: z.boolean().optional(),
});

export class IntelligenceController {
  public static getKpis(req: Request, res: Response, next: NextFunction): void {
    try {
      const kpis = SyntheticDataStore.getKpis();
      sendSuccess(req, res, kpis);
    } catch (err) {
      next(err);
    }
  }

  public static getSystemStatus(req: Request, res: Response, next: NextFunction): void {
    try {
      const status = SyntheticDataStore.getSystemStatus();
      sendSuccess(req, res, status);
    } catch (err) {
      next(err);
    }
  }

  public static getAssessment(req: Request, res: Response, next: NextFunction): void {
    try {
      const assessment = SyntheticDataStore.getAssessment();
      sendSuccess(req, res, assessment);
    } catch (err) {
      next(err);
    }
  }

  public static getEntities(req: Request, res: Response, next: NextFunction): void {
    try {
      const type = req.query.type as string | undefined;
      const status = req.query.status as string | undefined;
      const entities = SyntheticDataStore.getEntities({ type, status });
      sendSuccess(req, res, entities);
    } catch (err) {
      next(err);
    }
  }

  public static getEntityById(req: Request, res: Response, next: NextFunction): void {
    try {
      const { id } = req.params;
      const entity = SyntheticDataStore.getEntityById(id);
      if (!entity) {
        sendError(req, res, {
          code: 'ENTITY_NOT_FOUND',
          message: `Entity with ID ${id} was not found in synthetic registry`,
          statusCode: 404,
        });
        return;
      }
      sendSuccess(req, res, entity);
    } catch (err) {
      next(err);
    }
  }

  public static getAlerts(req: Request, res: Response, next: NextFunction): void {
    try {
      const severity = req.query.severity as string | undefined;
      const status = req.query.status as string | undefined;
      const alerts = SyntheticDataStore.getAlerts({ severity, status });
      sendSuccess(req, res, alerts);
    } catch (err) {
      next(err);
    }
  }

  public static getEvents(req: Request, res: Response, next: NextFunction): void {
    try {
      const type = req.query.type as string | undefined;
      const severity = req.query.severity as string | undefined;
      const events = SyntheticDataStore.getEvents({ type, severity });
      sendSuccess(req, res, events);
    } catch (err) {
      next(err);
    }
  }

  public static getEvidence(req: Request, res: Response, next: NextFunction): void {
    try {
      const entityId = req.query.entityId as string | undefined;
      const eventId = req.query.eventId as string | undefined;
      const evidence = SyntheticDataStore.getEvidence({ entityId, eventId });
      sendSuccess(req, res, evidence);
    } catch (err) {
      next(err);
    }
  }

  public static getFeed(req: Request, res: Response, next: NextFunction): void {
    try {
      const feed = SyntheticDataStore.getFeed();
      sendSuccess(req, res, feed);
    } catch (err) {
      next(err);
    }
  }

  public static askNetra(req: Request, res: Response, next: NextFunction): void {
    try {
      const validated = askQuerySchema.parse(req.body);
      const answer = SyntheticDataStore.askNetra(validated.query);
      sendSuccess(req, res, answer);
    } catch (err) {
      next(err);
    }
  }
}
