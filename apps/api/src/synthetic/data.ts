/**
 * NETRA Synthetic Intelligence Data Layer (Phase 1)
 * Strictly labelled as: SIMULATION // DEMO // SYNTHETIC DATA
 * Contains no classified or real operational defence data.
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

export const SYNTHETIC_KPIS: CommandKpis = {
  alerts: 7,
  events: 186,
  entities: 73,
  anomalies: 8,
  risk: 72,
  confidence: 86,
  simulation: true,
};

export const SYNTHETIC_SYSTEM_STATUS: SystemStatus = {
  system: 'OPERATIONAL',
  backend: 'ONLINE',
  database: 'ONLINE',
  ai_core: 'SIMULATION', // Explicitly marked: Python AI Core in simulation mode
  data_stream: 'CONNECTED',
  websocket: 'READY',
  timestamp: new Date().toISOString(),
  uptime_seconds: 1420,
  simulation: true,
};

export const SYNTHETIC_ASSESSMENT: Assessment = {
  assessment_id: 'ASM-2026-0912-ALPHA',
  title: 'ELEVATED MULTI-DOMAIN ACTIVITY DETECTED',
  answer:
    'Coordinated sensor anomalies and atypical RF telemetry observed across Northern Surveillance Grid. Uncorrelated radar track ENT-UAV-09 shows flight profile inconsistent with standard commercial aviation corridors. Cross-sensor confidence indicates deliberate reconnaissance posture.',
  confidence: 86,
  risk_score: 72,
  priority: 'HIGH',
  evidence_count: 12,
  sources_count: 8,
  contradictions_count: 2,
  evidence: ['EVD-RAD-101', 'EVD-SIG-204', 'EVD-OPT-309', 'EVD-COR-411'],
  related_events: ['EVT-2026-0819', 'EVT-2026-0820', 'EVT-2026-0822'],
  related_entities: ['ENT-UAV-09', 'ENT-RAD-44', 'ENT-GND-12'],
  timestamp: new Date().toISOString(),
  simulation: true,
};

export const SYNTHETIC_ENTITIES: Entity[] = [
  {
    entity_id: 'ENT-UAV-09',
    name: 'UNMANNED AERIAL TRACK 09',
    type: 'UAV',
    status: 'SURVEILLANCE',
    risk_score: 84,
    anomaly_score: 91,
    confidence: 88,
    observations: 47,
    related_events: ['EVT-2026-0819', 'EVT-2026-0820'],
    related_entities: ['ENT-RAD-44'],
    assessment: 'Persistent loiter pattern observed 14km north of Sector Alpha perimeter.',
    evidence_count: 5,
    location: {
      latitude: 28.712,
      longitude: 77.294,
      sector: 'HQ-ALPHA-NORTH',
      elevationMeters: 4200,
    },
    simulation: true,
  },
  {
    entity_id: 'ENT-RAD-44',
    name: 'EMITTER ARRAY 44',
    type: 'RADAR_EMITTER',
    status: 'ACTIVE',
    risk_score: 76,
    anomaly_score: 82,
    confidence: 84,
    observations: 38,
    related_events: ['EVT-2026-0820'],
    related_entities: ['ENT-UAV-09'],
    assessment: 'Phased array emission detected matching non-standard frequency hopping pattern.',
    evidence_count: 4,
    location: {
      latitude: 28.654,
      longitude: 77.382,
      sector: 'SECTOR-BRAVO',
      elevationMeters: 280,
    },
    simulation: true,
  },
  {
    entity_id: 'ENT-GND-12',
    name: 'MOBILE SENSOR CONVOY',
    type: 'GROUND_NODE',
    status: 'STANDBY',
    risk_score: 45,
    anomaly_score: 30,
    confidence: 92,
    observations: 64,
    related_events: ['EVT-2026-0822'],
    related_entities: ['ENT-UAV-09'],
    assessment: 'Allied mobile sensor relay establishing secondary triangulation baseline.',
    evidence_count: 3,
    location: {
      latitude: 28.581,
      longitude: 77.164,
      sector: 'HQ-ALPHA-SOUTH',
      elevationMeters: 210,
    },
    simulation: true,
  },
  {
    entity_id: 'ENT-SIG-18',
    name: 'ENCRYPTED DATA BURST SOURCE',
    type: 'RF_TRANSMITTER',
    status: 'UNKNOWN',
    risk_score: 68,
    anomaly_score: 74,
    confidence: 79,
    observations: 19,
    related_events: ['EVT-2026-0821'],
    related_entities: [],
    assessment: 'Intermittent Ku-band pulse emissions without registered flight plan or transponder.',
    evidence_count: 2,
    location: {
      latitude: 28.789,
      longitude: 77.215,
      sector: 'SECTOR-CHARLIE',
      elevationMeters: 850,
    },
    simulation: true,
  },
];

export const SYNTHETIC_ALERTS: Alert[] = [
  {
    alert_id: 'ALT-701',
    severity: 'CRITICAL',
    title: 'CORRIDOR BREACH: UNIDENTIFIED FLIGHT VECTOR',
    description: 'Track ENT-UAV-09 deviated 3.2nm inside restricted Northern Surveillance Buffer.',
    confidence: 94,
    risk_score: 92,
    entity_id: 'ENT-UAV-09',
    event_id: 'EVT-2026-0819',
    status: 'NEW',
    timestamp: new Date(Date.now() - 4 * 60000).toISOString(),
    simulation: true,
  },
  {
    alert_id: 'ALT-702',
    severity: 'HIGH',
    title: 'ATYPICAL RF EMISSION FREQUENCY DETECTED',
    description: 'Coordinated frequency modulation matching military-grade datalink signatures.',
    confidence: 87,
    risk_score: 85,
    entity_id: 'ENT-RAD-44',
    event_id: 'EVT-2026-0820',
    status: 'INVESTIGATING',
    timestamp: new Date(Date.now() - 18 * 60000).toISOString(),
    simulation: true,
  },
  {
    alert_id: 'ALT-703',
    severity: 'HIGH',
    title: 'SECONDARY SENSOR FUSION CORRELATION DEVIATION',
    description: 'Thermal infrared tracking conflicts with transponder return vector by 1.1km.',
    confidence: 82,
    risk_score: 78,
    entity_id: 'ENT-UAV-09',
    event_id: 'EVT-2026-0822',
    status: 'NEW',
    timestamp: new Date(Date.now() - 32 * 60000).toISOString(),
    simulation: true,
  },
  {
    alert_id: 'ALT-704',
    severity: 'MEDIUM',
    title: 'SURVEILLANCE RELAY LATENCY INCREASE',
    description: 'Ground telemetry relay experiencing packet jitter exceeding 180ms threshold.',
    confidence: 90,
    risk_score: 55,
    entity_id: 'ENT-GND-12',
    status: 'ACKNOWLEDGED',
    timestamp: new Date(Date.now() - 55 * 60000).toISOString(),
    simulation: true,
  },
  {
    alert_id: 'ALT-705',
    severity: 'LOW',
    title: 'ATMOSPHERIC RADAR ATTENUATION ADVISORY',
    description: 'Localized precipitation front inducing 4.2% S-band attenuation in Sector Bravo.',
    confidence: 96,
    risk_score: 28,
    status: 'ACKNOWLEDGED',
    timestamp: new Date(Date.now() - 90 * 60000).toISOString(),
    simulation: true,
  },
  {
    alert_id: 'ALT-706',
    severity: 'INFO',
    title: 'OPTICAL RECONNAISSANCE PASS SCHEDULED',
    description: 'Orbital pass EO satellite synchronization window open for 14 minutes.',
    confidence: 99,
    risk_score: 10,
    status: 'RESOLVED',
    timestamp: new Date(Date.now() - 140 * 60000).toISOString(),
    simulation: true,
  },
  {
    alert_id: 'ALT-707',
    severity: 'INFO',
    title: 'SIMULATED DATASET INTEGRITY VERIFIED',
    description: 'Phase 1 synthetic intelligence pipeline self-test passed with zero anomalies.',
    confidence: 100,
    risk_score: 0,
    status: 'RESOLVED',
    timestamp: new Date(Date.now() - 220 * 60000).toISOString(),
    simulation: true,
  },
];

export const SYNTHETIC_EVENTS: Event[] = [
  {
    event_id: 'EVT-2026-0819',
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
    type: 'PERIMETER_INCURSION',
    severity: 'CRITICAL',
    confidence: 94,
    risk_score: 92,
    entities: ['ENT-UAV-09'],
    location: {
      latitude: 28.712,
      longitude: 77.294,
      sector: 'HQ-ALPHA-NORTH',
      elevationMeters: 4200,
    },
    assessment: 'Unannounced flight profile breached buffer boundary at velocity 210 knots.',
    evidence: ['EVD-RAD-101', 'EVD-OPT-309'],
    simulation: true,
  },
  {
    event_id: 'EVT-2026-0820',
    timestamp: new Date(Date.now() - 20 * 60000).toISOString(),
    type: 'ELECTRONIC_EMISSION',
    severity: 'HIGH',
    confidence: 87,
    risk_score: 85,
    entities: ['ENT-RAD-44', 'ENT-UAV-09'],
    location: {
      latitude: 28.654,
      longitude: 77.382,
      sector: 'SECTOR-BRAVO',
      elevationMeters: 280,
    },
    assessment: 'Coordinated radar search pulse coincided with UAV ingress trajectory.',
    evidence: ['EVD-SIG-204'],
    simulation: true,
  },
  {
    event_id: 'EVT-2026-0821',
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    type: 'COMMUNICATION_BURST',
    severity: 'MEDIUM',
    confidence: 79,
    risk_score: 68,
    entities: ['ENT-SIG-18'],
    location: {
      latitude: 28.789,
      longitude: 77.215,
      sector: 'SECTOR-CHARLIE',
      elevationMeters: 850,
    },
    assessment: 'High-bandwidth encrypted upload burst lasting 340ms detected.',
    evidence: ['EVD-COR-411'],
    simulation: true,
  },
  {
    event_id: 'EVT-2026-0822',
    timestamp: new Date(Date.now() - 75 * 60000).toISOString(),
    type: 'SENSOR_TRIANGULATION',
    severity: 'LOW',
    confidence: 91,
    risk_score: 45,
    entities: ['ENT-GND-12', 'ENT-UAV-09'],
    location: {
      latitude: 28.581,
      longitude: 77.164,
      sector: 'HQ-ALPHA-SOUTH',
      elevationMeters: 210,
    },
    assessment: 'Passive RF triangulation confirmed emitter origin azimuth.',
    evidence: ['EVD-COR-411'],
    simulation: true,
  },
  {
    event_id: 'EVT-2026-0823',
    timestamp: new Date(Date.now() - 110 * 60000).toISOString(),
    type: 'BASELINE_CALIBRATION',
    severity: 'INFO',
    confidence: 98,
    risk_score: 12,
    entities: ['ENT-GND-12'],
    location: {
      latitude: 28.581,
      longitude: 77.164,
      sector: 'HQ-ALPHA-SOUTH',
    },
    assessment: 'Ground surveillance radar array zero-point calibration successful.',
    evidence: [],
    simulation: true,
  },
];

export const SYNTHETIC_EVIDENCE: Evidence[] = [
  {
    evidence_id: 'EVD-RAD-101',
    source: 'PRIMARY S-BAND RADAR (NETRA-01)',
    type: 'RADAR_RETURN',
    timestamp: new Date(Date.now() - 6 * 60000).toISOString(),
    relationship: 'Direct detection of ENT-UAV-09 flight track',
    confidence: 94,
    reliability: 'CONFIRMED',
    summary: 'Kinematic track confirms 210 kts ground speed, constant heading 194° towards buffer.',
    related_entity_id: 'ENT-UAV-09',
    related_event_id: 'EVT-2026-0819',
    simulation: true,
  },
  {
    evidence_id: 'EVD-SIG-204',
    source: 'ESM INTERCEPT RECEIVER (SIG-BRAVO)',
    type: 'RF_SPECTRUM',
    timestamp: new Date(Date.now() - 21 * 60000).toISOString(),
    relationship: 'Cross-correlated with ENT-RAD-44 emission schedule',
    confidence: 89,
    reliability: 'PROBABLE',
    summary: '9.4 GHz pulsed signal with pulse repetition frequency matching search doctrine.',
    related_entity_id: 'ENT-RAD-44',
    related_event_id: 'EVT-2026-0820',
    simulation: true,
  },
  {
    evidence_id: 'EVD-OPT-309',
    source: 'LONG-RANGE EO/IR TURRET (CAM-ALPHA)',
    type: 'THERMAL_IMAGERY',
    timestamp: new Date(Date.now() - 7 * 60000).toISOString(),
    relationship: 'Visual verification of UAV twin-boom airframe',
    confidence: 91,
    reliability: 'CONFIRMED',
    summary: 'Mid-wave IR silhouette corresponds to medium-altitude surveillance airframe.',
    related_entity_id: 'ENT-UAV-09',
    related_event_id: 'EVT-2026-0819',
    simulation: true,
  },
  {
    evidence_id: 'EVD-COR-411',
    source: 'GROUND ACOUSTIC & SEISMIC ARRAY (GEO-SOUTH)',
    type: 'ACOUSTIC_PROFILE',
    timestamp: new Date(Date.now() - 76 * 60000).toISOString(),
    relationship: 'Corroboration of low-altitude ground convoy movement',
    confidence: 86,
    reliability: 'PROBABLE',
    summary: 'Heavy diesel engine acoustic signature corroborates friendly convoy position.',
    related_entity_id: 'ENT-GND-12',
    related_event_id: 'EVT-2026-0822',
    simulation: true,
  },
];

export const SYNTHETIC_FEED: IntelligenceFeedItem[] = [
  {
    id: 'FEED-01',
    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
    category: 'ALERT',
    title: 'ALT-701 FLIGHT CORRIDOR BREACH',
    detail: 'Entity ENT-UAV-09 crossed northern perimeter vector. Severity: CRITICAL.',
    severity: 'CRITICAL',
    simulation: true,
  },
  {
    id: 'FEED-02',
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
    category: 'ASSESSMENT',
    title: 'AI ASSESSMENT UPDATED [SIMULATED]',
    detail: 'Confidence rose to 86% based on multi-sensor correlation across Sector Alpha.',
    severity: 'HIGH',
    simulation: true,
  },
  {
    id: 'FEED-03',
    timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
    category: 'ENTITY',
    title: 'ENTITY RISK RE-EVALUATED',
    detail: 'ENT-RAD-44 risk rating adjusted to 76% following frequency analysis.',
    severity: 'MEDIUM',
    simulation: true,
  },
  {
    id: 'FEED-04',
    timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
    category: 'SYSTEM',
    title: 'DATA STREAM SYNCHRONIZED',
    detail: 'Phase 1 telemetry gateway connected with 12 synthetic node channels.',
    severity: 'INFO',
    simulation: true,
  },
];

export function getSyntheticAskResponse(query: string): AskNetraResponse {
  const normalized = query.toLowerCase();

  let responseText =
    'Based on synthetic intelligence in Sector HQ-ALPHA, tracked entity ENT-UAV-09 represents the primary source of operational risk (84%). Cross-sensor analysis with radar emitter ENT-RAD-44 suggests coordinated surveillance.';

  if (normalized.includes('uav') || normalized.includes('drone') || normalized.includes('ent-uav-09')) {
    responseText =
      'Entity ENT-UAV-09 is currently loitering at coordinates 28.712° N, 77.294° E at 4,200m elevation. Flight path exhibits 91% anomaly rating relative to standard airspace corridors. Thermal evidence EVD-OPT-309 confirms twin-boom configuration.';
  } else if (normalized.includes('threat') || normalized.includes('risk') || normalized.includes('alert')) {
    responseText =
      'There is 1 CRITICAL alert (ALT-701) and 2 HIGH alerts active. Overall sector threat posture is DEFCON 4 / ADVISORY with 72% aggregate operational risk. All actions remain advisory pending human command verification.';
  } else if (normalized.includes('radar') || normalized.includes('emitter')) {
    responseText =
      'Emitter ENT-RAD-44 is operating on 9.4 GHz frequency hopping mode. Radar track correlation indicates synchronized sweeps during UAV perimeter incursions.';
  } else if (normalized.includes('status') || normalized.includes('system')) {
    responseText =
      'NETRA Core Platform is OPERATIONAL in SIMULATION mode. Backend, database, and telemetry gateways are online. Atul Python AI service interface is configured in advisory simulation mode.';
  }

  return {
    query_id: `ASK-${Date.now()}`,
    query,
    response: responseText,
    confidence: 86,
    sources_used: ['SYNTHETIC_RADAR_GATEWAY', 'SYNTHETIC_ESM_STREAM', 'SYNTHETIC_EO_IR_FUSION'],
    recommended_actions: [
      'Task ground sensor convoy ENT-GND-12 to optimize triangulation geometry.',
      'Maintain continuous EO/IR thermal track on ENT-UAV-09.',
      'Notify regional sector command of corridor breach warning ALT-701.',
    ],
    guardrail_note:
      'SIMULATION ONLY // ADVISORY ADVICE: NETRA provides advisory intelligence decision-support. Autonomous operations strictly prohibited.',
    timestamp: new Date().toISOString(),
    simulation: true,
  };
}
