import { useState, useEffect, useRef } from 'react';

export type SocketState = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED';

export interface TelemetryTick {
  pulse: number;
  sector: string;
  rf_spectrum_mhz: number;
  signal_margin_db: number;
  simulation: true;
}

export function useWebSocket() {
  const [status, setStatus] = useState<SocketState>('CONNECTING');
  const [latestTick, setLatestTick] = useState<TelemetryTick | null>(null);
  const [messagesReceived, setMessagesReceived] = useState<number>(0);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Construct WebSocket URL based on current host or backend port 5000
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // If running under Vite dev proxy on 5173, point directly to 5000 for WS or relative path
    const host = window.location.hostname === 'localhost' ? 'localhost:5000' : window.location.host;
    const wsUrl = `${protocol}//${host}/ws/telemetry`;

    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let isCleanedUp = false;

    function connect() {
      if (isCleanedUp) return;
      setStatus('CONNECTING');

      try {
        const ws = new WebSocket(wsUrl);
        socketRef.current = ws;

        ws.onopen = () => {
          if (!isCleanedUp) {
            setStatus('CONNECTED');
          }
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'TELEMETRY_TICK') {
              setLatestTick(data.payload as TelemetryTick);
            }
            setMessagesReceived((prev) => prev + 1);
          } catch {
            // Non-JSON or malformed packet
          }
        };

        ws.onclose = () => {
          if (!isCleanedUp) {
            setStatus('DISCONNECTED');
            // Try reconnecting after 4s
            reconnectTimer = setTimeout(connect, 4000);
          }
        };

        ws.onerror = () => {
          if (!isCleanedUp) {
            setStatus('DISCONNECTED');
          }
        };
      } catch {
        setStatus('DISCONNECTED');
        reconnectTimer = setTimeout(connect, 5000);
      }
    }

    connect();

    return () => {
      isCleanedUp = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  return { status, latestTick, messagesReceived };
}
