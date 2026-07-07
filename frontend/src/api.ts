// Typed fetch helpers for the backend JSON API. All paths are same-origin:
// in dev, Vite proxies them to Flask; in production Flask serves both.

import type { ClusterState, DriveFrame, SignalAction } from "./types";

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    throw new Error(`request to ${res.url} failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function getState(): Promise<ClusterState> {
  return jsonOrThrow<ClusterState>(await fetch("/api/state"));
}

export async function postInput(partial: Record<string, unknown>): Promise<void> {
  const res = await fetch("/api/input", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(partial),
  });
  if (!res.ok) {
    throw new Error(`input failed: ${res.status}`);
  }
}

export async function postSignal(action: SignalAction): Promise<void> {
  const res = await fetch(`/api/signal/${action}`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`signal failed: ${res.status}`);
  }
}

export async function getVersion(): Promise<string> {
  const data = await jsonOrThrow<{ version: string }>(await fetch("/version"));
  return data.version;
}

export async function getDriveCycle(): Promise<DriveFrame[]> {
  return jsonOrThrow<DriveFrame[]>(await fetch("/api/drive-cycle"));
}
