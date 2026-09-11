/**
 * Standard API Response Envelope
 */
export interface ApiResponseMeta {
  requestId: string;
  timestamp: string;
  latencyMs?: number;
}

export interface ApiResponse<T = unknown> {
  success: true;
  data: T;
  meta: ApiResponseMeta;
}

export interface ApiErrorDetail {
  field?: string;
  message: string;
  code?: string;
}

export interface ApiErrorEnvelope {
  code: string;
  message: string;
  details?: ApiErrorDetail[];
}

export interface ApiErrorResponse {
  success: false;
  error: ApiErrorEnvelope;
  meta: ApiResponseMeta;
}
