import { useState, useEffect } from 'react';

export interface TacticalTime {
  zuluTime: string;
  zuluDate: string;
  localTime: string;
  epoch: number;
}

export function useZuluClock(): TacticalTime {
  const [now, setNow] = useState<Date>(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const hours = String(now.getUTCHours()).padStart(2, '0');
  const minutes = String(now.getUTCMinutes()).padStart(2, '0');
  const seconds = String(now.getUTCSeconds()).padStart(2, '0');
  const year = now.getUTCFullYear();
  const month = String(now.getUTCMonth() + 1).padStart(2, '0');
  const day = String(now.getUTCDate()).padStart(2, '0');

  return {
    zuluTime: `${hours}:${minutes}:${seconds} Z`,
    zuluDate: `${year}-${month}-${day}`,
    localTime: now.toLocaleTimeString(),
    epoch: Math.floor(now.getTime() / 1000),
  };
}
