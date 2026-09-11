/**
 * NETRA Synthetic Data Store & Service Interface
 */

import {
  Event,
  Entity,
  Alert,
  Assessment,
  Evidence,
  CommandKpis,
  IntelligenceFeedItem,
  SystemStatus,
  AskNetraResponse,
} from '@netra/shared';
import {
  SYNTHETIC_KPIS,
  SYNTHETIC_SYSTEM_STATUS,
  SYNTHETIC_ASSESSMENT,
  SYNTHETIC_ENTITIES,
  SYNTHETIC_ALERTS,
  SYNTHETIC_EVENTS,
  SYNTHETIC_EVIDENCE,
  SYNTHETIC_FEED,
  getSyntheticAskResponse,
} from './data.js';

export class SyntheticDataStore {
  public static getKpis(): CommandKpis {
    return { ...SYNTHETIC_KPIS };
  }

  public static getSystemStatus(): SystemStatus {
    return {
      ...SYNTHETIC_SYSTEM_STATUS,
      timestamp: new Date().toISOString(),
      uptime_seconds: Math.floor(process.uptime()),
    };
  }

  public static getAssessment(): Assessment {
    return {
      ...SYNTHETIC_ASSESSMENT,
      timestamp: new Date().toISOString(),
    };
  }

  public static getEntities(filter?: { type?: string; status?: string }): Entity[] {
    let entities = [...SYNTHETIC_ENTITIES];
    if (filter?.type) {
      entities = entities.filter((e) => e.type.toLowerCase() === filter.type?.toLowerCase());
    }
    if (filter?.status) {
      entities = entities.filter((e) => e.status.toLowerCase() === filter.status?.toLowerCase());
    }
    return entities;
  }

  public static getEntityById(id: string): Entity | undefined {
    return SYNTHETIC_ENTITIES.find((e) => e.entity_id === id);
  }

  public static getAlerts(filter?: { severity?: string; status?: string }): Alert[] {
    let alerts = [...SYNTHETIC_ALERTS];
    if (filter?.severity) {
      alerts = alerts.filter((a) => a.severity.toLowerCase() === filter.severity?.toLowerCase());
    }
    if (filter?.status) {
      alerts = alerts.filter((a) => a.status.toLowerCase() === filter.status?.toLowerCase());
    }
    return alerts;
  }

  public static getEvents(filter?: { type?: string; severity?: string }): Event[] {
    let events = [...SYNTHETIC_EVENTS];
    if (filter?.type) {
      events = events.filter((e) => e.type.toLowerCase() === filter.type?.toLowerCase());
    }
    if (filter?.severity) {
      events = events.filter((e) => e.severity.toLowerCase() === filter.severity?.toLowerCase());
    }
    return events;
  }

  public static getEvidence(filter?: { entityId?: string; eventId?: string }): Evidence[] {
    let evidence = [...SYNTHETIC_EVIDENCE];
    if (filter?.entityId) {
      evidence = evidence.filter((e) => e.related_entity_id === filter.entityId);
    }
    if (filter?.eventId) {
      evidence = evidence.filter((e) => e.related_event_id === filter.eventId);
    }
    return evidence;
  }

  public static getFeed(): IntelligenceFeedItem[] {
    return [...SYNTHETIC_FEED];
  }

  public static askNetra(query: string): AskNetraResponse {
    return getSyntheticAskResponse(query);
  }
}
