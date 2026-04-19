"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../components/AppShell";
import { ChatAssistant } from "../../../components/ChatAssistant";
import { DriverBars } from "../../../components/DriverBars";
import { SeverityBadge } from "../../../components/SeverityBadge";
import { Simulator } from "../../../components/Simulator";
import { getAssessment, type Assessment } from "../../../lib/api";

const dimensionLabels: Record<string, string> = {
  startup_complexity: "Startup Complexity",
  enrollment_feasibility: "Enrollment Feasibility",
  participant_burden: "Participant Burden",
  site_execution_burden: "Site Execution Burden",
  amendment_susceptibility: "Amendment Susceptibility"
};

const metricDefinitions = [
  ["Overall Inefficiency Warning", "Early warning score for operational inefficiencies before trial launch."],
  ["Startup Complexity", "Warns when startup requirements may slow activation timelines."],
  ["Enrollment Feasibility", "Warns when criteria and visit design may reduce enrollment speed."],
  ["Participant Burden", "Warns when participant workload may increase drop-off or missed tasks."],
  ["Site Execution Burden", "Warns when site workflows are likely to create delays or rework."],
  ["Amendment Susceptibility", "Warns when protocol complexity may trigger clarifications or amendments."]
];

export default function ProtocolDashboard() {
  const params = useParams<{ id: string }>();
  const protocolId = params.id;
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAssessment(protocolId).then(setAssessment).catch((err) => setError(err instanceof Error ? err.message : "Unable to load assessment"));
  }, [protocolId]);

  if (error) {
    return (
      <AppShell active="dashboard" title="Pre-trial inefficiency warnings">
        <p className="rounded-lg border border-line bg-white p-5 text-coral shadow-soft">{error}</p>
      </AppShell>
    );
  }

  if (!assessment) {
    return (
      <AppShell active="dashboard" title="Pre-trial inefficiency warnings">
        <p className="rounded-lg border border-line bg-white p-5 text-graphite shadow-soft">Loading early warning assessment...</p>
      </AppShell>
    );
  }

  const topDimension = Object.entries(assessment.risk_dimensions).sort((a, b) => b[1].score - a[1].score)[0];

  return (
    <AppShell
      active="dashboard"
      eyebrow="Early Warning"
      title="Pre-trial inefficiency warnings for this protocol"
    >
      <section className="relative overflow-hidden rounded-lg border border-[#dfe5e1] bg-white p-6 shadow-soft">
        <div className="absolute inset-y-0 right-0 hidden w-1/2 lg:block" style={{ background: "linear-gradient(48deg, #CDF5FD 0%, #D8FEF3 48%, #E8FED7 100%)" }} />
        <div className="relative grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <p className="text-sm font-semibold text-[#0ba299]">Overall inefficiency warning</p>
            <div className="mt-3 flex items-center gap-4">
              <p className="text-7xl font-semibold text-[#111112]">{assessment.overall_feasibility_risk}</p>
              <SeverityBadge label={assessment.overall_label} />
            </div>
            <p className="mt-4 max-w-xl text-sm leading-6 text-[#63656a]">
              A protocol-grounded early warning signal designed to flag likely inefficiencies before trial execution.
            </p>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {Object.entries(assessment.risk_dimensions).map(([key, dimension]) => (
              <article key={key} className="rounded-lg border border-white/70 bg-white/85 p-4 shadow-soft backdrop-blur">
                <div className="flex items-start justify-between gap-3">
                  <h2 className="text-sm font-semibold text-[#111112]">{dimensionLabels[key] ?? key}</h2>
                  <div className="flex items-center gap-3">
                    <SeverityBadge label={dimension.label} />
                    <strong className="text-2xl text-[#0ba299]">{dimension.score}</strong>
                  </div>
                </div>
                <p className="mt-2 text-xs leading-5 text-[#63656a]">{dimension.summary}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-5 rounded-lg border border-[#e1e7e3] bg-white shadow-soft">
        <details open>
          <summary className="cursor-pointer list-none px-5 py-4 text-base font-semibold text-[#111112]">How these warning signals work</summary>
          <div className="grid gap-0 border-t border-[#e1e7e3] md:grid-cols-2 xl:grid-cols-3">
            {metricDefinitions.map(([title, description]) => (
              <article key={title} className="border-b border-[#e1e7e3] p-5 xl:border-r">
                <h2 className="text-sm font-semibold text-[#111112]">{title}</h2>
                <p className="mt-2 text-sm leading-6 text-[#63656a]">{description}</p>
              </article>
            ))}
          </div>
        </details>
      </section>

      <section className="mt-5 grid gap-5 lg:grid-cols-[1.35fr_0.65fr]">
        <div className="rounded-lg border border-[#e1e7e3] bg-white shadow-soft">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e1e7e3] px-5 py-4">
            <div>
              <p className="text-xs font-semibold uppercase text-[#0ba299]">Top inefficiency warnings by dimension</p>
              <h2 className="mt-1 text-base font-semibold text-[#111112]">Operational pressure by dimension</h2>
            </div>
            <span className="rounded-md border border-[#e1e7e3] bg-[#fbfcfb] px-3 py-1 text-xs text-[#63656a]">
              Highest: {dimensionLabels[topDimension[0]]}
            </span>
          </div>
          <div className="divide-y divide-[#e1e7e3]">
            {Object.entries(assessment.risk_dimensions).map(([key, dimension]) => (
              <article key={key} className="grid gap-5 px-5 py-5 xl:grid-cols-[0.8fr_1.2fr]">
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-sm font-semibold text-[#111112]">{dimensionLabels[key] ?? key}</h3>
                    <strong className="text-lg text-[#0ba299]">{dimension.score}</strong>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-[#63656a]">{dimension.summary}</p>
                </div>
                <DriverBars drivers={dimension.top_drivers} />
              </article>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-[#e1e7e3] bg-white shadow-soft">
          <div className="border-b border-[#e1e7e3] px-5 py-4">
            <p className="text-xs font-semibold uppercase text-[#0ba299]">Mitigation actions</p>
            <h2 className="mt-1 text-base font-semibold text-[#111112]">What to fix before trial launch</h2>
          </div>
          <div className="divide-y divide-[#e1e7e3]">
            {assessment.recommendations.map((rec, index) => (
              <article key={String(rec.feature ?? index)} className="px-5 py-4">
                <p className="text-xs font-semibold text-[#0ba299]">{String(rec.impact_area ?? "Protocol design")}</p>
                <h3 className="mt-2 text-sm font-semibold text-[#111112]">{String(rec.title ?? "Review driver")}</h3>
                <p className="mt-2 text-sm leading-6 text-[#63656a]">{String(rec.action ?? "")}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-5 rounded-lg border border-[#e1e7e3] bg-white shadow-soft">
        <div className="border-b border-[#e1e7e3] px-5 py-4">
          <p className="text-xs font-semibold uppercase text-[#0ba299]">Protocol evidence</p>
          <h2 className="mt-1 text-base font-semibold text-[#111112]">Cited snippets behind these warnings</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[48rem] text-left text-sm">
            <thead className="bg-[#fbfcfb] text-xs text-[#63656a]">
              <tr>
                <th className="px-5 py-3 font-semibold">Feature</th>
                <th className="px-5 py-3 font-semibold">Section</th>
                <th className="px-5 py-3 font-semibold">Page</th>
                <th className="px-5 py-3 font-semibold">Method</th>
                <th className="px-5 py-3 font-semibold">Snippet</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e1e7e3]">
              {assessment.evidence.slice(0, 8).map((item, index) => (
                <tr key={`${item.feature}-${index}`}>
                  <td className="px-5 py-4 font-medium text-[#111112]">{item.feature.replaceAll("_", " ")}</td>
                  <td className="px-5 py-4 text-[#63656a]">{item.section ?? "Unmapped"}</td>
                  <td className="px-5 py-4 text-[#63656a]">{item.page ?? "n/a"}</td>
                  <td className="px-5 py-4 text-[#63656a]">{item.method}</td>
                  <td className="max-w-xl px-5 py-4 text-[#63656a]">{item.snippet || "No snippet captured."}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <Simulator protocolId={assessment.protocol_id} assessment={assessment} />
      <ChatAssistant protocolId={assessment.protocol_id} />
    </AppShell>
  );
}
