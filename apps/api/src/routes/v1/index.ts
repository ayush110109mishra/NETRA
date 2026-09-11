import { Router } from 'express';
import { healthRouter } from './health.router.js';
import { intelligenceRouter } from './intelligence.router.js';

export const v1Router = Router();

// Mount feature routers
v1Router.use('/', healthRouter);
v1Router.use('/', intelligenceRouter);
