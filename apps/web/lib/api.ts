const base = () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${base()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${base()}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json() as Promise<T>;
}

export async function apiUpload(file: File): Promise<{ document_id: string; status: string }> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${base()}/api/ingest/upload`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}
