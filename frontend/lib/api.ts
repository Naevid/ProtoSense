export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type Evidence = {
  feature: string;
  snippet: string;
  page?: number | null;
  section?: string | null;
  confidence: number;
  method: "rule" | "gemini" | "inferred" | "user_simulation" | "fixture";
};

export type TopDriver = {
  feature: string;
  impact: number;
  contribution_percent: number;
  value: unknown;
  evidence?: Evidence | null;
};

export type RiskDimension = {
  score: number;
  label: "Low" | "Medium" | "High";
  top_drivers: TopDriver[];
  summary: string;
  recommendations: string[];
};

export type Assessment = {
  protocol_id: string;
  overall_feasibility_risk: number;
  overall_label: "Low" | "Medium" | "High";
  risk_dimensions: Record<string, RiskDimension>;
  features: Record<string, unknown>;
  evidence: Evidence[];
  recommendations: Array<Record<string, unknown>>;
};

export type SimulationResponse = {
  protocol_id: string;
  before: Assessment;
  after: Assessment;
  deltas: Record<string, number>;
  applied_overrides: Record<string, unknown>;
};

export type ChatResponse = {
  protocol_id: string;
  answer: string;
  cited_evidence: Evidence[];
  method: "gemini" | "fallback";
  caveat: string;
};

export async function uploadProtocol(file: File) {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${API_BASE}/protocols/upload`, { method: "POST", body });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<{ protocol_id: string; filename: string; pages: number }>;
}

export async function runPipeline(protocolId: string) {
  await fetchOrThrow(`${API_BASE}/protocols/${protocolId}/section-map`, "POST");
  await fetchOrThrow(`${API_BASE}/protocols/${protocolId}/extract`, "POST");
  return fetchOrThrow(`${API_BASE}/protocols/${protocolId}/score`, "POST") as Promise<Assessment>;
}

export async function getAssessment(protocolId: string) {
  return fetchOrThrow(`${API_BASE}/protocols/${protocolId}/assessment`, "GET") as Promise<Assessment>;
}

export async function simulate(protocolId: string, overrides: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/protocols/${protocolId}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ overrides })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<SimulationResponse>;
}

export async function askProtocol(protocolId: string, message: string) {
  const response = await fetch(`${API_BASE}/protocols/${protocolId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<ChatResponse>;
}

async function fetchOrThrow(url: string, method: "GET" | "POST") {
  const response = await fetch(url, { method });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
