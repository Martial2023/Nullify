import type { ApiError } from "@/types";

function buildQueryString(params: Record<string, string>): string {
  const search = new URLSearchParams(params);
  return search.toString() ? `?${search.toString()}` : "";
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const error: ApiError = await res.json().catch(() => ({
      message: res.statusText,
    }));
    throw new Error(error.message);
  }

  return res.json() as Promise<T>;
}

export const apiClient = {
  get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const qs = params ? buildQueryString(params) : "";
    return request<T>(`${path}${qs}`);
  },

  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(path: string): Promise<T> {
    return request<T>(path, { method: "DELETE" });
  },
};
