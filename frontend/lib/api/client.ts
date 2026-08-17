export interface ApiResponse<T = unknown> {
  success: boolean;
  data: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: unknown[];
  };
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };

  const res = await fetch(url, { ...options, headers });
  
  if (!res.ok) {
    let errorData: any = {};
    try {
      errorData = await res.json();
    } catch {
      errorData = { message: res.statusText };
    }
    const errObj = errorData.error || errorData.detail || errorData;
    const message = typeof errObj === "string" ? errObj : errObj.message || "API request failed";
    throw { status: res.status, message, error: errObj };
  }

  // Handle 204 No Content
  if (res.status === 204) {
    return {} as T;
  }

  return await res.json();
}

export const api = {
  get: <T = any>(endpoint: string) => apiRequest<T>(endpoint, { method: "GET" }),
  post: <T = any>(endpoint: string, body?: any) =>
    apiRequest<T>(endpoint, { method: "POST", body: JSON.stringify(body) }),
  put: <T = any>(endpoint: string, body?: any) =>
    apiRequest<T>(endpoint, { method: "PUT", body: JSON.stringify(body) }),
  patch: <T = any>(endpoint: string, body?: any) =>
    apiRequest<T>(endpoint, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T = any>(endpoint: string) => apiRequest<T>(endpoint, { method: "DELETE" }),
};
