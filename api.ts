const raw = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const API_BASE = raw.startsWith("http://") || raw.startsWith("https://") ? raw : `https://${raw}`;
export async function api<T=any>(path:string, options:RequestInit = {}):Promise<T> {
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type","application/json");
  const response = await fetch(`${API_BASE}${path}`, {...options, headers, credentials:"include", cache:"no-store"});
  const body = await response.json().catch(()=>({detail:"The server returned an unexpected response"}));
  if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
  return body as T;
}
