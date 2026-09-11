import { describe, it } from 'node:test';
import assert from 'node:assert';
import { SyntheticDataStore } from '../src/synthetic/store.js';

describe('NETRA Phase 1 - Synthetic Intelligence Data Store', () => {
  it('should return command layer KPIs with exact specification values', () => {
    const kpis = SyntheticDataStore.getKpis();
    assert.strictEqual(kpis.alerts, 7);
    assert.strictEqual(kpis.events, 186);
    assert.strictEqual(kpis.entities, 73);
    assert.strictEqual(kpis.anomalies, 8);
    assert.strictEqual(kpis.risk, 72);
    assert.strictEqual(kpis.confidence, 86);
    assert.strictEqual(kpis.simulation, true);
  });

  it('should return system status with explicit AI Core simulation state', () => {
    const status = SyntheticDataStore.getSystemStatus();
    assert.strictEqual(status.system, 'OPERATIONAL');
    assert.strictEqual(status.backend, 'ONLINE');
    assert.strictEqual(status.ai_core, 'SIMULATION'); // Crucial: Atul AI is simulation
    assert.strictEqual(status.simulation, true);
  });

  it('should return assessment marked as simulation with evidence count', () => {
    const assessment = SyntheticDataStore.getAssessment();
    assert.ok(assessment.assessment_id.startsWith('ASM-'));
    assert.strictEqual(assessment.confidence, 86);
    assert.strictEqual(assessment.evidence_count, 12);
    assert.strictEqual(assessment.sources_count, 8);
    assert.strictEqual(assessment.contradictions_count, 2);
    assert.strictEqual(assessment.simulation, true);
  });

  it('should return synthetic entities and filter by type', () => {
    const allEntities = SyntheticDataStore.getEntities();
    assert.ok(allEntities.length >= 4);

    const uavs = SyntheticDataStore.getEntities({ type: 'UAV' });
    assert.strictEqual(uavs.length, 1);
    assert.strictEqual(uavs[0].entity_id, 'ENT-UAV-09');
    assert.strictEqual(uavs[0].simulation, true);
  });

  it('should return alerts sorted by severity and filter by severity level', () => {
    const allAlerts = SyntheticDataStore.getAlerts();
    assert.strictEqual(allAlerts.length, 7);

    const criticalAlerts = SyntheticDataStore.getAlerts({ severity: 'CRITICAL' });
    assert.strictEqual(criticalAlerts.length, 1);
    assert.strictEqual(criticalAlerts[0].alert_id, 'ALT-701');
  });

  it('should return events with location and associated entity metadata', () => {
    const events = SyntheticDataStore.getEvents();
    assert.ok(events.length >= 5);

    const firstEvent = events[0];
    assert.ok(firstEvent.location.latitude > 0);
    assert.ok(firstEvent.location.longitude > 0);
    assert.ok(firstEvent.entities.length > 0);
    assert.strictEqual(firstEvent.simulation, true);
  });

  it('should return correlated evidence items with reliability ratings', () => {
    const evidence = SyntheticDataStore.getEvidence();
    assert.ok(evidence.length >= 4);

    const firstItem = evidence[0];
    assert.ok(['CONFIRMED', 'PROBABLE', 'DOUBTFUL', 'CANNOT_JUDGE'].includes(firstItem.reliability));
    assert.strictEqual(firstItem.simulation, true);
  });

  it('should return Ask NETRA response with guardrail notice and advisory actions', () => {
    const res = SyntheticDataStore.askNetra('Report threat posture and UAV track');
    assert.ok(res.response.length > 20);
    assert.strictEqual(res.confidence, 86);
    assert.ok(res.recommended_actions.length > 0);
    assert.ok(res.guardrail_note.includes('ADVISORY'));
    assert.strictEqual(res.simulation, true);
  });
});
