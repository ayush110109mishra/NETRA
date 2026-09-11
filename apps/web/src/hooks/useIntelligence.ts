import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { netraApi } from '../services/api.js';
import { AskNetraQuery } from '@netra/shared';

export function useKpis() {
  return useQuery({
    queryKey: ['kpis'],
    queryFn: netraApi.getKpis,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useSystemStatus() {
  return useQuery({
    queryKey: ['system-status'],
    queryFn: netraApi.getSystemStatus,
    refetchInterval: 8000,
    staleTime: 4000,
  });
}

export function useAssessment() {
  return useQuery({
    queryKey: ['assessment'],
    queryFn: netraApi.getAssessment,
    refetchInterval: 12000,
    staleTime: 6000,
  });
}

export function useEntities(filter?: { type?: string; status?: string }) {
  return useQuery({
    queryKey: ['entities', filter],
    queryFn: () => netraApi.getEntities(filter),
    refetchInterval: 15000,
    staleTime: 8000,
  });
}

export function useAlerts(filter?: { severity?: string; status?: string }) {
  return useQuery({
    queryKey: ['alerts', filter],
    queryFn: () => netraApi.getAlerts(filter),
    refetchInterval: 8000,
    staleTime: 4000,
  });
}

export function useEvents(filter?: { type?: string; severity?: string }) {
  return useQuery({
    queryKey: ['events', filter],
    queryFn: () => netraApi.getEvents(filter),
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useEvidence(filter?: { entityId?: string; eventId?: string }) {
  return useQuery({
    queryKey: ['evidence', filter],
    queryFn: () => netraApi.getEvidence(filter),
    refetchInterval: 20000,
    staleTime: 10000,
  });
}

export function useFeed() {
  return useQuery({
    queryKey: ['feed'],
    queryFn: netraApi.getFeed,
    refetchInterval: 6000,
    staleTime: 3000,
  });
}

export function useAskNetra() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AskNetraQuery) => netraApi.askNetra(payload),
    onSuccess: () => {
      // Invalidate feed after query
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });
}
