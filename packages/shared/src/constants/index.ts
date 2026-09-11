/**
 * Core Platform Constants
 */

export const APP_NAME = 'NETRA';
export const APP_COMPANY = 'Astraveda Defence';
export const APP_TAGLINE = 'See. Understand. Respond.';
export const APP_VERSION = '1.0.0-alpha';

export const API_VERSION = 'v1';

export const ROUTES = {
  DASHBOARD: '/',
  MISSIONS: '/missions',
  ASSETS: '/assets',
  INTELLIGENCE: '/intelligence',
  ALERTS: '/alerts',
  TELEMETRY: '/telemetry',
  DOCUMENTS: '/documents',
  ANALYTICS: '/analytics',
  AUDIT_LOGS: '/audit-logs',
  SETTINGS: '/settings',
} as const;

export type AppRoute = typeof ROUTES[keyof typeof ROUTES];
