import { Server as HttpServer } from 'node:http';
import { WebSocketServer, WebSocket } from 'ws';

export interface TacticalSocketMessage {
  type: 'HEARTBEAT' | 'TELEMETRY_TICK' | 'ALERT_NOTIFY' | 'SYSTEM_STATE';
  payload: unknown;
  timestamp: string;
  simulation: true;
}

export class TacticalWebSocketServer {
  private static wss: WebSocketServer | null = null;
  private static heartbeatTimer: NodeJS.Timeout | null = null;

  public static initialize(server: HttpServer): WebSocketServer {
    this.wss = new WebSocketServer({
      server,
      path: '/ws/telemetry',
    });

    this.wss.on('connection', (ws: WebSocket, req) => {
      const clientIp = req.socket.remoteAddress;
      console.log(`📡 [WEBSOCKET] Client connected: ${clientIp}`);

      // Send initial handshake state
      const initialPayload: TacticalSocketMessage = {
        type: 'SYSTEM_STATE',
        payload: {
          status: 'CONNECTED',
          channel: 'TELEMETRY_PIPELINE',
          simulation: true,
          nodes_online: 12,
        },
        timestamp: new Date().toISOString(),
        simulation: true,
      };

      ws.send(JSON.stringify(initialPayload));

      ws.on('message', (message) => {
        try {
          const parsed = JSON.parse(message.toString());
          if (parsed.type === 'PING') {
            ws.send(JSON.stringify({ type: 'PONG', timestamp: new Date().toISOString() }));
          }
        } catch {
          // Ignore invalid JSON payloads
        }
      });

      ws.on('close', () => {
        console.log(`📡 [WEBSOCKET] Client disconnected: ${clientIp}`);
      });

      ws.on('error', (err) => {
        console.error(`❌ [WEBSOCKET] Error on client connection:`, err.message);
      });
    });

    // Broadcast synthetic telemetry heartbeat every 5 seconds
    this.heartbeatTimer = setInterval(() => {
      if (!this.wss) return;

      const heartbeat: TacticalSocketMessage = {
        type: 'TELEMETRY_TICK',
        payload: {
          pulse: Date.now(),
          sector: 'HQ-ALPHA',
          rf_spectrum_mhz: 9420 + Math.floor(Math.random() * 80),
          signal_margin_db: 24.5 + (Math.random() * 2 - 1),
          simulation: true,
        },
        timestamp: new Date().toISOString(),
        simulation: true,
      };

      const serialized = JSON.stringify(heartbeat);
      for (const client of this.wss.clients) {
        if (client.readyState === WebSocket.OPEN) {
          client.send(serialized);
        }
      }
    }, 5000);

    return this.wss;
  }

  public static shutdown(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    if (this.wss) {
      for (const client of this.wss.clients) {
        client.terminate();
      }
      this.wss.close();
      this.wss = null;
    }
  }
}
