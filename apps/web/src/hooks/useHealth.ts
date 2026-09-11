import { useQuery } from '@tanstack/react-query';
import { netraApi } from '../services/api.js';

export function useHealth(refetchIntervalMs: number = 5000) {
  return useQuery({
    queryKey: ['system-health'],
    queryFn: netraApi.getHealth,
    refetchInterval: refetchIntervalMs,
    retry: 2,
    staleTime: 3000,
  });
}
