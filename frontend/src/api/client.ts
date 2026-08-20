/**
 * Minimal typed fetch client for the BI Platform API. Attaches the bearer
 * token from memory (set by the auth flow, not shown in this skeleton) and
 * normalizes the backend's `{ error: { code, message, details } }` shape
 * into a thrown `ApiError`.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number,
    public readonly details?: unknown,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const err = body?.error ?? { code: 'unknown_error', message: response.statusText };
    throw new ApiError(err.code, err.message, response.status, err.details);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export interface DashboardSummary {
  id: string;
  name: string;
  description: string;
  is_public: boolean;
  widgets: { id: string; title: string; chart_type: string; datasource_id: string; position: Record<string, number> }[];
}

export interface WidgetData {
  columns: string[];
  rows: unknown[][];
  truncated: boolean;
  cache_status: 'hit' | 'miss';
}

export const api = {
  listDashboards: () => request<DashboardSummary[]>('/dashboards'),
  getDashboard: (id: string) => request<DashboardSummary>(`/dashboards/${id}`),
  getWidgetData: (dashboardId: string, widgetId: string) =>
    request<WidgetData>(`/dashboards/${dashboardId}/widgets/${widgetId}/data`),
  login: (email: string, password: string, organizationId: string) =>
    request<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, organization_id: organizationId }),
    }),
};
