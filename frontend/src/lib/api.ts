import type { BehaviourKey, RiskLevel, WarehouseEvent } from "@/lib/warehouse-data";

// Point this at your FastAPI backend. Override by setting VITE_API_URL
// (e.g. in a .env file) — falls back to the local dev default.
const API_BASE_URL = ((import.meta.env["VITE_API_URL"] as string | undefined) ?? "http://localhost:8000").replace(/\/$/, "");

export type ApiEvent = {
  event_id: string;
  timestamp_video: string;
  camera_id: string;
  bay: string;
  objects: string[];
  behaviour: string;
  confidence: number;
  risk_level: RiskLevel;
  risk_score?: number;
  evidence: { clip_start: string; clip_end: string; frame_snapshot: string };
  explanation: string;
};

export type ApiStats = {
  total_events: number;
  by_risk_level: Record<string, number>;
  by_bay: Record<string, number>;
  by_behaviour: Record<string, number>;
  by_behaviour_and_risk: { behaviour: string; risk_level: string; count: number }[];
};

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

// Backend sends bay as "bay1" — display it as "Bay 01".
function formatBay(bay: string | null | undefined): string {
  const match = /^([a-zA-Z]+?)(\d+)$/.exec(bay ?? "");
  if (!match) return bay || "Unknown bay";
  const label = match[1] ?? "";
  const number = match[2] ?? "";
  if (!label || !number) return bay || "Unknown bay";
  return `${label.charAt(0).toUpperCase()}${label.slice(1)} ${number.padStart(2, "0")}`;
}

// The backend doesn't send `rules` (a rules checklist) or `boxes` (video
// bounding-box overlays) — those are frontend-only enrichments. We fall
// back to the model's explanation as a single "rule" so the UI still has
// something to show, and render no overlay boxes.
export function toWarehouseEvent(raw: ApiEvent): WarehouseEvent {
  return {
    event_id: raw.event_id,
    timestamp_video: raw.timestamp_video,
    camera_id: raw.camera_id,
    bay: formatBay(raw.bay),
    objects: raw.objects ?? [],
    behaviour: (raw.behaviour as BehaviourKey) ?? "product_dropped",
    confidence: raw.confidence,
    risk_level: raw.risk_level,
    evidence: raw.evidence ?? { clip_start: "00:00:00", clip_end: "00:00:00", frame_snapshot: "" },
    explanation: raw.explanation ?? "",
    rules: raw.explanation ? [raw.explanation] : [],
    boxes: [],
  };
}

export async function fetchEvents(params?: {
  risk_level?: RiskLevel;
  behaviour?: string;
  bay?: string;
  limit?: number;
}): Promise<WarehouseEvent[]> {
  const query = new URLSearchParams();
  if (params?.risk_level) query.set("risk_level", params.risk_level);
  if (params?.behaviour) query.set("behaviour", params.behaviour);
  if (params?.bay) query.set("bay", params.bay);
  if (params?.limit) query.set("limit", String(params.limit));

  const qs = query.toString();
  const raw = await apiFetch<ApiEvent[]>(`/events${qs ? `?${qs}` : ""}`);
  return raw.map(toWarehouseEvent);
}

export async function fetchStats(): Promise<ApiStats> {
  return apiFetch<ApiStats>("/stats");
}

export async function askAssistant(question: string): Promise<string> {
  const data = await apiFetch<{ question: string; answer: string }>("/assistant/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
  return data.answer;
}
