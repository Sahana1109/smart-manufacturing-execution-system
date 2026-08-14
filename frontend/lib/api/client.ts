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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "/api/v1";

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, { ...options, headers });
    const json = await res.json();
    return json;
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Failed to communicate with SmartMES server";
    return {
      success: false,
      data: null as T,
      error: {
        code: "NETWORK_ERROR",
        message: errorMessage,
      },
    };
  }
}
