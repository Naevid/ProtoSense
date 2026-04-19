"use client";

import { useMemo, useState } from "react";
import type { Assessment, SimulationResponse } from "../lib/api";
import { simulate } from "../lib/api";

const numericControls = [
  ["number_exploratory_endpoints", 0, 12],
  ["inclusion_count", 0, 20],
  ["exclusion_count", 0, 25],
  ["total_visit_count", 0, 24],
  ["in_person_visit_count", 0, 24],
  ["remote_visit_count", 0, 12],
  ["invasive_procedures_count", 0, 8],
  ["number_of_countries", 1, 20],
  ["number_of_timepoints", 0, 28]
] as const;

const booleanControls = ["biomarker_requirement", "specialized_equipment_required"] as const;

function readFeature(assessment: Assessment, key: string) {
  for (const group of Object.values(assessment.features) as Array<Record<string, { value?: unknown }>>) {
    if (group && key in group) return group[key]?.value;
  }
  return undefined;
}

export function Simulator({ protocolId, assessment }: { protocolId: string; assessment: Assessment }) {
  const defaults = useMemo(() => {
    const values: Record<string, number | boolean> = {};
    numericControls.forEach(([key]) => {
      values[key] = Number(readFeature(assessment, key) ?? 0);
    });
    booleanControls.forEach((key) => {
      values[key] = Boolean(readFeature(assessment, key));
    });
    return values;
  }, [assessment]);

  const [values, setValues] = useState(defaults);
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setBusy(true);
    setError(null);
    try {
      const changed = Object.fromEntries(Object.entries(values).filter(([key, value]) => value !== defaults[key]));
      setResult(await simulate(protocolId, changed));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setBusy(false);
    }
  }

  const active = result?.after ?? assessment;
  return (
    <section className="mt-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase text-teal">What-if simulator</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Redesign assumptions and recalculate</h2>
        </div>
        <button className="focus-ring rounded-md bg-teal px-4 py-2 text-sm font-semibold text-white" onClick={run} disabled={busy}>
          {busy ? "Recalculating..." : "Run simulation"}
        </button>
      </div>
      <div className="mt-5 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-lg border border-line bg-white p-5 shadow-soft">
          <div className="grid gap-5 md:grid-cols-2">
            {numericControls.map(([key, min, max]) => (
              <label key={key} className="block">
                <span className="flex items-center justify-between gap-3 text-sm font-medium text-ink">
                  {key.replaceAll("_", " ")}
                  <strong>{Number(values[key])}</strong>
                </span>
                <input
                  className="mt-3 w-full accent-teal"
                  type="range"
                  min={min}
                  max={max}
                  value={Number(values[key])}
                  onChange={(event) => setValues((current) => ({ ...current, [key]: Number(event.target.value) }))}
                />
              </label>
            ))}
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            {booleanControls.map((key) => (
              <label key={key} className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm">
                <input
                  type="checkbox"
                  checked={Boolean(values[key])}
                  onChange={(event) => setValues((current) => ({ ...current, [key]: event.target.checked }))}
                />
                {key.replaceAll("_", " ")}
              </label>
            ))}
          </div>
          {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
        </div>
        <div className="rounded-lg border border-line bg-white p-5 shadow-soft">
          <p className="text-sm font-semibold text-graphite">Before vs after</p>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="rounded-lg bg-mist p-4">
              <p className="text-xs text-graphite">Current</p>
              <p className="mt-1 text-4xl font-bold text-ink">{assessment.overall_feasibility_risk}</p>
            </div>
            <div className="rounded-lg bg-mint p-4">
              <p className="text-xs text-graphite">Simulated</p>
              <p className="mt-1 text-4xl font-bold text-teal">{active.overall_feasibility_risk}</p>
            </div>
          </div>
          <div className="mt-5 space-y-2">
            {result
              ? Object.entries(result.deltas).map(([key, delta]) => (
                  <div key={key} className="flex items-center justify-between gap-3 text-sm">
                    <span>{key.replaceAll("_", " ")}</span>
                    <strong className={delta <= 0 ? "text-emerald-700" : "text-coral"}>{delta > 0 ? `+${delta}` : delta}</strong>
                  </div>
                ))
              : <p className="text-sm leading-6 text-graphite">Adjust assumptions to see deterministic score movement, updated drivers, and revised redesign guidance.</p>}
          </div>
        </div>
      </div>
    </section>
  );
}
