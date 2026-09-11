import React, { useState } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  Crosshair,
} from 'lucide-react';
import { Card } from '../ui/Card.js';
import { Badge } from '../ui/Badge.js';
import { Entity, Event } from '@netra/shared';

interface MapContainerProps {
  entities?: Entity[];
  events?: Event[];
  selectedEntityId?: string | null;
  onSelectEntity?: (entityId: string) => void;
  className?: string;
}

export const MapContainer: React.FC<MapContainerProps> = ({
  entities = [],
  events = [],
  selectedEntityId,
  onSelectEntity,
  className,
}) => {
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [showSectors, setShowSectors] = useState<boolean>(true);
  const [showRadarSweep, setShowRadarSweep] = useState<boolean>(true);
  const [showMenu, setShowMenu] = useState<boolean>(false);

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.25, 2.5));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.25, 0.75));
  const handleReset = () => setZoomLevel(1);

  return (
    <Card
      title="SITUATIONAL MAP"
      subtitle="CONTEXTUAL VIEW (30%)"
      badge={<Badge variant="cyan">GRID-NORTH</Badge>}
      headerAction={
        <div className="flex items-center gap-1">
          {/* Layer toggles dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
              title="Toggle Map Layers"
            >
              <Layers className="w-3.5 h-3.5" />
            </button>
            {showMenu && (
              <div className="absolute right-0 top-6 z-30 w-36 bg-slate-950 border border-slate-700 p-2 shadow-tactical-card font-mono text-[10px] space-y-1.5 text-slate-300">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showSectors}
                    onChange={(e) => setShowSectors(e.target.checked)}
                    className="accent-cyan-500"
                  />
                  <span>SECTORS</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showRadarSweep}
                    onChange={(e) => setShowRadarSweep(e.target.checked)}
                    className="accent-cyan-500"
                  />
                  <span>RADAR SWEEP</span>
                </label>
              </div>
            )}
          </div>

          <button
            onClick={handleZoomIn}
            className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleReset}
            className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
            title="Reset Pan & Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      }
      className={`relative flex flex-col ${className || 'h-[440px]'}`}
      bodyClassName="p-0 relative flex-1 flex items-center justify-center overflow-hidden bg-slate-950/90 select-none"
    >
      {/* Tactical Coordinate Grid Background */}
      <div className="absolute inset-0 tactical-grid-bg opacity-30 pointer-events-none" />
      <div className="absolute inset-0 tactical-cross-bg opacity-40 pointer-events-none" />

      {/* SVG Interactive Tactical Map Layer */}
      <div
        className="w-full h-full flex items-center justify-center transition-transform duration-200 p-2"
        style={{ transform: `scale(${zoomLevel})` }}
      >
        <svg viewBox="0 0 500 400" className="w-full h-full max-w-full max-h-[380px] overflow-visible">
          {/* Range rings */}
          <circle cx="250" cy="200" r="180" stroke="#06b6d4" strokeWidth="1" strokeDasharray="4 4" opacity="0.25" fill="none" />
          <circle cx="250" cy="200" r="120" stroke="#06b6d4" strokeWidth="1" strokeDasharray="3 3" opacity="0.35" fill="none" />
          <circle cx="250" cy="200" r="60" stroke="#06b6d4" strokeWidth="1" opacity="0.4" fill="none" />
          <circle cx="250" cy="200" r="4" fill="#06b6d4" />

          {/* Crosshairs */}
          <line x1="250" y1="20" x2="250" y2="380" stroke="#06b6d4" strokeWidth="1" opacity="0.2" />
          <line x1="30" y1="200" x2="470" y2="200" stroke="#06b6d4" strokeWidth="1" opacity="0.2" />

          {/* Radar Sweep Effect */}
          {showRadarSweep && (
            <g className="origin-[250px_200px] animate-radar-sweep pointer-events-none">
              <line x1="250" y1="200" x2="250" y2="20" stroke="#22d3ee" strokeWidth="1.5" opacity="0.7" />
              <path
                d="M 250 200 L 250 20 A 180 180 0 0 1 370 70 Z"
                fill="url(#radarGradient)"
                opacity="0.15"
              />
            </g>
          )}

          <defs>
            <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Sectors overlay */}
          {showSectors && (
            <g className="font-mono text-[9px] fill-slate-500 pointer-events-none">
              <text x="140" y="80">SECTOR ALPHA-NORTH</text>
              <text x="310" y="110">SECTOR BRAVO</text>
              <text x="120" y="320">SECTOR ALPHA-SOUTH</text>
              <text x="330" y="310">SECTOR CHARLIE</text>
            </g>
          )}

          {/* Plotted Events (Pulsing circles) */}
          {events.map((evt, idx) => {
            const cx = 200 + (idx * 55) % 180;
            const cy = 130 + (idx * 45) % 160;
            const isCritical = evt.severity === 'CRITICAL';
            return (
              <g key={evt.event_id} className="cursor-pointer" opacity="0.9">
                <circle
                  cx={cx}
                  cy={cy}
                  r={isCritical ? '9' : '6'}
                  fill={isCritical ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)'}
                  stroke={isCritical ? '#ef4444' : '#f59e0b'}
                  strokeWidth="1.5"
                  className={isCritical ? 'animate-ping origin-center' : ''}
                />
                <circle cx={cx} cy={cy} r="3" fill={isCritical ? '#ef4444' : '#f59e0b'} />
                <text
                  x={cx + 7}
                  y={cy - 4}
                  className="font-mono text-[8px] fill-slate-400 select-none pointer-events-none"
                >
                  {evt.event_id.replace('EVT-2026-', 'E-')}
                </text>
              </g>
            );
          })}

          {/* Plotted Entities */}
          {entities.map((entity) => {
            // Coordinate mapping to SVG space
            const baseLat = 28.65;
            const baseLon = 77.25;
            const latDiff = ((entity.location?.latitude || baseLat) - baseLat) * 900;
            const lonDiff = ((entity.location?.longitude || baseLon) - baseLon) * 900;
            const cx = Math.max(50, Math.min(450, 250 + lonDiff));
            const cy = Math.max(40, Math.min(360, 200 - latDiff));

            const isSelected = selectedEntityId === entity.entity_id;
            const isHostile = entity.status === 'HOSTILE' || entity.risk_score > 80;
            const color = isHostile ? '#ef4444' : '#06b6d4';

            return (
              <g
                key={entity.entity_id}
                onClick={() => onSelectEntity && onSelectEntity(entity.entity_id)}
                className="cursor-pointer group"
              >
                {isSelected && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r="14"
                    fill="none"
                    stroke="#22d3ee"
                    strokeWidth="1.5"
                    strokeDasharray="2 2"
                    className="animate-spin origin-center"
                  />
                )}
                {/* Entity Symbol */}
                <rect
                  x={cx - 6}
                  y={cy - 6}
                  width="12"
                  height="12"
                  fill="#0d131f"
                  stroke={color}
                  strokeWidth="1.5"
                  transform={`rotate(45 ${cx} ${cy})`}
                />
                <circle cx={cx} cy={cy} r="2" fill={color} />
                <text
                  x={cx + 10}
                  y={cy + 3}
                  className={`font-mono text-[9px] font-semibold select-none ${
                    isSelected ? 'fill-cyan-300' : 'fill-slate-300'
                  }`}
                >
                  {entity.entity_id}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Map Footer Metadata & Coordinates */}
      <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between font-mono text-[9px] text-slate-500 bg-slate-950/80 px-2.5 py-1 border border-slate-800 rounded-xs">
        <div className="flex items-center gap-2">
          <Crosshair className="w-3 h-3 text-cyan-400" />
          <span>28.712° N, 77.294° E</span>
          <span className="text-slate-600">|</span>
          <span>ZOOM: {(zoomLevel * 100).toFixed(0)}%</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-cyan-400">ENTITIES: {entities.length}</span>
          <span className="text-slate-600">|</span>
          <span className="text-amber-400">EVENTS: {events.length}</span>
        </div>
      </div>
    </Card>
  );
};
